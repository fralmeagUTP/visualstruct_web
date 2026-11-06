import json
from app.services.hash_structure_service import HashStructureService
from app.domain.hash.snapshot_pool import HashSnapshotPool
history=[{'operation':'create_table','payload':{'capacity':3}},{'operation':'insert','payload':{'key':1,'value':10}}]
logical=HashStructureService.execute_operation('hash_table','keys',{},history)['execution_trace']
with open('qa_general/hash-codec-fixture.json','w') as f:json.dump({'logical':logical,'wire':HashSnapshotPool().pack(logical)},f)
