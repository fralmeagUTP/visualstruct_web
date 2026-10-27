import json
from pathlib import Path
import unittest
from app.services.structure_service import StructureService
from app.services.execution_trace_service import ExecutionTraceService

class SpanishEncodingTests(unittest.TestCase):
    def test_priority_trace_text_utf8(self):
        history=[]
        for value,priority in [(7,3),(8,1),(9,1)]:
            result=StructureService.execute_operation('priority_queue','encolar',{'value':value,'priority':priority},history)
            history=result['history']
        for operation in ['frente','desencolar']:
            result=StructureService.execute_operation('priority_queue',operation,{},history)
            self.assertTrue(result['success'])
            text=json.dumps(result['execution_trace'],ensure_ascii=False)
            for invalid in ['Ã','Â','âœ']:
                self.assertNotIn(invalid,text)
            self.assertIn('asignación',text)
    def test_source_text_has_no_corrupted_utf8(self):
        for folder in ['app','static','templates']:
            for file in Path(folder).rglob('*'):
                if file.suffix not in ['.py','.js','.html','.css']: continue
                with self.subTest(file=str(file)):
                    text=file.read_text()
                    for invalid in ['Ã','Â','âœ','â€','ðŸ']:
                        self.assertNotIn(invalid,text)
    def test_c_literal_unicode_and_newlines(self):
        self.assertEqual(ExecutionTraceService._printf_literal('printf("Cola vacía.\\n");',preserve_trailing_newlines=True),'Cola vacía.\n')

if __name__=='__main__':unittest.main()
