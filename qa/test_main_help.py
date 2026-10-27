"""Rendered guide/access contracts for complete frontend-generated main programs."""
import tempfile,unittest
from html.parser import HTMLParser
from app import create_app
from app.config import Config
class HistoryAccess(HTMLParser):
 def __init__(self): super().__init__();self.stack=[];self.hidden_history=None;self.links=0;self.ids=0
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='a' and attrs.get('href')=='#action-history':self.links+=1
  if attrs.get('id')=='action-history':
   self.ids+=1;self.hidden_history=any('didactic-technical' in item.get('class','').split() for item in self.stack)
  if tag not in ['input','br','hr','meta','link','img']:self.stack.append(attrs|{'tag':tag})
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i]['tag']==tag:del self.stack[i:];break
class MainHelpTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory()
  class T(Config):TESTING=True;SESSION_CACHE_DIR=cls.tmp.name
  cls.client=create_app(T).test_client()
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_main_access_for_all_ten_structure_pages(self):
  for area,names in [('sequential',['stack','queue','priority_queue','linked_list','circular_list','sublist']),('hierarchical',['abb','avl','red_black','binary_heap'])]:
   for name in names:
    with self.subTest(name=name):
     r=self.client.get(f'/{area}/{name}');self.assertEqual(r.status_code,200)
     p=HistoryAccess();p.feed(r.get_data(as_text=True));self.assertEqual(p.ids,1);self.assertEqual(p.links,1);self.assertFalse(p.hidden_history)
 def test_sublist_and_circular_guide_match_generated_main(self):
  r=self.client.get('/help/sequential/sublist');text=r.get_data(as_text=True);self.assertEqual(r.status_code,200);self.assertNotIn('main mostrado es un fragmento',text);self.assertIn('ya incluye stdio.h y tad_sublista.h',text)
  text=self.client.get('/help/sequential/circular_list').get_data(as_text=True);self.assertNotIn('En Circular pasa NULL, 0',text);self.assertIn('arreglo de posiciones',text)
 def test_manual_no_longer_requires_manual_headers(self):
  text=self.client.get('/help/manual').get_data(as_text=True);self.assertIn('ya incluye los encabezados necesarios',text);self.assertNotIn('Para compilar ese main, añade',text)
if __name__=='__main__':unittest.main()
