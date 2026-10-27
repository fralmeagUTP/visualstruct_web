import tempfile,sys
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.config import Config
class IDs(HTMLParser):
 def __init__(self):super().__init__();self.ids=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:self.ids.append(attrs['id'])
with tempfile.TemporaryDirectory() as folder:
 class T(Config):TESTING=True;SESSION_CACHE_DIR=folder
 app=create_app(T);client=app.test_client()
 for url in ['/sequential/stack','/hierarchical/abb','/graph/graph/construccion','/hash/hash_table','/sorting/sorting_array']:
  response=client.get(url);assert response.status_code==200,(url,response.status_code)
  html=response.get_data(as_text=True);parser=IDs();parser.feed(html)
  assert len(parser.ids)==len(set(parser.ids)),url
  assert 'classroom_view.js' in html and 'classroom_view.css' in html,url
  if 'hierarchical' in url:
   assert '<details class="classroom-examples">' in html
   assert 'id="hier-guided-example"' in html and 'id="hier-load-example"' in html
  print('PASS template',url,'unique IDs and shared imports')
