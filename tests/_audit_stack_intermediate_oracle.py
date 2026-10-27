"""Observe real stack assignments and allocator calls in a verified source copy."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PREFIX=r"""
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#define VS_OBSERVE 1
static void *qa_blocks[32];
static unsigned qa_ids[32], qa_sequence, qa_next_id, qa_live;
static int qa_fail_next;
static unsigned qa_id(const void *p) {
    unsigned i;
    if (p == NULL) return 0;
    for (i=0; i<32; ++i) if (qa_blocks[i] == p) return qa_ids[i];
    fprintf(stderr,"observer: unknown live object\n"); exit(90);
}
static void qa_event(const char *kind,const char *phase,const char *fn,int line,unsigned id,int value,unsigned next,unsigned head) {
    int value_known=strstr(kind,"assignment")!=NULL;
    int next_known=strcmp(kind,"link_assignment")==0 || strcmp(kind,"head_assignment")==0;
    fprintf(stderr,"{\"schema\":\"didactic-c-event/v1\",\"sequence\":%u,\"structure_id\":\"stack\",\"source\":\"docs/tads_C/tad_pila.c\",\"function\":\"%s\",\"line\":%d,\"event\":\"%s\",\"phase\":\"%s\",\"id\":%u,\"value\":%d,\"next\":%u,\"head\":%u,\"heap_live\":%u,\"value_known\":%s,\"next_known\":%s,\"head_known\":%s}\n",++qa_sequence,fn,line,kind,phase,id,value,next,head,qa_live,value_known ? "true" : "false",next_known ? "true" : "false",value_known ? "true" : "false");
}
static void *qa_malloc(size_t size,const char *fn,int line) {
    unsigned i; void *p;
    qa_event("allocation","before",fn,line,0,0,0,0);
    if (qa_fail_next) { qa_fail_next=0; p=NULL; } else p=malloc(size);
    if (p != NULL) {
        for (i=0;i<32 && qa_blocks[i]!=NULL;++i) { }
        if (i==32) { fprintf(stderr,"observer capacity exceeded\n"); exit(91); }
        qa_blocks[i]=p; qa_ids[i]=++qa_next_id; ++qa_live;
    }
    qa_event(p==NULL ? "allocation_failed" : "allocation","after",fn,line,qa_id(p),0,0,0);
    return p;
}
static void qa_free(void *p,const char *fn,int line) {
    unsigned id=qa_id(p),i;
    qa_event("free","before",fn,line,id,0,0,0);
    /* Erase the alias while the object is still alive; never inspect p after free. */
    if (p!=NULL) for (i=0;i<32;++i) if (qa_blocks[i]==p) { qa_blocks[i]=NULL; break; }
    free(p);
    if (id!=0) --qa_live;
    qa_event("free","after",fn,line,id,0,0,0);
}
static int qa_printf(const char *fn,int line,const char *format,...) {
    va_list args,copy; int result,length,i; char text[512];
    va_start(args,format); va_copy(copy,args);
    result=vprintf(format,args); length=vsnprintf(text,sizeof text,format,copy);
    va_end(copy); va_end(args);
    if (length<0 || (size_t)length>=sizeof text) { fprintf(stderr,"observer console overflow\n"); exit(92); }
    fprintf(stderr,"{\"schema\":\"didactic-c-event/v1\",\"sequence\":%u,\"event\":\"console\",\"phase\":\"after\",\"function\":\"%s\",\"line\":%d,\"text\":\"",++qa_sequence,fn,line);
    for (i=0;i<length;++i) {
        unsigned char ch=(unsigned char)text[i];
        if (ch=='"' || ch=='\\') fprintf(stderr,"\\%c",ch);
        else if (ch<32) fprintf(stderr,"\\u%04x",(unsigned)ch);
        else fputc(ch,stderr);
    }
    fprintf(stderr,"\"}\n"); return result;
}
#define malloc(size) qa_malloc((size),__func__,__LINE__)
#define free(pointer) qa_free((pointer),__func__,__LINE__)
#define printf(...) qa_printf(__func__,__LINE__,__VA_ARGS__)
"""
MAIN=r"""
#line 1 "stack_observer_main.c"
int main(int argc,char **argv) {
    ptrPila p=NULL;
    (void)argv;
    if (argc>1) {
#ifdef VS_OBSERVE
        qa_fail_next=1;
#endif
        pila_apilar(&p,99);
        printf("EMPTY=%d\n",p==NULL);
        pila_destruir(&p);
        return 0;
    }
    (void)pila_desapilar(NULL);
    pila_apilar(&p,7); pila_apilar(&p,7); pila_mostrar(p);
    printf("RETURN=%d\n",pila_desapilar(&p));
    pila_destruir(&p); printf("EMPTY=%d\n",p==NULL);
    return 0;
}
"""
def instrument(source):
    result=[PREFIX,'#line 1 "docs/tads_C/tad_pila.c"\n']; hits={}
    hooks={
      'aux->nro = valor;':'qa_event("value_assignment","after",__func__,__LINE__,qa_id(aux),valor,0,qa_id(*p));',
      'aux->sgte = *p;':'qa_event("link_assignment","after",__func__,__LINE__,qa_id(aux),aux->nro,qa_id(aux->sgte),qa_id(*p));',
      '*p = aux;':'qa_event("head_assignment","after",__func__,__LINE__,qa_id(aux),aux->nro,qa_id(aux->sgte),qa_id(*p));',
      '*p = aux->sgte;':'qa_event("head_assignment","after",__func__,__LINE__,qa_id(aux),aux->nro,qa_id(aux->sgte),qa_id(*p));',
    }
    for n,line in enumerate(source.splitlines(keepends=True),1):
        result.append(line)
        key=line.strip()
        if key in hooks:
            hits[key]=hits.get(key,0)+1
            result.append('    '+hooks[key].replace('__LINE__',str(n))+'\n#line '+str(n+1)+' "docs/tads_C/tad_pila.c"\n')
    assert hits=={'aux->nro = valor;':1,'aux->sgte = *p;':1,'*p = aux;':1,'*p = aux->sgte;':2},hits
    return ''.join(result),hits

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    source_path=ROOT/'docs/tads_C/tad_pila.c';raw=source_path.read_bytes();sha=hashlib.sha256(raw).hexdigest();source=raw.decode('utf-8-sig').replace('\r\n','\n')
    observed,hits=instrument(source);(out/'original.c').write_bytes(raw);(out/'observed.c').write_bytes((observed+MAIN).encode('utf-8'));(out/'control.c').write_bytes((source+MAIN).encode('utf-8'))
    gcc=r'C:\msys64\mingw64\bin\gcc.exe'
    for name in ['control','observed']:
        subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/(name+'.c')),'-o',str(out/(name+'.exe'))],check=True,capture_output=True,timeout=30)
    control=subprocess.run([str(out/'control.exe')],capture_output=True,check=True,timeout=10)
    actual=subprocess.run([str(out/'observed.exe')],capture_output=True,check=True,timeout=10)
    assert actual.stdout==control.stdout
    (out/'nominal.stdout').write_bytes(actual.stdout);(out/'nominal.events.jsonl').write_bytes(actual.stderr)
    events=[json.loads(line) for line in actual.stderr.splitlines()];assert all(row['sequence']==i+1 for i,row in enumerate(events))
    for event in events:
        if event.get('event') in ['value_assignment','link_assignment','head_assignment']:
            assert source.splitlines()[event['line']-1].strip() in hits
            assert event['value_known'] and event['head_known']
        if event.get('event')=='value_assignment': assert event['next_known'] is False
        if event.get('event') in ['allocation','free']: assert event['value_known'] is False
    for event in events:
        if event.get('event') in ['allocation','allocation_failed','free']:
            assert ('malloc(' if event['event'].startswith('allocation') else 'free(aux);') in source.splitlines()[event['line']-1]
    allocated=[x['id'] for x in events if x.get('event')=='allocation' and x.get('phase')=='after'];freed=[x['id'] for x in events if x.get('event')=='free' and x.get('phase')=='after'];assert allocated==[1,2] and freed==[2,1]
    heads=[x['head'] for x in events if x.get('event')=='head_assignment'];assert heads==[1,2,1,0]
    console=''.join(x['text'] for x in events if x.get('event')=='console');assert console.encode()==actual.stdout.replace(b'\r\n',b'\n')
    fault=subprocess.run([str(out/'observed.exe'),'fault'],capture_output=True,check=True,timeout=10);(out/'fault.stdout').write_bytes(fault.stdout);(out/'fault.events.jsonl').write_bytes(fault.stderr);fe=[json.loads(line) for line in fault.stderr.splitlines()]
    assert sum(x.get('event')=='allocation_failed' for x in fe)==1
    assert not any(x.get('event') in ['head_assignment','link_assignment','value_assignment','free'] for x in fe)
    assert b'EMPTY=1' in fault.stdout
    assert source_path.read_bytes()==raw
    report={'schema':'stack-intermediate-oracle/v1','source_sha256':sha,'source_unchanged':True,'observer_only_copy':True,'anchors':hits,'c17_strict':True,'source_lines_verified':True,'uninitialized_fields_explicitly_unknown':True,'nominal_stdout_equals_control':True,'nominal_events':len(events),'allocated_ids':allocated,'freed_ids':freed,'intermediate_heads':heads,'console_equals_stdout_after_crlf_normalization':True,'fault_injection':'one malloc returns NULL; source logic unchanged','fault_events':len(fe),'fault_preserves_empty_head':True,'asan_ubsan':False,'scope':'stack pilot malloc/free and relevant value/link/head assignments; not full13TAD matrix'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
