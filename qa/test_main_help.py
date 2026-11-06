"""Rendered guide/access contracts for complete frontend-generated main programs."""
import html,re,subprocess,tempfile,unittest
from pathlib import Path
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
  text=self.client.get('/help/manual').get_data(as_text=True)
  self.assertIn('main.c del historial',text)
  self.assertIn('Compílalo con el C/H del TAD, no por sí solo.',text)
  self.assertNotIn('Para compilar ese main, añade',text)
  # The current guide supplies a complete example instead of the old sentence.
  # Compile its actual rendered bytes with the downloaded TAD, without adding headers.
  examples=re.findall(r'<pre class="didactic-code">([\s\S]*?)</pre>',text)
  self.assertEqual(len(examples),1)
  source=html.unescape(examples[0])
  self.assertIn('#include <stdio.h>',source)
  self.assertIn('#include "tad_pila.h"',source)
  root=Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as folder:
   directory=Path(folder);main=directory/'main.c';main.write_text(source)
   result=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic',
       '-I',str(root/'docs/tads_C'),str(main),str(root/'docs/tads_C/tad_pila.c'),
       '-o',str(directory/'example')],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
   output=subprocess.run([str(directory/'example')],capture_output=True,text=True)
   self.assertEqual(output.returncode,0,output.stderr)
   self.assertEqual(output.stdout,'Sale: 30\n')
if __name__=='__main__':unittest.main()
