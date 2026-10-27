"""Frozen first-phase QA, excluding superseded graph-contract expectations."""
import sys, unittest, importlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
suite=unittest.TestSuite()
for file in sorted(Path('qa').glob('test_*.py')):
    if file.name.startswith('test_graph_') or file.stem=='test_http_sessions':continue
    suite.addTests(unittest.defaultTestLoader.loadTestsFromName('qa.'+file.stem))
from qa.test_http_sessions import HttpSessionTests
original=HttpSessionTests.setUpClass.__func__
def setup(cls):
    original(cls)
    cls.matrix=[row for row in cls.matrix if row['module']!='graph']
HttpSessionTests.setUpClass=classmethod(setup)
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(HttpSessionTests))
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
