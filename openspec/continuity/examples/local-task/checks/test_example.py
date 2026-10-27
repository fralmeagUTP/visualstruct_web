"""Example-specific tests: no application or harness-core imports."""
import copy
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('local_example',ROOT/'build_example.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ExampleTests(unittest.TestCase):
    def task(self):
        return {'tasks':{'sample':{'objective':'Document one task','role':'code','owner':'author','allowed_paths':['local/file'],'next_step':'Independent QA'}}}
    def test_snapshot_matches_source(self):
        data=self.task();html=module.render(data,'sample')
        payload=json.loads(re.search(r'<script id="snapshot" type="application/json">(.*?)</script>',html,re.S).group(1))
        self.assertEqual(payload,{**data['tasks']['sample'],'task_id':'sample'})
    def test_markup_cannot_break_snapshot_script(self):
        data=self.task();data['tasks']['sample']['objective']='</script><script>window.__injected=true</script><b>hello</b>'
        html=module.render(data,'sample')
        payload=re.search(r'<script id="snapshot" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertNotIn('<',payload);self.assertEqual(json.loads(payload)['objective'],data['tasks']['sample']['objective'])
    def test_literal_unicode_escapes_preserved(self):
        data=self.task();data['tasks']['sample']['objective']=chr(92)+'u003c <angle> & literal'
        html=module.render(data,'sample')
        payload=re.search(r'<script id="snapshot" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertEqual(json.loads(payload)['objective'],data['tasks']['sample']['objective'])
    def test_unknown_id_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'config.json';output=root/'missing.html';source.write_text(json.dumps(self.task()),encoding='utf-8')
            run=subprocess.run([sys.executable,'-B',str(ROOT/'build_example.py'),'--config',str(source),'--task','missing','--output',str(output)],capture_output=True,text=True)
            self.assertEqual(run.returncode,2);self.assertFalse(output.exists())
    def test_render_is_deterministic_and_keeps_input(self):
        data=self.task();old=copy.deepcopy(data);self.assertEqual(module.render(data,'sample'),module.render(data,'sample'));self.assertEqual(data,old)
    def test_invalid_required_fields_fail(self):
        for field,value in [('owner',''),('allowed_paths',[]),('objective',None)]:
            data=self.task();data['tasks']['sample'][field]=value
            with self.assertRaises(ValueError):module.render(data,'sample')
if __name__=='__main__':unittest.main()
