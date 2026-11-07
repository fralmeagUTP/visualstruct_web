"""Exact live call rows, not a nonempty placeholder mistaken for activity."""
import json

EMPTY_STACK = 'No hay una función en ejecución en este punto. Las llamadas aparecen al entrar en una función.'
STACK_ROWS = """el => Array.from(el.querySelectorAll(':scope > li'), row => ({function: row.querySelector('strong')?.textContent ?? null, text: row.textContent}))"""


def assert_sorting_stack(rows, calls):
    expected = [dict(function=call['function'], text=call['function']+'('+json.dumps(call.get('parameters') or {}, ensure_ascii=False, separators=(',', ':'))+')'+(call.get('continuation') or '')) for call in calls]
    assert rows == (expected if calls else [dict(function=None, text=EMPTY_STACK)])
    return bool(calls)
