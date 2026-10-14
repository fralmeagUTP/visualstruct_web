"""Conservative source-binding extraction checks; no application requests."""
import ast
from scripts.build_app_quality_bindings import request_cases,matches,ui_cases,ui_matches

def test_request_is_linked_to_its_own_assertions_and_context():
 source="""def test_calls(client):
    first=client.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':7}})
    assert first.status_code==200
    second=client.post('/sequential/stack/operate',json={'operation':'desapilar','payload':{}})
    data=second.get_json()
    assert data['result']==7
 """
 cases=request_cases(ast.parse(source),source)
 assert len(cases)==2
 assert cases[0]['expected']['assertions'][0]['literal_expected']==[200]
 assert cases[1]['expected']['assertions'][0]['literal_expected']==[7]
 assert len(cases[1]['input']['preceding_literal_requests'])==1

def test_unrelated_assertion_does_not_create_a_case():
 source="""def test_unchecked(client):
    unrelated=42
    response=client.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':7}})
    assert unrelated==42
 """
 assert request_cases(ast.parse(source),source)==[]

def test_symbolic_payload_is_not_fabricated():
 source="""def test_symbolic(client,value):
    response=client.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':value}})
    assert response.status_code==200
 """
 assert request_cases(ast.parse(source),source)==[]

def test_graph_phase_is_not_inferred_from_plain_api_algorithm():
 item={'category':'algorithm','module':'graph','metadata':{'phase':'recorridos','algorithm':'run_bfs'}}
 case={'input':{'request':{'method':'POST','path':'/graph/graph/operate','json':{'operation':'run_bfs','payload':{'start':1}}},'preceding_literal_requests':[]}}
 assert not matches(item,case)
 case['input']['preceding_literal_requests']=[{'method':'GET','path':'/graph/graph/recorridos'}]
 assert matches(item,case)

def test_ui_case_preserves_actual_gesture_and_anonymous_selector():
 source="""def test_playwright_tab():
    page.goto(f'{base_url}/sequential/queue')
    page.click('[data-seq-tab="code"]')
    assert page.locator('#seq-code-region').is_visible()
 """
 cases=ui_cases(ast.parse(source),source)
 item={'category':'control','metadata':{'identifier':'anonymous-2','synthetic_identifier':True,'attributes':{'data-seq-tab':'code'}}}
 assert len(cases)==1 and ui_matches(item,cases[0])
 item['metadata']['attributes']={'data-seq-tab':'visual'}
 assert not ui_matches(item,cases[0])
