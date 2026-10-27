"""Actual HTTP C/native/API sorting baseline; endpoint parity is not instruction fidelity."""
from pathlib import Path
import sys,json,re,shutil,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.domain.sorting import SORTING_ALGORITHMS
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
CASES={'empty':[],'single':[7],'duplicates':[3,1,3,1,0],'negative':[-3,-1,-2,0,-3],'ordered':[-3,-1,0,2,4],'reverse':[4,2,0,-1,-3],'extremes':[2147483647,0,-2147483648,2147483647],'near_min':[-2147483646,-2147483648,-2147483647],'near_max':[2147483647,2147483645,2147483646],'range_rejected':[1000001,0]}
INT_RET={'mergesort','counting_sort','binsort','radixsort'}
app=create_app();client=app.test_client();hashes={}
for kind,ext in [('source','c'),('header','h')]:
 r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;p=OUT/('tad_ordenamiento.'+ext);p.write_bytes(r.data);hashes[p.name]=hashlib.sha256(r.data).hexdigest()
source='#include "tad_ordenamiento.h"\n#include <stdio.h>\nint main(void){\n';fixtures=[]
for alg in SORTING_ALGORITHMS:
 for name,arr in CASES.items():
  idx=len(fixtures);fixtures.append((alg,name,arr));source+='{int a[]={' + (','.join(map(str,arr)) if arr else '42') + '};'
  call=f'{alg["c_function"]}(a,{len(arr)})'
  source+=(f'int status={call};' if alg['id'] in INT_RET else f'{call};int status=-1;')
  source+=f'printf("CASE {idx} %d ",status);imprimir_arreglo(a,{len(arr)});}}\n'
source+='return 0;}\n';(OUT/'observed-main.c').write_text(source,encoding='utf-8');compiler=shutil.which('gcc');assert compiler
p=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(OUT/'observed-main.c'),str(OUT/'tad_ordenamiento.c'),'-o',str(OUT/'native.exe')],capture_output=True,text=True,timeout=30);(OUT/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0 and not p.stderr,p.stderr
p=subprocess.run([str(OUT/'native.exe')],capture_output=True,text=True,timeout=15);(OUT/'native.stdout.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
actual={int(m[1]):{'status':int(m[2]),'array':json.loads(m[3])} for m in re.finditer(r'^CASE (\d+) (-?\d+) (.*)$',p.stdout,re.M)};assert len(actual)==len(fixtures)
rows=[]
for i,(alg,name,arr) in enumerate(fixtures):
 client=app.test_client();create=client.post('/api/ordenamiento/create-array',json={'values':arr});select=client.post('/api/ordenamiento/algorithm',json={'algorithm_id':alg['id']});assert select.status_code==200
 modes=[]
 for mode in ['fast','step_by_step']:
  response=client.post('/api/ordenamiento/run',json={'mode':mode,'algorithm_id':alg['id']});d=response.get_json();state=client.get('/api/ordenamiento/state').get_json();modes.append({'mode':mode,'http':response.status_code,'success':d['success'],'message':d['message'],'array':d['visual_state']['items'],'history_runs':sum(e['operation']=='run' for e in d['history']),'after_get_array':state['visual_state']['items'],'trace_steps':len(d.get('execution_trace',{}).get('steps',[])),'missing_source_steps':sum(e.get('line_index') is None for e in d.get('execution_trace',{}).get('steps',[]))})
 n=actual[i];expected_error=not arr or (alg['id'] in ['counting_sort','binsort'] and max(arr)-min(arr)+1>1000000)
 differences=[]
 if alg['id'] in INT_RET and n['status']!=(0 if expected_error else 1):differences.append('native_status')
 if n['array']!=(arr if expected_error else sorted(arr)):differences.append('native_array')
 for r in modes:
  if r['success']==expected_error:differences.append(r['mode']+'_status')
  if r['array']!=(arr if expected_error else n['array']):differences.append(r['mode']+'_array')
 row={'algorithm':alg['id'],'case':name,'input':arr,'native':n,'api_modes':modes,'differences':differences,'instruction_verified':False};rows.append(row);print(alg['id'],name,differences,flush=True)
report={'methods':SORTING_ALGORITHMS,'cases':len(rows),'rows':rows,'hashes':hashes,'strict_c17':True,'divergent_cases':sum(bool(r['differences']) for r in rows),'limits':['normal allocation; small arrays','int32 extrema use defined C guards/uint32 radix','not stability of equal tagged records or instruction proof']};(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
