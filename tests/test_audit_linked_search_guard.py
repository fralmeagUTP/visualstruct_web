"""The final C search condition is evaluated even after successful matches."""
import shutil,subprocess
import pytest

@pytest.mark.parametrize('seed,value',[([7],7),([7,8,9],8),([7,7,9],7),([],7)])
def test_search_final_guard_matches_independently_executed_download(client,tmp_path,seed,value):
    if not shutil.which('gcc'):pytest.skip('gcc unavailable: native search condition unverified')
    for kind,ext in [('source','c'),('header','h')]:
        response=client.get('/help/source/linked_list/'+kind)
        assert response.status_code==200
        (tmp_path/('tad_lista.'+ext)).write_bytes(response.data)
    insert=''.join('lista_insertar_final(&l,'+str(x)+');' for x in seed)
    code='#include "tad_lista.h"\n#include <stddef.h>\nint main(void){Tlista l=NULL;'+insert+'lista_buscar_elemento(l,'+str(value)+');lista_limpiar(&l);return 0;}'
    p=tmp_path/'probe.c';p.write_text(code,encoding='utf-8');exe=tmp_path/'probe.exe'
    built=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(p),str(tmp_path/'tad_lista.c'),'-o',str(exe)],capture_output=True,text=True)
    assert built.returncode==0,built.stderr
    native=subprocess.run([str(exe)],capture_output=True,text=True)
    assert native.returncode==0,native.stderr
    for x in seed:assert client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':x}}).get_json()['success']
    data=client.post('/sequential/linked_list/operate',json={'operation':'buscar_elemento','payload':{'value':value}}).get_json()
    steps=data['execution_trace']['steps']
    guards=[step for step in steps if step['line_text'].strip()=='if (!encontrado) {']
    assert len(guards)==1,'C evaluates final guard exactly once even when matches were found'
    assert guards[0]['pedagogy']['condition']['result']==('Numero no encontrado' in native.stdout)
    assert all(step['state_after']['items']==[{'value':x} for x in seed] for step in steps)
