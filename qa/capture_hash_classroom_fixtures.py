import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.hash_structure_service import HashStructureService as H
h=[];out=[]
for op,p in [('create_table',{'capacity':5}),('insert',{'key':3,'value':7}),('insert',{'key':8,'value':9}),('get',{'key':3}),('remove',{'key':8}),('clear',{})]:
 r=H.execute_operation('hash_table',op,p,h);assert r['success'],r['message'];out.append({'operation':op,'steps':r['execution_trace']['steps']});h.append({'operation':op,'payload':p})
(ROOT/'qa/hash_classroom_fixtures.json').write_text(json.dumps(out,ensure_ascii=False));print([(c['operation'],len(c['steps'])) for c in out])
f=out[1]['steps'][8]['pedagogy'];print(json.dumps(f['memory'],ensure_ascii=False)[:6500])
# Partially initialized char[] has valid text, not an entirely indeterminate buffer.
r=H.execute_operation('hash_table','values',{},[{'operation':'create_table','payload':{'capacity':5}},{'operation':'insert','payload':{'key':3,'value':7}}])
assert r['success']
(ROOT/'qa/hash_buffer_fixture.json').write_text(json.dumps(r['execution_trace']['steps'],ensure_ascii=False))
r=H.execute_operation('hash_table','destroy_table',{},[{'operation':'create_table','payload':{'capacity':5}},{'operation':'insert','payload':{'key':3,'value':7}}])
assert r['success']
(ROOT/'qa/hash_destroy_fixture.json').write_text(json.dumps(r['execution_trace']['steps'],ensure_ascii=False))
