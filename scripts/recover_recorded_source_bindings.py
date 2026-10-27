"""Append authentic authority files required by declared source supersessions."""
import argparse,ast,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);args=parser.parse_args()
 tree=ast.parse((ROOT/'tests/_audit_approved_source_supersessions.py').read_text(encoding='utf-8'))
 bindings=next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='SUPERSESSIONS' for target in node.targets))
 expected={path:digest for row in bindings.values() for path,digest in row['reference_bindings'].items()}
 package=ROOT/'tests/fixtures/published-audit-inputs';manifest=json.loads((package/'manifest.json').read_text());rows={row['path']:row for row in manifest['files']};added={};rejected=[]
 for name,digest in expected.items():
  path=Path(name)
  if path.is_absolute() or '..' in path.parts or path.suffix not in {'.json','.md'}:raise ValueError('Unexpected source-binding path')
  if name in rows:
   with zipfile.ZipFile(package/'inputs.zip') as archive:raw=archive.read(name)
   if digest not in {hashlib.sha256(raw).hexdigest(),hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()}:raise ValueError('Existing authority binding mismatch: '+name)
   continue
  original=args.source/path
  if not original.is_file():rejected.append({'path':name,'reason':'original unavailable','expected':digest});continue
  raw=original.read_bytes()
  actual=hashlib.sha256(raw).hexdigest();normalized=hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()
  if digest not in {actual,normalized}:
   rejected.append({'path':name,'reason':'original does not match declared raw or LF binding','expected':digest,'original_sha256':actual,'lf_sha256':normalized});continue
  added[name]=original;rows[name]={'path':name,'sha256':actual,'bytes':len(raw),'reference_binding_sha256':digest,'lf_sha256':normalized,'provenance':'Exact original source-supersession authority; verified against pre-existing declared reference hash, allowing only Git CRLF/LF transport.'}
 if added:
  new=package/'inputs.bindings.zip'
  with zipfile.ZipFile(package/'inputs.zip') as old,zipfile.ZipFile(new,'w',compression=zipfile.ZIP_DEFLATED) as archive:
   for name in sorted(rows):
    with archive.open(name,'w',force_zip64=True) as destination:
     with (added[name].open('rb') if name in added else old.open(name)) as source:shutil.copyfileobj(source,destination)
  new.replace(package/'inputs.zip');manifest['files']=sorted(rows.values(),key=lambda row:row['path']);manifest['archive_sha256']=hashlib.sha256((package/'inputs.zip').read_bytes()).hexdigest();(package/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (package/'source-binding-recovery-report.json').write_text(json.dumps({'added':sorted(added),'rejected':rejected},indent=2)+'\n',encoding='utf-8')
 print('Recovered exact declared source-authority files:',len(added),'records:',len(rows),'rejected mismatches:',len(rejected))

if __name__=='__main__':main()
