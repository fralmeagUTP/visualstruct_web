"""One finite caller-output AST, rendered to C and interpreted over TAD cells."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import json
from app.services.caller_printf import c_printf


@dataclass(frozen=True)
class Expr:
    kind: str
    value: Any
    args: tuple['Expr', ...] = ()

    def c(self) -> str:
        if self.kind == 'name': return self.value
        if self.kind == 'literal': return str(self.value)
        if self.kind == 'field': return self.args[0].c() + self.value
        if self.kind == 'index': return self.args[0].c() + '[' + self.args[1].c() + ']'
        if self.kind == 'cast': return '(' + self.value + ')' + self.args[0].c()
        if self.kind == 'binary': return '(' + self.args[0].c() + ' ' + self.value + ' ' + self.args[1].c() + ')'
        if self.kind == 'choose': return '(' + self.args[0].c() + ' ? ' + self.args[1].c() + ' : ' + self.args[2].c() + ')'
        raise ValueError('Unknown caller expression')

    def eval(self, cells: dict[str, Any]) -> Any:
        if self.kind == 'name': return cells[self.value]
        if self.kind == 'literal': return self.value
        first = self.args[0].eval(cells)
        if self.kind == 'field': return first[self.value.removeprefix('->').removeprefix('.')]
        if self.kind == 'index': return first[self.args[1].eval(cells)]
        if self.kind == 'cast': return float(first) if self.value == 'double' else int(first)
        if self.kind == 'choose': return self.args[1 if first else 2].eval(cells)
        if self.kind == 'binary':
            if self.value == '&&': return bool(first) and bool(self.args[1].eval(cells))
            second = self.args[1].eval(cells)
            if self.value == '>': return first > second
            if self.value == '/': return first / second
        raise ValueError('Unknown caller expression')


def name(value): return Expr('name', value)
def field(value, member): return Expr('field', member, (value,))
def cast(typ, value): return Expr('cast', typ, (value,))
def binary(op, left, right): return Expr('binary', op, (left, right))


@dataclass(frozen=True)
class Printf:
    format: str
    arguments: tuple[Expr, ...] = ()

    def lines(self) -> list[str]:
        return ['printf(' + ', '.join([json.dumps(self.format), *(arg.c() for arg in self.arguments)]) + ');']

    def execute(self, cells, emit):
        fragment = c_printf(self.format, [arg.eval(cells) for arg in self.arguments])
        emit(self.lines()[0], fragment, cells)


@dataclass(frozen=True)
class If:
    condition: Expr
    body: tuple[Any, ...]

    def lines(self):
        return ['if (' + self.condition.c() + ') {', *['    '+line for stmt in self.body for line in stmt.lines()], '}']

    def execute(self, cells, emit):
        if self.condition.eval(cells):
            for statement in self.body: statement.execute(cells, emit)


@dataclass(frozen=True)
class Buckets:
    body: tuple[Any, ...]

    def lines(self):
        return ['for (int i = 0; tabla.buckets && i < tabla.capacidad; i++) {',
                '    for (const THNodo *node = tabla.buckets[i]; node; node = node->siguiente) {',
                *['        '+line for stmt in self.body for line in stmt.lines()], '    }', '}']

    def execute(self, cells, emit):
        table = cells['tabla']
        for index in range(table['capacidad'] if table['buckets'] else 0):
            cells['i'] = index
            node = table['buckets'][index]
            while node is not None:
                cells['node'] = node
                for statement in self.body: statement.execute(cells, emit)
                node = node['siguiente']
        cells.pop('node', None)
        cells.pop('i', None)


def output_program(operation: str) -> tuple[Any, ...]:
    """Only printf/control instructions; values come from actual return cells."""
    table = name('tabla')
    capacity, size = field(table, '.capacidad'), field(table, '.cantidad')
    if operation == 'create_table': return (Printf('create:%d\n', (capacity,)),)
    if operation == 'insert': return (Printf('insert:%d:%d:%d\n', (name('key'), name('value'), cast('int', name('ok')))),)
    if operation == 'get':
        return (Printf('get:%d:%d', (name('key'), cast('int', name('found')))),
                If(name('found'), (Printf(':%d', (name('output'),)),)), Printf('\n'))
    if operation == 'contains': return (Printf('contains:%d:%d\n', (name('key'), cast('int', name('found')))),)
    if operation == 'remove': return (Printf('remove:%d\n', (cast('int', name('removed')),)),)
    if operation == 'stats':
        stats = name('stats')
        ratio = Expr('choose', None, (binary('>', capacity, Expr('literal', 0)),
            binary('/', cast('double', size), cast('double', capacity)), Expr('literal', 0.0)))
        return (Printf('stats-C:%d:%d:%d:%d:%.9g\n', tuple(field(stats, '.'+key) for key in
                    ('capacidad', 'cantidad', 'buckets_ocupados', 'colisiones')) + (cast('double', field(stats, '.factor_carga')),)),
                Printf('stats-format:\n%s', (name('texto'),)),
                Printf('stats-API-projection:%d:%d:%.17g\n', (capacity, size, ratio)))
    if operation in {'keys', 'values', 'items'}:
        node = name('node')
        item = Printf('%d:%d;', (field(node, '->clave'), field(node, '->valor'))) if operation == 'items' else Printf('%d;', (field(node, '->clave' if operation == 'keys' else '->valor'),))
        return (Printf('format:'+operation+':\n%s', (name('buffer'),)), Printf(operation+':'), Buckets((item,)), Printf('\n'))
    if operation == 'epilogue': return (Printf('state:%d:%d\n', (capacity, size)),)
    return ()


def output_lines(operation: str, substitutions: dict[str, str] | None = None) -> list[str]:
    """Render the exact same instructions used by the caller VM."""
    import re
    lines = [line for statement in output_program(operation) for line in statement.lines()]
    if substitutions:
        pattern = r'\b(' + '|'.join(re.escape(key) for key in substitutions) + r')\b'
        lines = [re.sub(pattern, lambda match: substitutions[match.group()], line) for line in lines]
    return lines
