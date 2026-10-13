"""Independent C17 parameter types, object aliases, and scope restoration."""
from pathlib import Path
import json,subprocess,shutil
import pytest
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('capacity,key',[(3,-1),(17,-2147483648),(1,2147483647)])
def test_hash_scoped_parameters_fields_aliases_match_c17(client,tmp_path,capacity,key):
    source=(ROOT/'docs/tads_C/tad_tabla_hash.c').read_text(encoding='utf-8')
    prefix='#include <stdio.h>\nstatic const void *expected_root;\n'
    init='void th_inicializar(TablaHash *tabla, int capacidad) {'
    helper='int th_indice(const TablaHash *tabla, int clave) {'
    source=source.replace(init,init+'\n printf("{\\"function\\":\\"th_inicializar\\",\\"parameter\\":%d,\\"field\\":%d,\\"int_type\\":%d,\\"alias\\":%d}\\n", capacidad, tabla->capacidad, _Generic(capacidad,int:1,default:0), (const void*)tabla==expected_root);',1)
    source=source.replace(helper,helper+'\n printf("{\\"function\\":\\"th_indice\\",\\"const_type\\":%d,\\"key_type\\":%d,\\"key\\":%d,\\"alias\\":%d}\\n", _Generic(tabla,const TablaHash*:1,default:0), _Generic(clave,int:1,default:0), clave,(const void*)tabla==expected_root);',1)
    literal='(-2147483647 - 1)' if key==-2147483648 else str(key)
    main=f'\nint main(void){{TablaHash tabla={{0}};expected_root=&tabla;th_inicializar(&tabla,{capacity});if(!tabla.buckets)return 1;bool ok=th_insertar(&tabla,{literal},10);th_destruir(&tabla);return ok?0:2;}}\n'
    (tmp_path/'observed.c').write_text(prefix+source+main,encoding='utf-8');shutil.copyfile(ROOT/'docs/tads_C/tad_tabla_hash.h',tmp_path/'tad_tabla_hash.h')
    r=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'observed.c'),'-o',str(tmp_path/'observed.exe')],capture_output=True,text=True,timeout=30);assert r.returncode==0 and not r.stderr,r.stderr
    r=subprocess.run([str(tmp_path/'observed.exe')],capture_output=True,text=True,timeout=10);assert r.returncode==0
    rows=[json.loads(line) for line in r.stdout.splitlines()];assert rows==[{'function':'th_inicializar','parameter':capacity,'field':0,'int_type':1,'alias':1},{'function':'th_indice','const_type':1,'key_type':1,'key':key,'alias':1}]
    created=client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':capacity}}).get_json()
    init_frame=next(f for f in created['execution_trace']['steps'] if f['event_type']=='init_entry')
    assert init_frame['pedagogy']['variables']['capacidad']==rows[0]['parameter']
    assert init_frame['pedagogy']['variables']['tabla->capacidad']==rows[0]['field']
    assert init_frame['pedagogy']['struct_fields']['tabla']['capacidad']==0
    assert init_frame['debug']['scopes'][0]['variables']['capacidad']['type']=='int'
    inserted=client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':key,'value':10}}).get_json();frames=inserted['execution_trace']['steps']
    for frame in frames:
        debug=frame['debug'];variables=debug['variables']
        assert frame['pedagogy']['variables']=={**{name:item['value'] for name,item in variables.items()},'tabla->capacidad':debug['root']['capacity'],'tabla->cantidad':debug['root']['size'],'retorno':debug['return_status']}
        if debug['function']=='th_indice' and frame['event_type']!='index_return':
            caller,helper_scope=debug['scopes']
            assert caller['variables']['tabla']['type']=='TablaHash *'
            assert helper_scope['variables']['tabla']['type']=='const TablaHash *'
            assert helper_scope['variables']['tabla']['value']==caller['variables']['tabla']['value']==debug['root_identity']
            assert helper_scope['variables']['clave']['value']==rows[1]['key']
            assert variables['indice']['initialized'] is False
        if frame['event_type']=='index_return':
            assert debug['call_stack']==['th_insertar']
            assert not any(name.startswith('th_indice.') for name in variables)
            assert variables['indice']['initialized'] is False
        if frame['event_type']=='index_assign':assert variables['indice']['value']==key%capacity
        if frame['event_type']=='insert_return':assert not debug['scopes'] and not variables
