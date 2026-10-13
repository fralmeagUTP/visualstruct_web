"""Add only mallocNULL with valid empty root; retain original 13 C calls."""
from pathlib import Path
import ast,json,subprocess,shutil
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-apilar-baseline-low';N=E/'native'
tree=ast.parse((R/'tests/_audit_stack_apilar_baseline_low.py').read_text(encoding='utf-8-sig'));driver=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DRIVER' for t in n.targets))
source=N/'driver-empty-fault.c';source.write_text(driver+'int main(void){sid=13;ptrPila p=NULL;sample(&p,9,1);assert(p==NULL&&allocs==0&&frees==0);fprintf(stderr,"OWNERSHIP 0 0 0\\n");return 0;}\n',encoding='utf-8')
flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];r=subprocess.run(flags+[str(source),str(N/'pila.o'),'-o',str(N/'driver-empty-fault.exe')],capture_output=True,text=True);(N/'compile-empty-fault.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
r=subprocess.run([str(N/'driver-empty-fault.exe')],capture_output=True,text=True);(N/'empty-fault-events.jsonl').write_text(r.stdout,encoding='utf-8');(N/'empty-fault-stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
extra=[json.loads(s) for s in r.stdout.splitlines()];assert len(extra)==8 and all(not x['root_argument_NULL'] and not x['live'] and not x['root_values'] for x in extra)
p=E/'native-report.json';initial=[n for n in json.loads(p.read_text(encoding='utf-8-sig')) if n['sample']!=13];assert len(initial)==116;(E/'native-report-initial13.json').write_text(json.dumps(initial,indent=2),encoding='utf-8');p.write_text(json.dumps(initial+extra,indent=2),encoding='utf-8')
print('native union14calls124events27conditions; normal calls not rerun')
