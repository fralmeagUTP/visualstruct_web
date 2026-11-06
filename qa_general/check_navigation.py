"""Read-only Flask crawl of actual internal navigation and static references."""
from pathlib import Path
import json,sys,tempfile
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.config import Config
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.assets=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and a.get('href'):self.links.append(a['href'])
  if tag in ['script','link']:
   v=a.get('src') if tag=='script' else a.get('href')
   if v:self.assets.append(v)
with tempfile.TemporaryDirectory() as folder:
 class C(Config):TESTING=True;SESSION_CACHE_DIR=folder
 capture=ROOT/'qa_general/tmp/navigation-dom';capture.mkdir(parents=True,exist_ok=True)
 client=create_app(C).test_client();queue=['/'];seen=set();rows=[];targets=[];downloads=[]
 while queue:
  route=queue.pop(0)
  if route in seen:continue
  seen.add(route);r=client.get(route,follow_redirects=True)
  assert r.status_code==200,(route,r.status_code)
  if not r.content_type.startswith('text/html'):
   downloads.append({'route':route,'bytes':len(r.data),'status':r.status_code});continue
  p=Links();p.feed(r.get_data(as_text=True));duplicates=sorted({x for x in p.ids if p.ids.count(x)>1})
  assert not duplicates,(route,'duplicate IDs',duplicates)
  (capture/f'{len(rows)}.html').write_text(r.get_data(as_text=True))
  rows.append({'route':route,'status':r.status_code,'ids':len(p.ids),'links':len(p.links)})
  for href in p.links:
   u=urlsplit(urljoin(route,href))
   if u.netloc or u.scheme:continue
   if u.fragment:targets.append((route,u.path or route,u.fragment))
   target=u.path+('?' + u.query if u.query else '')
   if target not in seen:queue.append(target)
  for href in p.assets:
   u=urlsplit(href)
   if u.netloc or u.scheme:continue
   asset=client.get(href);assert asset.status_code==200,(route,href,asset.status_code)
 for source,target,fragment in targets:
  p=Links();p.feed(client.get(target,follow_redirects=True).get_data(as_text=True));assert fragment in p.ids,(source,target,fragment)
 result={'html_pages':len(rows),'pages':rows,'downloads':downloads,'fragment_targets':len(targets),'limits':'Flask links and HTML, no browser, layout, responsive or keyboard claim'}
 (ROOT/'qa_general/navigation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(f'PASS {len(rows)} linked HTML pages, {len(downloads)} downloads, {len(targets)} fragment targets, static resources and no duplicate IDs.')
