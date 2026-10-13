import os,json,subprocess,shutil
from pathlib import Path
import pytest
from app import create_app
OUT=Path(os.environ['CANDIDATE_OUT']);ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def client():
 app=create_app();app.config.update(TESTING=True); assert str(OUT) in str(app.config['SESSION_CACHE_DIR']);return app.test_client()
@pytest.mark.parametrize('seed',[[],[9],[4,5,6]])
def test_ultimo_native_and_causal(client,seed):
 for value in seed:assert client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':value}}).get_json()['success']
 r=client.post('/sequential/linked_list/operate',json={'operation':'ultimo','payload':{}});d=r.get_json();t=d['execution_trace']
 assert r.status_code==(200 if seed else 400)
 if not seed:assert t['steps']==[] and t['execution_started'] is False;return
 steps=t['steps'];conds=[s for s in steps if s['event_type']=='condition' and 'while (' in s['line_text']];stores=[s for s in steps if s['event_type']=='statement' and 'while (' in s['line_text']]
 assert [s['condition_result'] for s in conds]==[True]*(len(seed)-1)+[False]
 assert [s['debug']['lista'] for s in conds]==[f'N{i+1}' for i in range(len(seed))]
 assert len(stores)==len(seed)-1 and all(s['debug']['head']=='N1' for s in steps)
 assert all('NULL->' not in str(s['pedagogy']['condition']) for s in conds)
 assert steps[-1]['pedagogy']['call_stack']==[] and steps[-1]['pedagogy']['scopes'][0]['state']=='ended'
 assert steps[-1]['state_after']==d['visual_state'] and steps[-1]['debug']['output']==seed[-1]
 c=(ROOT/'docs/tads_C/tad_lista.c').read_text(encoding='utf-8-sig')
 body='while (lista->sgte != NULL) lista = lista->sgte;';assert c.count(body)==1
 c=c.replace(body,'while (++checks && lista->sgte != NULL) { lista = lista->sgte; ++advances; }')
 c=c.replace('int lista_ultimo(', 'static int checks, advances;\nint lista_ultimo(')
 c+='\nint main(void) { Tlista p=NULL; int value=0;\n'+''.join(f'lista_insertar_final(&p,{v});\n' for v in seed)+'Tlista original=p; int r=lista_ultimo(p,&value); printf("OBS %d %d %d %d %d\\n",r,value,checks,advances,p==original); lista_limpiar(&p); return p!=NULL; }\n'
 native=OUT/f'ultimo-{len(seed)}.c';native.write_text(c,encoding='utf-8');exe=native.with_suffix('.exe');args=['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(native),'-o',str(exe)]
 compile=subprocess.run(args,capture_output=True,text=True,timeout=25);assert compile.returncode==0,compile.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0
 assert f'OBS 1 {seed[-1]} {len(seed)} {len(seed)-1} 1' in run.stdout
 (OUT/f'ultimo-{len(seed)}.json').write_text(json.dumps({'trace':t,'compile':args,'native':run.stdout},indent=2),encoding='utf-8')
@pytest.mark.parametrize('operation,payload',[('hijos_de',{'parent':'abc'}),('hijos_de',{}),('insertar_padre',{'parent':'abc'}),('insertar_hijo',{'parent':3,'child':'abc'}),('eliminar_hijo',{'parent':3,'child':'abc'})])
def test_sublist_invalid_has_no_C(client,operation,payload):
 for op,p in [('insertar_padre',{'parent':3}),('insertar_hijo',{'parent':3,'child':7})]:assert client.post('/sequential/sublist/operate',json={'operation':op,'payload':p}).get_json()['success']
 before=client.get('/sequential/sublist').status_code
 r=client.post('/sequential/sublist/operate',json={'operation':operation,'payload':payload});d=r.get_json();assert r.status_code==400 and d is not None and not d['success']
 assert len(d['history'])==2 and d['execution_trace']['steps']==[] and d['execution_trace']['execution_started'] is False
 assert client.get('/sequential/sublist').status_code==before==200
@pytest.mark.parametrize('parent',[3,99])
def test_sublist_valid_numeric_still_C(client,parent):
 assert client.post('/sequential/sublist/operate',json={'operation':'insertar_padre','payload':{'parent':3}}).get_json()['success']
 r=client.post('/sequential/sublist/operate',json={'operation':'hijos_de','payload':{'parent':parent}});d=r.get_json();assert r.status_code==(200 if parent==3 else 400) and d['success']==(parent==3) and d['execution_trace']['steps']
 assert len(d['history'])==(2 if parent==3 else 1)
 if parent==3:assert d['result']==[]
