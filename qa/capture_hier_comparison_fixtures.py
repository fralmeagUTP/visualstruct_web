import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.hierarchical_structure_service import HierarchicalStructureService as H
cases=[H.compare_structures(kind,[10,20,30,40,50]) for kind in ['abb-avl','avl-red-black','abb-heap','traversals']]
(ROOT/'qa/hier_comparison_fixtures.json').write_text(json.dumps(cases,ensure_ascii=False))
