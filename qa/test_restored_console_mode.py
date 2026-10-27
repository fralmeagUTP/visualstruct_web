"""Legacy prepared traces acquire producer-owned metadata without storage writes."""
import copy
import importlib
import importlib.util
import os
from pathlib import Path
import unittest
from flask import Flask,session

class RestoredConsoleModeTests(unittest.TestCase):
    def test_legacy_and_explicit_modes_return_independent_copies(self):
        app=Flask(__name__);app.secret_key='isolated-test-only'
        for name,structure,operation,method in [('stack_push','stack','apilar','prepared_push'),('queue_enqueue','queue','encolar','prepared_enqueue'),('queue_dequeue','queue','desencolar','prepared_dequeue')]:
            if os.environ.get('STDOUT_SESSION_BASELINE'):
                path=Path(os.environ['STDOUT_SESSION_BASELINE'])/f'qa_stdout_contract_{name}_session_baseline.py'
                spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            else:module=importlib.import_module(f'app.services.{name}_session_service')
            for mode in [None,'events','snapshot','future-schema']:
                with self.subTest(producer=name,mode=mode),app.test_request_context('/'):
                    history=[{'operation':operation,'payload':{}}]
                    trace={'structure_id':structure,'operation_name':operation,'source_code':'C source','steps':[{'console':['igual\n','igual\n']}]}
                    if mode is not None:trace['console_mode']=mode
                    session[module._KEY]={'history_digest':module._digest(history),'trace':copy.deepcopy(trace)}
                    session['untouched']={'history':copy.deepcopy(history)}
                    expected=copy.deepcopy(dict(session));session.modified=False
                    kwargs={'source_code':'C source'} if name=='queue_dequeue' else {}
                    restored=getattr(module,method)(history,**kwargs)
                    self.assertEqual(restored['console_mode'],mode if mode is not None else 'snapshot')
                    restored['steps'][0]['console'].append('changed copy')
                    self.assertEqual(dict(session),expected);self.assertFalse(session.modified)
                    self.assertEqual(history,[{'operation':operation,'payload':{}}])
                    self.assertIsNone(getattr(module,method)([],**kwargs))
if __name__=='__main__':unittest.main(verbosity=2)
