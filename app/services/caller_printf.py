"""Finite printf conversion boundary for generated callers, using the host C CRT.

No compiler, shell, user C source, locale mutation or Python numeric formatting.
Only the conversions used by our generated caller ASTs are accepted.
"""
from __future__ import annotations
import ctypes
import os
import re
from functools import lru_cache
from typing import Any, Sequence


@lru_cache(maxsize=1)
def _snprintf():
    library = ctypes.CDLL('msvcrt') if os.name == 'nt' else ctypes.CDLL(None)
    function = library._snprintf if os.name == 'nt' else library.snprintf
    function.restype = ctypes.c_int
    function.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_char_p]
    return function


def c_printf(fmt: str, arguments: Sequence[Any]) -> str:
    """Interpret one printf conversion using correctly promoted C varargs.

    The caller VM owns stdout and appends this fragment at its printf event.
    Windows uses its exported MSVCRT boundary; Unix uses the process libc. Unsupported
    formats fail explicitly, including %n and unbounded user format strings.
    """
    typed = []
    if '\0' in fmt:
        raise ValueError('NUL is not allowed in a generated printf format')
    capacity = len(fmt.encode('utf8')) + 1
    index = 0
    values = iter(arguments)
    while index < len(fmt):
        if fmt[index] != '%':
            index += 1
            continue
        if fmt[index:index+2] == '%%':
            index += 2
            continue
        match = re.match(r'%(?:\.[0-9]{1,2})?([dsgf])', fmt[index:])
        if not match:
            raise ValueError('Unsupported generated caller printf conversion')
        try:
            value = next(values)
        except StopIteration as error:
            raise ValueError('Missing printf argument') from error
        conversion = match.group(1)
        if conversion == 'd':
            if not isinstance(value, int) or not -(1 << 31) <= value < (1 << 31):
                raise ValueError('printf %d requires initialized C int32')
            typed.append(ctypes.c_int(value))
            capacity += 512
        elif conversion == 's':
            if not isinstance(value, str) or '\0' in value:
                raise ValueError('printf %s requires initialized terminated text')
            typed.append(ctypes.c_char_p(value.encode('utf8')))
            capacity += len(value.encode('utf8'))
        else:
            if not isinstance(value, (int, float)):
                raise ValueError('printf floating conversion requires a numeric value')
            typed.append(ctypes.c_double(value))
            capacity += 512
        index += len(match.group(0))
    try:
        next(values)
    except StopIteration:
        pass
    else:
        raise ValueError('Extra printf argument')
    encoded = fmt.encode('utf8')
    if capacity > 1_000_000:
        raise ValueError('Generated printf output exceeds the finite boundary')
    buffer = ctypes.create_string_buffer(capacity)
    # MSVCRT's bounded buffer call avoids its non-C17 NULL/zero behavior.
    count = _snprintf()(buffer, len(buffer), encoded, *typed)
    if not 0 <= count < capacity:
        raise ValueError('C printf boundary failed or truncated its output')
    return buffer.raw[:count].decode('utf8')
