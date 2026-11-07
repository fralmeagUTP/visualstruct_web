"""Finite independent expectations for instruction prose in the browser audits."""
import pytest
from _audit_sorting_narration import expected_instruction_narration


@pytest.mark.parametrize(('action', 'expected'), [
    ('Antes de llamar ordenar_intercambio; no se ejecutó una instrucción C.',
     'Antes de llamar ordenar_intercambio; no se ejecutó una instrucción C.'),
    ('Retornar la validación; termina su scope.',
     'Retornar la validación; termina su ámbito de la variable.'),
    ('Entrar en intercambiar; caller suspendido.',
     'Entrar en intercambiar; función que llamó suspendida.'),
    ('Retorno void; retirar scope y alias del helper.',
     'Retorno void; retirar ámbito de la variable y alias de la función auxiliar.'),
    ('Retorno void al caller; el TAD no ejecuta printf.',
     'Retorno void a la función que llamó; el TAD no ejecuta printf.'),
    ('Asignar *a=*b; duplicación provisional.',
     'Asignar *a=*b; duplicación provisional.'),
])
def test_instruction_meaning_is_preserved_in_student_text(action, expected):
    assert expected_instruction_narration(action) == expected


def test_different_instruction_is_not_accepted_as_same_narration():
    assert expected_instruction_narration('Asignar *a=*b; duplicación provisional.') != expected_instruction_narration('Asignar *b=temporal; completar el intercambio.')
