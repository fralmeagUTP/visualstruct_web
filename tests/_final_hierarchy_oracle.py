"""Independent structural oracle for the final public hierarchical state."""
def assert_final_hierarchical_invariant(structure_id, state):
    if structure_id == 'binary_heap':
        array = state['array']
        assert state['size'] == len(array) and state['capacity'] >= len(array)
        assert state['empty'] is (not array)
        for index in range(1, len(array)):
            assert array[(index-1)//2] <= array[index], 'min-heap order'
        def tree(index):
            return None if index >= len(array) else {'value': array[index], 'left': tree(2*index+1), 'right': tree(2*index+2)}
        assert state['root'] == tree(0), 'complete heap tree and array disagree'
        return
    assert structure_id in {'abb', 'avl', 'red_black'}
    seen = set()
    def visit(node, lower=None, upper=None):
        if node is None:
            return 0, 1, []
        assert id(node) not in seen, 'cycle or aliased tree node'
        seen.add(id(node))
        value = node['value']
        assert type(value) is int
        assert lower is None or lower < value, 'BST lower bound'
        assert upper is None or value < upper, 'BST upper bound'
        lh, lb, left = visit(node['left'], lower, value)
        rh, rb, right = visit(node['right'], value, upper)
        height = 1 + max(lh, rh)
        if structure_id == 'avl':
            assert abs(rh-lh) <= 1, 'AVL balance'
            assert node['height'] == height, 'AVL height metadata'
            assert node['balance_factor'] == rh-lh, 'AVL balance-factor metadata'
        if structure_id == 'red_black':
            assert node['color'] in {'RED', 'BLACK'}, 'RN color'
            if node['color'] == 'RED':
                assert all(child is None or child['color'] == 'BLACK' for child in [node['left'], node['right']]), 'RN red/red edge'
            assert lb == rb, 'RN black height'
            black_height = lb + (node['color'] == 'BLACK')
        else:
            black_height = 1
        return height, black_height, left + [value] + right
    root = state['root']
    if structure_id == 'red_black' and root is not None:
        assert root['color'] == 'BLACK', 'RN root color'
    height, _, inorder = visit(root)
    assert state['size'] == len(seen) and state['empty'] is (root is None)
    assert state['height'] == height
    assert state['traversals']['inorden'] == inorder
    assert state['validation'] is True, 'reported domain/native validator'
