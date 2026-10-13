"""Focused stable-state validation integration; branch map on QA copy only."""
import sys,json,subprocess,shutil,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from _audit_rbt_insert_native_observer import CHECK
from _audit_rbt_full_validator_baseline_low import oracle
from app.domain.hierarchical.tad_rojo_negro import rbt_insertar,rbt_eliminar,rbt_validar
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-red-black-full-validator-implementation-medium/rotation-integration';E.mkdir(exist_ok=True)
CASES=[('LL',[30,20],10,False),('RR',[10,20],30,False),('LR',[30,10],20,False),('RL',[10,30],20,False),('recolor',[10,5,15],1,False)]
deletions=[([11,2,14,1,7,15,5,8,4],1),([41,38,31,12,19,8],41),([7,3,18,10,22,8,11,26],3),(list(range(1,16)),1)]
for i,(seed,v) in enumerate(deletions):
 for mirror in [False,True]:CASES.append((f'delete{i}_'+('right' if mirror else 'left'),[-x for x in seed] if mirror else seed,-v if mirror else v,True))
raw=(ROOT/'docs/tads_C/tad_rojo_negro.c').read_text(encoding='utf-8-sig');header=(ROOT/'docs/tads_C/tad_rojo_negro.h').read_bytes();(E/'tad_rojo_negro.h').write_bytes(header);(E/'original.c').write_text(raw,encoding='utf-8');copy=raw
start=copy.index('void arreglarEliminacion(');end=copy.index('\n}',start)+2;body=copy[start:end];split=body.index('        } else {\n            /* Lado derecho: casos espejo */');parts=[body[:split],body[split:]]
for side,part in enumerate(parts):
 patterns=['if (colorOf(w) == ROJO) {','if (colorOf(w_izq) == NEGRO && colorOf(w_der) == NEGRO) {' if side==0 else 'if (colorOf(w_der) == NEGRO && colorOf(w_izq) == NEGRO) {','if (colorOf(w_der) == NEGRO) {' if side==0 else 'if (colorOf(w_izq) == NEGRO) {','if (w) w->rbt_color = colorOf(x_parent);']
 for j,needle in enumerate(patterns):assert part.count(needle)==1;part=part.replace(needle,needle+' rn_qa_hit(%d);'%(side*4+j) if j<3 else 'rn_qa_hit(%d); '%(side*4+j)+needle)
 parts[side]=part
copy=copy[:start]+''.join(parts)+copy[end:]
for fn,index in [('rbt_rotar_izda',8),('rbt_rotar_dcha',9)]:
 m=re.search(r'void\s+'+fn+r'\([^;{}]*\)\s*\{',copy);assert m;copy=copy[:m.end()]+' rn_qa_hit(%d);'%index+copy[m.end():]
copy='extern void rn_qa_hit(int index);\n'+copy;(E/'branch-copy.c').write_text(copy,encoding='utf-8')
main='#include <stdio.h>\n#include <stdlib.h>\n#include <limits.h>\n#include "tad_rojo_negro.h"\n'+CHECK.split('static void audit_tree')[0]+r'''
static int hits[10],allocs,frees,checks;void rn_qa_hit(int i){hits[i]++;}
void *rnqa_malloc(size_t n){allocs++;return malloc(n);}
void rnqa_free(void *p){if(p)frees++;free(p);}
static void check(RBT root){int a=allocs,f=frees;if((root&&root->rbt_color!=NEGRO)||audit_valid(root,NULL,LLONG_MIN,LLONG_MAX)<=0||rbt_validar(root)!=1||a!=allocs||f!=frees)exit(91);checks++;}
int main(void){RBT root=NULL;
'''
py=[]
for index,(name,seed,value,delete) in enumerate(CASES):
 ref=[None];assert oracle(ref[0]) and rbt_validar(ref[0]);checkcount=1
 for v in seed:rbt_insertar(ref,v);assert oracle(ref[0]) and rbt_validar(ref[0]);checkcount+=1
 (rbt_eliminar if delete else rbt_insertar)(ref,value);assert oracle(ref[0]) and rbt_validar(ref[0]);checkcount+=1
 py.append(dict(id=name,seed=seed,value=value,delete=delete,python_stable_checks=checkcount))
 main+='root=NULL;check(root);'+''.join(f'rbt_insertar(&root,{v});check(root);' for v in seed)+'for(int j=0;j<10;j++)hits[j]=0;'+f'rbt_{"eliminar" if delete else "insertar"}(&root,{value});check(root);printf("QA {index} %d %d",allocs,frees);for(int j=0;j<10;j++)printf(" %d",hits[j]);puts("");rbt_liberar(root);root=NULL;check(root);'
main+='printf("TOTAL %d %d %d\\n",allocs,frees,checks);return allocs!=frees;}';(E/'main.c').write_text(main,encoding='utf-8')
outputs=[]
for name in ['original','branch-copy']:
 kernel=['gcc','-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-Dmalloc=rnqa_malloc','-Dfree=rnqa_free','-c',name+'.c','-o',name+'.o'];b=subprocess.run(kernel,cwd=E,capture_output=True,text=True,timeout=30);assert b.returncode==0,b.stderr
 cmd=['gcc','-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','main.c',name+'.o','-o',name+'.exe'];b=subprocess.run(cmd,cwd=E,capture_output=True,text=True,timeout=30);(E/(name+'-compile.log')).write_text(b.stdout+b.stderr,encoding='utf-8');assert b.returncode==0,b.stderr
 run=subprocess.run([str(E/(name+'.exe'))],capture_output=True,text=True,timeout=5);assert run.returncode==0;outputs.append(run.stdout);(E/(name+'-stdout.log')).write_text(run.stdout,encoding='utf-8')
lines=[l for l in outputs[1].splitlines() if l.startswith('QA ')];union=[0]*10
for line in lines:
 values=list(map(int,line.split()[1:]));index,a,f,*hits=values;py[index]['native_hits']=hits
 for j,v in enumerate(hits):union[j]+=v
assert all(union),union
# Instrumentation changes only branch observations: original and copy expose same ownership/check totals.
assert [l for l in outputs[0].splitlines() if l.startswith('TOTAL')]==[l for l in outputs[1].splitlines() if l.startswith('TOTAL')]
(E/'report.json').write_text(json.dumps(dict(cases=py,native_hit_totals=union,labels=['left_sibling_red','left_both_nephews_black','left_near_red_far_black','left_far_red_resolution','right_sibling_red','right_both_nephews_black','right_near_red_far_black','right_far_red_resolution','rotate_left','rotate_right'],total=outputs[1].splitlines()[-1],notes='13 focused sequences. Branch copy only; original exported validator plus independent C oracle after complete operations; no invariant asserted during rotations. Historical evidence used to choose reachable seeds, not added to new counts.'),indent=2),encoding='utf-8');print(outputs[1].splitlines()[-1],union)
