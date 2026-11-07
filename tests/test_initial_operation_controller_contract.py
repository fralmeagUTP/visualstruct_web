"""Full local HTML/scripts/player regression; never a Chromium certification."""
import json
import subprocess
from pathlib import Path
import pytest
from app import create_app
from app.config import Config
from e2e_initial_operation_contract import operation_card
from test_audit_abb_insert_native import abb_insert_native_review
from test_audit_sublist_child_source_native import sublist_native_review
from test_audit_rbt_clear_instruction_native import rbt_clear_native

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def controller_fixtures(tmp_path_factory,abb_insert_native_review,sublist_native_review,rbt_clear_native):
    folder=tmp_path_factory.mktemp('initial-controller')
    class Local(Config):
        TESTING=True
        SESSION_CACHE_DIR=str(folder/'sessions')
    app=create_app(Local);rows=[]
    plans=[]
    for case,meta in enumerate(abb_insert_native_review['cases']):
        plans.append(('abb',case,meta,0))
    for case in [0,17,1,2,3,18,4,5,6,7,19,23,13,14,15,21,16,22]:
        plans.append(('sublist',case,sublist_native_review['cases'][case],0))
    for case in range(10):
        plans.append(('red_black',case,rbt_clear_native['cases'][case%5],int(case>=5)))
    for family,case,meta,repeat in plans:
        prefix='seq' if family=='sublist' else 'hier';route=('sequential/' if prefix=='seq' else 'hierarchical/')+family
        op=meta['operation'] if family=='sublist' else 'insertar' if family=='abb' else 'limpiar'
        payload={k:v for k,v in meta['payload'].items() if k=='parent' or (op=='insertar_hijo' and k=='child')} if family=='sublist' else meta['payload'] if family=='abb' else {}
        with app.test_client() as client:
            def post(operation,body):return client.post('/'+route+'/operate',json={'operation':operation,'payload':body}).json
            if family=='sublist':
                for parent,children in meta['seed']:
                    assert post('insertar_padre',{'parent':parent})['success']
                    for child in children:assert post('insertar_hijo',{'parent':parent,'child':child})['success']
            else:
                for value in meta['seed']:assert post('insertar',{'value':value})['success']
            if repeat:assert post('limpiar',{})['success']
            html=client.get('/'+route).text
            response=client.post('/'+route+'/operate',json={'operation':op,'payload':payload});data=response.json
            rejected=(family=='abb' and case==4) or (family=='sublist' and case in [3,18,15,21])
            assert data['success'] is not rejected
            other='limpiar' if op!='limpiar' else 'insertar_padre' if family=='sublist' else 'insertar'
            rows.append(dict(case=f'{family}-{case}',family=family,prefix=prefix,route=route,op=op,payload=payload,html=html,data=data,http_status=response.status_code,card=operation_card(family,op),other=other,other_card=operation_card(family,other)))
    return rows


def run_controller(tmp_path,rows,mode='normal'):
    path=tmp_path/'input.json';path.write_text(json.dumps(rows))
    return subprocess.run(['node','qa/check_initial_operation_controller.cjs',str(path),mode],cwd=ROOT,capture_output=True,text=True,timeout=240)


def test_full_controllers_replay_initial_operation_cards_and_exact_memory(tmp_path,controller_fixtures):
    run=run_controller(tmp_path,controller_fixtures)
    assert run.returncode==0,run.stderr
    rows=json.loads(run.stdout)
    assert len(rows)==34 and sum(row.get('rejected',False) for row in rows)==5
    assert all(row.get('post_count')==1 for row in rows if not row.get('rejected'))
    assert all(row['frames']>1 for row in rows if not row.get('rejected'))


@pytest.mark.parametrize('family',['abb','sublist'])
@pytest.mark.parametrize('mode',['omit_contextual','renderer_only'])
def test_initial_card_rejects_missing_help_or_renderer_only_observation(tmp_path,controller_fixtures,family,mode):
    row=next(row for row in controller_fixtures if row['family']==family and row['data']['success'])
    run=run_controller(tmp_path,[row],mode)
    assert run.returncode!=0
    assert 'OPERATION_CARD' in run.stderr,run.stderr


@pytest.mark.parametrize('mode',['extra_fetch_url','extra_fetch_method','extra_fetch_body','extra_fetch_valid'])
def test_every_extra_fetch_attempt_is_rejected_even_if_caught(tmp_path,controller_fixtures,mode):
    row=next(row for row in controller_fixtures if row['case']=='sublist-4')
    run=run_controller(tmp_path,[row],mode)
    assert run.returncode!=0
    assert 'TRANSPORT_ATTEMPTS' in run.stderr,run.stderr


@pytest.mark.parametrize('mode',['no_linked_handler','no_current_handler','stale_view_dom'])
def test_both_sublist_view_handlers_and_rendered_modes_are_required(tmp_path,controller_fixtures,mode):
    row=next(row for row in controller_fixtures if row['case']=='sublist-4')
    run=run_controller(tmp_path,[row],mode)
    assert run.returncode!=0
    assert ('VIEW_DOM_DISPLAY' if mode=='stale_view_dom' else 'VIEW_MODE') in run.stderr,run.stderr
