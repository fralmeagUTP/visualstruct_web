"""Separate recreation paths, do not overwrite the sixteen-call baseline."""
from pathlib import Path
import json,sys,ast,subprocess,shutil
R=Path.cwd();sys.path.insert(0,str(R));from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-clear-destroy-baseline-low';N=E/'native-recreation';N.mkdir(exist_ok=True)
tree=ast.parse((R/'tests/_audit_hash_clear_destroy_baseline_low.py').read_text(encoding='utf-8'));driver=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DRIVER' for t in n.targets))
extra=r'''static int bucket_id(const TablaHash*t){for(int j=0;j<used;j++){if(alive[j]&&objects[j]==t->buckets)return j;}assert(0);return -1;}
int main(void){for(operation=0;operation<2;operation++){cid=operation;phase=0;TablaHash t={0};new_bucket=1;th_inicializar(&t,3);assert(th_insertar(&t,1,10));assert(th_insertar(&t,4,40));assert(th_insertar(&t,7,70));int old_id=bucket_id(&t);sample(&t,1);
 if(operation==1){new_bucket=1;th_inicializar(&t,5);}assert(th_insertar(&t,8,80));int new_id=bucket_id(&t);assert(operation?new_id!=old_id:new_id==old_id);
 printf("IDENTITY %d %d %d %d %d\n",operation,old_id,new_id,t.capacidad,t.cantidad);sample(&t,2);phase=3;th_destruir(&t);}
 assert(allocs==frees);for(int j=0;j<used;j++)assert(!alive[j]);printf("OWNERSHIP %d %d\n",allocs,frees);return 0;}
'''
# Raw C needs one slash for newline, not a literal backslash-n stream.
(N/'driver.c').write_text(driver+extra,encoding='utf-8')
flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];p=subprocess.run(flags+['-I',str(E/'native'),str(N/'driver.c'),str(E/'native/hash.o'),'-o',str(N/'driver.exe')],capture_output=True,text=True);(N/'compile.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'run.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
records=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')];identities=[list(map(int,x.split()[1:])) for x in p.stdout.splitlines() if x.startswith('IDENTITY ')];ownership=next(list(map(int,x.split()[1:])) for x in p.stdout.splitlines() if x.startswith('OWNERSHIP '));assert ownership==[11,11]
app=create_app();app.config['TESTING']=True;report=[]
for operation,op in enumerate(['clear','destroy_table']):
 c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
 for k,v in [(1,10),(4,40),(7,70)]:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 first=c.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()
 if operation:c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':5}})
 inserted=c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':8,'value':80}}).get_json();assert inserted['success'];identity=identities[operation];assert inserted['visual_state']['metadata']['capacity']==identity[3] and inserted['visual_state']['metadata']['size']==identity[4]
 second=c.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()
 for repeat,d in [(1,first),(2,second)]:
  n=next(x for x in records if x['event']=='result' and x['operation']==operation and x['repeat']==repeat);assert d['success'] and d['visual_state']['metadata']['capacity']==n['capacity'] and d['visual_state']['metadata']['size']==0
 (E/'callers'/('recreation-'+op+'.c')).write_bytes(c.get('/help/source/hash_table/main').data);report.append({'operation':op,'native_allocation_identity':identity,'C_API_target_results_match':2,'insertion_success':True,'native_target_records':[x for x in records if x['event']=='result' and x['operation']==operation],'ownership_program_separate':ownership})
(E/'recreation-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'paths':2,'extra_target_calls':4,'insertions':2,'native_ownership_separate_program':ownership,'bucket_identity_retained_for_clear_new_lifetime_for_destroy':True}))
