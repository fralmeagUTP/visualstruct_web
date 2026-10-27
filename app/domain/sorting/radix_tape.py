"""Radix-only lossless state tape: field/cell deltas and bounded checkpoints."""
from __future__ import annotations
from copy import deepcopy
from threading import RLock
from typing import Any

_MISSING=object()
def _diff(old: Any,new: Any) -> Any:
    if old==new:return None
    if isinstance(old,dict) and isinstance(new,dict) and old.keys()==new.keys():
        return {'kind':'dict','patch':{k:d for k in new if (d:=_diff(old[k],new[k])) is not None}}
    if isinstance(old,list) and isinstance(new,list) and len(old)==len(new):
        return {'kind':'cells','patch':[[i,deepcopy(v)] for i,v in enumerate(new) if old[i]!=v]}
    return {'kind':'value','value':deepcopy(new)}

def _apply(old: Any,delta: dict) -> Any:
    if delta['kind']=='value':return deepcopy(delta['value'])
    if delta['kind']=='dict':
        for k,d in delta['patch'].items():old[k]=_apply(old[k],d)
    else:
        for i,v in delta['patch']:old[i]=deepcopy(v)
    return old

class RadixTape:
    """Immutable logical rows; reading never runs the algorithm."""
    def __init__(self):
        self._decode_lock=RLock()
        self.records:list[dict]=[]
        self._last:dict | None=None
        self._decoded_index=-1
        self._decoded=None
    def __len__(self) -> int:return len(self.records)
    def append(self,row:dict) -> None:
        self.records.append({'kind':'checkpoint','state':deepcopy(row)} if len(self)%128==0 else {'kind':'delta','patch':_diff(self._last,row)})
        self._last=deepcopy(row)
    def __getitem__(self,index:int) -> dict:
        with self._decode_lock:
            return self._decode(index)
    def _decode(self,index:int) -> dict:
        if index<0:index+=len(self)
        if not 0<=index<len(self):raise IndexError(index)
        if index==len(self)-1:return deepcopy(self._last)
        checkpoint=index-index%128
        if checkpoint <= self._decoded_index <= index:
            state=self._decoded
            begin=self._decoded_index+1
        else:
            state=deepcopy(self.records[checkpoint]['state']);begin=checkpoint+1
        for i in range(begin,index+1):state=_apply(state,self.records[i]['patch'])
        self._decoded_index=index;self._decoded=state
        return deepcopy(state)
    def manifest(self) -> dict:
        return dict(schema='radix-tape-manifest/v1',codec='radix-delta-tape/v1',lossless=True,step_count=len(self),stored_records=len(self),checkpoint_interval_stored_records=128,page_limit=128)
