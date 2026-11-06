"""QA regressions for JSON envelopes and repeated reset/replay of ten structures."""
from __future__ import annotations

import pytest

CASES = [
    ("sequential", "stack", "apilar", {"value": "7"}),
    ("sequential", "queue", "encolar", {"value": "7"}),
    ("sequential", "priority_queue", "encolar", {"value": "7", "priority": "1"}),
    ("sequential", "linked_list", "insertar_final", {"value": "7"}),
    ("sequential", "circular_list", "insertar_final", {"value": "7"}),
    ("sequential", "sublist", "insertar_padre", {"parent": "7"}),
    *[("hierarchical", name, "insertar", {"value": "7"}) for name in ("abb", "avl", "red_black", "binary_heap")],
]

@pytest.mark.parametrize("path", [f"/{family}/{name}/operate" for family, name, _, _ in CASES] + ["/hierarchical/compare"])
@pytest.mark.parametrize("body", [[1], [], 42, 0, "oops", "", True, False, None])
def test_non_object_json_returns_controlled_error(client, path, body):
    response = client.post(path, json=body)
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["success"] is False

@pytest.mark.parametrize("family,name,operation,payload", CASES)
def test_invalid_envelope_preserves_state_and_repeat_reset_is_clean(client, family, name, operation, payload):
    base = f"/{family}/{name}"
    seeded = client.post(base + "/operate", json={"operation": operation, "payload": payload})
    assert seeded.status_code == 200
    with client.session_transaction() as session:
        before = dict(session)
    assert client.post(base + "/operate", json=[1]).status_code == 400
    with client.session_transaction() as session:
        assert dict(session) == before
    assert client.get(base).status_code == 200
    for _ in range(2):
        reset = client.post(base + "/reset").get_json()
        assert reset["success"] is True
        assert reset["history"] == []
        assert reset["visual_state"]["size"] == 0
    repeated = client.post(base + "/operate", json={"operation": operation, "payload": payload})
    assert repeated.status_code == 200
    assert repeated.get_json()["visual_state"] == seeded.get_json()["visual_state"]
    assert len(repeated.get_json()["history"]) == len(seeded.get_json()["history"])

@pytest.mark.parametrize("family,name,operation,payload", CASES)
@pytest.mark.parametrize("invalid_payload", [[1], 42, "bad", True, None])
def test_non_object_payload_returns_controlled_error(client, family, name, operation, payload, invalid_payload):
    response = client.post(f"/{family}/{name}/operate", json={"operation": operation, "payload": invalid_payload})
    assert response.status_code == 400
    assert response.get_json()["success"] is False

@pytest.mark.parametrize("path", ["/sequential/stack/operate", "/hierarchical/abb/operate", "/hierarchical/compare"])
def test_malformed_json_returns_controlled_error(client, path):
    response = client.post(path, data='{"broken":', content_type="application/json")
    assert response.status_code == 400
    assert response.get_json()["success"] is False

@pytest.mark.parametrize("family,name,operation,payload", CASES)
def test_history_capacity_rejects_atomically_and_reset_recovers(client, family, name, operation, payload):
    client.application.config["SESSION_MAX_HISTORY"] = 3
    base = f"/{family}/{name}"
    for value in (1, 2, 3):
        current_payload = {**payload, "parent" if name == "sublist" else "value": str(value)}
        previous = client.post(base + "/operate", json={"operation": operation, "payload": current_payload})
        assert previous.status_code == 200
    before_body = previous.get_json()
    with client.session_transaction() as session:
        before_session = dict(session)
    rejected = client.post(base + "/operate", json={"operation": operation, "payload": {**payload, "parent" if name == "sublist" else "value": "4"}})
    assert rejected.status_code == 409
    body = rejected.get_json()
    assert body["success"] is False and body["preserve_session"] is True
    assert body["history"] == before_body["history"]
    assert body["visual_state"] == before_body["visual_state"]
    assert "execution_trace" not in body
    with client.session_transaction() as session:
        assert dict(session) == before_session
    assert client.get(base).status_code == 200
    reset = client.post(base + "/reset").get_json()
    assert reset["history"] == [] and reset["visual_state"]["size"] == 0
    assert client.post(base + "/operate", json={"operation": operation, "payload": payload}).status_code == 200

def test_hierarchical_capacity_rejection_preserves_existing_player_and_history():
    """Execute the actual frontend handler's early rejection path in Node."""
    import subprocess
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / "static/js/hierarchical.js").read_text()
    handler = source.split("  async function executeOperationAndLoadTrace", 1)[1].split("  async function ensureTraceForCurrentSelection", 1)[0]
    script = r'''
const assert = require('node:assert/strict');
let pendingExecution = false;
const resetButton = {disabled: false};
const simStatus = {textContent: ''};
const form = {dataset: {operateUrl: '/hierarchical/abb/operate'}};
const messages = [];
let pauses = 0;
const tracePlayer = {pause: () => {pauses++;}};
function setSimulationButtonsEnabled() {}
function showHierMessage(message, success) {messages.push({message, success});}
const data = {success: false, preserve_session: true, message: 'Historial lleno', history: [{operation:'insertar'}], visual_state: {size:3}};
async function fetch() {return {json: async () => data};}
const window = {MultipleInput: {fetchUnit: fetch}};
'''
    script += "async function executeOperationAndLoadTrace" + handler
    script += r'''
(async () => {
  assert.equal(await executeOperationAndLoadTrace({name:'insertar'}, {value:'4'}, 'key'), null);
  assert.equal(await executeOperationAndLoadTrace({name:'insertar'}, {value:'4'}, 'key', {multiple:true}), data);
  assert.equal(pauses, 2);
  assert.equal(pendingExecution, false);
  assert.equal(resetButton.disabled, false);
  assert.deepEqual(messages.filter(x => !x.success), [{message:'Historial lleno',success:false},{message:'Historial lleno',success:false}]);
  assert.match(simStatus.textContent, /permanecen sin cambios/);
})().catch(error => {console.error(error); process.exitCode=1;});
'''
    subprocess.run(["node", "-e", script], check=True, capture_output=True, text=True)
