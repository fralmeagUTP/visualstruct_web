"""Output contracts distinguish cumulative snapshots from executed C fragments."""
import unittest
from app.services.execution_trace_service import ExecutionTraceService as E
from app.services.structure_service import StructureService as S

class StdoutContractTests(unittest.TestCase):
    def test_generic_literal_events_do_not_repeat_adapter_summary(self):
        source='void prueba(void) {\n printf("vacía\\n");\n printf("vacía\\n");\n return;\n}'
        state=S._new_adapter('linked_list').to_visual_state()
        trace=E.build_trace(structure_id='linked_list',operation_name='test_stdout',payload={},
            didactic_data={'operations':{'test_stdout':source}},before_state=state,after_state=state,
            success=True,message='host message',mutates=False,console_events=['whole-operation summary'])
        self.assertEqual(trace['console_mode'],'events')
        self.assertEqual([part for step in trace['steps'] for part in step.get('console',[])],['vacía\n','vacía\n'])
    def test_generic_adapter_only_events_preserve_repetitions_and_newlines(self):
        source='void prueba(void) {\n return;\n}'
        state=S._new_adapter('linked_list').to_visual_state()
        fragments=['igual\n','igual\n','\n','áé ñ']
        trace=E.build_trace(structure_id='linked_list',operation_name='test_stdout',payload={},
            didactic_data={'operations':{'test_stdout':source}},before_state=state,after_state=state,
            success=True,message='host message',mutates=False,console_events=fragments)
        self.assertEqual([part for step in trace['steps'] for part in step.get('console',[])],fragments)
    def test_linked_show_snapshot_and_search_events(self):
        history=[]
        for value in [7,3,7]:history=S.execute_operation('linked_list','insertar_final',{'value':value},history)['history']
        shown=S.execute_operation('linked_list','mostrar',{},history)['execution_trace']
        self.assertEqual(shown['console_mode'],'snapshot');self.assertEqual(shown['steps'][-1]['console'],[' 1) 7',' 2) 3',' 3) 7'])
        searched=S.execute_operation('linked_list','buscar_elemento',{'value':7},history)['execution_trace']
        self.assertEqual(searched['console_mode'],'events')
        self.assertEqual([part for step in searched['steps'] for part in step.get('console',[])],['\n Encontrado en la posicion 1\n','\n Encontrado en la posicion 3\n'])
if __name__=='__main__':unittest.main(verbosity=2)
