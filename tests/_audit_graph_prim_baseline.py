"""Independent downloaded-C Bellman-Ford endpoint baseline; reports differences, not a pass claim."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.services.graph_structure_service import GraphStructureService as S
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
MAX=2147483647
CASES=[{'name': 'single_vertex', 'v': [-1], 'e': [], 'start': -1, 'directed': False}, {'name': 'connected', 'v': [1, 2, 3], 'e': [(1, 2, 4), (1, 3, 1), (3, 2, 2)], 'start': 1, 'directed': False}, {'name': 'disconnected', 'v': [1, 2, 3, 4], 'e': [(1, 2, 2), (3, 4, 3)], 'start': 1, 'directed': False}, {'name': 'isolated_start', 'v': [0, 1, 2], 'e': [(1, 2, 3)], 'start': 0, 'directed': False}, {'name': 'equal_cost', 'v': [1, 2, 3, 4], 'e': [(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 4, 1)], 'start': 1, 'directed': False}, {'name': 'zero_weight', 'v': [1, 2, 3], 'e': [(1, 2, 0), (2, 3, 0), (1, 3, 1)], 'start': 1, 'directed': False}, {'name': 'negative_edge', 'v': [1, 2], 'e': [(1, 2, -1)], 'start': 1, 'directed': False}, {'name': 'mixed_negative', 'v': [1, 2, 3], 'e': [(1, 2, -2), (1, 3, 3), (2, 3, 1)], 'start': 1, 'directed': False}, {'name': 'self_loop', 'v': [1, 2], 'e': [(1, 1, -1), (1, 2, 2)], 'start': 1, 'directed': False}, {'name': 'negative_ids', 'v': [-2147483648, -1, 2147483647], 'e': [(-2147483648, -1, 2), (-1, 2147483647, 1)], 'start': -1, 'directed': False}, {'name': 'missing_start', 'v': [1, 2], 'e': [(1, 2, 3)], 'start': 999, 'directed': False}, {'name': 'empty', 'v': [], 'e': [], 'start': 0, 'directed': False}, {'name': 'intmax_minus_one', 'v': [1, 2], 'e': [(1, 2, 2147483646)], 'start': 1, 'directed': False}, {'name': 'intmax_sentinel', 'v': [1, 2], 'e': [(1, 2, 2147483647)], 'start': 1, 'directed': False}, {'name': 'safe_large_total', 'v': [1, 2, 3], 'e': [(1, 2, 2147483646), (2, 3, 2147483646)], 'start': 1, 'directed': False}, {'name': 'intmin_ignored', 'v': [1, 2], 'e': [(1, 2, -2147483648)], 'start': 1, 'directed': False}, {'name': 'directed_native_difference', 'v': [1, 2], 'e': [(1, 2, 3)], 'start': 1, 'directed': True}]

if len(sys.argv)>2:
 selected_names=set(sys.argv[2:])
 CASES=[case for case in CASES if case['name'] in selected_names]
 assert len(CASES)==len(selected_names),'Unknown requested native/application case'
from _graph_book_endpoint_oracle import observe
observe(CASES,'prim',OUT)
