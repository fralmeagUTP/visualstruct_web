"""Reproducible conservative source census of HTML control creators; no app import."""
from pathlib import Path
import argparse,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def census(root=ROOT):
 sources=[];sites=[];unsupported=[];template_factories=[]
 for path in sorted((root/'static/js').glob('*.js')):
  text=path.read_text(encoding='utf-8-sig');relative=path.relative_to(root).as_posix();digest=hashlib.sha256(path.read_bytes()).hexdigest();sources.append({'path':relative,'sha256':digest})
  for match in re.finditer(r'(?:createElement(?:NS)?|insertAdjacentHTML|createContextualFragment|document\.write)\s*\(([^\n;]{0,200})',text):
   if 'createElement' in match.group() and not re.search(r'button|input|select|textarea|[\"\x27]a[\"\x27]|summary|details',match.group(),re.I):continue
   sites.append({'source':relative,'line':text.count('\n',0,match.start())+1,'kind':'DOM_FACTORY','expression':match.group()[:200],'sha256':digest})
  for match in re.finditer(r'<(?:button|input|select|textarea|a|summary)\b[^>]{0,160}',text,re.I):sites.append({'source':relative,'line':text.count('\n',0,match.start())+1,'kind':'STRING_MARKUP','expression':match.group()[:200],'sha256':digest})
  for match in re.finditer(r'createElement\s*\(\s*([^\n;]{1,90})',text):
   if not match.group(1).startswith(('"',"'")):unsupported.append({'source':relative,'line':text.count('\n',0,match.start())+1,'expression':match.group()})
  for index,line in enumerate(text.splitlines(),1):
   if re.search(r'=\s*(?:document\.)?createElement(?:\.bind)?\s*(?:;|\.)|eval\(|new Function|outerHTML\s*=|insertAdjacentHTML|createContextualFragment|document\.write',line):unsupported.append({'source':relative,'line':index,'expression':line[:200]})
 loaded=set()
 for path in sorted((root/'templates').rglob('*.html')):
  text=path.read_text(encoding='utf-8-sig')
  loaded.update(re.findall(r'js/[a-zA-Z_]+\.js',text))
  for index,line in enumerate(text.splitlines(),1):
   if re.search(r'createElement|insertAdjacentHTML|createContextualFragment|outerHTML\s*=',line):template_factories.append({'source':path.relative_to(root).as_posix(),'line':index,'expression':line[:200]})
 return {'schema':'dynamic-control-source-census/v1','sources':sources,'template_loaded_JS':sorted(loaded),'source_sites':sites,'unsupported_producers':unsupported,'inline_template_factories':template_factories,'interpretation':'Lexical candidate census, not JS parser or runtime proof. Literal creators plus interactive string markup; loops/metadata instantiate families, not arbitrary value cases. SVGgeometry/noninteractivecreateElement omitted by explicit HTMLcontrolscope. Unknown producers remain reported, never silently excluded.'}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();data=census();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'sites':len(data['source_sites']),'sources':len(data['sources']),'unsupported':len(data['unsupported_producers']),'inline':len(data['inline_template_factories'])}))
