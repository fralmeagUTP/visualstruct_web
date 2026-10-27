"""All highlighted/plain code renderers preserve blank and preprocessor lines."""
import json,subprocess
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.depth=0;self.active=None;self.lines=[];self.indices=[]
 def handle_starttag(self,tag,attrs):
  self.depth+=1;attrs=dict(attrs)
  if attrs.get('class')=='code-line':self.active=self.depth;self.lines.append('');self.indices.append(int(attrs['data-line']))
 def handle_data(self,data):
  if self.active is not None:self.lines[-1]+=data
 def handle_endtag(self,tag):
  if self.active==self.depth:self.active=None
  self.depth-=1
subprocess.run(['node','qa/export_code_renderer_fixtures.js'],cwd=ROOT,check=True)
out=ROOT.parent/'qa_hier_dom_main';fixtures=json.loads((out/'renderers.json').read_text())
for i,row in enumerate(fixtures['results']):
 p=Parser();p.feed(row['html']);source='\n'.join(p.lines)
 assert source==fixtures['raw'],row['name']
 assert '\u00a0' not in source and '&nbsp;' not in row['html']
 assert p.indices==list(range(len(fixtures['raw'].split('\n'))))
 path=out/f'renderer_{i}.c';path.write_text(source)
 subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic',str(path),'-o',str(out/f'renderer_{i}')],check=True,capture_output=True)
 subprocess.run([str(out/f'renderer_{i}')],check=True)
print('PASS',len(fixtures['results']),'actual rendering paths; exact decoded source, empty/trailing lines, macro continuation, line indices and C17 execution')
