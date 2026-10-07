"""Exact per-request structural sharing and versioned numeric Graph transport.

Every logical field and event survives. References name immutable JSON subtrees,
not C pointers or sampled states. The unchanged player receives expanded shared
objects; a consumer can expand this codec without executing the operation.
"""
from __future__ import annotations
from dataclasses import replace
from time import perf_counter
from typing import Any
import json
from math import isfinite

CODEC = 'graph-snapshot-pool/v1'
REFERENCE = '$graph_ref'

class GraphLogicalTrace(dict):
    """Public logical dictionary with a private, request-local transport pool."""
    def __init__(self, *args, snapshot_pool, **kwargs):
        super().__init__(*args, **kwargs);self.snapshot_pool=snapshot_pool

class GraphSnapshotRecords(list):
    """Request-owned encoded table; encode tracks finite JSON primitives."""
    def __init__(self):
        super().__init__();self.is_json_safe=True

class SnapshotPool:
    """Intern complete dictionaries/lists by typed structural value."""
    def __init__(self, *, preserve_tuples=False):
        self.preserve_tuples=preserve_tuples
        self.objects=[];self.keys={};self.identities={};self.records=GraphSnapshotRecords()

    @staticmethod
    def primitive_key(value):
        if value is None:return ('null',)
        if type(value) is bool:return ('bool',value)
        if type(value) is int:return ('int',value)
        if type(value) is float:return ('float',value.hex())
        if isinstance(value,str):return ('text',value)
        raise TypeError(('Unsupported snapshot JSON value',type(value)))

    def intern(self,value):
        return self._intern(value, {})

    def _intern(self,value,seen):
        return self._intern_with_token(value,seen)[0]

    def _intern_with_token(self,value,seen):
        if isinstance(value,tuple) and not self.preserve_tuples:value=list(value)
        if not isinstance(value,(dict,list,tuple)):
            return value,self.primitive_key(value)
        prior=seen.get(id(value))
        if prior is not None and prior[0] is value:return prior[1],prior[2]
        old=self.identities.get(id(value))
        if old is not None and self.objects[old] is value:return value,('ref',old)
        if isinstance(value,dict):
            def text_key(k):
                if isinstance(k,str):return k
                if k is None:return 'null'
                if type(k) is bool:return 'true' if k else 'false'
                if isinstance(k,(int,float)):return json.dumps(k)
                raise TypeError('Unsupported JSON snapshot key')
            pairs=[(k if self.preserve_tuples else text_key(k),v) for k,v in value.items()]
            if len({text_key(k) for k,v in pairs})!=len(pairs):raise ValueError('Duplicate normalized snapshot keys')
            children=[(k,*self._intern_with_token(v,seen)) for k,v in pairs]
            key=('dict',tuple((self.primitive_key(k) if self.preserve_tuples else k,token) for k,child,token in children))
        else:
            children=[self._intern_with_token(v,seen) for v in value]
            key=('tuple' if isinstance(value,tuple) else 'list',tuple(token for child,token in children))
        existing=self.keys.get(key)
        if existing is not None:
            result=self.objects[existing];token=('ref',existing)
            seen[id(value)]=(value,result,token);return result,token
        if isinstance(value,dict):result={k:child for k,child,token in children}
        else:result=tuple(child for child,token in children) if isinstance(value,tuple) else [child for child,token in children]
        index=len(self.objects);self.keys[key]=index;self.objects.append(result);self.identities[id(result)]=index
        record=[0,[[text_key(k),self.encode(child)] for k,child,token in children]] if isinstance(value,dict) else [1,[self.encode(child) for child,token in children]]
        self.records.append(record);token=('ref',index);seen[id(value)]=(value,result,token);return result,token

    def token(self,value):
        if isinstance(value,(dict,list,tuple)):return ('ref',self.identities[id(value)])
        return self.primitive_key(value)

    def encode(self,value):
        if isinstance(value,(dict,list,tuple)):return {REFERENCE:self.identities[id(value)]}
        if isinstance(value,float) and not isfinite(value):self.records.is_json_safe=False
        return value

    def pack(self,trace):
        # Metadata/events stay ordinary JSON. Only repetitive step subtrees and
        # the final C memory use the table, keeping one header per actual step.
        steps=[{k:self.encode(self.intern(v)) if isinstance(v,(dict,list)) and k!='console' else v for k,v in step.items()} for step in trace['steps']]
        result={**trace,'steps':steps,'numeric_C_memory':self.encode(self.intern(trace['numeric_C_memory']))} if 'numeric_C_memory' in trace else {**trace,'steps':steps}
        result.update(graph_snapshot_codec=CODEC,graph_snapshot_pool=self.records,
            graph_snapshot_stats={'compound_nodes':len(self.records),'steps':len(steps),'C_events':len(trace.get('C_instruction_events',[])),'sampling':False})
        return result


def expand_graph_trace(trace:dict[str,Any])->dict[str,Any]:
    """Expand transport exactly with shared objects; pass legacy traces through."""
    if 'graph_snapshot_codec' not in trace:return trace
    if trace['graph_snapshot_codec']!=CODEC:raise ValueError('Unknown Graph snapshot codec')
    objects=[]
    def decode(value):
        if isinstance(value,dict):
            if set(value)!={REFERENCE}:raise ValueError('Malformed Graph snapshot reference')
            index=value[REFERENCE]
            if type(index) is not int or not 0<=index<len(objects):raise ValueError('Invalid or forward Graph snapshot reference')
            return objects[index]
        if isinstance(value,list):raise ValueError('Unexpected nested transport list')
        return value
    for record in trace['graph_snapshot_pool']:
        if not isinstance(record,list) or len(record)!=2 or record[0] not in (0,1):raise ValueError('Malformed Graph pool record')
        if record[0]==0:
            keys=[item[0] for item in record[1]]
            if not all(isinstance(k,str) for k in keys) or len(set(keys))!=len(keys):raise ValueError('Invalid Graph pool dictionary keys')
            value={k:decode(v) for k,v in record[1]}
        else:value=[decode(v) for v in record[1]]
        objects.append(value)
    result={k:v for k,v in trace.items() if k not in {'graph_snapshot_codec','graph_snapshot_pool','graph_snapshot_stats'}}
    result['steps']=[{k:decode(v) if isinstance(v,dict) and REFERENCE in v else v for k,v in step.items()} for step in trace['steps']]
    if 'numeric_C_memory' in trace:result['numeric_C_memory']=decode(trace['numeric_C_memory'])
    return result


def validate_graph_logical_trace(trace):
    """Preserve legacy round-trip/types plus all engine boundary/source checks.

Validate one compatibility conversion at a time. Retain only its semantic
states for the engine; retaining every copied legacy pedagogy was redundant.
No generic engine or other family changes are needed.
"""
    from app.services.trace.compatibility import LegacyTraceAdapter
    from app.services.trace.strategies import TraceStrategyRegistry
    from app.services.trace.engine import TraceEngine
    from app.services.observability import emit_operational_event
    start=perf_counter();strategy=TraceStrategyRegistry.resolve('graph');semantic=[]
    # These semantic views never escape this synchronous, read-only validation.
    # Keep both conversions and every check, without cloning discarded pedagogy.
    borrow = lambda value: value
    for step in trace['steps']:
        if LegacyTraceAdapter.round_trip([step], copy_value=borrow)!=[step]:raise ValueError('Graph compatibility round-trip changed logical step')
        normalized=strategy.normalize_steps([step], copy_value=borrow)[0]
        semantic.append(replace(normalized,before_state=step['state_snapshot'],after_state=step['state_after'],metadata={}))
    TraceEngine.validate_steps(semantic,trace['final_state'],trace['source_code'])
    emit_operational_event('trace_validation',outcome='success',duration_ms=(perf_counter()-start)*1000,
        structure_id='graph',strategy=strategy.family,step_count=len(semantic))


def finish_graph_trace(trace,pool,compact=True):
    trace['final_state']=pool.intern(trace['final_state'])
    validate_graph_logical_trace(trace)
    return pool.pack(trace) if compact else trace
