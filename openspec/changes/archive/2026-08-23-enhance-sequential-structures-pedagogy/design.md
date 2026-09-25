# Diseño pedagógico del módulo de estructuras secuenciales

## Principios

1. Cada cambio visual es consecuencia de un evento real del intérprete C.
2. El frontend representa frames; no deduce ramas ni interpola estados por proporción.
3. Cada frame responde: qué se ejecutó, por qué, qué cambió y qué invariante se conserva.
4. Los niveles alteran la presentación, nunca la traza ni el resultado.
5. Toda navegación es reversible y restaura estado, variables, pila, memoria y consola.
6. Ningún significado depende únicamente del color o de una animación.

## Arquitectura de pantalla

- **Preparar:** TAD, operación, entrada, ejemplos y estado inicial.
- **Predecir:** pregunta opcional antes de ramas, enlaces, liberaciones y cambios de extremos.
- **Ejecutar:** reproductor y progreso navegable.
- **Comprender:** objetivo, condición sustituida, variables, memoria e invariante.
- **Relacionar con C:** código, función activa, pila, parámetros, retorno y `printf`.
- **Reflexionar:** historial, comparación entre TAD, errores frecuentes y exportación.

En escritorio, estado y C permanecen visibles. En móvil se usan pestañas persistentes.

## Contrato de frame secuencial

```json
{
  "schema_version": 1,
  "structure": "queue",
  "concept": "allocation|condition|assignment|link|call|return|free|invariant",
  "phase": {"id": "enqueue-link", "label": "Enlazar nodo", "goal": "..."},
  "condition": {"source": "cola->frente == NULL", "substituted": "NULL == NULL", "result": true},
  "variables": [{"name": "aux", "type": "ptrNodo", "value": "n2", "changed": true}],
  "pointers": [{"name": "cola->atras", "target": "n2", "previous_target": "n1"}],
  "heap_objects": [{"id": "n2", "allocated": true, "freed": false, "fields": {"nro": 8}}],
  "call_stack": [{"function": "cola_encolar", "parameters": {"valor": 8}, "continuation": "main"}],
  "invariant": {"text": "FRONT alcanza BACK", "holds": true},
  "narration": {"basic": "...", "intermediate": "...", "advanced": "..."}
}
```

## Invariantes y visualizaciones

| TAD | Invariante | Representación principal |
|---|---|---|
| Pila | `TOP` es el único extremo de entrada/salida; LIFO | nodos verticales, `TOP`, auxiliar, asignación y `free` |
| Cola | inserta por `BACK`, retira por `FRONT`; vacía implica ambos `NULL` | extremos simultáneos y transición último nodo |
| Cola de prioridad | enlaces por llegada; selección por prioridad y empate estable | orden físico, número de llegada, candidato y seleccionado |
| Lista enlazada | todos los nodos son alcanzables una vez desde `HEAD` | `actual`, `anterior`, enlace reemplazado y nodo desconectado |
| Lista circular | el último enlaza al primero y el recorrido tiene criterio de parada | cierre estructural, vuelta al inicio y terminación |
| Sublista | cada hijo pertenece a su padre y otras ramas permanecen intactas | dos niveles, propiedad, rama activa y liberación jerárquica |

## Niveles

- Básico: metáfora, valores, extremos, operación e invariante.
- Intermedio: enlaces, recorrido, condiciones y variables principales.
- Avanzado: C completo, tipos, direcciones lógicas, `malloc`, `free`, pila y temporales.

## Comparación conceptual

El comparador ejecuta una secuencia equivalente sobre copias aisladas y permite contrastar pila/cola,
cola/cola de prioridad, lista lineal/circular y lista/sublista. Compara semántica, extremos, enlaces e
invariantes; no presenta una comparación de rendimiento cuando no sea conceptualmente válida.

## Estrategia de pruebas

- Contratos de frame y golden traces por operación/caso límite.
- Propiedades de LIFO, FIFO, prioridad estable, conectividad, circularidad y propiedad de sublistas.
- Equivalencia entre C, backend, traza, historial, consola y visualización.
- Reversibilidad, modo rápido/paso a paso, práctica y comparación.
- Playwright en escritorio, tableta y móvil; teclado, roles, nombres y contraste.
- C17 y sanitizadores para operaciones con reserva y liberación de memoria.

