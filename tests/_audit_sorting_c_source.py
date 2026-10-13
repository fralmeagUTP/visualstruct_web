"""Extract real C function bodies without reimplementing their algorithms."""
import re

def function_body(source, name):
    match=re.search(r'^(?:static )?(?:void|int) '+re.escape(name)+r'\([^\n]*\{',source,re.M)
    assert match, name
    balance=0
    for index in range(source.index('{',match.start()),len(source)):
        if source[index]=='{': balance+=1
        elif source[index]=='}':
            balance-=1
            if balance==0: return source[match.start():index+1]
    raise AssertionError('Unclosed C function '+name)

def replace_once(body, old, new):
    assert body.count(old)==1, old
    return body.replace(old,new)
