"""Instrument actual shown C; observe native frames, returns and printf independently."""
import json,re,subprocess,shutil
from pathlib import Path
HELPER=r'''
#include <stdarg.h>
#include <string.h>
static RBT nodes[128];static int node_count,depth=-1,serial,returned,wrapper,wrapper_set;static char output[16384];static int output_len;
typedef struct{const char*name;int value,state;}Var;
typedef struct{const char*function;int id,np,nl;Var parameters[8],locals[8];}Frame;
static Frame frames[128];
static int ident(RBT n){if(!n)return 0;for(int i=0;i<node_count;i++)if(nodes[i]==n)return i+1;return -1;}
static void reg(RBT n){if(!n)return;nodes[node_count++]=n;reg(n->izq);reg(n->der);}
static void emit(int line,const char*phase,int result){
 printf("AUDIT {\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"returned\":%d,\"wrapper\":%d,\"wrapper_set\":%d,\"frames\":[",line,phase,result,returned,wrapper,wrapper_set);
 for(int i=0;i<=depth;i++){Frame*f=&frames[i];printf("%s{\"function\":\"%s\",\"id\":\"F%d\",\"parameters\":{",i?",":"",f->function,f->id);for(int j=0;j<f->np;j++)printf("%s\"%s\":%d",j?",":"",f->parameters[j].name,f->parameters[j].value);printf("},\"locals\":{");for(int j=0;j<f->nl;j++){printf("%s\"%s\":",j?",":"",f->locals[j].name);if(f->locals[j].state==1)printf("\"sin inicializar\"");else printf("%d",f->locals[j].value);}printf("}}");}
 printf("],\"stdout_hex\":\"");for(int i=0;i<output_len;i++)printf("%02x",(unsigned char)output[i]);printf("\",\"heap\":[");for(int i=0;i<node_count;i++){RBT n=nodes[i];printf("%s{\"id\":%d,\"value\":%d,\"left\":%d,\"right\":%d,\"parent\":%d,\"color\":\"%s\"}",i?",":"",i+1,n->nro,ident(n->izq),ident(n->der),ident(n->padre),n->rbt_color==ROJO?"RED":n->rbt_color==NEGRO?"BLACK":"INVALID");}puts("]}");
}
static void enter(const char*fn){frames[++depth]=(Frame){.function=fn,.id=++serial};}
static void par(const char*name,int value){Frame*f=&frames[depth];f->parameters[f->np++]=(Var){.name=name,.value=value,.state=2};}
static void local(const char*name,int value,int state){Frame*f=&frames[depth];for(int i=0;i<f->nl;i++)if(!strcmp(f->locals[i].name,name)){f->locals[i].value=value;f->locals[i].state=state;return;}f->locals[f->nl++]=(Var){.name=name,.value=value,.state=state};}
static int condition(int line,int result){emit(line,"condition",!!result);return result;}
static int operand(int line,int result){emit(line,"operand",!!result);return result;}
static int leave(int line,int result){if(depth==0){wrapper=result;wrapper_set=1;}depth--;returned=result;emit(line,"return",result);return result;}
static RBT leave_pointer(int line,RBT result){(void)leave(line,ident(result));return result;}
static void leave_void(int line){(void)leave(line,-2);}
static int output_at(int line,const char*fmt,...){va_list ap;va_start(ap,fmt);int n=vsnprintf(output+output_len,sizeof(output)-(size_t)output_len,fmt,ap);va_end(ap);if(n<0||output_len+n>=(int)sizeof(output))exit(91);output_len+=n;emit(line,"printf",-2);return n;}
'''
def observe(source,operation,seed,target,raw_c,raw_h,out,mutation="",live_fixture=None):
 out.mkdir(parents=True,exist_ok=True);(out/'downloaded.c').write_bytes(raw_c);(out/'downloaded.h').write_bytes(raw_h);lines=source.splitlines();text=source
 def body(fn):
  match=re.search(r'(?:static\s+)?(?:void|RBT|int)\s+'+fn+r'\([^;{}]*\)\s*\{',text);assert match,fn
  a=match.start();p=match.end();level=1
  while level:
   if text[p]=='{':level+=1
   elif text[p]=='}':level-=1
   p+=1
  return a,p,text[a:p]
 functions={'inorden':['rbt_inorden'],'altura':['rbt_altura'],'validar':['rbt_validar_altura_negra','rbt_validar'],'buscar':['rbt_buscar']}[operation]+['ejecutar_'+operation]
 patches=[]
 for fn in functions:
  a,b,t=body(fn);orig=t;start=source[:a].count('\n');end=start+orig.count('\n')
  def line(snippet,last=False):
   matches=[i+1 for i in range(start,end+1) if snippet in lines[i]];assert matches,(fn,snippet);return matches[-1] if last else matches[0]
  def replace(old,new):
   nonlocal t
   assert t.count(old)==1,(fn,old,t.count(old));t=t.replace(old,new)
  names={'rbt_inorden':[('nodo',True)],'rbt_altura':[('nodo',True)],'rbt_validar':[('raiz',True)],'rbt_validar_altura_negra':[('nodo',True),('padreEsperado',True),('tieneMin',False),('minimo',False),('tieneMax',False),('maximo',False)],'rbt_buscar':[('nodoRBT',True),('dato',False)]}.get(fn,[('raiz',True)]+([('dato',False)] if operation=='buscar' else []))
  entry='enter("'+fn+'");'+''.join('par("'+n+'",'+('ident('+n+')' if ptr else n)+');' for n,ptr in names)+f'emit({start+1},"enter",-2);'
  t=t.replace('{','{'+entry,1)
  if fn=='rbt_inorden':
   replace('if (nodo == NULL) return;',f'if(condition({line("if (nodo == NULL)")},nodo==NULL)){{leave_void({line("return;")});return;}}')
   for field in ['izq','der']:
    old='rbt_inorden(nodo->'+field+');';number=line(old);replace(old,f'emit({number},"call",-2);{old}emit({number},"resume",-2);')
   replace('printf("%d ", nodo->nro);',f'output_at({line("printf(")},"%d ",nodo->nro);');t=t[:-1]+f'leave_void({end+1});}}'
  elif fn=='rbt_altura':
   replace('if (nodo == NULL) return 0;',f'if(condition({line("if (nodo == NULL)")},nodo==NULL))return leave({line("return 0;")},0);')
   for name,field in [('altIzq','izq'),('altDer','der')]:
    old=f'int {name} = rbt_altura(nodo->{field});';number=line(old);replace(old,f'int {name}=(local("{name}",0,1),emit({number},"call",-2),rbt_altura(nodo->{field}));local("{name}",{name},2);emit({number},"assignment",-2);')
   old='return (altIzq > altDer ? altIzq : altDer) + 1;';number=line(old);replace(old,f'return leave({number},(condition({number},altIzq>altDer)?altIzq:altDer)+1);')
  elif fn=='rbt_validar_altura_negra':
   for snippet,expr,result in [('if (nodo == NULL)','nodo==NULL',1),('if (nodo->padre','nodo->padre!=padreEsperado',0),('if (nodo->rbt_color !=','nodo->rbt_color!=ROJO && nodo->rbt_color!=NEGRO',0),('if (tieneMin','tieneMin && nodo->nro<=minimo',0),('if (tieneMax','tieneMax && nodo->nro>=maximo',0),('if (bhIzq == 0)','bhIzq==0',0),('if (bhDer == 0','bhDer==0 || bhIzq!=bhDer',0),('if (nodo->rbt_color == NEGRO','nodo->rbt_color==NEGRO && bhIzq==INT_MAX',0)]:
    old=next(l.strip() for l in orig.splitlines() if snippet in l);number=line(snippet);replace(old,f'if(condition({number},{expr}))return leave({number},{result});')
   old='if (nodo->rbt_color == ROJO &&\n        ((nodo->izq != NULL && nodo->izq->rbt_color == ROJO) ||\n         (nodo->der != NULL && nodo->der->rbt_color == ROJO))) return 0;'
   replace(old,f'if(condition({line("if (nodo->rbt_color == ROJO")},nodo->rbt_color==ROJO && ((nodo->izq!=NULL && nodo->izq->rbt_color==ROJO)||(nodo->der!=NULL && nodo->der->rbt_color==ROJO))))return leave({line("(nodo->der != NULL")},0);')
   for name,field,args in [('bhIzq','izq','tieneMin, minimo, 1, nodo->nro'),('bhDer','der','1, nodo->nro, tieneMax, maximo')]:
    call=f'rbt_validar_altura_negra(nodo->{field}, nodo, {args})';old=f'int {name} = {call};';number=line(old);replace(old,f'int {name}=(local("{name}",0,1),emit({number},"call",-2),{call});local("{name}",{name},2);emit({number},"assignment",-2);')
   old='return bhIzq + (nodo->rbt_color == NEGRO ? 1 : 0);';number=line(old);replace(old,f'return leave({number},bhIzq+(condition({number},nodo->rbt_color==NEGRO)?1:0));')
  elif fn=='rbt_validar':
   for snippet,expr,result in [('if (raiz == NULL)','raiz==NULL',1),('if (raiz->rbt_color','raiz->rbt_color!=NEGRO',0)]:
    old=next(l.strip() for l in orig.splitlines() if snippet in l);number=line(snippet);replace(old,f'if(condition({number},{expr}))return leave({number},{result});')
   old='return rbt_validar_altura_negra(raiz, NULL, 0, 0, 0, 0) != 0;';number=line(old);replace(old,f'emit({number},"call",-2);audit_tmp[depth]=rbt_validar_altura_negra(raiz,NULL,0,0,0,0);emit({number},"resume",-2);return leave({number},audit_tmp[depth]!=0);')
  elif fn=='rbt_buscar':
   old='RBT actual = nodoRBT;';replace(old,old+f'local("actual",ident(actual),2);emit({line(old)},"assignment",-2);')
   for expr in ['nodoRBT == NULL','actual != NULL','dato == actual->nro','dato < actual->nro','dato > actual->nro']:
    replace('('+expr+')',f'(condition({line(expr)},{expr}))')
   for m in re.finditer(r'printf\(([^;]+)\);',orig):
    old=m.group();replace(old,'output_at('+str(line(old))+','+m.group(1)+');')
   for field in ['izq','der']:
    old='actual = actual->'+field+';';replace(old,'{'+old+f'local("actual",ident(actual),2);emit({line(old)},"assignment",-2);'+'}')
   # Both NULL returns retain their physical source offsets.
   t=t.replace('return NULL;',f'return leave_pointer({line("return NULL;")},NULL);',1);t=t.replace('return NULL;',f'return leave_pointer({line("return NULL;",True)},NULL);',1);replace('return actual;',f'return leave_pointer({line("return actual;")},actual);')
  else:
   old=('return ' if operation!='inorden' else '')+'rbt_'+operation+'(raiz'+(', dato' if operation=='buscar' else '')+');';number=line(old)
   if operation=='inorden':replace(old,f'emit({number},"call",-2);rbt_inorden(raiz);emit({number},"resume",-2);');t=t[:-1]+f'leave_void({end+1});}}'
   elif operation=='buscar':replace(old,f'emit({number},"call",-2);RBT result=rbt_buscar(raiz,dato);emit({number},"resume",-2);return leave_pointer({number},result);')
   else:replace(old,f'emit({number},"call",-2);int result=rbt_{operation}(raiz);emit({number},"resume",-2);return leave({number},result);')
  patches.append((a,b,t))
 for a,b,t in sorted(patches,reverse=True):text=text[:a]+t+text[b:]
 c=raw_c.decode('utf-8-sig').replace('\r\n','\n')
 if operation=='buscar':
  a=c.index('RBT rbt_buscar(RBT nodoRBT, int dato) {');b=c.index('\n}',a)+2;c=c[:a]+c[b:]
 if operation=='validar':
  for fn in ['rbt_validar_altura_negra','rbt_validar']:
   m=re.search(r'(?:static\s+)?int\s+'+fn+r'\([^;{}]*\)\s*\{',c);assert m;end=c.index('\n}',m.end())+2;c=c[:m.start()]+c[end:]
 (out/'tad_rojo_negro.c').write_text(c,encoding='utf-8');(out/'tad_rojo_negro.h').write_bytes(raw_h)
 main='\nint main(void){RBT root=NULL;'+''.join(f'rbt_insertar(&root,{v});' for v in seed)+'reg(root);'+mutation+'(void)ejecutar_'+operation+'(root'+(','+str(target) if operation=='buscar' else '')+');rbt_liberar(root);return 0;}'
 def live_setup(registry,count):
  desc=live_fixture;setup=f'nodoRBT a[{max(1,len(desc))}]={{0}};RBT root='+('a;' if desc else 'NULL;')
  ptr=lambda i:'NULL' if i is None else f'&a[{i}]'
  for j,(v,col,parent,left,right) in enumerate(desc):
   literal='INT_MIN' if v==-2147483648 else 'INT_MAX' if v==2147483647 else str(v)
   setup+=f"a[{j}]=(nodoRBT){{.nro={literal},.rbt_color='{col}',.padre={ptr(parent)},.izq={ptr(left)},.der={ptr(right)}}};{registry}[{j}]=&a[{j}];"
  return setup+f'{count}={len(desc)};(void)a;'
 if live_fixture is not None:
  main='\nint main(void){'+live_setup('nodes','node_count')+'(void)ejecutar_validar(root);return 0;}'
 code='#include <stdio.h>\n#include <stdlib.h>\n#include "tad_rojo_negro.h"\n'+HELPER+'\nstatic int audit_tmp[128];\n'+text+main
 # Suppress observer-only unused helpers, never product warnings, via unused attributes.
 code=code.replace('static ', 'static __attribute__((unused)) ')
 (out/'instrumented.c').write_text(code,encoding='utf-8');(out/'shown-source.c').write_text(source,encoding='utf-8');build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),str(out/'tad_rojo_negro.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr;(out/'stdout.log').write_text(run.stdout);events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')];assert events
 registry='static RBT raw_nodes[128];static int raw_count;static void raw_register(RBT n){if(!n)return;raw_nodes[raw_count++]=n;raw_register(n->izq);raw_register(n->der);}static int raw_ident(RBT n){if(!n)return 0;for(int i=0;i<raw_count;i++)if(raw_nodes[i]==n)return i+1;return -1;}'
 invocation='ejecutar_'+operation+'(root'+(','+str(target) if operation=='buscar' else '')+')'
 expression='raw_ident('+invocation+')' if operation=='buscar' else invocation
 original_main='int main(void){RBT root=NULL;'+''.join(f'rbt_insertar(&root,{v});' for v in seed)+'raw_register(root);'+mutation.replace('nodes[','raw_nodes[')+'puts("AUDIT_ORIGINAL_BEGIN");'+(invocation+';int result=-2;' if operation=='inorden' else 'int result='+expression+';')+'printf("\\nAUDIT_ORIGINAL_END %d\\n",result);rbt_liberar(root);return 0;}'
 original_source=source
 if operation=='validar':
  for fn in ['rbt_validar_altura_negra','rbt_validar']:
   m=re.search(r'(?:static\s+)?int\s+'+fn+r'\([^;{}]*\)\s*\{',original_source);assert m;end=original_source.index('\n}',m.end())+2;original_source=original_source[:m.start()]+original_source[end:]
 if live_fixture is not None:
  original_main='int main(void){'+live_setup('raw_nodes','raw_count')+'puts("AUDIT_ORIGINAL_BEGIN");int result=ejecutar_validar(root);printf("\\nAUDIT_ORIGINAL_END %d\\n",result);return 0;}'
 if operation=='buscar':
  a=original_source.index('RBT rbt_buscar(');b=original_source.index('\n}',a)+2;original_source=original_source[:a]+original_source[b:]
 original_code='#include <stdio.h>\n#include <stdlib.h>\n#include "tad_rojo_negro.h"\n'+registry+'\n'+original_source+original_main
 original_code=original_code.replace('static ', 'static __attribute__((unused)) ')
 (out/'original-caller.c').write_text(original_code,encoding='utf-8');build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'original-caller.c'),str(out/'downloaded.c'),'-o',str(out/'original.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 original=subprocess.run([str(out/'original.exe')],capture_output=True,text=True,timeout=5);assert original.returncode==0;query,result_text=original.stdout.split('AUDIT_ORIGINAL_BEGIN\n',1)[1].rsplit('\nAUDIT_ORIGINAL_END ',1);assert query==bytes.fromhex(events[-1]['stdout_hex']).decode('utf-8');assert int(result_text.strip())==events[-1]['wrapper'];(out/'original-stdout.log').write_text(original.stdout)
 (out/'review.json').write_text(json.dumps(events,indent=2));return events
