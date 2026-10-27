"""Recover safe text artifacts in exact legacy subtrees consumed by named tests."""
import argparse,hashlib,json,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TESTS=['test_priority_queue_encolar_baseline_low.py','test_priority_queue_limpiar_baseline_low.py','test_priority_queue_limpiar_baseline_completion_low.py','test_priority_intermediate_residual_focal.py','test_queue_encolar_baseline_low.py','test_queue_limpiar_baseline_completion_low.py','test_queue_intermediate_residual_focal.py','test_stack_apilar_baseline_low.py','test_stack_limpiar_baseline_low.py','test_stack_limpiar_instructions_medium.py','test_stack_queue_show_baseline_low.py','test_hash_two_consumer_oracle_controls.py']
PREFIX='openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/'
SAFE={'.json','.jsonl','.c','.h','.py'}
SIGNATURES=[re.compile(x) for x in [rb'-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'github_pat_[A-Za-z0-9_]{40,}',rb'AKIA[0-9A-Z]{16}']]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);args=parser.parse_args()
 texts=[(ROOT/'tests'/name).read_text(encoding='utf-8') for name in TESTS]
 folders={name for text in texts for name in re.findall(r'visible-[a-z0-9-]+',text) if not name.endswith('-')}
 # These four names are constructed from the explicit operation inventories in
 # the priority/queue intermediate-consumer tests rather than full literals.
 folders.update('visible-'+family+'-'+operation+'-baseline-low' for family in ['priority-queue','queue'] for operation in ['encolar','desencolar','limpiar'])
 folders=sorted(folders)
 package=ROOT/'tests/fixtures/published-audit-inputs';manifest=json.loads((package/'manifest.json').read_text());rows={row['path']:row for row in manifest['files']};added={};missing=[]
 for folder in folders:
  original=args.source/PREFIX/folder
  if not original.is_dir():missing.append(folder);continue
  for path in original.rglob('*'):
   if not path.is_file() or (path.suffix not in SAFE and not (path.suffix=='.xml' and 'caller-doxygen' in path.parts)):continue
   name=path.relative_to(args.source).as_posix()
   if name not in rows:added[name]=path
 # This exact log is asserted by the enqueue test; do not scoop arbitrary logs.
 logname=PREFIX+'visible-priority-queue-encolar-instructions-medium/native/stderr.log'
 if logname not in rows:
  log=args.source/logname
  if not log.is_file():raise FileNotFoundError(logname)
  added[logname]=log
 for relative in ['visible-priority-queue-limpiar-instructions-medium/native/stderr.log','visible-queue-encolar-instructions-medium/native/stderr.log','visible-stack-apilar-instructions-medium/native/stderr.log','visible-stack-limpiar-baseline-low/native/stderr.log','visible-stack-cima-baseline-low/caller-doxygen/warnings.log','visible-queue-front-final-baseline-low/caller-doxygen/warnings.log']:
  name=PREFIX+relative
  if name not in rows:
   original=args.source/name
   if not original.is_file():raise FileNotFoundError(name)
   added[name]=original
 reuse=args.source/(PREFIX+'visible-stack-queue-show-instructions-medium/caller-input-reuse.json')
 if reuse.is_file():
  for record in json.loads(reuse.read_text(encoding='utf-8-sig'))['inputs']:
   for key in ['current','baseline']:
    name=record[key].replace('\\','/').replace('openspec/changes/audit-local-quality-and-unified-controls/','openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/')
    if not name.startswith(PREFIX) or name in rows:continue
    original=args.source/name
    if not original.is_file() or original.suffix not in SAFE:raise ValueError('Unexpected caller reuse input: '+name)
    added[name]=original
 # Despite its historical suffix, this exact asserted input is UTF-8 C source,
 # not an executable/binary artifact. Preserve it without changing its bytes.
 text_source=PREFIX+'visible-hash-two-consumers-low/before-3.bin'
 if text_source not in rows:
  source_path=args.source/text_source;raw=source_path.read_bytes();text=raw.decode('utf-8-sig')
  if '\x00' in text or '#include' not in text:raise ValueError('Expected textual C source: '+text_source)
  added[text_source]=source_path
 for name,path in added.items():
  digest=hashlib.sha256();size=0;overlap=b''
  with path.open('rb') as source:
   for chunk in iter(lambda:source.read(65536),b''):
    if any(pattern.search(overlap+chunk) for pattern in SIGNATURES):raise ValueError('Credential signature: '+name)
    digest.update(chunk);size+=len(chunk);overlap=chunk[-256:]
  rows[name]={'path':name,'sha256':digest.hexdigest(),'bytes':size,'provenance':'Exact original safe-text fixture in an evidence subtree consumed by named permanent regression tests; no new execution.'}
 if added:
  new=package/'inputs.legacy-recovery.zip'
  with zipfile.ZipFile(package/'inputs.zip') as old,zipfile.ZipFile(new,'w',compression=zipfile.ZIP_DEFLATED) as archive:
   for name in sorted(rows):
    with archive.open(name,'w',force_zip64=True) as output:
     with (added[name].open('rb') if name in added else old.open(name)) as source:shutil.copyfileobj(source,output)
  new.replace(package/'inputs.zip');manifest['files']=sorted(rows.values(),key=lambda row:row['path']);manifest['archive_sha256']=hashlib.sha256((package/'inputs.zip').read_bytes()).hexdigest();(package/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report={'consumer_tests':TESTS,'exact_evidence_subtrees':folders,'added':sorted(added),'unavailable_original_subtrees':missing,'records':len(rows)}
 (package/'legacy-recovery-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print('Recovered legacy consumed fixtures:',len(added),'records:',len(rows),'unavailable subtrees:',missing)

if __name__=='__main__':main()
