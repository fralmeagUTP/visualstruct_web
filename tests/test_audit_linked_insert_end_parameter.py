"""A valid caller head address remains non-NULL when its linked list is empty."""
import shutil,subprocess,re
import pytest
@pytest.mark.parametrize('seed',[[],[7],[7,8,9],[7,7,9]])
def test_insert_end_head_guard_matches_downloaded_native_c(client,tmp_path,seed):
    if not shutil.which('gcc'):pytest.skip('Native GCC unavailable')
    c=client.get('/help/source/linked_list/source');h=client.get('/help/source/linked_list/header');assert c.status_code==h.status_code==200
    source=c.data.decode('utf-8-sig');start=source.index('void lista_insertar_final(');end=source.index('\n}',start)+2
    body=source[start:end];assert body.count('if (*lista == NULL)')==1
    body=body.replace('if (*lista == NULL)', 'printf("AUDITGUARD %d\\n", *lista == NULL);\n    if (*lista == NULL)')
    (tmp_path/'tad_lista.c').write_text(source[:start]+body+source[end:],encoding='utf-8');(tmp_path/'tad_lista.h').write_bytes(h.data)
    main='#include "tad_lista.h"\n#include <stddef.h>\nint main(void){Tlista l=NULL;'+''.join(f'lista_insertar_final(&l,{x});' for x in seed)+'lista_insertar_final(&l,11);lista_limpiar(&l);return 0;}'
    (tmp_path/'main.c').write_text(main,encoding='utf-8');exe=tmp_path/'probe.exe'
    build=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_lista.c'),'-o',str(exe)],capture_output=True,text=True);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0,run.stderr
    result=bool(int(re.findall(r'AUDITGUARD ([01])',run.stdout)[-1]))
    for x in seed:assert client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':x}}).get_json()['success']
    data=client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':11}}).get_json();assert data['success']
    guards=[s for s in data['execution_trace']['steps'] if s['line_text'].strip()=='if (*lista == NULL) {'];assert len(guards)==1
    guard=guards[0]['pedagogy']['condition'];assert guard['result']==result
    assert guard['substituted']==('NULL == NULL' if not seed else 'N1 == NULL')
    assert data['visual_state']['items']==[{'value':x} for x in seed+[11]]
    assert data['execution_trace']['steps'][-1]['state_after']==data['visual_state']
