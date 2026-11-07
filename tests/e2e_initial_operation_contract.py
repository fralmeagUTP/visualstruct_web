"""The full player restores the selected operation card before instruction zero."""
RULES = {
    'abb': 'Los valores menores van a la izquierda; los mayores, a la derecha.',
    'sublist': 'Cada hijo pertenece a la sublista de un padre concreto.',
    'red_black': 'El orden de búsqueda y las reglas de color se conservan tras cada operación completa.',
}
OPERATIONS = {
    'insertar': ('Insertar', 'Ubicar el valor y conectarlo donde corresponde.'),
    'insertar_padre': ('Insertar padre', 'Crear el nodo padre con su sublista vacía.'),
    'insertar_hijo': ('Insertar hijo', 'Localizar el padre y agregar el hijo a su sublista.'),
    'eliminar_padre': ('Eliminar padre', 'Retirar el padre y liberar también su sublista.'),
    'hijos_de': ('Listar hijos', 'Localizar el padre y consultar únicamente los valores de su sublista.'),
    'limpiar': ('Limpiar', 'Liberar los nodos y dejar la estructura vacía.'),
}


def operation_card(family, operation):
    title, goal = OPERATIONS[operation]
    return [f'{title}: {goal}', f'Regla a observar: {RULES[family]}', 'Ahora: Prepara la operación y avanza con «Siguiente paso». Aún no hay instrucciones ejecutadas.']


def assert_initial_operation_card(page, prefix, family, operation):
    rows = page.locator(f'#{prefix}-pedagogy-summary > .contextual-help-points > li').all_text_contents()
    assert rows == operation_card(family, operation), (family, operation, rows)
