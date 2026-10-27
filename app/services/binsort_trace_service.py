"""Binsort-only presentation of the shared Counting codec; Counting defaults unchanged."""
from __future__ import annotations
from copy import deepcopy
import re
from app.services.counting_trace_service import CountingPageSource, deep_size
from app.domain.sorting.pedagogy import learning_profile, theory_profile, validate_pedagogical_frame
class BinsortPageSource(CountingPageSource):
    def __init__(self,tape,source_code,*,error_info=None,accepted_state=None):
        super().__init__(tape,source_code,error_info=error_info,accepted_state=accepted_state)
        start = next(i for i,line in enumerate(self.lines) if re.match(r'\s*int ordenar_binsort\(',line))
        call = next(i for i in range(start,len(self.lines)) if 'return ordenar_counting_sort(' in self.lines[i])
        self.lookup.update(binsort_entry=start,binsort_delegate=call,binsort_return=call)
        self.final_state['last_operation'].update(name='binsort')
        self.concept_runs=[];self.done_prefix=[];self.line_patterns=[]
        begin=0;done=set()
        for record,end in zip(tape.records,tape.ends):
            self.done_prefix.append(sorted(done))
            if record['kind']=='zero_span':
                pattern=['condition','condition','assignment']
                lines=[self.lookup[t] for t in ('rebuild_test','bucket_test','rebuild_increment')]
            else:
                row=tape[begin];token=row['line_token']
                concept='call' if token=='binsort_delegate' else 'comparison' if token in ('min_compare','max_compare') else 'condition' if row['condition_result'] is not None else 'return' if token.endswith('return') else 'call' if token.endswith(('call','entry','resume')) else 'phase' if token=='initial' else 'assignment'
                pattern=[concept];lines=[self.lookup.get(row.get('source_line_token',token))]
            self.line_patterns.append(lines);done.update(i for i in lines if i is not None);self.concept_runs.append((begin,end,pattern));begin=end
        self.retained_bytes=deep_size([tape.records,tape.ends,tape._last,self.lines,self.lookup,self.final_state,self.concept_runs,self.done_prefix,self.line_patterns,self.error_info,self.accepted_state])
    @staticmethod
    def state(row):
        state=CountingPageSource.state(row)
        state['algorithm']='binsort'
        state['binsort_context']=deepcopy(row['binsort_context'])
        return state
    def frame(self,index,dense=False):
        frame=super().frame(index,dense=dense)
        token=frame['debug']['instruction_event']['token']
        if token=='binsort_delegate':frame['pedagogy']['concept']='call'
        if token=='binsort_return':frame['debug']['native_status']=self.tape.native_status
        if not dense:frame['concept_occurrence']=self.ordinal(index,frame['pedagogy']['concept'])
        validate_pedagogical_frame(frame['pedagogy'],source_code=self.source_code)
        return frame
    def trace(self):
        trace=super().trace()
        trace.update(operation_name='binsort',native_status=self.tape.native_status,learning_profile=learning_profile('binsort'),theory_profile=theory_profile('binsort'))
        return trace
    def compact_export(self):
        trace=super().compact_export()
        trace.update(operation_name='binsort',native_status=self.tape.native_status,wrapper='ordenar_binsort',delegate='ordenar_counting_sort')
        return trace
