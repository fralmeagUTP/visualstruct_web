"""Compare every JSON-visible field with the preserved pre-QA constructors."""
import gc,hashlib,importlib.util,json
from pathlib import Path
from app.adapters.hash_table_adapter import HashTableAdapter
from app.services.c_code_service import CCodeService
from app.services.execution_trace_service import ExecutionTraceService
from app.services.hash_caller_stdout import attach_caller_stdout
from app.domain.hash.listing_instruction import build_hash_listing_trace
from app.domain.hash.stats_instruction import build_hash_stats_trace
BASE=Path('/workspace/scratch/644977913e22/visualstruct_ortografia_20261105/app/domain/hash')
def load(file,name):
 spec=importlib.util.spec_from_file_location('baseline_'+name,BASE/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return getattr(module,name)
def digest(trace):
 h=hashlib.sha256()
 for step in trace['steps']:h.update(json.dumps(step,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
 h.update(json.dumps({k:v for k,v in trace.items() if k!='steps'},sort_keys=True,ensure_ascii=False,separators=(',',':')).encode());return h.hexdigest()
old_listing=load('listing_instruction.py','build_hash_listing_trace');old_stats=load('stats_instruction.py','build_hash_stats_trace')
for cap in [3,64]:
 for op in ['keys','values','items','stats']:
  a=HashTableAdapter();a.execute('create_table',{'capacity':cap});a.execute('insert',{'key':-1,'value':2147483647});before=a.to_visual_state();result=a.execute(op,{});after=a.to_visual_state()
  source,title=ExecutionTraceService._get_operation_source(didactic_data=CCodeService.get_structure_data('hash_table'),operation_name=op)
  kwargs=dict(operation_name=op,payload={},source_code=source,code_title=title,before_state=before,after_state=after,success=True,message=result['message'])
  old=(old_stats if op=='stats' else old_listing)(**kwargs);attach_caller_stdout(old,op,{},after);expected=digest(old);count=len(old['steps']);del old;gc.collect()
  current=(build_hash_stats_trace if op=='stats' else build_hash_listing_trace)(**kwargs);attach_caller_stdout(current,op,{},after);actual=digest(current)
  assert actual==expected,(cap,op,expected,actual)
  print(json.dumps({'capacity':cap,'operation':op,'steps':count,'sha256':actual,'equal_all_json_fields':True}),flush=True);del current;gc.collect()
