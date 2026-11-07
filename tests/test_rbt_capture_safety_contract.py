"""Exercise the real CI test function with deterministic browser protocol doubles.

No browser is started and no image is claimed: these tests cover capture placement,
origin restriction and exception preservation, not visual output.
"""
from types import SimpleNamespace
from pathlib import Path
import pytest
import test_rbt_visual_safe_diagnostics_e2e as diagnostic

BASE='http://127.0.0.1:43210'
TARGET=BASE+'/hierarchical/red_black'
NODE={'id':'N1','value':5,'left':'NULL','right':'NULL','status':'live','parent':'NULL','color':'black'}

class Response:
 status=200
 def json(self):
  return {'success':True,'execution_trace':{'steps':[{'pedagogy':{'memory_state':{'heap_nodes':[dict(NODE)]}}}]}}

class Pending:
 value=Response()
 def __enter__(self):return self
 def __exit__(self,*args):return False

class Locator:
 def __init__(self,page,selector):self.page=page;self.selector=selector
 @property
 def first(self):return self
 def fill(self,value):self.page.events.append(('fill',value))
 def scroll_into_view_if_needed(self):self.page.maybe_fail('scroll')
 def evaluate_all(self,_):
  self.page.maybe_fail('assertions')
  if self.selector=='[data-abb-node]':return [{k:NODE[k] for k in ['id','value','left','right','status']}]
  if self.selector=='[data-rbt-svg-node]':return [{k:NODE[k] for k in ['id','parent','color']}]
  if self.selector=='[data-rbt-svg-from]':return [['N1','left','NULL'],['N1','right','NULL']]
  raise AssertionError(self.selector)
 def count(self):return 2 if self.selector=='.viz-tree-node.nil' else 0

class Page:
 viewport_size={'width':1366,'height':1000}
 def __init__(self,failure=None,redirect=None,fail_capture=False):
  self.failure=failure;self.redirect=redirect;self.fail_capture=fail_capture
  self.url='about:blank';self.events=[];self.captures=[]
 def maybe_fail(self,where):
  self.events.append((where,))
  if self.failure==where:raise RuntimeError('PRIMARY '+where)
 def on(self,*_):pass
 def goto(self,url,**_):
  self.url=self.redirect or url
  self.maybe_fail('goto')
 def select_option(self,*_):self.maybe_fail('interaction')
 def locator(self,selector):return Locator(self,selector)
 def click(self,*_):pass
 def expect_response(self,*_):return Pending()
 def wait_for_function(self,*_,**__):pass
 def screenshot(self,**kwargs):
  self.captures.append(kwargs);self.events.append(('capture',Path(kwargs['path']).name))
  if self.fail_capture:raise OSError('SCREENSHOT FAILED')

@pytest.fixture
def invoke(monkeypatch,tmp_path):
 def run(page,base=BASE):
  # Fixture setup and pytest report hooks must retain the original cwd.
  with monkeypatch.context() as scoped:
   scoped.chdir(tmp_path)
   scoped.setattr(diagnostic,'reveal_public',lambda *args:page.maybe_fail('reveal'))
   request=SimpleNamespace(post=lambda *args,**kwargs:Response())
   diagnostic.test_rn_null_projection_and_safe_viewport_capture((page,SimpleNamespace(request=request),base),'small',[7,3,9],5)
 return run

@pytest.mark.parametrize('failure',['goto','interaction','reveal','scroll','assertions'])
def test_real_test_captures_on_ui_failure_and_keeps_primary(invoke,failure):
 page=Page(failure=failure)
 with pytest.raises(RuntimeError,match='PRIMARY '+failure):invoke(page)
 assert page.captures[-1]=={'path':'visual-safe-diagnostics/rn-small-null-memory-1366x1000.png','full_page':False}
 if failure!='goto':
  assert page.events.index(('capture','rn-small-initial-1366x1000.png')) < page.events.index((failure,))

@pytest.mark.parametrize('redirect',['https://external.invalid/private','http://127.0.0.1:43211/hierarchical/red_black',BASE+'/unrelated','about:blank'])
def test_redirect_never_gets_captured(invoke,redirect):
 page=Page(redirect=redirect)
 with pytest.raises(AssertionError,match='unexpected destination'):invoke(page)
 assert page.captures==[]

@pytest.mark.parametrize('base',['https://external.invalid','http://localhost:43210','http://127.0.0.1:43210/extra','http://person@127.0.0.1:43210','http://127.0.0.1:43210?q=1'])
def test_non_fixture_base_rejected_before_interaction(invoke,base):
 page=Page()
 with pytest.raises(AssertionError):invoke(page,base)
 assert page.events==[] and page.captures==[]

def test_secondary_capture_failure_does_not_mask_primary(invoke,monkeypatch,capsys):
 page=Page(failure='reveal')
 initial=page.screenshot
 def screenshot(**kwargs):
  if 'null-memory' in kwargs['path']:page.fail_capture=True
  return initial(**kwargs)
 monkeypatch.setattr(page,'screenshot',screenshot)
 with pytest.raises(RuntimeError,match='PRIMARY reveal') as raised:invoke(page)
 assert 'SCREENSHOT FAILED' in '\n'.join(getattr(raised.value,'__notes__',[]))+capsys.readouterr().err
 assert len(page.captures)==2

def test_capture_failure_still_fails_without_primary(invoke,monkeypatch):
 page=Page();initial=page.screenshot
 def screenshot(**kwargs):
  if 'null-memory' in kwargs['path']:page.fail_capture=True
  return initial(**kwargs)
 monkeypatch.setattr(page,'screenshot',screenshot)
 with pytest.raises(OSError,match='SCREENSHOT FAILED'):invoke(page)
 assert len(page.captures)==2

def test_real_test_success_captures_before_and_after_assertions(invoke,tmp_path):
 page=Page();invoke(page)
 assert len(page.captures)==2
 assert page.events.index(('capture','rn-small-initial-1366x1000.png')) < page.events.index(('assertions',))
 assert page.events[-1]==('capture','rn-small-null-memory-1366x1000.png')
 assert (tmp_path/'visual-safe-diagnostics/rn-small-null-memory.json').is_file()


def test_primary_failure_then_external_url_keeps_error_and_skips_capture(invoke,monkeypatch,capsys):
 page=Page();original=page.maybe_fail
 def maybe_fail(where):
  if where=='reveal':
   page.url='https://external.invalid/private'
   raise RuntimeError('PRIMARY reveal')
  return original(where)
 monkeypatch.setattr(page,'maybe_fail',maybe_fail)
 with pytest.raises(RuntimeError,match='PRIMARY reveal') as raised:invoke(page)
 assert len(page.captures)==1
 assert 'unexpected destination' in '\n'.join(getattr(raised.value,'__notes__',[]))+capsys.readouterr().err


@pytest.mark.parametrize('secondary',['capture','external'])
@pytest.mark.parametrize('api',['missing','noncallable'])
def test_python310_exception_without_add_note_keeps_primary(invoke,monkeypatch,capsys,secondary,api):
 class LegacyError(RuntimeError):
  def __getattribute__(self,name):
   if name=='add_note':
    if api=='missing':raise AttributeError(name)
    return None
   return super().__getattribute__(name)
 page=Page();original=page.maybe_fail
 def maybe_fail(where):
  if where=='reveal':
   if secondary=='external':page.url='https://external.invalid/private'
   else:page.fail_capture=True
   raise LegacyError('PRIMARY Python 3.10')
  return original(where)
 monkeypatch.setattr(page,'maybe_fail',maybe_fail)
 with pytest.raises(LegacyError,match='PRIMARY Python 3.10'):invoke(page)
 assert 'Viewport diagnostic unavailable:' in capsys.readouterr().err
 assert len(page.captures)==(1 if secondary=='external' else 2)
