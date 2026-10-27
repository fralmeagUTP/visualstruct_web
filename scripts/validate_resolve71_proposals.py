"""Validate proposal scope, explicit oracles and existing-source integrity only."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];C=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals'
def validate(plans,allowed):
 errors=[];seen=set()
 for row in plans:
  ident=row.get('id')
  if ident not in allowed:errors.append('out-of-assignment:'+str(ident))
  if ident in seen:errors.append('duplicate:'+str(ident))
  seen.add(ident)
  if not row.get('expected') or not row.get('request_or_gesture'):errors.append('missing-input-or-oracle:'+str(ident))
  if row.get('status')!='PROPOSED_NOT_IMPLEMENTED_NOT_EXECUTED':errors.append('proposal-status:'+str(ident))
  vertices=[x for x in row.get('setup',[]) if x.get('operation')=='insert_vertex']
  if len(vertices)>8:errors.append('graph-test-bound:'+str(ident))
 return errors

def main():
 out=C/'bindings-resolve71';plans=json.loads((out/'proposed-tests.json').read_text(encoding='utf-8'));rows=json.loads((out/'missing-links71.json').read_text(encoding='utf-8'));allowed={x['id'] for x in rows};errors=validate(plans,allowed)
 for row in plans:
  for ref in row['sources']:
   p=R/ref['path']
   if hashlib.sha256(p.read_bytes()).hexdigest()!=ref['sha256']:errors.append('changed-source:'+ref['path'])
 assert not errors,errors
 result={'proposal_count':len(plans),'assigned_count':len(allowed),'errors':errors,'source_hashes_verified':True,'execution':False,'semantic_oracle_status':'Reviewed draft expectations, not executed proof or exhaustive missing-test assertion.'}
 (out/'proposal-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
