"""Counting-only bounded immutable page sources and session-owned local storage."""
from __future__ import annotations
from bisect import bisect_right
from copy import deepcopy
from dataclasses import dataclass
from secrets import token_urlsafe
from threading import RLock, BoundedSemaphore
from time import monotonic
import sys
from typing import Any
from app.domain.sorting.counting_sparse_tape import CountingTape, expand_small
from app.domain.sorting.counting_sparse_instructions import instruction_line_lookup, instruction_pedagogy
from app.domain.sorting.pedagogy import validate_pedagogical_frame, pedagogical_frame_schema, learning_profile, theory_profile

BUILD_SLOTS = BoundedSemaphore(2)

def deep_size(value: Any, seen: set[int] | None = None) -> int:
    """Account retained Python containers once, including sparse states and strings."""
    seen = seen if seen is not None else set()
    identity = id(value)
    if identity in seen: return 0
    seen.add(identity)
    total = sys.getsizeof(value)
    if isinstance(value, dict): total += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in value.items())
    elif isinstance(value, (list, tuple)): total += sum(deep_size(v, seen) for v in value)
    return total

class CountingTrace(dict):
    """JSON-compatible transport dictionary with a private unbound source attribute."""
    page_source: CountingPageSource

class CountingPageSource:
    """Render any logical event without enumerating intervening empty buckets."""
    def __init__(self, tape: CountingTape, source_code: str, *, error_info: dict[str,Any] | None = None, accepted_state: dict[str,Any] | None = None):
        self.error_info = deepcopy(error_info)
        self.accepted_state = deepcopy(accepted_state)
        self.tape = tape
        self.source_code = source_code
        self.lines = source_code.replace('\r\n', '\n').split('\n')
        self.lookup = instruction_line_lookup(source_code) if source_code else {}
        self.final_state = self.state(tape[-1])
        self.final_state['last_operation'] = dict(name='counting_sort', status='error' if error_info else 'success', message=error_info['message'] if error_info else 'Ordenamiento finalizado.')
        self.concept_runs = []
        start = 0
        done = set()
        self.done_prefix = []
        self.line_patterns = []
        for record, end in zip(tape.records, tape.ends):
            self.done_prefix.append(sorted(done))
            if record['kind'] == 'zero_span':
                pattern = ['condition', 'condition', 'assignment']
                line_pattern = [self.lookup.get(t) for t in ('rebuild_test', 'bucket_test', 'rebuild_increment')]
            else:
                row = tape[start]
                token = row['line_token']
                concept = 'comparison' if token in ('min_compare', 'max_compare') else 'condition' if row['condition_result'] is not None else 'return' if token == 'error_return' or token.endswith('return') else 'call' if token.endswith(('call', 'entry', 'resume')) else 'phase' if token == 'initial' else 'assignment'
                pattern = [concept]
                line_pattern = [self.lookup.get(row.get("source_line_token", token))]
            self.line_patterns.append(line_pattern)
            done.update(i for i in line_pattern if i is not None)
            self.concept_runs.append((start, end, pattern))
            start = end
        self.retained_bytes = deep_size([tape.records, tape.ends, tape._last, self.lines, self.lookup, self.final_state, self.concept_runs, self.done_prefix, self.line_patterns, self.error_info, self.accepted_state])

    @staticmethod
    def state(row: dict[str, Any]) -> dict[str, Any]:
        from app.adapters.sorting_adapter import SortingAdapter
        return SortingAdapter._build_visual_state_from_step(None, row, algorithm_id='counting_sort')

    def ordinal(self, index: int, concept: str) -> int:
        """Count a concept prefix algebraically across repeated control spans."""
        total = 0
        for start, end, pattern in self.concept_runs:
            take = min(end, index + 1) - start
            if take <= 0: break
            repeats, rest = divmod(take, len(pattern))
            total += repeats * pattern.count(concept) + pattern[:rest].count(concept)
        return total

    def locate(self, concept: str, occurrence: int) -> int | None:
        if occurrence < 1: raise ValueError('La ocurrencia debe ser positiva.')
        last = None
        for start, end, pattern in self.concept_runs:
            positions = [i for i, name in enumerate(pattern) if name == concept]
            count = (end-start)//len(pattern)*len(positions)
            if count:
                last = end-len(pattern)+positions[-1]
                if occurrence <= count:
                    repeat, offset = divmod(occurrence-1, len(positions))
                    return start + repeat*len(pattern) + positions[offset]
                occurrence -= count
        return last

    @staticmethod
    def dense_row(row: dict[str, Any]) -> dict[str, Any]:
        row = deepcopy(row)
        row['instruction_event']['conteo'] = expand_small(row['instruction_event']['conteo'])
        row['auxiliary_snapshot'] = expand_small(row['auxiliary_snapshot'])
        ctx = row['counting_context']
        ctx['buckets'] = [dict(index=i, value=ctx['minimo']+i, count=v) for i, v in enumerate(row['auxiliary_snapshot'] or [])]
        return row

    def frame(self, index: int, dense: bool = False) -> dict[str, Any]:
        row = self.tape[index]
        prev = self.tape[max(0, index-1)]
        if dense: row, prev = self.dense_row(row), self.dense_row(prev)
        token = row['line_token']
        line_index = self.lookup.get(row.get("source_line_token", token))
        text = self.lines[line_index] if line_index is not None else ''
        pedagogy = instruction_pedagogy(row, line_index, text)
        validate_pedagogical_frame(pedagogy, source_code=self.source_code)
        after = self.final_state if index == len(self.tape)-1 else self.state(row)
        frame = dict(step_index=index, line_index=line_index, line_text=text, event_type='line', phase='start' if index==0 else 'end' if index==len(self.tape)-1 else 'progress', delay_ms=160, state_snapshot=self.state(prev), state_after=deepcopy(after), debug=dict(stage='sorting', note=row['action'], instruction_event=row['instruction_event'], console_events=[]), pedagogy=pedagogy)
        if not dense:
            frame['concept_occurrence'] = self.ordinal(index, pedagogy['concept'])
            physical = bisect_right(self.tape.ends, index)
            begin = self.tape.ends[physical-1] if physical else 0
            prior = self.line_patterns[physical][:min(index-begin, len(self.line_patterns[physical]))]
            frame['done_lines'] = sorted(set(self.done_prefix[physical]).union(i for i in prior if i is not None))
        assert frame['state_after']['items'] == row['array_snapshot']
        assert frame['debug']['instruction_event']['token'] == frame['state_after']['trace_token']
        return frame

    def page(self, start: int, limit: int = 64) -> dict[str, Any]:
        if not 1 <= limit <= 128: raise ValueError('El limite de pagina debe ser 1..128.')
        if not 0 <= start < len(self.tape): raise ValueError('El indice esta fuera de la traza.')
        end = min(len(self.tape), start + limit)
        return dict(schema='counting-trace-page/v1', start=start, end=end, step_count=len(self.tape), steps=[self.frame(i) for i in range(start, end)])

    def trace(self) -> dict[str, Any]:
        trace = CountingTrace(structure_id='sorting', operation_name='counting_sort', payload={}, success=True, mutates=True, message='Ordenamiento ejecutado correctamente.', code_title='Codigo C', source_code=self.source_code, final_state=deepcopy(self.final_state), pedagogy_schema_version=1, pedagogy_schema=pedagogical_frame_schema(), learning_profile=learning_profile('counting_sort'), theory_profile=theory_profile('counting_sort'))
        if self.error_info:
            trace.update(success=False,mutates=False,message=self.error_info['message'],native_status=0,error=deepcopy(self.error_info),accepted_state=deepcopy(self.accepted_state))
        n = len(self.tape[0]['array_snapshot'])
        # Transport budget only: both representations use this same semantic tape.
        k = max(((r.get('state', r.get('patch', {})).get('counting_context', {}).get('count_state') or {}).get('length',0)) for r in self.tape.records)
        dense_estimate = len(self.tape)*(n+k+1)*256
        if len(self.tape) <= 2000 and k <= 2048 and dense_estimate <= 2*1024*1024:
            trace['steps'] = [self.frame(i, dense=True) for i in range(len(self.tape))]
            from app.services.trace.engine import TraceEngine
            TraceEngine.validate_legacy_trace(trace)
        else:
            trace.update(schema='counting-paged-trace/v1', step_count=len(self.tape), manifest={**self.tape.manifest(), 'retained_bytes':self.retained_bytes}, initial_page=self.page(0, 16))
        trace.page_source = self
        return trace

    def compact_export(self) -> dict[str, Any]:
        exported = dict(schema='counting-compact-export/v1', source_code=self.source_code, records=deepcopy(self.tape.records), ends=list(self.tape.ends), step_count=len(self.tape), final_state=deepcopy(self.final_state), codec='counting-sparse-tape/v1')
        if self.error_info:exported.update(success=False,mutates=False,error=deepcopy(self.error_info),native_status=0,accepted_state=deepcopy(self.accepted_state))
        return exported

@dataclass(frozen=True)
class StoredTrace:
    owner: str
    source: CountingPageSource
    expires: float

class CountingTraceStore:
    """Process-local, lock-protected storage; GETs leave tape and session untouched."""
    def __init__(self, max_bytes: int = 128*1024*1024, max_traces: int = 32, ttl: float = 900):
        self.max_bytes, self.max_traces, self.ttl = max_bytes, max_traces, ttl
        self.entries: dict[str, StoredTrace] = {}
        self.lock = RLock()

    def register(self, owner: str, source: CountingPageSource) -> str:
        if source.retained_bytes > self.max_bytes: raise ValueError('La traza supera el presupuesto de almacenamiento local.')
        with self.lock:
            now = monotonic()
            self.entries = {k:v for k,v in self.entries.items() if v.expires > now}
            while self.entries and (len(self.entries) >= self.max_traces or sum(v.source.retained_bytes for v in self.entries.values()) + source.retained_bytes > self.max_bytes):
                del self.entries[next(iter(self.entries))]
            key = token_urlsafe(24)
            self.entries[key] = StoredTrace(owner, source, now+self.ttl)
            return key

    def get(self, owner: str | None, key: str) -> CountingPageSource:
        with self.lock:
            item = self.entries.get(key)
            if item is None or item.owner != owner: raise KeyError(key)
            if item.expires <= monotonic(): raise TimeoutError('La traza expiro. La navegacion no vuelve a ejecutar el algoritmo.')
            return item.source

    def revoke(self, owner: str | None) -> None:
        with self.lock: self.entries = {k:v for k,v in self.entries.items() if v.owner != owner}

_STORE_INIT_LOCK = RLock()
def get_counting_store() -> CountingTraceStore:
    from flask import current_app
    with _STORE_INIT_LOCK:
        if 'counting_trace_store' not in current_app.extensions:
            current_app.extensions['counting_trace_store'] = CountingTraceStore()
        return current_app.extensions['counting_trace_store']
