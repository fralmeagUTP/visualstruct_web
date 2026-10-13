"""Actual queue dequeue DOM caller compiler/ownership/Doxygen baseline."""
from pathlib import Path
import json,sys,subprocess,shutil,ast,re,os
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8');E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-queue-desencolar-baseline-low';N=E/'native';O=E/'caller-ownership';O.mkdir(exist_ok=True)
old=ast.parse((R/'tests/_audit_queue_encolar_caller_low.py').read_text(encoding='utf-8-sig'));WRAPPER=next(ast.literal_eval(n.value) for n in old.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='WRAPPER' for t in n.targets));(O/'ownership.c').write_text(WRAPPER,encoding='utf-8');(O/'ownership.h').write_text('#include <stddef.h>\nvoid*audit_malloc(size_t);void audit_free(void*);\n',encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];p=subprocess.run(flags+['-include',str(O/'ownership.h'),'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(N/'tad_cola.c'),'-o',str(O/'cola.o')],capture_output=True);(O/'compile-source.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0;rows=[]
for name,count in [('single',1),('multi',2),('duplicate',2),('bounds',2)]:
 D=O/name;D.mkdir(exist_ok=True);main=E/'actual-callers'/name/'main.c';row={'case':name,'seed_allocations':count,'main_SHA':__import__('hashlib').sha256(main.read_bytes()).hexdigest()}
 for variant,args in [('C17',[str(main),str(N/'tad_cola.c')]),('ownership',[str(main),str(O/'ownership.c'),str(O/'cola.o')])]:
  exe=D/(variant+'.exe');p=subprocess.run(flags+['-I',str(N)]+args+['-o',str(exe)],capture_output=True);(D/(variant+'-compile.log')).write_bytes(p.stdout+p.stderr);row[variant+'_compile_exit']=p.returncode
  if p.returncode==0:
   q=subprocess.run([str(exe)],capture_output=True);(D/(variant+'-run.log')).write_bytes(q.stdout+q.stderr);row[variant+'_exit']=q.returncode;row[variant+'_stdout']=q.stdout.decode('utf-8',errors='replace')
   if variant=='ownership':
    match=re.search(rb'OWNERSHIP (\d+) (\d+) (\d+)',q.stderr);row.update(dict(zip(['allocs','frees','live'],map(int,match.groups()))))
    faults=[]
    for point in range(1,count+1):
     q=subprocess.run([str(exe)],capture_output=True,env=dict(os.environ,QA_NULL_POINT=str(point)));(D/(f'NULL-{point}.log')).write_bytes(q.stdout+q.stderr);faults.append({'point':point,'exit':q.returncode,'stderr':q.stderr.decode('utf-8',errors='replace'),'stdout':q.stdout.decode('utf-8',errors='replace')})
    row['NULL_faults']=faults
 rows.append(row)
from tests.test_graph_bfs_documentation import run_doxygen
import xml.etree.ElementTree as ET
D=E/'caller-doxygen';D.mkdir(exist_ok=True)
try:run_doxygen(D,[N/'tad_cola.c',N/'tad_cola.h']+[E/'actual-callers'/x['case']/'main.c' for x in rows]);clean=True
except AssertionError:clean=False
warnings=(D/'warnings.log').read_text(encoding='utf-8');mains=[]
for p in (D/'doxygen/xml').glob('*.xml'):
 for member in ET.parse(p).findall('.//memberdef'):
  if member.findtext('name')=='main':mains.append({'file':p.name,'documented':member.find('briefdescription/para') is not None or member.find('detaileddescription/para') is not None})
report={'cases':rows,'Doxygen_warnings':len(warnings.splitlines()),'Doxygen_clean':clean,'documented_mains':sum(x['documented'] for x in mains),'XML_mains':mains,'limits':'4 actual DOM mains with include wrapper; strict C17; ownership wrappers only; 7 deterministic NULL setup positions, not real OOM/sanitizer/leak universal claim'};(E/'caller-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('callers',[(x['case'],x.get('C17_compile_exit'),x.get('ownership_exit'),[x.get(k) for k in ['allocs','frees','live']]) for x in rows],'Dox',len(warnings.splitlines()),report['documented_mains'])
