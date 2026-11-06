"""Fresh hidden positional HTTP/renderer/C17 callers; real browser coverage is separate."""
import pytest

from _hidden_linked_caller_contract import CASES, HIDDEN, SEED, rendered_caller, verify_native_caller


@pytest.mark.parametrize('case_id,operation,payload', CASES, ids=[row[0] for row in CASES])
def test_hidden_caller_matches_API_and_owns_allocations(client, tmp_path, case_id, operation, payload):
    for value in SEED:
        response = client.post('/sequential/linked_list/operate', json={
            'operation': 'insertar_final', 'payload': {'value': value}})
        assert response.status_code == 200 and response.get_json()['success']
    response = client.post('/sequential/linked_list/operate', json={'operation': operation, 'payload': payload})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']
    expected = [item['value'] for item in data['visual_state']['items']]
    first = client.get('/sequential/linked_list')
    assert first.status_code == 200
    rendered = rendered_caller(first.text, tmp_path)
    assert not HIDDEN.intersection(op['name'] for op in rendered['operations'] if not op.get('hidden'))
    reloaded = client.get('/sequential/linked_list')
    assert reloaded.status_code == 200
    assert rendered_caller(reloaded.text, tmp_path)['code'] == rendered['code']
    # jsdom checks the actual highlighted text and renderer. Browser startup,
    # selector contents, and page reload are still mandatory in the e2e companion.
    verify_native_caller(rendered['code'], expected, tmp_path, client)
