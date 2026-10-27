"""Source-locked statement model for the canonical book graph implementation.

This is deliberately not a general C interpreter. Only the actual downloaded
functions named below, their types/operators and the explicit int32/longlong64/size_t64 ABI profile are
accepted. Unknown syntax, uninitialized reads, dead pointers and overflow fail
explicitly; there is no synthetic fallback or sampled execution.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
import json
import re
from typing import Any, Callable

from .book_source import canonical_source, verify_source, function_names, FIELDS, STATUS_NAMES, HASHES
TYPES = frozenset({"int", "long", "void", "size_t", "GrafoEstado", "Trabajo", "Grafo", "ListaVertice", "ListaArco", "Conjunto", "struct"})

UNINIT = "sin inicializar"
NULL = "NULL"
CONSTANTS = {"NULL": NULL, "INT_MIN": -(1 << 31), "INT_MAX": (1 << 31)-1,
             "SIZE_MAX": (1 << 64)-1, **dict(zip(STATUS_NAMES,range(8))), "LLONG_MIN": -(1 << 63), "LLONG_MAX": (1 << 63)-1}
SIZES = {"int": 4, "long long": 8, "size_t": 8, "ListaVertice": 8, "ListaArco": 8,
         "struct NodoV": 24, "struct NodoA": 24, "Grafo": 16, "Conjunto": 16, "Trabajo":48, "GrafoEstado":4, "void":1}


@dataclass
class Token:
    text: str
    pos: int
    end: int
    line: int


@dataclass
class Node:
    kind: str
    token: Token
    end: int
    data: dict[str, Any]


class Program:
    """Parse precisely the bounded expression/statement vocabulary of these functions."""
    def __init__(self, source: str):
        verify_source(source)
        self.source = source
        functions = function_names(source)
        # Includes are not executed. Keep byte positions/newlines for source mapping.
        source = re.sub(r'^#[^\n]*',lambda m:' '*len(m.group()),source,flags=re.M)
        pattern = r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\d+|[A-Za-z_]\w*|->|\+\+|--|<=|>=|==|!=|&&|\|\||[{}()[\],;:?.+*/%<>=!&-]'
        self.tokens = []
        cursor = 0
        for m in re.finditer(pattern, source, re.S):
            gap = source[cursor:m.start()]
            if gap.strip():
                raise ValueError(f"Unsupported C token at {cursor}: {gap!r}")
            cursor = m.end()
            if m.group().startswith(('/*', '//')):
                continue
            self.tokens.append(Token(m.group(), m.start(), m.end(), source.count('\n', 0, m.start())))
        if source[cursor:].strip():
            raise ValueError("Unsupported trailing C syntax")
        self.at = 0
        self.functions = {}
        while self.at < len(self.tokens):
            if self.peek()=='typedef':
                depth=0
                while self.at<len(self.tokens):
                    item=self.pop().text
                    depth += (item=='{')-(item=='}')
                    if item==';' and depth==0:break
                continue
            typ = self.type_name()
            name = self.pop()
            if name.text not in functions:
                raise ValueError(f"Function outside graph trace scope: {name.text}")
            self.need('(')
            params = []
            if self.peek()=='void' and self.peek(1)==')':self.pop()
            while self.peek() != ')':
                ptyp = self.type_name(); param = self.pop()
                params.append((param.text, ptyp))
                if self.peek() != ',':
                    break
                self.pop()
            self.need(')')
            body = self.statement()
            self.functions[name.text] = dict(name=name.text, type=typ, parameters=params,
                                            body=body, token=name)

    def text(self, node: Node) -> str:
        return self.source[node.token.pos:node.end]

    def peek(self, offset: int = 0) -> str:
        return self.tokens[self.at+offset].text if self.at+offset < len(self.tokens) else ''

    def pop(self) -> Token:
        tok = self.tokens[self.at]; self.at += 1; return tok

    def need(self, text: str) -> Token:
        tok = self.pop()
        if tok.text != text:
            raise ValueError(("Expected", text, tok.text, tok.line+1))
        return tok

    def type_name(self) -> str:
        parts = []
        while self.peek() in {'static', 'const'}:
            self.pop()
        tok = self.pop()
        if tok.text not in TYPES:
            raise ValueError(("Unsupported type", tok.text, tok.line+1))
        parts.append(tok.text)
        if tok.text == 'long':
            parts.append(self.need('long').text)
        elif tok.text == 'struct':
            name = self.pop().text
            if name not in {'NodoV', 'NodoA'}:
                raise ValueError(("Unsupported struct", name))
            parts.append(name)
        while self.peek() == '*':
            parts.append(self.pop().text)
        return ' '.join(parts)

    def node(self, kind: str, token: Token, **data: Any) -> Node:
        return Node(kind, token, self.tokens[self.at-1].end, data)

    def aggregate(self, typ, token):
        self.need('{');items=[]
        while self.peek()!='}':
            items.append(self.expression(2))
            if self.peek()!=',':break
            self.pop()
        self.need('}')
        return self.node('aggregate',token,type=typ,items=items)

    def declaration(self, delimiter: str = ';') -> Node:
        first=self.tokens[self.at];typ=self.type_name();base=typ.rstrip(' *');first_type=typ;declarations=[]
        while True:
            name=self.pop();init=None
            if self.peek()=='=':
                self.pop();init=self.aggregate(typ,name) if self.peek()=='{' else self.expression(2)
            declarations.append(dict(name=name.text,type=typ,init=init,token=name))
            if self.peek()!=',':break
            self.pop();typ=base
            while self.peek()=='*':self.pop();typ+=' *'
        self.need(delimiter)
        return self.node('decl',first,declarations=declarations)

    def statement(self) -> Node:
        tok = self.tokens[self.at]
        if tok.text == '{':
            self.pop(); items = []
            while self.peek() != '}':
                items.append(self.statement())
            close = self.pop()
            return self.node('block', tok, items=items, close=close)
        if tok.text in {'if', 'while', 'for'}:
            self.pop(); self.need('(')
            if tok.text == 'for':
                if self.peek() in TYPES:
                    initial = self.declaration()
                else:
                    expr = None if self.peek() == ';' else self.expression()
                    semicolon = self.need(';')
                    initial = Node('expr', expr.token if expr else semicolon, semicolon.end, {'expr': expr})
                condition = None if self.peek() == ';' else self.expression()
                self.need(';'); increment = None if self.peek() == ')' else self.expression()
                self.need(')'); body = self.statement()
                return self.node('for', tok, initial=initial, condition=condition, increment=increment, body=body)
            condition = self.expression(); self.need(')'); body = self.statement()
            otherwise = None
            if tok.text == 'if' and self.peek() == 'else':
                self.pop(); otherwise = self.statement()
            return self.node(tok.text, tok, condition=condition, body=body, otherwise=otherwise)
        if tok.text in {'return', 'break', 'continue', 'goto'}:
            self.pop(); value = None
            if tok.text == 'return' and self.peek() != ';':
                value = self.expression()
            if tok.text == 'goto':
                value = self.pop().text
            self.need(';'); return self.node(tok.text, tok, value=value)
        if self.peek(1) == ':':
            self.pop(); self.pop(); return self.node('label', tok, name=tok.text)
        if tok.text in TYPES:
            return self.declaration()
        if tok.text == ';':
            self.pop(); return self.node('expr', tok, expr=None)
        expr = self.expression(); self.need(';'); return self.node('expr', tok, expr=expr)

    PRECEDENCE = {',': 1, '=': 2, '||': 3, '&&': 4, '==': 5, '!=': 5,
                  '<': 6, '>': 6, '<=': 6, '>=': 6, '+': 7, '-': 7,
                  '*': 8, '/': 8, '%': 8}

    def expression(self, minimum: int = 1) -> Node:
        tok = self.pop()
        if tok.text == '(':
            if self.peek() in TYPES or self.peek() == 'const':
                typ = self.type_name(); self.need(')')
                if self.peek()=='{':left=self.aggregate(typ,tok)
                else:
                    value=self.expression(9);left=self.node('cast',tok,type=typ,value=value)
            else:
                value = self.expression(); self.need(')'); left = self.node('group', tok, value=value)
        elif tok.text == 'sizeof':
            if self.peek()=='(' and (self.peek(1) in TYPES or self.peek(1)=='const'):
                self.pop();typ=self.type_name();self.need(')');left=self.node('sizeof',tok,type=typ)
            else:
                value=self.expression(9);left=self.node('sizeof',tok,value=value)
        elif tok.text in {'!', '-', '+', '&', '*', '++', '--'}:
            left = self.node('unary', tok, op=tok.text, value=self.expression(9))
            left.end = self.tokens[self.at-1].end
        elif tok.text.startswith('"'):
            left = self.node('literal', tok, value=json.loads(tok.text))
        elif tok.text.isdigit():
            left = self.node('literal', tok, value=int(tok.text))
        else:
            left = self.node('name', tok, name=tok.text)
        while True:
            text = self.peek()
            if text=='?' and minimum<=2:
                self.pop();yes=self.expression();self.need(':');no=self.expression(2);left=self.node('ternary',tok,condition=left,yes=yes,no=no);continue
            if text in {'(', '[', '.', '->', '++', '--'} and minimum <= 10:
                op = self.pop()
                if text == '(':
                    args = []
                    while self.peek() != ')':
                        args.append(self.expression(2))
                        if self.peek() != ',':
                            break
                        self.pop()
                    self.need(')'); left = self.node('call', left.token, function=left, args=args)
                elif text == '[':
                    index = self.expression(); self.need(']'); left = self.node('index', left.token, base=left, index=index)
                elif text in {'.', '->'}:
                    member = self.pop().text; left = self.node('field', left.token, base=left, field=member, indirect=text=='->')
                else:
                    left = self.node('postfix', left.token, op=text, value=left)
                continue
            precedence = self.PRECEDENCE.get(text, 0)
            if precedence < minimum:
                break
            self.pop(); right = self.expression(precedence if text == '=' else precedence+1)
            left = self.node('binary', left.token, op=text, left=left, right=right)
        return left


@dataclass
class Reference:
    def __deepcopy__(self, memo):return self
    container: Any
    key: Any
    type: str
    identity: str
    owner: Any = None


class Control(Exception):
    def __init__(self, kind: str, value: Any = None):
        self.kind, self.value = kind, value


class BookEventLimitExceeded(RuntimeError):
    """Preflight budget exceeded before committing the next symbolic event.

    The partially executed machine is disposable; never publish its graph/state.
    """
    def __init__(self,limit,attempted_events):
        self.limit=limit;self.attempted_events=attempted_events
        super().__init__(f'Book trace requires more than {limit} events (next event {attempted_events}); discard preflight state')


class GraphMachine:
    """Evaluate the accepted C AST, maintaining typed scopes and symbolic memory."""
    def __init__(self, program: Program, vertices: list[int], arcs: list[tuple[int,int,int]],
                 marks: dict[int,int] | None = None, callback: Callable | None = None,
                 fail_allocation: int | None = None, record_events: bool = True, event_limit: int | None = None, event_observer: Callable | None = None):
        if event_limit is not None and (type(event_limit) is not int or event_limit<0):raise ValueError('event_limit must be a nonnegative integer')
        self.event_limit=event_limit;self.event_count=0;self.event_observer=event_observer
        self.program = program; self.record_events=record_events; self.callback = callback; self.fail_allocation = fail_allocation
        self.frames = []; self.heap = {}; self.retired = []; self.events = []
        self.serial = 0; self.frame_serial = 0; self.allocations = 0; self.attempts = 0; self.frees = 0
        self.stdout = ''; self.returned = UNINIT; self.root_function = None; self.evaluations = {}
        vhead = NULL; ahead = NULL
        for i, vertex in enumerate(vertices):
            key = f'V{i+1}'; self.heap[key] = dict(id=key, kind='struct NodoV', borrowed=False,
                fields={'dato':vertex,'marcado':(marks or {}).get(vertex,0),'sig':vhead}, alive=True)
            vhead = key
        for i,(o,d,w) in enumerate(arcs):
            key = f'E{i+1}'; self.heap[key] = dict(id=key, kind='struct NodoA', borrowed=False,
                fields={'origen':o,'destino':d,'costo':w,'sig':ahead}, alive=True)
            ahead = key
        self.graph = {'v':vhead, 'a':ahead}

    def encoded(self, value: Any) -> Any:
        if isinstance(value, Reference):
            return '&'+value.identity
        if isinstance(value, dict):
            return {k:self.encoded(v) for k,v in value.items()}
        if isinstance(value, (list,tuple)):
            return [self.encoded(v) for v in value]
        if isinstance(value,int) and abs(value)>(1<<53)-1:return {'exact_integer':str(value)}
        return value

    def _snapshot_heap(self):
        return self.encoded(list(self.heap.values()))

    def snapshot(self) -> dict[str,Any]:
        frames = []
        for f in self.frames:
            frames.append(dict(id=f['id'], function=f['function'], parameters={n:self.encoded(c['value']) for n,c in f['parameter_cells'].items()},parameter_types={n:c['type'] for n,c in f['parameter_cells'].items()},status=f.get('status','active'),
                scopes=[dict(id=s['id'], variables={n:dict(type=v['type'],value=self.encoded(v['value']))
                     for n,v in s['variables'].items()}) for s in f['scopes']]))
        return dict(external=self.encoded(getattr(self,'external',{})), frames=frames, heap_nodes=self._snapshot_heap(),
                    retired_objects=self.encoded(self.retired), graph=deepcopy(self.graph),
                    allocations=self.allocations, allocation_attempts=self.attempts, frees=self.frees,
                    console_stdout=self.stdout, returned=self.encoded(self.returned))

    def _count_event(self):
        if self.event_limit is not None and self.event_count>=self.event_limit:
            raise BookEventLimitExceeded(self.event_limit,self.event_count+1)
        self.event_count+=1

    def emit(self, node: Node | Token, phase: str, name: str = '', value: Any = None,
             change: Callable | None = None) -> None:
        self._count_event()
        tok = node.token if isinstance(node,Node) else node
        old = self.snapshot() if self.callback else None
        if change:
            change()
        fn = name if phase=='function_exit' else self.frames[-1]['function'] if self.frames else self.root_function
        event = dict(function=fn, pos=tok.pos, line_index=tok.line, phase=phase,
                     name=name, value=self.encoded(value), C_executed=True, source_role='canonical')
        if self.record_events:self.events.append(event)
        if self.event_observer:self.event_observer(event)
        if self.callback:
            detail={**event, 'evaluated_nodes':deepcopy(list(self.evaluations.values()))} if phase in {'condition','operand'} else event
            self.callback(detail, old, self.snapshot())

    def host_event(self,name,change=None,**metadata):
        self._count_event()
        old=self.snapshot() if self.callback else None
        if change:change()
        event=dict(function=None,pos=-1,line_index=-1,phase=name,name=name,value=None,
                   C_executed=False,source_role='caller',**metadata)
        if self.record_events:self.events.append(event)
        if self.event_observer:self.event_observer(event)
        if self.callback:self.callback(event,old,self.snapshot())

    def scope(self, node: Node) -> dict:
        scope = dict(id=f"{self.frames[-1]['id']}:B{node.token.pos}", variables={}, _alive=True)
        self.emit(node,'scope_enter',value=node.token.pos,change=lambda:self.frames[-1]['scopes'].append(scope))
        return scope

    def pop_scope(self, node: Node) -> None:
        self.emit(node,'scope_exit',value=node.token.pos,change=lambda:self.frames[-1]['scopes'].pop().__setitem__('_alive',False))

    def variable(self, name: str) -> Reference:
        frame = self.frames[-1]
        for scope in reversed(frame['scopes']):
            if name in scope['variables']:
                cell = scope['variables'][name]
                return Reference(cell,'value',cell['type'],f"{scope['id']}:{name}",scope)
        if name in frame['parameter_cells']:
            cell=frame['parameter_cells'][name]
            return Reference(cell,'value',cell['type'],f"{frame['id']}:{name}",frame)
        raise ValueError(('Undefined local',frame['function'],name))

    def check_reference(self,ref):
        if ref.owner is not None and (ref.owner.get('_alive') is False or ref.owner.get('alive') is False):
            raise ValueError(('Expired C reference',ref.identity))

    def read(self, ref: Reference) -> Any:
        self.check_reference(ref)
        value = ref.container[ref.key]
        if value == UNINIT:
            raise ValueError(('Uninitialized C read',ref.identity))
        if isinstance(value,str) and any(n['id']==value for n in self.retired):
            raise ValueError(('Indeterminate retired pointer read',ref.identity,value))
        return value

    def pointee(self, value: Any) -> Any:
        if isinstance(value,Reference):
            return self.read(value)
        if value not in self.heap:
            raise ValueError(('Non-live C pointer read',self.encoded(value)))
        return self.heap[value].get('fields',self.heap[value].get('items'))

    @staticmethod
    def pointee_type(typ):
        if typ=='ListaVertice':return 'struct NodoV'
        if typ=='ListaArco':return 'struct NodoA'
        if typ.endswith('*'):return typ[:-1].strip()
        raise ValueError(('Not pointer type',typ))

    def infer_type(self,node):
        d=node.data
        if node.kind=='name':return 'int' if d['name'] in CONSTANTS else self.variable(d['name']).type
        if node.kind in {'group','postfix'}:return self.infer_type(d['value'])
        if node.kind in {'cast','aggregate'}:return d['type']
        if node.kind=='literal':return 'char *' if isinstance(d['value'],str) else 'int'
        if node.kind=='unary':
            typ=self.infer_type(d['value'])
            return self.pointee_type(typ) if d['op']=='*' else typ+' *' if d['op']=='&' else typ
        if node.kind=='index':return self.pointee_type(self.infer_type(d['base']))
        if node.kind=='field':
            typ=self.infer_type(d['base']);typ=self.pointee_type(typ) if d['indirect'] else typ
            return FIELDS[typ][d['field']]
        if node.kind=='call':return self.program.functions[d['function'].data['name']]['type']
        if node.kind=='binary':
            left=self.infer_type(d['left']);right=self.infer_type(d['right'])
            return 'long long' if 'long long' in (left,right) else left
        raise ValueError(('No supported expression type',node.kind))

    def ref(self, node: Node) -> Reference:
        d=node.data
        if node.kind=='name':
            return self.variable(d['name'])
        if node.kind=='group':
            return self.ref(d['value'])
        if node.kind=='field':
            base=self.eval(d['base'])
            if d['indirect']:
                obj=self.pointee(base)
            else:
                obj=base
            field=d['field']
            base_type=self.infer_type(d['base']);base_type=self.pointee_type(base_type) if d['indirect'] else base_type
            typ=FIELDS[base_type][field]
            owner=base.owner if isinstance(base,Reference) else self.heap.get(base) if isinstance(base,str) else self.ref(d['base']).owner
            return Reference(obj,field,typ,self.encoded(base).__str__()+'.'+field,owner)
        if node.kind=='index':
            pointer=self.eval(d['base']);index=self.eval(d['index'])
            if pointer not in self.heap or 'items' not in self.heap[pointer]:
                raise ValueError(('Invalid array pointer',pointer))
            array=self.heap[pointer];items=array['items']
            if not isinstance(index,int) or not 0<=index<len(items):
                raise ValueError(('C bounds',pointer,index,len(items)))
            return Reference(items,index,array['element_type'],f'{pointer}[{index}]',array)
        if node.kind=='unary' and d['op']=='*':
            value=self.eval(d['value'])
            if isinstance(value,Reference):self.check_reference(value);return value
            if isinstance(value,str) and value in self.heap:
                obj=self.heap[value]
                if 'fields' in obj:return Reference(obj,'fields',obj['kind'],value,obj)
                return Reference(obj['items'],0,obj['element_type'],value+'[0]',obj)
        raise ValueError(('Unsupported lvalue',node.kind,self.program.text(node)))

    @staticmethod
    def truth(value: Any) -> bool:
        if value==UNINIT:
            raise ValueError('Uninitialized condition')
        return value not in (NULL,0,None)

    @staticmethod
    def cast(value: Any, typ: str) -> Any:
        if typ=='size_t':return int(value) % (1<<64)
        if typ=='GrafoEstado':typ='int'
        if typ in {'int','long long'}:
            if not isinstance(value,int):raise ValueError(('Not an integer',value))
            bound=1<< (31 if typ=='int' else 63)
            if not -bound<=value<bound:raise ValueError(('C integer overflow',typ,value))
        if (typ.endswith('*') or typ in {'ListaVertice','ListaArco'}) and value==0:return NULL
        return value

    def condition(self, node: Node) -> bool:
        suspended=self.evaluations;self.evaluations={}
        try:
            result=self.eval(node)
            truth=self.truth(result)
            self.emit(node,'condition',self.program.text(node),int(truth))
            return truth
        finally:self.evaluations=suspended

    def eval(self, node: Node) -> Any:
        value=self._eval(node)
        encoded=self.encoded(value)
        if isinstance(encoded,int) and abs(encoded)>(1<<53)-1:
            encoded={'exact_integer':str(encoded)}
        self.evaluations[(node.token.pos,node.end,node.kind)]={'pos':node.token.pos,'end':node.end,'kind':node.kind,
            'source':self.program.text(node),'value':encoded}
        return value

    def _eval(self, node: Node) -> Any:
        d=node.data;kind=node.kind
        if kind=='ternary':return self.eval(d['yes'] if self.condition(d['condition']) else d['no'])
        if kind=='literal':return d['value']
        if kind=='name':
            return CONSTANTS[d['name']] if d['name'] in CONSTANTS else self.read(self.ref(node))
        if kind in {'index','field'}:return self.read(self.ref(node))
        if kind=='group':return self.eval(d['value'])
        if kind=='aggregate':
            fields=FIELDS[d['type']]
            if len(d['items'])>len(fields):raise ValueError('Too many aggregate fields')
            values=[self.eval(item) for item in d['items']]
            return {name:self.cast(values[i] if i<len(values) else 0,typ) for i,(name,typ) in enumerate(fields.items())}
        if kind=='sizeof':
            typ=d.get('type') or self.infer_type(d['value'])
            return 8 if typ.endswith('*') else SIZES[typ]
        if kind=='cast':return self.cast(self.eval(d['value']),d['type'])
        if kind in {'unary','postfix'}:
            op=d['op']
            if op=='&':return self.ref(d['value'])
            if op=='*':return self.read(self.ref(node))
            if op in {'++','--'}:
                ref=self.ref(d['value']);old=self.read(ref);new=self.cast(old+(1 if op=='++' else -1),ref.type)
                self.emit(node,'write',self.program.text(d['value']),new,lambda:ref.container.__setitem__(ref.key,new))
                return old if kind=='postfix' else new
            value=self.eval(d['value'])
            return int(not self.truth(value)) if op=='!' else -value if op=='-' else value
        if kind=='binary':
            op=d['op']
            if op=='=':
                ref=self.ref(d['left']);self.check_reference(ref);value=self.cast(self.eval(d['right']),ref.type)
                self.emit(node,'write',self.program.text(d['left']),value,lambda:ref.container.__setitem__(ref.key,deepcopy(value)))
                return value
            left=self.eval(d['left'])
            if op in {'&&','||'}:
                left_bool=self.truth(left);self.emit(d['left'],'operand',self.program.text(d['left']),int(left_bool))
                if (op=='&&' and not left_bool) or (op=='||' and left_bool):return int(left_bool)
                right=self.eval(d['right']);right_bool=self.truth(right)
                self.emit(d['right'],'operand',self.program.text(d['right']),int(right_bool))
                return int(right_bool)
            right=self.eval(d['right'])
            if op==',':return right
            if op in {'==','!=','<','>','<=','>='}:
                return int({'==':lambda:left==right,'!=':lambda:left!=right,'<':lambda:left<right,
                            '>':lambda:left>right,'<=':lambda:left<=right,'>=':lambda:left>=right}[op]())
            if op=='+':return left+right
            if op=='-':return left-right
            if op=='*':return left*right
            if op in {'/','%'}:
                if not right:raise ValueError('Division by zero')
                quotient=(abs(left)//abs(right))*(-1 if (left<0)!=(right<0) else 1)
                return quotient if op=='/' else left-quotient*right
        if kind=='call':
            function=d['function'].data['name'];args=[self.eval(arg) for arg in d['args']]
            self.emit(node,'call',function,None)
            if function in {'malloc','calloc'}:
                size=args[0] if function=='malloc' else args[0]*args[1]
                attempt=self.attempts+1
                if attempt==self.fail_allocation:
                    self.emit(node,'allocate',function,dict(pointer=NULL,size=size,zeroed=function=='calloc'),lambda:setattr(self,'attempts',attempt))
                    return NULL
                typnode=next((x for x in walk(node) if x.kind=='sizeof'),None)
                element=(typnode.data.get('type') or self.infer_type(typnode.data['value'])) if typnode else None
                if element is None:raise ValueError('Allocation without explicit supported sizeof type')
                self.serial+=1;key=f'M{self.serial}'
                obj=dict(id=key,kind=element,borrowed=False,alive=True,bytes=size)
                if element.startswith('struct '):
                    fields=['dato','sig','marcado'] if element=='struct NodoV' else ['origen','destino','costo','sig']
                    obj['fields']={n:0 if function=='calloc' else UNINIT for n in fields}
                else:
                    width=8 if element.endswith('*') else SIZES[element];assert size%width==0
                    obj.update(element_type=element,items=[0 if function=='calloc' else UNINIT]*(size//width))
                def change():self.attempts=attempt;self.heap[key]=obj;self.allocations+=1
                self.emit(node,'allocate',function,dict(pointer=key,size=size,zeroed=function=='calloc'),change)
                return key
            if function=='free':
                pointer=args[0]
                if pointer!=NULL and (pointer not in self.heap or self.heap[pointer]['borrowed']):
                    raise ValueError(('Invalid algorithm free',pointer))
                def change():
                    if pointer!=NULL:
                        obj=self.heap.pop(pointer);obj['alive']=False;obj['historical_identity_only']=True
                        self.retired.append(obj);self.frees+=1
                        # Keep historical identities in snapshots, never read them again.
                self.emit(node,'free',function,pointer,change)
                return None
            if function=='printf':
                text=args[0] % tuple(args[1:]) if len(args)>1 else args[0]
                self.emit(node,'stdout',function,text,lambda:setattr(self,'stdout',self.stdout+text))
                return len(text)
            if function not in self.program.functions:
                raise ValueError(('Missing actual C helper',function))
            return self.invoke(function,args)
        raise ValueError(('Unsupported expression',kind,self.program.text(node)))

    def statement(self, node: Node) -> None:
        d=node.data;kind=node.kind
        if kind=='block':
            self.scope(node)
            try:
                i=0
                while i<len(d['items']):
                    try:self.statement(d['items'][i])
                    except Control as control:
                        if control.kind!='goto':raise
                        found=next((j for j,item in enumerate(d['items']) if item.kind=='label' and item.data['name']==control.value),None)
                        if found is None:raise
                        i=found;continue
                    i+=1
            finally:self.pop_scope(node)
        elif kind=='decl':
            for decl in d['declarations']:
                scope=self.frames[-1]['scopes'][-1];name=decl['name'];typ=decl['type']
                initial={n:UNINIT for n in FIELDS[typ]} if typ in FIELDS else UNINIT
                self.emit(decl['token'],'declare',name,initial,lambda:scope['variables'].__setitem__(name,dict(type=typ,value=deepcopy(initial))))
                if decl['init'] is not None:
                    value=self.cast(self.eval(decl['init']),typ)
                    self.emit(decl['token'],'write',name,value,lambda:scope['variables'][name].__setitem__('value',deepcopy(value)))
        elif kind=='expr':
            if d['expr'] is not None:self.eval(d['expr'])
        elif kind=='if':
            if self.condition(d['condition']):self.statement(d['body'])
            elif d['otherwise']:self.statement(d['otherwise'])
        elif kind in {'while','for'}:
            if kind=='for':self.scope(node);self.statement(d['initial'])
            try:
                while d['condition'] is None or self.condition(d['condition']):
                    try:self.statement(d['body'])
                    except Control as control:
                        if control.kind=='break':break
                        if control.kind!='continue':raise
                    if kind=='for' and d['increment'] is not None:self.eval(d['increment'])
            finally:
                if kind=='for':self.pop_scope(node)
        elif kind=='return':
            value=self.eval(d['value']) if d['value'] else None
            self.emit(node,'return','',value,lambda:self.frames[-1].__setitem__('status','returning'))
            raise Control('return',value)
        elif kind=='break':
            self.emit(node,'break');raise Control('break')
        elif kind=='continue':
            self.emit(node,'continue');raise Control('continue')
        elif kind=='goto':
            self.emit(node,'goto',value=d['value']);raise Control('goto',d['value'])
        elif kind=='label':self.emit(node,'label',d['name'])
        else:raise ValueError(('Unsupported statement',kind))

    def invoke(self, function: str, args: list[Any]) -> Any:
        fn=self.program.functions[function]
        if len(args)!=len(fn['parameters']):raise ValueError(('C arity',function))
        if self.root_function is None:self.root_function=function
        self.frame_serial+=1
        params={name:deepcopy(value) if typ in FIELDS else value for (name,typ),value in zip(fn['parameters'],args)}
        frame=dict(id=f'F{self.frame_serial}',function=function,parameters=params,scopes=[],_alive=True,
                   parameter_cells={name:dict(type=typ,value=params[name]) for name,typ in fn['parameters']})
        self.emit(fn['token'],'enter',change=lambda:self.frames.append(frame))
        for name,typ in fn['parameters']:
            value=params[name]
            if typ=='Grafo':
                for field in ['v','a']:self.emit(fn['token'],'parameter',name+'.'+field,value[field])
            else:self.emit(fn['token'],'parameter',name,value)
        result=None
        try:self.statement(fn['body'])
        except Control as control:
            if control.kind!='return':raise
            result=control.value
        else:
            if fn['type']!='void':raise ValueError(('Missing C return',function))
            self.emit(fn['body'].data['close'],'return','',None,change=lambda:frame.update(status='returning'))
        def finish():
            self.frames.pop();frame['_alive']=False
            if not self.frames:self.returned=result
        self.emit(fn['body'].data['close'],'function_exit',function,result,finish)
        return result


def walk(node: Node):
    yield node
    for value in node.data.values():
        if isinstance(value,Node):yield from walk(value)
        elif isinstance(value,list):
            for item in value:
                if isinstance(item,Node):yield from walk(item)
                elif isinstance(item,dict):
                    for nested in item.values():
                        if isinstance(nested,Node):yield from walk(nested)

# Public runner: the very same evaluator is used with or without event capture.
OWNED_RESULTS=frozenset({'grafo_sucesores','grafo_predecesores','grafo_bfs','grafo_dfs','grafo_dijkstra','grafo_bellman_ford','grafo_prim','grafo_kruskal'})
BORROWED_RESULTS=frozenset({'grafo_vertices','grafo_arcos'})

class BookSession:
    """Canonical directed C graph, with explicit caller-owned status/output cells.

    Seed vertices/arcs are in insertion order; graph_after lists are HEAD order.
    Undirected policy belongs to the caller (two actual calls), not this engine.
    """
    def __init__(self, vertices=(), arcs=(), marks=None, *, trace=False, callback=None, fail_allocation=None, event_limit=None, event_observer=None):
        vertices=list(vertices);arcs=[tuple(a) for a in arcs]
        for value in vertices:
            if type(value) is not int:raise ValueError('Vertex must be int32')
            GraphMachine.cast(value,'int')
        if len(set(vertices))!=len(vertices):raise ValueError('Duplicate seeded vertex')
        pairs=set()
        for a in arcs:
            if len(a)!=3 or a[0] not in vertices or a[1] not in vertices:raise ValueError('Seeded arc endpoints must exist')
            for value in a:
                if type(value) is not int:raise ValueError('Arc fields must be int32')
                GraphMachine.cast(value,'int')
            if a[:2] in pairs:raise ValueError('Duplicate seeded arc')
            pairs.add(a[:2])
        self.source=canonical_source();self.program=Program(self.source)
        self.transitions=[]
        def capture(event,before,after):
            if trace:self.transitions.append({'event':deepcopy(event),'before':before,'after':after})
            if callback:callback(event,before,after)
        self.machine=GraphMachine(self.program,vertices,arcs,marks,callback=capture if trace or callback else None,fail_allocation=fail_allocation,record_events=trace,event_limit=event_limit,event_observer=event_observer)
        self.machine.external={};self.trace=trace
        self.capture_result_memory=bool(trace or callback or event_limit is None)

    def _list(self,pointer,kind):
        result=[];seen=set()
        while pointer!=NULL:
            if pointer in seen:raise ValueError('Cycle in returned list')
            seen.add(pointer)
            node=self.machine.heap[pointer]
            if node['kind']!=kind:raise ValueError('Returned list type mismatch')
            f=node['fields'];result.append(f['dato'] if kind=='struct NodoV' else [f['origen'],f['destino'],f['costo']]);pointer=f['sig']
        return result

    def graph_state(self):
        m=self.machine
        vertices=self._list(m.graph['v'],'struct NodoV');arcs=self._list(m.graph['a'],'struct NodoA');marks={}
        p=m.graph['v']
        while p!=NULL:
            f=m.heap[p]['fields'];marks[f['dato']]=f['marcado'];p=f['sig']
        return {'vertices':vertices,'arcs':arcs,'marks':marks}

    def call(self,function,arguments=(), *, state_pointer=True, output_pointer=True):
        if function not in self.program.functions or function.startswith(('fijar_','liberar_','preparar','indice','agregar_','publicar_','sumar_','reconstruir','vecinos','buscar_')):
            raise ValueError('Use machine.invoke for private helper QA; public caller requires canonical function')
        m=self.machine;fn=self.program.functions[function];values=iter(arguments);args=[]
        external={}
        def cell(name,typ,value=UNINIT):
            external[name]={'type':typ,'value':value}
            return Reference(external[name],'value',typ,'caller:'+name)
        for name,typ in fn['parameters']:
            if typ=='Grafo':args.append(m.graph)
            elif name=='estado' and typ=='GrafoEstado *':args.append(cell('estado','GrafoEstado') if state_pointer else NULL)
            elif name=='salida' and typ=='int *':args.append(cell('salida','int') if output_pointer else NULL)
            elif typ=='Grafo *':args.append(cell('grafo','Grafo',m.graph))
            else:
                try:value=next(values)
                except StopIteration:raise ValueError(('Missing caller argument',function,name))
                if typ=='int' and type(value) is not int:raise ValueError('Argument must be int32')
                args.append(m.cast(value,typ))
        try:next(values)
        except StopIteration:pass
        else:raise ValueError('Extra caller argument')
        start=len(m.events);start_t=len(self.transitions);start_count=m.event_count
        def prepare():
            m.external=external;m.root_function=function;m.returned=UNINIT
        m.host_event('caller_prepare',prepare,called_function=function,arguments=m.encoded(args))
        returned=m.invoke(function,args)
        def publish():
            if fn['type']=='Grafo':m.graph=deepcopy(returned)
            if 'grafo' in external:m.graph=external['grafo']['value']
            external['result']={'type':fn['type'],'value':deepcopy(returned)}
        m.host_event('caller_receipt',publish,called_function=function,returned=m.encoded(returned),return_type=fn['type'])
        status=external.get('estado',{}).get('value')
        ownership='owned' if function in OWNED_RESULTS else 'borrowed' if function in BORROWED_RESULTS else 'none'
        items=None
        if fn['type'] in {'ListaVertice','ListaArco'}:items=self._list(returned,'struct NodoV' if fn['type']=='ListaVertice' else 'struct NodoA')
        return {'function':function,'returned':m.encoded(returned),'return_type':fn['type'],'status':status,
                'status_name':STATUS_NAMES[status] if type(status) is int and 0<=status<len(STATUS_NAMES) else None,
                'output':m.encoded(external.get('salida',{}).get('value',UNINIT)),
                'graph_after':self.graph_state(),'result_items':items,'ownership':ownership,
                'owned_result':items if ownership=='owned' else None,'borrowed_result':items if ownership=='borrowed' else None,
                'source_sha256':HASHES['tad_grafo.c'],
                'memory':m.snapshot() if self.capture_result_memory else None,'event_count':m.event_count,'call_event_count':m.event_count-start_count,'events':deepcopy(m.events[start:]),'transitions':self.transitions[start_t:],
                'stdout':m.stdout,'source_code':self.source}

    def free_result(self,pointer,kind):
        """Explicit caller action; never automatically free borrowed graph lists."""
        if pointer!=NULL:
            reachable=set();p=self.machine.graph['v'];q=self.machine.graph['a']
            for head in (p,q):
                while head!=NULL:reachable.add(head);head=self.machine.heap[head]['fields']['sig']
            if pointer in reachable:raise ValueError('Cannot free borrowed graph result')
        if kind not in {'ListaVertice','ListaArco'}:raise ValueError('Expected owned list type')
        holder=self.machine.external.get('result')
        if not holder or holder['value']!=pointer:
            holder={'type':kind,'value':pointer}
            self.machine.host_event('caller_prepare_release',lambda:self.machine.external.__setitem__('cleanup_result',holder))
        ref=Reference(holder,'value',kind,'caller:result')
        self.machine.invoke('grafo_liberar_vertices' if kind=='ListaVertice' else 'grafo_liberar_arcos',[ref])
        return holder['value']


def run_book(function, *, vertices=(), arcs=(), marks=None, arguments=(), trace=False, fail_allocation=None, state_pointer=True, output_pointer=True, event_limit=None, event_observer=None):
    return BookSession(vertices,arcs,marks,trace=trace,fail_allocation=fail_allocation,event_limit=event_limit,event_observer=event_observer).call(function,arguments,state_pointer=state_pointer,output_pointer=output_pointer)
