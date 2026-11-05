"""Render test inputs without a server, browser, network or persistent session."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app
from app.config import Config

destination = Path(sys.argv[1])
destination.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as folder:
    class TestConfig(Config):
        TESTING = True
        SESSION_CACHE_DIR = folder

    client = create_app(TestConfig).test_client()
    routes = {
        "stack": "/sequential/stack",
        "queue": "/sequential/queue",
        "priority_queue": "/sequential/priority_queue",
        "linked_list": "/sequential/linked_list",
        "circular_list": "/sequential/circular_list",
        "sublist": "/sequential/sublist",
        "abb": "/hierarchical/abb",
        "avl": "/hierarchical/avl",
        "red_black": "/hierarchical/red_black",
        "binary_heap": "/hierarchical/binary_heap",
        "graph": "/graph/graph/construccion",
        "hash": "/hash/hash_table",
        "sorting": "/sorting/visualizador",
    }
    for name, route in routes.items():
        response = client.get(route)
        assert response.status_code == 200, (route, response.status_code)
        (destination / f"{name}.html").write_text(response.get_data(as_text=True))
    (destination / "routes.json").write_text(json.dumps(routes))
    batches = {}
    for name, operation in [("stack", "apilar"), ("queue", "encolar")]:
        client = create_app(TestConfig).test_client()
        batches[name] = []
        for value in [10, 20, 30]:
            response = client.post(f"/sequential/{name}/operate", json={"operation": operation, "payload": {"value": str(value)}})
            data = response.get_json()
            assert data["success"], data
            batches[name].append(data)
    (destination / "batches.json").write_text(json.dumps(batches))
print(f"PASS: rendered {len(routes)} isolated route fixtures.")
