"""Two exact reviewed swap display labels; never normalize C or execution data."""
from copy import deepcopy

_SWAP_LABELS = {
    'Asignar 1 a la primera posicion; temporal conserva 2.':
        'Asignar 1 a la primera posición; temporal conserva 2.',
    'Asignar temporal (2) a la segunda posicion.':
        'Asignar temporal (2) a la segunda posición.',
}

def current_swap_display(value):
    value = deepcopy(value)
    def update(item):
        if isinstance(item, list):
            for child in item: update(child)
        elif isinstance(item, dict):
            for key, child in item.items():
                if key in {'action', 'console_output'} and isinstance(child, str):
                    item[key] = _SWAP_LABELS.get(child, child)
                else:
                    update(child)
    update(value)
    return value
