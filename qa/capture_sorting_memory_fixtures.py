"""Capture real frontend memory descriptors for the eleven sorting traces."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.sorting_structure_service import SortingStructureService as Service
from app.adapters.sorting_adapter import SortingAdapter
fixtures=[];radix=[]
for algorithm in SortingAdapter().get_supported_algorithms():
 name=algorithm['id'];result=Service.execute_operation(structure_id='sorting_array',operation_name='run',payload={'algorithm_id':name,'mode':'step_by_step'},history=[{'operation':'create_array','payload':{'values':[3,1,2,1]}}]);frames=[]
 for index,step in enumerate(result['execution_trace']['steps']):
  frame={key:step['pedagogy'].get(key) for key in ['source','variables','pointers']};frames.append(frame)
  if name=='radixsort' and index+1 in [9,10,50,135,158,159]:radix.append({'display_step':index+1,'frame':frame})
 fixtures.append({'algorithm':name,'input':[3,1,2,1],'frames':frames})
(ROOT/'qa/sorting_memory_control_fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False,separators=(',',':')))
(ROOT/'qa/radix_compact_memory_fixtures.json').write_text(json.dumps(radix,ensure_ascii=False,indent=2))
print('Captured',sum(len(item['frames']) for item in fixtures),'real memory frames across',len(fixtures),'algorithms')
