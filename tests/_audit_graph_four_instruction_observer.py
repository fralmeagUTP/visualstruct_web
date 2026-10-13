"""Independent C17 event observer for the four current graph kernels.

The Python parser supplies source locations only. Generated C executes the
actual expressions, conditions, calls and writes. Events carry the values C
computed; none are copied from GraphMachine results. ABI and finite buffers are
asserted, and the original downloadable C is preserved next to each variant.
"""
from __future__ import annotations
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.domain.graph.c_algorithm_subset import Program,Node,GraphMachine,UNINIT
from app.services.c_code_service import CCodeService


def q(value):
    return json.dumps(value,ensure_ascii=True)


def jq(value):
    return q(json.dumps(value,ensure_ascii=True,separators=(',',':')))


class ObserverGenerator:
    def __init__(self,program):
        self.program=program;self.scopes=[];self.types=[];self.loops=[];self.function='';self.fn=None;self.thunks={}

    def hook(self,node,phase,name='',value=None):
        token=node.token if isinstance(node,Node) else node
        return f'obs_emit({q(self.function)},{token.pos},{q(phase)},{jq(name)},{jq(value)});'

    def typ(self,node):
        d=node.data;k=node.kind
        if k=='name':
            if d['name']=='NULL':return 'void *'
            if d['name'].startswith('LLONG'):return 'long long'
            if d['name'].startswith('INT_'):return 'int'
            for scope in reversed(self.types):
                if d['name'] in scope:return scope[d['name']]
            raise ValueError(('Native unknown type',d['name']))
        if k=='literal':return 'const char *' if isinstance(d['value'],str) else 'int'
        if k=='sizeof':return 'size_t'
        if k=='cast':return d['type']
        if k=='group':return self.typ(d['value'])
        if k=='field':
            f=d['field'];base=self.typ(d['base'])
            if f=='padre':return 'int *'
            if f=='v':return 'ListaVertice'
            if f=='a':return 'ListaArco'
            if f=='sig':return 'ListaVertice' if base=='ListaVertice' else 'ListaArco'
            return 'int'
        if k=='index':
            base=self.typ(d['base']);assert base.endswith('*'),base
            return base[:-1].strip()
        if k in {'unary','postfix'}:
            if d['op']=='!':return 'int'
            typ=self.typ(d['value']);return typ+' *' if d['op']=='&' else typ[:-1].strip() if d['op']=='*' else typ
        if k=='binary':
            if d['op'] in {'&&','||','==','!=','<','>','<=','>='}:return 'int'
            if d['op']=='=':return self.typ(d['left'])
            types={self.typ(d['left']),self.typ(d['right'])}
            return 'size_t' if 'size_t' in types else 'long long' if 'long long' in types else 'int'
        if k=='call':
            name=d['function'].data['name']
            return self.program.functions[name]['type'] if name in self.program.functions else 'void *' if name in {'malloc','calloc'} else 'void' if name=='free' else 'int'
        raise ValueError(('Native expression type',k))

    ASSIGN={'int':'int','long long':'long','size_t':'size','ListaArco':'arc','ListaVertice':'vertex',
            'int *':'int_pointer','long long *':'long_pointer','ListaArco *':'arc_pointer'}

    def expression(self,node):
        d=node.data;k=node.kind;pos=node.token.pos;fn=q(self.function)
        if k in {'literal','name','sizeof'}:return self.program.text(node)
        if k=='group':return '('+self.expression(d['value'])+')'
        if k=='cast':return '('+d['type']+')('+self.expression(d['value'])+')'
        if k=='field':return '('+self.expression(d['base'])+')'+('->' if d['indirect'] else '.')+d['field']
        if k=='index':return '('+self.expression(d['base'])+')['+self.expression(d['index'])+']'
        if k in {'unary','postfix'}:
            op=d['op']
            if op in {'++','--'}:
                typ=self.typ(d['value']);assert typ=='int',typ
                return f'obs_increment({fn},{pos},{jq(self.program.text(d["value"]))},&({self.expression(d["value"])}),{1 if op=="++" else -1},{1 if k=="postfix" else 0})'
            return op+'('+self.expression(d['value'])+')'
        if k=='binary':
            op=d['op'];left=d['left'];right=d['right']
            if op=='=':
                typ=self.typ(left);suffix=self.ASSIGN[typ]
                return f'obs_assign_{suffix}({fn},{pos},{jq(self.program.text(left))},&({self.expression(left)}),{self.expression(right)})'
            if op in {'&&','||'}:
                def operand(x):return f'obs_boolean({fn},{x.token.pos},"operand",{jq(self.program.text(x))},!!({self.expression(x)}))'
                return '('+operand(left)+' '+op+' '+operand(right)+')'
            return '('+self.expression(left)+' '+op+' '+self.expression(right)+')'
        if k=='call':
            name=d['function'].data['name'];args=', '.join(self.expression(arg) for arg in d['args'])
            if name in self.program.functions:
                self.thunks[pos]=(self.function,name)
                return f'obs_site_{pos}({args})'
            call=f'{name}({args})'
            if name=='printf':
                assert len(d['args'])==1 and d['args'][0].kind=='literal'
                call=f'obs_stdout({fn},{pos},{self.expression(d["args"][0])},{jq(d["args"][0].data["value"])})'
            return f'(obs_call({fn},{pos},{q(name)},{jq(name)}),{call})'
        raise ValueError(('Native unsupported expression',k))

    def condition(self,node):
        return f'obs_boolean({q(self.function)},{node.token.pos},"condition",{jq(self.program.text(node))},!!({self.expression(node)}))'

    def scope_open(self,node):
        self.scopes.append(node.token.pos);self.types.append({})
        return self.hook(node,'scope_enter',value=node.token.pos)

    def scope_close(self,node):
        assert self.scopes.pop()==node.token.pos;self.types.pop()
        return self.hook(node,'scope_exit',value=node.token.pos)

    def unwind(self,keep):
        return ''.join(f'obs_emit({q(self.function)},{pos},"scope_exit",{jq("")},{jq(pos)});' for pos in reversed(self.scopes[keep:]))

    def statement(self,node):
        d=node.data;k=node.kind
        if k=='block':
            out='{'+self.scope_open(node)
            out+=''.join(self.statement(item) for item in d['items'])
            out+=self.scope_close(node)
            if node is self.fn['body'] and self.fn['type']=='void':
                out+=self.hook(d['close'],'return')+'obs_leave();'
            return out+'}'
        if k=='decl':
            out=''
            for decl in d['declarations']:
                typ=decl['type'];name=decl['name'];self.types[-1][name]=typ
                initial={'padre':UNINIT,'n':UNINIT} if typ=='Conjunto' else UNINIT
                out+=typ+' '+name+';'+self.hook(decl['token'],'declare',name,initial)
                if typ=='Conjunto' or name=='suces_ok':
                    out+=f'obs_local(&{name},{q(name)},{self.scopes[-1]});'
                if decl['init'] is not None:
                    suffix=self.ASSIGN[typ]
                    out+=f'obs_assign_{suffix}({q(self.function)},{decl["token"].pos},{jq(name)},&{name},{self.expression(decl["init"])});'
            return out
        if k=='expr':return (self.expression(d['expr'])+';') if d['expr'] else ';'
        if k=='if':
            out='if('+self.condition(d['condition'])+')'+self.control_body(d['body'])
            if d['otherwise']:out+='else '+self.control_body(d['otherwise'])
            return out
        if k in {'while','for'}:
            out=''
            if k=='for':out+='{'+self.scope_open(node)+self.statement(d['initial'])
            self.loops.append(len(self.scopes))
            condition=self.condition(d['condition']) if d['condition'] else '1'
            out+='while('+condition+'){'+self.statement(d['body'])
            if k=='for' and d['increment']:out+=self.expression(d['increment'])+';'
            out+='}';self.loops.pop()
            if k=='for':out+=self.scope_close(node)+'}'
            return out
        if k=='break':return '{'+self.hook(node,'break')+self.unwind(self.loops[-1])+'break;}'
        if k=='goto':return '{'+self.hook(node,'goto',value=d['value'])+self.unwind(1)+'goto '+d['value']+';}'
        if k=='label':return d['name']+':;'+self.hook(node,'label',d['name'])
        if k=='return':
            typ=self.fn['type'];value=self.expression(d['value']) if d['value'] else None
            suffix='pointer' if typ in {'ListaArco','ListaVertice'} else 'integer'
            out='{'
            if value is not None:
                out+=typ+' obs_return_value = '+value+';'
                out+=f'obs_return_{suffix}({q(self.function)},{node.token.pos},obs_return_value);'
            else:out+=self.hook(node,'return')
            out+=self.unwind(0)+'obs_leave();return'+(' obs_return_value;' if value is not None else ';')+'}'
            return out
        raise ValueError(('Native statement',k))

    def control_body(self,node):
        # Multiple declaration hooks are one controlled statement without a new
        # modeled scope; the inserted C braces contain no original locals.
        return self.statement(node) if node.kind=='block' else '{'+self.statement(node)+'}'

    def body(self,name):
        self.function=name;self.fn=self.program.functions[name];self.types=[dict(self.fn['parameters'])];self.scopes=[];self.loops=[]
        header=f'obs_enter({q(name)},{self.fn["token"].pos});'
        for param,typ in self.fn['parameters']:
            if typ=='Grafo':
                for field in ['v','a']:header+=f'obs_parameter_pointer({q(name)},{self.fn["token"].pos},{jq(param+"."+field)},{param}.{field});'
            elif typ.endswith('*') or typ in {'ListaArco','ListaVertice'}:
                header+=f'obs_parameter_pointer({q(name)},{self.fn["token"].pos},{jq(param)},{param});'
            else:header+=f'obs_parameter_integer({q(name)},{self.fn["token"].pos},{jq(param)},{param});'
        body=self.statement(self.fn['body']);return '{'+header+body[1:]


HEADER=r'''
#include <stddef.h>
typedef struct NodoV *ListaVertice;
typedef struct NodoA *ListaArco;
typedef struct nodoGrafo Grafo;
typedef struct Conjunto Conjunto;
void obs_emit(const char*,size_t,const char*,const char*,const char*);
void obs_enter(const char*,size_t);void obs_leave(void);void obs_local(void*,const char*,size_t);
void obs_call(const char*,size_t,const char*,const char*);
void obs_parameter_pointer(const char*,size_t,const char*,const void*);
void obs_parameter_integer(const char*,size_t,const char*,long long);
void obs_return_pointer(const char*,size_t,const void*);void obs_return_integer(const char*,size_t,long long);
int obs_boolean(const char*,size_t,const char*,const char*,int);
int obs_increment(const char*,size_t,const char*,int*,int,int);
int obs_assign_int(const char*,size_t,const char*,int*,int);
long long obs_assign_long(const char*,size_t,const char*,long long*,long long);
size_t obs_assign_size(const char*,size_t,const char*,size_t*,size_t);
ListaArco obs_assign_arc(const char*,size_t,const char*,ListaArco*,ListaArco);
ListaVertice obs_assign_vertex(const char*,size_t,const char*,ListaVertice*,ListaVertice);
int *obs_assign_int_pointer(const char*,size_t,const char*,int**,int*);
long long *obs_assign_long_pointer(const char*,size_t,const char*,long long**,long long*);
ListaArco *obs_assign_arc_pointer(const char*,size_t,const char*,ListaArco**,ListaArco*);
int obs_stdout(const char*,size_t,const char*,const char*);
void *observed_malloc(size_t);void *observed_calloc(size_t,size_t);void observed_free(void*);
void obs_start(Grafo,int);void obs_end(void);
'''


SUPPORT=r'''
#include "observation.h"
#include "tad_grafo.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <limits.h>
_Static_assert(sizeof(int)==4 && INT_MAX==2147483647,"requires int32");
_Static_assert(sizeof(long long)==8 && sizeof(size_t)==8 && sizeof(void*)==8,"requires verified 64-bit ABI");
_Static_assert(sizeof(struct NodoV)==24 && sizeof(struct NodoA)==24,"requires verified node layout");
static int active,serial,frame_serial,frames[128],depth,total,attempts,fail_attempt,allocations,frees;
static void *pointers[4096];static int live[4096],owned[4096];static char identities[4096][96];
static const char *call_fn;static size_t call_pos;
void obs_emit(const char *fn,size_t pos,const char *phase,const char *name,const char *value){if(active)printf("E {\"function\":\"%s\",\"pos\":%zu,\"phase\":\"%s\",\"name\":%s,\"value\":%s}\n",fn,pos,phase,name,value);}
static void register_pointer(void *p,const char *id,int own){assert(total<4096);pointers[total]=p;live[total]=1;owned[total]=own;snprintf(identities[total],96,"%s",id);total++;}
static const char *pointer_json(const void *p){static char buffers[16][128];static unsigned cursor;char *s=buffers[(cursor++)%16];if(!p){strcpy(s,"\"NULL\"");return s;}for(int i=total-1;i>=0;i--){if(live[i]&&pointers[i]==p){snprintf(s,128,"\"%s\"",identities[i]);return s;}}assert(!"unregistered live pointer value");return "null";}
static void integer_event(const char *fn,size_t pos,const char *phase,const char *name,long long value){char s[64];snprintf(s,sizeof s,"%lld",value);obs_emit(fn,pos,phase,name,s);}
void obs_enter(const char *fn,size_t pos){if(!active)return;assert(depth<128);frames[depth++]=++frame_serial;obs_emit(fn,pos,"enter","\"\"","null");}
void obs_leave(void){if(active){assert(depth>0);depth--;}}
void obs_local(void *p,const char *name,size_t scope){if(active){char id[96];snprintf(id,sizeof id,"&F%d:B%zu:%s",frames[depth-1],scope,name);register_pointer(p,id,0);}}
void obs_call(const char *fn,size_t pos,const char *callee,const char *name){(void)callee;if(active){call_fn=fn;call_pos=pos;obs_emit(fn,pos,"call",name,"null");}}
void obs_parameter_pointer(const char *fn,size_t pos,const char *name,const void *p){if(active)obs_emit(fn,pos,"parameter",name,pointer_json(p));}
void obs_parameter_integer(const char *fn,size_t pos,const char *name,long long v){integer_event(fn,pos,"parameter",name,v);}
void obs_return_pointer(const char *fn,size_t pos,const void *p){if(active)obs_emit(fn,pos,"return","\"\"",pointer_json(p));}
void obs_return_integer(const char *fn,size_t pos,long long v){integer_event(fn,pos,"return","\"\"",v);}
int obs_boolean(const char *fn,size_t pos,const char *phase,const char *name,int v){integer_event(fn,pos,phase,name,v);return v;}
int obs_increment(const char *fn,size_t pos,const char *name,int *p,int delta,int post){int old=*p;*p+=delta;integer_event(fn,pos,"write",name,*p);return post?old:*p;}
#define INTEGER_ASSIGN(suffix,type) type obs_assign_##suffix(const char *fn,size_t pos,const char *name,type *p,type v){*p=v;integer_event(fn,pos,"write",name,(long long)v);return v;}
INTEGER_ASSIGN(int,int) INTEGER_ASSIGN(long,long long) INTEGER_ASSIGN(size,size_t)
#define POINTER_ASSIGN(suffix,type) type obs_assign_##suffix(const char *fn,size_t pos,const char *name,type *p,type v){*p=v;if(active)obs_emit(fn,pos,"write",name,pointer_json(v));return v;}
POINTER_ASSIGN(arc,ListaArco) POINTER_ASSIGN(vertex,ListaVertice) POINTER_ASSIGN(int_pointer,int*) POINTER_ASSIGN(long_pointer,long long*) POINTER_ASSIGN(arc_pointer,ListaArco*)
int obs_stdout(const char *fn,size_t pos,const char *text,const char *json){obs_emit(fn,pos,"stdout","\"printf\"",json);return printf("%s",text);}
static void *track_allocation(void *p,size_t size,int zeroed){if(active){char id[32],value[224];if(p){snprintf(id,sizeof id,"M%d",++serial);register_pointer(p,id,1);allocations++;}snprintf(value,sizeof value,"{\"pointer\":%s,\"size\":%zu,\"zeroed\":%s}",pointer_json(p),size,zeroed?"true":"false");obs_emit(call_fn,call_pos,"allocate",zeroed?"\"calloc\"":"\"malloc\"",value);}return p;}
void *observed_malloc(size_t n){if(active&&++attempts==fail_attempt)return track_allocation(NULL,n,0);return track_allocation(malloc(n),n,0);}
void *observed_calloc(size_t n,size_t s){if(active&&++attempts==fail_attempt)return track_allocation(NULL,n*s,1);return track_allocation(calloc(n,s),n*s,1);}
void observed_free(void *p){char value[128];if(active){snprintf(value,sizeof value,"%s",pointer_json(p));if(p){int found=0;for(int i=total-1;i>=0;i--){if(live[i]&&pointers[i]==p){assert(owned[i]);live[i]=0;found=1;frees++;break;}}assert(found);}}free(p);if(active)obs_emit(call_fn,call_pos,"free","\"free\"",value);}
void obs_start(Grafo g,int fail){active=0;total=0;serial=0;frame_serial=0;depth=0;attempts=0;allocations=0;frees=0;fail_attempt=fail;int n=0;for(ListaVertice v=g.v;v;v=v->sig)n++;for(ListaVertice v=g.v;v;v=v->sig){char id[32];snprintf(id,sizeof id,"V%d",n--);register_pointer(v,id,0);}int m=0;for(ListaArco a=g.a;a;a=a->sig)m++;for(ListaArco a=g.a;a;a=a->sig){char id[32];snprintf(id,sizeof id,"E%d",m--);register_pointer(a,id,0);}active=1;}
void obs_end(void){assert(depth==0);active=0;int remaining=0;for(int i=0;i<total;i++)remaining+=live[i]&&owned[i];printf("MEMORY %d %d %d %d\n",attempts,allocations,frees,remaining);}
'''


def cases_from_baseline(algorithm):
    path=ROOT/'tests'/('_audit_graph_'+algorithm+'_baseline.py')
    module=ast.parse(path.read_text(encoding='utf-8-sig'))
    for n in module.body:
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CASES' for t in n.targets):
            # Dijkstra uses dict calls and MAX expressions: evaluate only this
            # trusted repository assignment, never invoke its baseline script.
            code=compile(ast.Module(body=[n],type_ignores=[]),str(path),'exec')
            context={'MAX':2147483647,'dict':dict};exec(code,{'__builtins__':{}},context);return context['CASES']
    raise ValueError('Fixture assignment missing')


def function_body_span(source,name):
    match=re.search(r'^(?:\s*static\s+)?\s*(?:int|void|Grafo|ListaArco|ListaVertice)\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',source,re.M)
    assert match,name
    start=source.index('{',match.start());depth=1;end=start+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return start,end


def run_algorithm(algorithm,out,fixtures=None):
    operation='run_'+algorithm;source=CCodeService._build_graph_data()['operations'][operation];program=Program(source)
    out.mkdir(parents=True,exist_ok=True);(out/'displayed-source.c').write_text(source,encoding='utf-8')
    original=(ROOT/'docs/tads_C/tad_grafo.c').read_text(encoding='utf-8-sig');variant=original;generator=ObserverGenerator(program);replacements=[]
    for name in program.functions:
        start,end=function_body_span(original,name);replacements.append((start,end,generator.body(name)))
    for start,end,body in sorted(replacements,reverse=True):variant=variant[:start]+body+variant[end:]
    prototypes=[];definitions=[]
    for pos,(caller,callee) in generator.thunks.items():
        fn=program.functions[callee]
        params=', '.join(typ+' arg'+str(i) for i,(_,typ) in enumerate(fn['parameters'])) or 'void'
        args=', '.join('arg'+str(i) for i in range(len(fn['parameters'])))
        signature=fn['type']+' obs_site_'+str(pos)+'('+params+')'
        prototypes.append(signature+';')
        call=callee+'('+args+');'
        definitions.append(signature+'{obs_call('+q(caller)+','+str(pos)+','+q(callee)+','+jq(callee)+');'+('return '+call if fn['type']!='void' else call)+'}')
    variant+='\n'+'\n'.join(definitions)+'\n'
    native_header=HEADER+'\n'+'\n'.join(prototypes)+'\n'
    (out/'tad_grafo.original.c').write_bytes((ROOT/'docs/tads_C/tad_grafo.c').read_bytes());(out/'tad_grafo.c').write_text(variant,encoding='utf-8');(out/'observation.h').write_text(native_header,encoding='utf-8');(out/'observation.c').write_text(SUPPORT,encoding='utf-8')
    for stem in ['tad_grafo','tad_cola']:
        (out/(stem+'.h')).write_bytes((ROOT/'docs/tads_C'/(stem+'.h')).read_bytes())
    (out/'tad_cola.c').write_bytes((ROOT/'docs/tads_C/tad_cola.c').read_bytes())
    fixtures=cases_from_baseline(algorithm) if fixtures is None else fixtures
    main='#include "tad_grafo.h"\n#include "observation.h"\n#include <stdio.h>\n#include <stdlib.h>\n#include <limits.h>\nint main(void){\n'
    for i,c in enumerate(fixtures):
        main+='{Grafo g=grafo_crear();'
        for v in c['v']:main+=f'g=grafo_insertar_vertice(g,{v});'
        for a,b,w in c['e']:
            main+=f'g=grafo_insertar_arco(g,{a},{b},{w});'
            if not c.get('directed',True) and a!=b:main+=f'g=grafo_insertar_arco(g,{b},{a},{w});'
        args=['g']+([str(c['start']),str(c['end'])] if algorithm in {'bellman_ford','dijkstra'} else [str(c['start'])] if algorithm=='prim' else [])
        main+=f'printf("BEGIN {i}\\n");obs_start(g,{c.get("fail_allocation",0)});ListaArco result=grafo_{algorithm}('+','.join(args)+');obs_end();printf("RESULT [");int first=1;for(ListaArco a=result;a;a=a->sig){printf("%s[%d,%d,%d]",first?"":",",a->origen,a->destino,a->costo);first=0;}puts("]");while(result){ListaArco p=result;result=result->sig;free(p);}while(g.a){ListaArco p=g.a;g.a=g.a->sig;free(p);}while(g.v){ListaVertice p=g.v;g.v=g.v->sig;free(p);}}\n'
    main+='return 0;}\n';(out/'observed-main.c').write_text(main,encoding='utf-8')
    compiler=shutil.which('gcc');assert compiler;objects=[];logs=[]
    for stem in ['tad_grafo','tad_cola']:
        obj=out/(stem+'.o');p=subprocess.run([compiler,'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-include',str(out/'observation.h'),'-Dmalloc=observed_malloc','-Dcalloc=observed_calloc','-Dfree=observed_free','-c',str(out/(stem+'.c')),'-o',str(obj)],capture_output=True,text=True,timeout=30);logs.append(p.stdout+p.stderr)
        if p.returncode: (out/'compile.log').write_text(''.join(logs),encoding='utf-8');raise AssertionError(p.stderr[:1600])
        assert not p.stderr,p.stderr[:1600];objects.append(obj)
    p=subprocess.run([compiler,'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed-main.c'),str(out/'observation.c'),*map(str,objects),'-o',str(out/'native.exe')],capture_output=True,text=True,timeout=30);logs.append(p.stdout+p.stderr);(out/'compile.log').write_text(''.join(logs),encoding='utf-8');assert p.returncode==0 and not p.stderr,p.stderr[:1600]
    p=subprocess.run([str(out/'native.exe')],capture_output=True,text=True,timeout=30);(out/'native.stdout.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
    segments=re.split(r'^BEGIN (\d+)\n',p.stdout,flags=re.M);rows=[]
    for k in range(1,len(segments),2):
        i=int(segments[k]);text=segments[k+1];case=fixtures[i]
        events=[json.loads(line[2:]) for line in text.splitlines() if line.startswith('E ')]
        arcs=[]
        for o,d,w in case['e']:
            # Duplicate arc updates keep their original C list position.
            candidates=[(o,d,w)]+([(d,o,w)] if not case.get('directed',True) and o!=d else [])
            for candidate in candidates:
                found=next((j for j,existing in enumerate(arcs) if existing[:2]==candidate[:2]),None)
                if found is None:arcs.append(candidate)
                else:arcs[found]=candidate
        machine=GraphMachine(program,case['v'],arcs,fail_allocation=case.get('fail_allocation'));params=[machine.graph]+([case['start'],case['end']] if algorithm in {'bellman_ford','dijkstra'} else [case['start']] if algorithm=='prim' else [])
        result=machine.invoke('grafo_'+algorithm,params)
        expected=[{key:value for key,value in event.items() if key!='line_index'} for event in machine.events]
        (out/f'native-events-{i}.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8');(out/f'python-events-{i}.json').write_text(json.dumps(expected,ensure_ascii=False,indent=2),encoding='utf-8')
        differences=[]
        if len(events)!=len(expected):differences.append({'event_counts':[len(events),len(expected)]})
        for j,(actual,wanted) in enumerate(zip(events,expected)):
            if actual!=wanted:
                differences.append({'event':j,'C':actual,'Python':wanted});break
        result_arcs=[];pointer=result
        while pointer!='NULL':
            fields=machine.heap[pointer]['fields'];result_arcs.append([fields['origen'],fields['destino'],fields['costo']]);pointer=fields['sig']
        native_result=json.loads(re.search(r'^RESULT (.*)$',text,re.M)[1]);assert result_arcs==native_result,(case['name'],result_arcs,native_result)
        memory=list(map(int,re.search(r'^MEMORY (\d+) (\d+) (\d+) (\d+)$',text,re.M).groups()));assert memory==[machine.attempts,machine.allocations,machine.frees,sum(not n['borrowed'] for n in machine.heap.values())]
        rows.append(dict(name=case['name'],input=case,native_events=len(events),python_events=len(expected),differences=differences,result_arcs=result_arcs,memory=memory,stdout=machine.stdout,conditions=sum(e['phase']=='condition' for e in events),operands=sum(e['phase']=='operand' for e in events)))
        print(algorithm,case['name'],len(events),'MATCH' if not differences else differences[:1],flush=True)
    report=dict(algorithm=algorithm,fixtures=len(rows),rows=rows,strict_C17_O2=True,original_C_sha256=hashlib.sha256((out/'tad_grafo.original.c').read_bytes()).hexdigest(),scope='Native raw C instruction comparison; API preconditions reviewed separately, not simulated as C.',differing_fixtures=sum(bool(row['differences']) for row in rows))
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');return report


if __name__=='__main__':
    algorithm=sys.argv[1];out=Path(sys.argv[2]).resolve()
    fixtures=None
    if len(sys.argv)>3 and sys.argv[3]=='--allocation-faults':
        base=cases_from_baseline(algorithm)[2 if algorithm in {'bellman_ford','dijkstra'} else 1]
        attempts={'bellman_ford':6,'prim':13,'dijkstra':9,'kruskal':5}[algorithm]
        fixtures=[{**base,'name':base['name']+'_malloc_attempt_'+str(i),'fail_allocation':i} for i in range(1,attempts+1)]
    run_algorithm(algorithm,out,fixtures=fixtures)
