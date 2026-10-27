"""Counting-only immutable sparse/delta tape with lossless zero-bucket control spans."""
from __future__ import annotations
from bisect import bisect_right
from copy import deepcopy
from typing import Any

class SparseCounts:
    """Logical calloc int[k]: zero default and at most n nonzero buckets."""
    def __init__(self,length: int):
        self.length=length;self.nonzero: dict[int,int]={};self.total=0
    def __getitem__(self,index: int) -> int:
        if not 0<=index<self.length:raise IndexError(index)
        return self.nonzero.get(index,0)
    def __setitem__(self,index: int,value: int) -> None:
        old=self[index];self.total+=value-old
        if value:self.nonzero[index]=value
        else:self.nonzero.pop(index,None)
    def snapshot(self) -> dict[str,Any]:
        return dict(schema='counting-sparse-array/v1',length=self.length,default=0,nonzero=[[k,v] for k,v in sorted(self.nonzero.items())])
    def next_nonzero(self,start: int) -> int:
        return min((k for k in self.nonzero if k>=start),default=self.length)

def sparse_window(snapshot: dict[str,Any] | None,start: int=0,limit: int=64) -> list[dict[str,int]]:
    """Read an exact bounded bucket window; never expand a whole large calloc."""
    if not 1<=limit<=128:raise ValueError('window limit must be 1..128')
    if snapshot is None:return []
    if not 0<=start<=snapshot['length']:raise IndexError(start)
    nonzero=dict(snapshot['nonzero'])
    return [dict(index=k,count=nonzero.get(k,0)) for k in range(start,min(snapshot['length'],start+limit))]

def expand_small(snapshot: dict[str,Any] | None,max_length: int=2048) -> list[int] | None:
    """Compatibility/oracle helper with an explicit materialization budget."""
    if snapshot is None:return None
    if snapshot['length']>max_length:raise ValueError('dense expansion exceeds budget')
    out=[0]*snapshot['length']
    for k,v in snapshot['nonzero']:out[k]=v
    return out

class CountingTape:
    """Deltas plus checkpoints on stored records, not on millions of logical steps."""
    def __init__(self):
        self.records: list[dict[str,Any]]=[];self.ends: list[int]=[];self._last: dict[str,Any] | None=None
    def __len__(self) -> int:return self.ends[-1] if self.ends else 0
    def append(self,row: dict[str,Any]) -> None:
        if row['step']!=len(self)+1:raise ValueError('non-contiguous instruction')
        if self._last is None or len(self.records)%32==0:record=dict(kind='checkpoint',state=deepcopy(row))
        else:record=dict(kind='delta',patch={k:deepcopy(v) for k,v in row.items() if self._last.get(k)!=v})
        self.records.append(record);self.ends.append(len(self)+1);self._last=deepcopy(row)
    @staticmethod
    def _zero(base: dict[str,Any],start: int,relative: int,absolute: int) -> dict[str,Any]:
        row=deepcopy(base);iteration,stage=divmod(relative,3);i=start+iteration+(stage==2)
        token=('rebuild_test','bucket_test','rebuild_increment')[stage];condition=(True,False,None)[stage]
        row.update(step=absolute+1,line_token=token,action=token.replace('_',' '),condition_result=condition,condition_expression=f"{i} < {base['counting_context']['rango']}" if stage==0 else '0 > 0' if stage==1 else '')
        row['instruction_event'].update(token=token,condition=condition,i=i)
        row['counting_context']['i']=i
        for v in row['instruction_variables']:
            if v['scope']=='ordenar_counting_sort' and v['name']=='i':v.update(value=i,previous=i-1 if stage==2 else i,changed=stage==2)
            else:v.update(previous=v['value'],changed=False)
        return row
    def append_zero(self,start: int,end: int) -> None:
        if end<start:return
        if self._last is None or self._last['instruction_event']['i']!=start:raise ValueError('zero span does not start at current C i')
        snapshot=self._last['instruction_event']['conteo'];nonzero=dict(snapshot['nonzero'])
        if any(start<=k<=end for k in nonzero):raise ValueError('zero span contains nonzero bucket')
        if not 0<=start<=end<snapshot['length']:raise IndexError('zero span outside calloc')
        before=len(self);size=3*(end-start+1);self.records.append(dict(kind='zero_span',start=start,end=end));self.ends.append(before+size)
        self._last=self._zero(self._last,start,size-1,before+size-1)
    def __getitem__(self,index: int) -> dict[str,Any]:
        if index<0:index+=len(self)
        if not 0<=index<len(self):raise IndexError(index)
        if index==len(self)-1:return deepcopy(self._last)
        physical=bisect_right(self.ends,index);checkpoint=physical
        while self.records[checkpoint]['kind']!='checkpoint':checkpoint-=1
        state=deepcopy(self.records[checkpoint]['state'])
        for pos in range(checkpoint+1,physical+1):
            rec=self.records[pos];begin=self.ends[pos-1];end=self.ends[pos]
            if rec['kind']=='checkpoint':state=deepcopy(rec['state'])
            elif rec['kind']=='delta':state.update(deepcopy(rec['patch']))
            else:state=self._zero(state,rec['start'],index-begin if pos==physical else end-begin-1,index if pos==physical else end-1)
        return state
    def page(self,start: int,limit: int=64) -> list[dict[str,Any]]:
        """Pure read/decode: no algorithm dispatch and no mutation of tape or history."""
        if not 1<=limit<=128:raise ValueError('page limit must be 1..128')
        if not 0<=start<=len(self):raise IndexError(start)
        return [self[i] for i in range(start,min(len(self),start+limit))]
    def manifest(self) -> dict[str,Any]:
        return dict(schema='counting-tape-manifest/v1',lossless=True,step_count=len(self),stored_records=len(self.records),checkpoint_interval_stored_records=32,page_limit=128)
