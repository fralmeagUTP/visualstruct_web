"""Negatives ensure final-state certification cannot be replaced by a constant."""
from copy import deepcopy
import pytest
from _final_hierarchy_oracle import assert_final_hierarchical_invariant

def leaf(value, *, color=None):
    node={'value':value,'left':None,'right':None,'height':1,'balance_factor':0}
    if color:node['color']=color
    return node

def state(root, size=1, height=1, inorder=None):
    return {'root':root,'size':size,'height':height,'empty':root is None,'validation':True,'traversals':{'inorden':[10] if inorder is None else inorder}}

def corrupt(case):
    if case=='heap_order':return 'binary_heap',{'array':[9,1],'root':{'value':9,'left':{'value':1,'left':None,'right':None},'right':None},'size':2,'capacity':8,'empty':False}
    if case=='heap_shape':return 'binary_heap',{'array':[1],'root':{'value':2,'left':None,'right':None},'size':1,'capacity':8,'empty':False}
    if case=='avl_height':return 'avl',state({**leaf(10),'height':99})
    if case=='avl_balance':
        root=leaf(10);root.update(left=leaf(5),height=3,balance_factor=-2);root['left'].update(left=leaf(1),height=2,balance_factor=-1);return 'avl',state(root,3,3,[1,5,10])
    if case=='bst_order':
        root=leaf(10);root.update(left=leaf(20),height=2,balance_factor=-1);return 'avl',state(root,2,2,[20,10])
    if case=='rn_root':return 'red_black',state(leaf(10,color='RED'))
    if case=='rn_red_edge':
        root=leaf(10,color='BLACK');root['left']=leaf(5,color='RED');root['left']['left']=leaf(1,color='RED');return 'red_black',state(root,3,3,[1,5,10])
    if case=='rn_black_height':
        root=leaf(10,color='BLACK');root['left']=leaf(5,color='BLACK');return 'red_black',state(root,2,2,[5,10])
    raise AssertionError(case)

@pytest.mark.parametrize('case',['heap_order','heap_shape','avl_height','avl_balance','bst_order','rn_root','rn_red_edge','rn_black_height'])
def test_oracle_rejects_invalid_structure_even_when_reported_valid(case):
    kind, final=corrupt(case)
    assert final.get('validation',True) is True
    with pytest.raises(AssertionError):assert_final_hierarchical_invariant(kind,final)
