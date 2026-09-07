# Diseño pedagógico del módulo de estructuras jerárquicas

## Principios

1. Cada frame visual corresponde a una instrucción C realmente ejecutada.
2. El frontend representa estados y eventos canónicos; no infiere ramas, rotaciones ni recoloreos.
3. Cada frame responde qué se comparó, qué rama se tomó, qué cambió y qué invariante se conserva.
4. Cambiar el nivel modifica la explicación, nunca la traza ni el cursor.
5. Avanzar y retroceder restaura árbol, arreglo, variables, pila, consola y memoria exactamente.
6. Color y movimiento siempre tienen texto, símbolos o patrones equivalentes.

## Arquitectura de pantalla

- **Preparar:** estructura, operación, entradas, nivel, ejemplo y estado inicial.
- **Predecir:** rama, caso de eliminación, rotación, recoloreo o intercambio esperado.
- **Ejecutar:** visualización, código y controles completos.
- **Comprender:** condición sustituida, pila recursiva, alturas, factores, colores e invariante.
- **Relacionar con C:** función activa, parámetros, retornos, punteros, memoria y `printf`.
- **Comparar:** dos ejecuciones aisladas sincronizadas por operación o concepto.
- **Reflexionar:** conclusión, historial, errores frecuentes y exportación.

En escritorio, visual y C permanecen simultáneamente visibles. En móvil se usan pestañas persistentes sin perder cursor ni contexto.

## Contrato de frame jerárquico

```json
{
  "schema_version": 1,
  "structure": "avl",
  "operation": "insertar",
  "concept": "compare|descend|return|height|imbalance|rotation|recolor|swap|free|invariant",
  "source": {"line_index": 42, "line_text": "balance = altura(n->izq) - altura(n->der);"},
  "condition": {"source": "balance > 1", "substituted": "2 > 1", "result": true},
  "variables": [{"name": "balance", "type": "int", "previous": 0, "value": 2}],
  "call_stack": [{"function": "avl_insertar", "parameters": {"raiz": "n30", "valor": 10}, "continuation": "actualizar altura"}],
  "nodes": [{"id": "n30", "height": 3, "balance": 2, "color": null}],
  "adjustment": {"kind": "LL", "pivot": "n30", "child": "n20", "transferred_subtree": "T2"},
  "invariant": {"name": "balance AVL", "holds": false, "evidence": "FE(30)=2"},
  "state_before": {},
  "state_after": {},
  "narration": {"basic": "...", "intermediate": "...", "advanced": "..."}
}
```

## Invariantes

| TAD | Evidencia requerida |
|---|---|
| ABB | límites inferior/superior por nodo e inorden estrictamente creciente |
| AVL | propiedad ABB, altura calculada y `|FE| ≤ 1` por nodo |
| Rojo-negro | raíz negra, ausencia de rojo-rojo y black-height igual por camino |
| Min-heap | forma casi completa y `A[parent(i)] ≤ A[i]` |

Un frame puede mostrar temporalmente un invariante incumplido durante un ajuste, pero debe indicar que el algoritmo está en fase de reparación y verificarlo al finalizar.

## Explicación de ajustes

- AVL: inserción/eliminación → actualización de altura → desequilibrio → LL/RR/LR/RL → rotación(es) → nuevas alturas.
- Rojo-negro: nodo/padre/abuelo/tío → caso → recoloreo/rotación → propagación → raíz negra.
- Heap: índice actual → padre/hijos → comparación → intercambio → nueva posición → criterio de parada.
- ABB: comparación → descenso recursivo → caso hoja/un hijo/dos hijos → sucesor → retorno y reconexión.

## Niveles

- **Básico:** valores, rama, regla estructural, resultado e invariante.
- **Intermedio:** alturas, factores, casos, índices, rutas y enlaces.
- **Avanzado:** C completo, recursión, punteros, memoria, retornos y direcciones lógicas.

## Comparaciones

Las comparaciones usan copias profundas de una entrada inmutable y sincronizan por concepto: ABB/AVL con entrada ordenada, AVL/rojo-negro, ABB/heap y recorridos. Cada lado mantiene traza, cursor y estado independientes.

## Estrategia de pruebas

- Golden traces para comparación, recursión, retorno, tres casos de eliminación, cuatro rotaciones AVL, casos RN y heapify.
- Propiedades de orden, balance, color, black-height, forma completa y heap.
- Equivalencia C/backend/traza/historial/consola/visual y rápido/paso a paso.
- Reversibilidad, práctica, comparación, teclado, móvil y reducción de movimiento.
- Suite completa, cobertura, C17, AddressSanitizer y UndefinedBehaviorSanitizer.
