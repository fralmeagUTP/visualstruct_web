"""Live-object RN V3 fixtures; independent oracle and current native helper baseline."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app import create_app
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.tad_rojo_negro import nodoRBT
from app.domain.hierarchical.tad_wrappers import RojoNegro
# tuples: value,color,parent,left,right. Indices always reference live objects.
CASES=[
('empty',[]),('black_leaf',[(10,'n',None,None,None)]),
('int_min',[(-2147483648,'n',None,None,None)]),('int_max',[(2147483647,'n',None,None,None)]),
('balanced_black',[(10,'n',None,1,2),(5,'n',0,None,None),(15,'n',0,None,None)]),
('balanced_red',[(10,'n',None,1,2),(5,'r',0,None,None),(15,'r',0,None,None)]),
('root_red',[(10,'r',None,None,None)]),
('invalid_color',[(10,'n',None,1,None),(5,'x',0,None,None)]),
('red_red',[(10,'n',None,1,None),(5,'r',0,2,None),(3,'r',1,None,None)]),
('black_height',[(10,'n',None,1,None),(5,'n',0,None,None)]),
('root_parent',[(10,'n',1,None,None),(20,'n',None,None,None)]),
('child_parent',[(10,'n',None,1,None),(5,'r',None,None,None)]),
('duplicate',[(10,'n',None,1,None),(10,'r',0,None,None)]),
('ancestor_bound',[(10,'n',None,1,2),(5,'n',0,None,3),(15,'n',0,None,None),(12,'r',1,None,None)]),
('self_cycle',[(10,'n',None,0,None)]),
('interior_cycle',[(20,'n',None,1,None),(10,'n',0,2,None),(5,'r',1,None,1)]),
('shared',[(10,'n',None,1,1),(5,'r',0,None,None)])]
def build(desc):
 nodes=[nodoRBT(v,c) for v,c,*_ in desc]
 for n,(_,_,p,l,r) in zip(nodes,desc):
  n.padre=None if p is None else nodes[p];n.izq=None if l is None else nodes[l];n.der=None if r is None else nodes[r]
 return nodes
def snapshot(nodes):return [(n.nro,n.rbt_color,id(n.padre),id(n.izq),id(n.der)) for n in nodes]
def oracle(root):
 seen=set()
 def visit(n,parent,lo,hi):
  if n is None:return 1
  if id(n) in seen or n.padre is not parent or n.rbt_color not in ('r','n'):return 0
  seen.add(id(n))
  if (lo is not None and n.nro<=lo) or (hi is not None and n.nro>=hi):return 0
  if n.rbt_color=='r' and any(x is not None and x.rbt_color=='r' for x in (n.izq,n.der)):return 0
  left=visit(n.izq,n,lo,n.nro)
  if not left:return 0
  right=visit(n.der,n,n.nro,hi)
  return left+(n.rbt_color=='n') if right==left else 0
 return root is None or (root.rbt_color=='n' and visit(root,None,None,None)>0)
from scripts.published_test_inputs import audit_input_path
def run(out):
 out.mkdir(parents=True,exist_ok=True);client=create_app().test_client()
 raw=client.get('/help/source/red_black/source');header=client.get('/help/source/red_black/header')
 assert raw.status_code==header.status_code==200
 assert raw.data.replace(b'\r\n',b'\n')==(audit_input_path(ROOT/'docs/tads_C/tad_rojo_negro.c')).read_bytes().replace(b'\r\n',b'\n')
 assert header.data.replace(b'\r\n',b'\n')==(audit_input_path(ROOT/'docs/tads_C/tad_rojo_negro.h')).read_bytes().replace(b'\r\n',b'\n')
 (out/'tad_rojo_negro.c').write_bytes(raw.data);(out/'tad_rojo_negro.h').write_bytes(header.data)
 exported=bool(re.search(rb'\bint\s+rbt_validar\s*\(',header.data))
 helper='' if exported else CCodeService._build_red_black_data()['operations']['validar']
 (out/'shown-validator.c').write_text(helper,encoding='utf-8')
 source=['#include <stdio.h>\n#include <stdlib.h>\n#include <limits.h>\n#include "tad_rojo_negro.h"\n',helper,'static int qa_alloc,qa_free; void *__real_malloc(size_t n); void __real_free(void *p); void *__wrap_malloc(size_t n) {qa_alloc++;return __real_malloc(n);} void __wrap_free(void *p) {qa_free++;__real_free(p);}', 'int main(void) {']
 records=[]
 for i,(name,desc) in enumerate(CASES):
  nodes=build(desc);before=snapshot(nodes);wrapper=RojoNegro();wrapper._root_ref[0]=nodes[0] if nodes else None
  expected=bool(oracle(wrapper._root_ref[0]));actual=bool(wrapper.validar());assert snapshot(nodes)==before
  records.append(dict(id=name,expected=expected,python=actual,python_readonly=True,node_count=len(nodes)))
  source.append('{ nodoRBT a[%d] = {0}; nodoRBT saved[%d]; int same=1; int alloc_before=qa_alloc,free_before=qa_free;'%(max(1,len(desc)),max(1,len(desc))))
  ptr=lambda j:'NULL' if j is None else '&a[%d]'%j
  for j,(v,c,p,l,r) in enumerate(desc):
   literal='INT_MIN' if v==-2147483648 else 'INT_MAX' if v==2147483647 else str(v)
   source.append("a[%d]=(nodoRBT){.nro=%s,.rbt_color='%s',.padre=%s,.izq=%s,.der=%s};"%(j,literal,c,ptr(p),ptr(l),ptr(r)))
  source.append('for(int j=0;j<%d;j++) { saved[j]=a[j]; } int result=rbt_validar(%s);'%(len(desc),'a' if desc else 'NULL'))
  source.append('for(int j=0;j<%d;j++) if(a[j].nro!=saved[j].nro || a[j].rbt_color!=saved[j].rbt_color || a[j].padre!=saved[j].padre || a[j].izq!=saved[j].izq || a[j].der!=saved[j].der) same=0;'%len(desc))
  source.append('printf("%d %%d %%d %%d %%d\\n",result,same,qa_alloc-alloc_before,qa_free-free_before); }'%i)
 source.append('return 0; }');(out/'main.c').write_text('\n'.join(source),encoding='utf-8')
 cmd=['gcc','-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','main.c','tad_rojo_negro.c','-Wl,--wrap=malloc','-Wl,--wrap=free','-o','baseline.exe']
 compile=subprocess.run(cmd,cwd=out,capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(compile.stdout+compile.stderr,encoding='utf-8');assert compile.returncode==0,compile.stderr
 native=subprocess.run([str((out/'baseline.exe').resolve())],capture_output=True,text=True,timeout=5);(out/'stdout.log').write_text(native.stdout,encoding='utf-8');assert native.returncode==0,native.stderr
 for line in native.stdout.splitlines():
  i,result,same,allocations,frees=map(int,line.split());records[i].update(native=bool(result),native_readonly=bool(same),native_allocations=allocations,native_frees=frees)
 assert all('native' in r for r in records)
 report=dict(exported=exported,cases=records,python_native_agreements=sum(r['python']==r['native'] for r in records),contract_matches=sum(r['native']==r['expected'] for r in records),divergences=[r['id'] for r in records if r['native']!=r['expected']],notes='17 unique live-object fixtures; current app-only helper when export absent. Fieldwise snapshots; no recursive serializer/destructor, no dangling pointers. Native link-wrapped malloc/free deltas per query; output rows emitted only by QA caller. Prior two counterexamples included, not added.')
 (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
if __name__=='__main__':
 print(json.dumps(run(ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-red-black-full-validator-baseline-low/native'),indent=2))
