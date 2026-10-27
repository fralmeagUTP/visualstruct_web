"""Compile actual highlighted history markup, preserving every emitted character.
Browser innerText/clipboard remains independently verified by the UI auditor.
"""
import subprocess
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class Lines(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.depth=0;self.active=None;self.lines=[];self.indices=[]
 def handle_starttag(self,tag,attrs):
  self.depth+=1;attrs=dict(attrs)
  if tag=='span' and attrs.get('class')=='code-line':self.active=self.depth;self.lines.append('');self.indices.append(int(attrs['data-line']))
 def handle_data(self,data):
  if self.active is not None:self.lines[-1]+=data
 def handle_endtag(self,tag):
  if self.active==self.depth:self.active=None
  self.depth-=1
subprocess.run(['node','qa/frontend_hier_dom_export.js'],cwd=ROOT,check=True)
out=ROOT.parent/'qa_hier_dom_main';downloads=ROOT.parent/'qa_trazas/downloaded_c'
for kind,tad in [('abb','tad_abb'),('avl','tad_avl'),('red_black','tad_rojo_negro'),('binary_heap','tad_monticulo_binario')]:
 html=(out/f'{kind}.html').read_text();p=Lines();p.feed(html)
 source='\n'.join(p.lines)
 assert p.indices==list(range(len(p.lines)))
 assert source==(out/f'{kind}.expected.c').read_text(),kind
 assert '\u00a0' not in source and '&nbsp;' not in html,kind
 assert any(line=='' for line in p.lines),kind
 path=out/f'{kind}.c';path.write_text(source)
 cmd=['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-I',str(downloads),str(path),str(downloads/f'{tad}.c'),'-o',str(out/kind)]
 subprocess.run(cmd,check=True,capture_output=True)
 subprocess.run([str(out/kind)],check=True,capture_output=True)
 print('PASS',kind,'actual highlighted markup characters unchanged; downloaded C/H compile and run')
css=(ROOT/'static/css/contextual_help.css').read_text();assert '.code-line:empty { min-height: 1.4em; }' in css
