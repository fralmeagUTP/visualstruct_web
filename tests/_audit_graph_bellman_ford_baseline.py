"""Independent downloaded-C Bellman-Ford endpoint baseline; reports differences, not a pass claim."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.services.graph_structure_service import GraphStructureService as S
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
MAX=2147483647
CASES=[{'name': 'same_vertex', 'v': [0], 'e': [], 'start': 0, 'end': 0}, {'name': 'negative_edge', 'v': [1, 2], 'e': [(1, 2, -3)], 'start': 1, 'end': 2}, {'name': 'cheaper_negative_alternative', 'v': [1, 2, 3], 'e': [(1, 2, 4), (1, 3, 1), (3, 2, -5)], 'start': 1, 'end': 2}, {'name': 'reachable_negative_cycle', 'v': [1, 2, 3, 4], 'e': [(1, 2, 1), (2, 3, -3), (3, 2, 1), (3, 4, 1)], 'start': 1, 'end': 4}, {'name': 'reachable_cycle_with_direct_target', 'v': [1, 2, 4], 'e': [(1, 2, -2), (2, 1, 1), (1, 4, 7)], 'start': 1, 'end': 4}, {'name': 'unreachable_negative_cycle', 'v': [1, 2, 3, 4], 'e': [(1, 2, 3), (3, 4, -3), (4, 3, 1)], 'start': 1, 'end': 2}, {'name': 'unreachable_destination', 'v': [1, 2, 3], 'e': [(1, 2, -1)], 'start': 1, 'end': 3}, {'name': 'zero_cycle', 'v': [1, 2, 3], 'e': [(1, 2, 0), (2, 1, 0), (2, 3, -1), (1, 3, 2)], 'start': 1, 'end': 3}, {'name': 'equal_cost_order', 'v': [1, 2, 3, 4], 'e': [(1, 2, 1), (1, 3, 1), (2, 4, -1), (3, 4, -1)], 'start': 1, 'end': 4}, {'name': 'negative_ids', 'v': [-2147483648, -1, 2147483647], 'e': [(-2147483648, -1, -2), (-1, 2147483647, 1)], 'start': -2147483648, 'end': 2147483647}, {'name': 'missing_start', 'v': [1, 2], 'e': [(1, 2, 1)], 'start': 999, 'end': 2}, {'name': 'missing_end', 'v': [1, 2], 'e': [(1, 2, 1)], 'start': 1, 'end': 999}, {'name': 'intmax_minus_one', 'v': [1, 2], 'e': [(1, 2, 2147483646)], 'start': 1, 'end': 2}, {'name': 'intmax_infinity', 'v': [1, 2], 'e': [(1, 2, 2147483647)], 'start': 1, 'end': 2}, {'name': 'upper_bound_guard', 'v': [1, 2, 3], 'e': [(1, 2, 2147483646), (2, 3, 2)], 'start': 1, 'end': 3}, {'name': 'intmin_edge', 'v': [1, 2], 'e': [(1, 2, -2147483648)], 'start': 1, 'end': 2}, {'name': 'lower_bound_guard', 'v': [1, 2, 3], 'e': [(1, 2, -2147483648), (2, 3, -1)], 'start': 1, 'end': 3}, {'name': 'undirected_negative_cycle', 'v': [1, 2], 'e': [(1, 2, -1)], 'start': 1, 'end': 2, 'directed': False}, {'name': 'negative_cycle_bound_missed', 'v': [1, 2], 'e': [(1, 2, -2147483648), (2, 1, -2147483648)], 'start': 1, 'end': 2}, {'name': 'empty_graph', 'v': [], 'e': [], 'start': 0, 'end': 0}]

if len(sys.argv)>2:
 selected_names=set(sys.argv[2:])
 CASES=[case for case in CASES if case['name'] in selected_names]
 assert len(CASES)==len(selected_names),'Unknown requested native/application case'
from _graph_book_endpoint_oracle import observe
observe(CASES,'bellman_ford',OUT)
