"""No replay or storage writes for oversized saved tables."""
import copy,tempfile,unittest
from unittest.mock import patch
from app import create_app
from app.config import Config
from app.services.hash_structure_service import HashStructureService as S
from app.services.hash_main_service import build_hash_main
from app.services.session_service import SESSION_KEY
from app.services.hash_journal_service import KEY as JOURNAL_KEY,digest
class HashCapacityTests(unittest.TestCase):
 def history(self,cap):return [{'operation':'create_table','payload':{'capacity':cap}},{'operation':'insert','payload':{'key':3,'value':7}}]
 def test_legacy_before_replay(self):
  for cap in (129,2147483647):
   for later in ([],[{'operation':'create_table','payload':{'capacity':5}}]):
    h=self.history(cap)+later;original=copy.deepcopy(h)
    with self.subTest(cap=cap,later=bool(later)),patch.object(S,'_rebuild_adapter',side_effect=AssertionError('no replay')):
     model=S.get_view_model('hash_table',h);self.assertTrue(model['visual_state']['suspended']);self.assertNotIn('size',model['visual_state']['metadata']);self.assertEqual(model['history'],original);self.assertEqual(model['main_c'],build_hash_main(original))
     for op,p in [('insert',{'key':4,'value':8}),('create_table',{'capacity':5}),('clear',{}),('stats',{})]:
      r=S.execute_operation('hash_table',op,p,h);self.assertFalse(r['success']);self.assertTrue(r['preserve_session']);self.assertEqual(r['execution_trace']['steps'],[]);self.assertFalse(r['execution_trace']['execution_started']);self.assertEqual(r['history'],original)
     self.assertEqual(h,original)
 def test_new_frontier(self):
  h=self.history(5);before=S.get_view_model('hash_table',h)['visual_state']
  for cap in (129,2147483647,'129'):
   r=S.execute_operation('hash_table','create_table',{'capacity':cap},h);self.assertFalse(r['success']);self.assertEqual(r['visual_state'],before);self.assertEqual(r['history'],h);self.assertEqual(r['execution_trace']['steps'],[])
  r=S.execute_operation('hash_table','create_table',{'capacity':128},[]);self.assertTrue(r['success']);self.assertEqual(r['visual_state']['metadata']['capacity'],128)
  field=S.get_view_model('hash_table',[])['operations'][0]['inputs'][0];self.assertEqual((field['min'],field['max'],field['step']),(1,128,1))
 def test_http_no_writes_export_reset(self):
  with tempfile.TemporaryDirectory() as folder:
   class T(Config):TESTING=True;SESSION_CACHE_DIR=folder
   client=create_app(T).test_client();key='hash::hash_table'
   for legacy in (True,False):
    h=self.history(2147483647);checkpoint={'schema':'hash-trace/v1','history_digest':digest(h),'trace':{'steps':[{'narration':'STALE_CHECKPOINT_SENTINEL'}]}}
    record=h if legacy else {'schema_version':1,'history':h,'checkpoint':checkpoint};journal={'history_digest':digest(h),'entries':h+[{'operation':'get','payload':{'key':3}}]}
    with client.session_transaction() as sess:
     sess[SESSION_KEY]={key:copy.deepcopy(record)};sess[JOURNAL_KEY]={key:journal};saved=copy.deepcopy(dict(sess))
    with patch.object(S,'_rebuild_adapter',side_effect=AssertionError('no replay')):
     response=client.get('/hash/hash_table');self.assertEqual(response.status_code,200);self.assertNotIn('STALE_CHECKPOINT_SENTINEL',response.get_data(as_text=True))
     response=client.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}});self.assertEqual(response.status_code,400);body=response.get_json();self.assertEqual(body['history'],h);self.assertEqual(body['main_c'],build_hash_main(journal['entries']))
    with client.session_transaction() as sess:self.assertEqual(dict(sess),saved)
    response=client.post('/hash/hash_table/reset');self.assertEqual(response.status_code,200);self.assertEqual(response.get_json()['history'],[]);self.assertEqual(response.get_json()['main_c'],build_hash_main([]));self.assertEqual(response.get_json()['visual_state']['metadata']['capacity'],17)
if __name__=='__main__':unittest.main(verbosity=2)
