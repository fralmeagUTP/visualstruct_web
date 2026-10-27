"""Scope safety of concrete case proposals; no app/test campaign execution."""
from scripts.validate_resolve71_proposals import validate

def proposal(ident='operation:graph/graph/list_vertices'):
 return {'id':ident,'status':'PROPOSED_NOT_IMPLEMENTED_NOT_EXECUTED','request_or_gesture':{'path':'/graph/graph/operate'},'expected':{'result':[1]},'setup':[{'operation':'insert_vertex','payload':{'vertex':1}}]}

def test_scope_and_duplicates_are_rejected():
 row=proposal();allowed={row['id']}
 assert validate([row],allowed)==[]
 assert any('duplicate:' in e for e in validate([row,row],allowed))
 assert any('out-of-assignment:' in e for e in validate([proposal('unassigned')],allowed))

def test_no_input_or_expected_cannot_be_a_concrete_case():
 row=proposal();row['expected']={}
 assert any('missing-input-or-oracle:' in e for e in validate([row],{row['id']}))

def test_graph_proposals_preserve_the_eight_vertex_test_bound():
 row=proposal();row['setup']=[{'operation':'insert_vertex','payload':{'vertex':i}} for i in range(9)]
 assert any('graph-test-bound:' in e for e in validate([row],{row['id']}))
