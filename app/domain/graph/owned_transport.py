"""Private implementation of existing GraphLogicalTrace/snapshot_pool protocol.
Canonical codec records/references remain exactly legacy-deterministic.
"""
from app.domain.graph.snapshot_pool import SnapshotPool,GraphSnapshotRecords,REFERENCE
from math import isfinite
class OwnedTransportPool(SnapshotPool):
 def pack(self,trace):
  raw=super().pack(trace);source=self.records;target=GraphSnapshotRecords();memo={};keys={};work={'source_records_validated':len(source),'encoded_children_validated':0,'source_records_normalized':0,'normalized_child_visits':0}
  def reference(v,limit):
   if isinstance(v,(dict,list,tuple)):
    if not isinstance(v,dict) or set(v)!={REFERENCE}:raise ValueError('Malformed Graph snapshot reference')
    i=v[REFERENCE]
    if type(i) is not int or not 0<=i<limit:raise ValueError('Invalid or forward Graph snapshot reference')
    return i
   return None
  for i,record in enumerate(source):
   if not isinstance(record,list) or len(record)!=2 or type(record[0]) is not int or record[0] not in (0,1) or not isinstance(record[1],list):raise ValueError('Malformed Graph pool record')
   if record[0]==0:
    if any(not isinstance(pair,list) or len(pair)!=2 or not isinstance(pair[0],str) for pair in record[1]):raise ValueError('Invalid Graph pool dictionary keys')
    if len({pair[0] for pair in record[1]})!=len(record[1]):raise ValueError('Invalid Graph pool dictionary keys')
    children=[pair[1] for pair in record[1]]
   else:children=record[1]
   for value in children:
    work['encoded_children_validated']+=1
    if reference(value,i) is None:self.primitive_key(value)
  def child(v):
   work['normalized_child_visits']+=1;i=reference(v,len(source))
   if i is not None:
    n=visit(i);return {REFERENCE:n},('ref',n)
   if isinstance(v,float) and not isfinite(v):target.is_json_safe=False
   return v,self.primitive_key(v)
  def visit(i):
   if i in memo:return memo[i]
   record=source[i];work['source_records_normalized']+=1
   if record[0]==0:
    children=[(k,*child(v)) for k,v in record[1]];token=('dict',tuple((k,t) for k,v,t in children));encoded=[0,[[k,v] for k,v,t in children]]
   else:
    children=[child(v) for v in record[1]];token=('list',tuple(t for v,t in children));encoded=[1,[v for v,t in children]]
   if token in keys:n=keys[token]
   else:n=len(target);keys[token]=n;target.append(encoded)
   memo[i]=n;return n
  def root(v):
   i=reference(v,len(source));return {REFERENCE:visit(i)} if i is not None else v
  steps=[{k:root(v) if isinstance(v,dict) and REFERENCE in v else v for k,v in step.items()} for step in raw['steps']]
  result={**raw,'steps':steps,'graph_snapshot_pool':target,'graph_snapshot_stats':{**raw['graph_snapshot_stats'],'compound_nodes':len(target)}}
  if 'numeric_C_memory' in raw:result['numeric_C_memory']=root(raw['numeric_C_memory'])
  result['graph_snapshot_stats']['compound_nodes']=len(target)
  self.last_pack_work={**work,'output_records':len(target),'unreachable_or_normalized_duplicate_records_omitted':len(source)-len(target)}
  return result
