"""Compare raw utilities with captured independent native C oracle, C/H identity checked."""
import hashlib,json
from pathlib import Path
import pytest
from scripts.published_test_inputs import audit_input_path
from app.domain.hierarchical import tad_monticulo_binario as heap
ROOT=Path(__file__).resolve().parents[1]
ORACLE=json.loads((ROOT/'tests/fixtures/heap_utility_C_oracle.json').read_text(encoding='utf-8'))
@pytest.mark.parametrize('case',ORACLE['cases'],ids=lambda c:c['case_id'])
def test_raw_heap_utilities_match_valid_native_case(case):
    for name,digest in ORACLE['source_inputs'].items():
        if name.endswith(('.c','.h')):
            path=ROOT/name.replace('\\','/')
            historical=audit_input_path(path).read_bytes()
            assert hashlib.sha256(historical.replace(b'\r\n',b'\n')).hexdigest()==digest
            assert path.read_bytes().replace(b'\r\n',b'\n')==historical.replace(b'\r\n',b'\n')
    c=case['fixture'];m=heap.MonticuloBinario()
    heap.monticulo_inicializar(m,c.get('type',0),16)
    for value in c.get('seed',[6,5,4]):heap.monticulo_insertar(m,value)
    target=None if c.get('null_heap') else m
    if c['op']=='build':ok=heap.monticulo_construir(target,c['values'],c['quantity'])
    else:ok=heap.monticulo_eliminar_valor(target,c['value'])
    assert {'ok':int(ok),'array':m.datos,'quantity':m.cantidad,'capacity':m.capacidad}==case['expected']


def test_build_failed_python_copy_keeps_C_destroyed_reserve_state():
    class NoReserve(list):
        def __getitem__(self,key):
            raise MemoryError('controlled replacement allocation failure')
    m=heap.MonticuloBinario()
    heap.monticulo_inicializar(m,heap.MONTICULO_MAX,16)
    for value in [6,5,4]:heap.monticulo_insertar(m,value)
    assert heap.monticulo_construir(m,NoReserve([4,9,3,8,7]),5) is False
    assert (m.datos,m.cantidad,m.capacidad,m.tipo)==([],0,0,heap.MONTICULO_MAX)
