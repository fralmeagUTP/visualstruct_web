# Estado canónico C↔Python v1

El comparador diferencial usa el esquema `canonical-state/v1`. El contrato elimina campos de UI, mensajes y orden incidental, pero conserva toda diferencia observable del TAD.

| TAD | Estado contractual | Invariantes |
|---|---|---|
| Lista, pila, cola, cola de prioridad, lista circular y sublista | secuencia lógica y tamaño | tamaño real igual al declarado; el orden es significativo |
| ABB | in-order, pre-order, forma y tamaño | orden BST estricto |
| AVL | contrato ABB | orden BST y validación AVL |
| Rojinegro | contrato ABB | orden BST y validación de color |
| Montículo binario | arreglo lógico y tamaño | propiedad min-heap |
| Grafo | dirigido, vértices y aristas normalizadas | vértices únicos; orientación ignorada sólo si no es dirigido |
| Tabla hash | pares clave/valor y capacidad | tamaño y capacidad positiva; buckets no son contractuales |
| Ordenamiento | arreglo resultante y tamaño | tamaño consistente |

Los harnesses C deberán emitir datos equivalentes a este contrato. Una violación estructural produce `CanonicalStateError` y nunca se trata como una simple diferencia de presentación.
