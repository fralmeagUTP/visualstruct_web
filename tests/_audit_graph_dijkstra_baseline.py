"""Independent downloaded-C Dijkstra endpoint baseline; reports differences, not a pass claim."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.services.graph_structure_service import GraphStructureService as S
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
MAX=2147483647
CASES=[
 dict(name='same_vertex',v=[-1],e=[],start=-1,end=-1),
 dict(name='direct',v=[1,2],e=[(1,2,7)],start=1,end=2),
 dict(name='cheaper_alternative',v=[1,2,3],e=[(1,2,4),(1,3,1),(3,2,1)],start=1,end=2),
 dict(name='equal_priority_order',v=[1,2,3,4],e=[(1,2,1),(1,3,1),(2,4,1),(3,4,1)],start=1,end=4),
 dict(name='equal_priority_reverse_vertices',v=[4,3,2,1],e=[(1,2,1),(1,3,1),(2,4,1),(3,4,1)],start=1,end=4),
 dict(name='unreachable',v=[1,2,3],e=[(1,2,2)],start=1,end=3),
 dict(name='zero_cycle',v=[1,2,3],e=[(1,2,0),(2,1,0),(2,3,0),(1,3,1)],start=1,end=3),
 dict(name='undirected',v=[-2,-1,0],e=[(-2,-1,3),(-1,0,2)],start=0,end=-2,directed=False),
 dict(name='negative_ids',v=[-2147483648,-1,2147483647],e=[(-2147483648,-1,1),(-1,2147483647,2)],start=-2147483648,end=2147483647),
 dict(name='missing_start',v=[1,2],e=[(1,2,1)],start=999,end=2),
 dict(name='missing_end',v=[1,2],e=[(1,2,1)],start=1,end=999),
 dict(name='negative_weight_rejected',v=[1,2],e=[(1,2,-1)],start=1,end=2,reject=True),
 dict(name='negative_disconnected_rejected',v=[1,2,3,4],e=[(1,2,1),(3,4,-1)],start=1,end=2,reject=True),
 dict(name='intmax_minus_one',v=[1,2],e=[(1,2,MAX-1)],start=1,end=2),
 dict(name='intmax_infinity',v=[1,2],e=[(1,2,MAX)],start=1,end=2),
 dict(name='overflow_guard',v=[1,2,3],e=[(1,2,MAX-1),(2,3,2)],start=1,end=3),
]
if len(sys.argv)>2:
 selected_names=set(sys.argv[2:])
 CASES=[case for case in CASES if case['name'] in selected_names]
 assert len(CASES)==len(selected_names),'Unknown requested native/application case'
from _graph_book_endpoint_oracle import observe
observe(CASES,'dijkstra',OUT)
