"""Recover referenced, genuine historical test inputs; never synthesize evidence.

Run explicitly with the read-only original checkout as --source. Existing archive
entries are preserved byte for byte. Only existing source files referenced by
recorded JSON metadata can be appended.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'tests/fixtures/published-audit-inputs'
ALIASES = (
 ('openspec/changes/audit-local-quality-and-unified-controls/', 'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/'),
 ('openspec/changes/resolve-didactic-stack-c1-residuals/', 'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/'),
)
ALLOWED = {'.json', '.jsonl', '.c', '.h', '.py'}
SIGNATURES = [re.compile(x) for x in [rb'-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----', rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'github_pat_[A-Za-z0-9_]{40,}', rb'AKIA[0-9A-Z]{16}']]

def canonical(name):
 name=name.replace('\\','/')
 if 'openspec/changes/' not in name:return None
 name=name[name.index('openspec/changes/'):]
 for old,new in ALIASES:
  if name.startswith(old):name=new+name[len(old):]
 p=Path(name)
 if p.is_absolute() or '..' in p.parts or p.suffix not in ALLOWED or '/evidence/' not in name:return None
 return p.as_posix()

def strings(value):
 if isinstance(value,str):yield value
 elif isinstance(value,dict):
  for key,item in value.items():yield str(key);yield from strings(item)
 elif isinstance(value,list):
  for item in value:yield from strings(item)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--metadata',action='append',required=True,help='Exact registered JSON metadata whose referenced inputs are required by tests');args=parser.parse_args()
 source=args.source.resolve();manifest=json.loads((PACKAGE/'manifest.json').read_text(encoding='utf-8'))
 rows={row['path']:row for row in manifest['files']}
 added=[];missing=set();original_paths={}
 with zipfile.ZipFile(PACKAGE/'inputs.zip') as archive:
  assert set(archive.namelist())==set(rows)
  for name in args.metadata:
   if name not in rows or not name.endswith('.json'):raise ValueError('Metadata must be an exact registered JSON input')
   value=json.loads(archive.read(name).decode('utf-8-sig'))
   for candidate in strings(value):
    target=canonical(candidate)
    if target is None or target in rows or target in missing:continue
    path=source/target
    if not path.is_file():missing.add(target);continue
    digest=hashlib.sha256();size=0;overlap=b''
    with path.open('rb') as stream:
     for chunk in iter(lambda:stream.read(65536),b''):
      if any(pattern.search(overlap+chunk) for pattern in SIGNATURES):raise ValueError('Credential signature; not packaged: '+target)
      digest.update(chunk);size+=len(chunk);overlap=chunk[-256:]
    added.append(target);original_paths[target]=path
    rows[target]={'path':target,'sha256':digest.hexdigest(),'bytes':size,'provenance':'Exact original input referenced by recorded fixture metadata; no new execution.'}
 if added:
  new=PACKAGE/'inputs.recovered.zip'
  with zipfile.ZipFile(PACKAGE/'inputs.zip') as old,zipfile.ZipFile(new,'w',compression=zipfile.ZIP_DEFLATED) as archive:
   for name in sorted(rows):
    with archive.open(name,'w',force_zip64=True) as destination:
     with (original_paths[name].open('rb') if name in original_paths else old.open(name)) as entry:shutil.copyfileobj(entry,destination)
  new.replace(PACKAGE/'inputs.zip')
  manifest['files']=sorted(rows.values(),key=lambda row:row['path']);manifest['archive_sha256']=hashlib.sha256((PACKAGE/'inputs.zip').read_bytes()).hexdigest()
  (PACKAGE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report={'added':added,'missing_original_references':sorted(missing),'records':len(rows)}
 (PACKAGE/'recovery-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print('Recovered genuine referenced inputs:',len(added),'total records:',len(rows),'unavailable original references:',len(missing))

if __name__=='__main__':main()
