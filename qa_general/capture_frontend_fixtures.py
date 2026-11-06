"""Generate current inputs from real services/C, never replace frozen audit evidence."""
from pathlib import Path
import json, subprocess, sys, hashlib
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.services.structure_service import StructureService as S
from app.services.execution_trace_service import ExecutionTraceService as E
from qa.frontend_main_audit import build_fixtures
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'qa_general/frontend-fixtures'
out.mkdir(parents=True, exist_ok=True)
(out/'main-fixtures.json').write_text(json.dumps(build_fixtures(), ensure_ascii=False))
fixtures=[]
for sid,op in [('queue','encolar'),('stack','apilar')]:
    adapter=S._new_adapter(sid)
    for value in [7,3,7]:
        adapter.execute(op,{'value':value})
    state=adapter.to_visual_state()
    trace=E.build_trace(structure_id=sid,operation_name='mostrar',payload={},didactic_data=S._didactic_content(sid),before_state=state,after_state=state,success=True,message='Private helper QA; not an API operation',mutates=False,console_events=[])
    assert trace['steps']
    fixtures.append({'label':f'private {sid} mostrar [7, 3, 7]','trace':trace})
history=[]
for value in [7,3,7]:
    data=S.execute_operation('linked_list','insertar_final',{'value':value},history)
    assert data['success'];history=data['history']
data=S.execute_operation('linked_list','mostrar',{},history)
assert data['success']
fixtures.append({'label':'public linked mostrar [7, 3, 7]','trace':data['execution_trace']})
(out/'stdout-fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False))
# Compile the actual unmodified canonical C, independent from Python trace expectations.
driver=out/'queue-stdout.c'
driver.write_text('#include "tad_cola.h"\nint main(void) { struct Cola q={0}; cola_encolar(&q,7); cola_encolar(&q,3); cola_encolar(&q,7); cola_mostrar(q); cola_vaciar(&q); return 0; }\n')
command=['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'docs/tads_C'),str(driver),str(ROOT/'docs/tads_C/tad_cola.c'),'-o',str(out/'queue-stdout')]
subprocess.run(command,check=True,capture_output=True)
result=subprocess.run([str(out/'queue-stdout')],check=True,capture_output=True)
assert result.stdout==b'Cola: 7 3 7 \n'
(out/'native-queue-stdout-raw.bin').write_bytes(result.stdout)
(out/'provenance.json').write_text(json.dumps({'source':'current services + unmodified canonical C','compile_command':command,'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['docs/tads_C/tad_cola.c','app/services/execution_trace_service.py','static/js/sequential.js']}},indent=2))
print('PASS generated 9 current main fixtures, 3 stdout traces and native C stdout.')
