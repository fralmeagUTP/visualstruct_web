"""LOW listing projections and actual C formatter bounded-buffer observations."""
from pathlib import Path
import json,subprocess,shutil,sys,re
R=Path.cwd();sys.path.insert(0,str(R));from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-listings-baseline-low';N=E/'native';N.mkdir(exist_ok=True);sys.stdout.reconfigure(encoding='utf-8')
CASES=[('empty',3,[]),('mixed',3,[(1,10),(4,40),(7,40),(0,0),(-1,-10)]),('extremes',1,[(-2147483648,2147483647),(2147483647,-2147483648),(0,-2147483648),(1,0)]),('sparse',7,[(-7,70),(7,70),(14,-14),(2,2)])]
PREFIX=r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "tad_tabla_hash.h"
static void sample(int cid,int sample_id,const TablaHash*t,size_t cap,int null_dest){
 struct {unsigned char left[16];unsigned char buffer[4096];unsigned char right[16];} block;
 memset(&block,0xA5,sizeof(block));th_formatear(t,null_dest?NULL:(char*)block.buffer,cap);
 int outside=0;for(size_t i=cap;i<sizeof(block.buffer);i++)outside+=block.buffer[i]!=0xA5;
 for(int i=0;i<16;i++){assert(block.left[i]==0xA5);assert(block.right[i]==0xA5);}assert(!outside);
 printf("{\"case\":%d,\"sample\":%d,\"capacity\":%zu,\"null_destination\":%s,\"outside_changed\":%d,\"first_byte\":%u,\"hex\":\"",cid,sample_id,cap,null_dest?"true":"false",outside,(unsigned)block.buffer[0]);
 for(size_t i=0;i<cap;i++){printf("%02x",(unsigned)block.buffer[i]);}printf("\",\"pairs\":[");int first=1;
 if(t&&t->buckets){for(int i=0;i<t->capacidad;i++){for(const THNodo*n=t->buckets[i];n;n=n->siguiente){if(!first)printf(",");first=0;printf("[%d,%d]",n->clave,n->valor);}}}printf("]}\n");}
'''
def lit(v):return '(-2147483647-1)' if v==-2147483648 else str(v)
main='int main(void){'
for ci,(name,capacity,pairs) in enumerate(CASES):
 main+='{TablaHash t={0};th_inicializar(&t,'+str(capacity)+');if(!t.buckets)return 1;'
 for k,v in pairs:main+='if(!th_insertar(&t,'+lit(k)+','+lit(v)+'))return 2;'
 for si,cap in enumerate([0,1,2,8,16,64,128,2048,4096]):main+='sample('+str(ci)+','+str(si)+',&t,'+str(cap)+',0);'
 main+='th_destruir(&t);}'
main+='sample(4,0,NULL,64,0);{TablaHash t={0};sample(4,1,&t,64,0);sample(4,2,&t,64,1);}return 0;}'
(N/'probe.c').write_text(PREFIX+main,encoding='utf-8');shutil.copyfile(R/'docs/tads_C/tad_tabla_hash.c',N/'tad_tabla_hash.c');shutil.copyfile(R/'docs/tads_C/tad_tabla_hash.h',N/'tad_tabla_hash.h');r=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'probe.c'),str(N/'tad_tabla_hash.c'),'-o',str(N/'probe.exe')],capture_output=True,text=True);(N/'compile.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr;r=subprocess.run([str(N/'probe.exe')],capture_output=True,text=True);(N/'native.jsonl').write_text(r.stdout,encoding='utf-8');assert r.returncode==0;native=[json.loads(line) for line in r.stdout.splitlines()]
for ci,(_,cap,pairs) in enumerate(CASES):
 full=next(row for row in native if row['case']==ci and row['capacity']==4096);full_bytes=bytes.fromhex(full['hex']).split(b'\0',1)[0]
 for row in [r for r in native if r['case']==ci]:
  buf=bytes.fromhex(row['hex']);n=row['capacity']
  assert row['outside_changed']==0
  if n==0:assert row['first_byte']==0xA5
  else:assert buf.split(b'\0',1)[0]==full_bytes[:n-1] and b'\0' in buf
 assert [list(map(int,p)) for p in re.findall(rb'\((-?\d+):(-?\d+)\)',full_bytes)]==full['pairs']
app=create_app();app.config['TESTING']=True;report=[]
for ci,(name,capacity,pairs) in enumerate(CASES):
 client=app.test_client();client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':capacity}})
 for k,v in pairs:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 n=next(r for r in native if r['case']==ci and r['capacity']==2048);ordered=n['pairs']
 for op in ['keys','values','items']:
  response=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{}});data=response.get_json();expected=ordered if op=='items' else [p[0 if op=='keys' else 1] for p in ordered];assert response.status_code==200 and data['result']==expected;trace=data['execution_trace'];report.append({'case':name,'operation':op,'capacity':capacity,'pairs':pairs,'expected_projection':expected,'C_formatted_hex':n['hex'],'C_formatter_result_is_buffer_not_projection':True,'result_matches_C_projection':True,'history_length':len(data['history']),'frames':len(trace['steps']),'debug':any('debug' in f for f in trace['steps']),'formatter_definition_present':'void th_formatear(' in trace['source_code'],'append_definition_present':'void th_append_text(' in trace['source_code'],'data':data})
(E/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');(E/'buffer-report.json').write_text(json.dumps(native,indent=2),encoding='utf-8');print(json.dumps({'C_formatter_calls':len(native),'API_projections':len(report),'ordered_results_matches':len(report),'typed_debug_cases':sum(r['debug'] for r in report),'formatter_definitions':sum(r['formatter_definition_present'] for r in report),'append_definitions':sum(r['append_definition_present'] for r in report),'limit':'C projections come from independent live-node traversal/parsed formatter, not fictional C array-return functions; buffer caller sentinel-initialized'}))
