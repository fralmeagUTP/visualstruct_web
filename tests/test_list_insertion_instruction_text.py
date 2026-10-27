"""Truthful instructional insertion message at C's special first position."""
from __future__ import annotations
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client,post_operation

@pytest.mark.parametrize('position,relative,expected,phrase',[
 (1,0,[2,1,3],'al inicio'),(1,-1,[2,1,3],'al inicio'),(2,0,[1,3,2],'despues'),
])
def test_list_insertion_message_matches_reached_C_branch(residual58_client,position:int,relative:int,expected:list[int],phrase:str)->None:
 for value in [1,3]:post_operation(residual58_client,'sequential','linked_list','insertar_final',{'value':value})
 body=post_operation(residual58_client,'sequential','linked_list','insertar_elemento',{'value':2,'position':position,'relative':relative})
 assert phrase in body['message']
 if position==1:assert 'despues' not in body['message']
 assert post_operation(residual58_client,'sequential','linked_list','mostrar')['result']==expected
