# Diseño: remediación de fidelidad didáctica C

## Fuente única de semántica

Para cada operación se elegirá y documentará un contrato canónico antes de cambiar código. Cuando
la interfaz afirma interpretar C, `docs/tads_C/` será la fuente semántica y Python deberá ser una
transcripción observable. Si una capacidad pública exige extender el C, se modifican juntos el
header, implementación, harness, mapa de código, adapter y pruebas; no se conservarán dos
algoritmos diferentes sólo porque coincidan en el resultado final.

## Flujo causal de estado

```text
evento C instrumentado
        ↓
snapshot canónico + temporales + consola
        ↓
TraceStep validado (before/after, línea, identidad)
        ↓
adapter de presentación
        ↓
frame DOM determinista
```

El renderer no deduce estados desde el resultado final ni interpreta literales `printf`. Los
eventos transportan identidad lógica estable, enlaces, variables temporales y salida acumulada.

## Decisiones por prioridad

### P0: seguridad y semántica C

- `SORT-003`: obtener la magnitud de negativos en un tipo capaz de representar `INT_MIN`, sin
  evaluar `-INT_MIN` en `int`; el algoritmo debe conservar el multiconjunto completo.

### P1: contratos y resultados observables

- Grafos: formalizar dirección, tipo de peso, duplicados, extremos ausentes, orden BFS/DFS,
  política Dijkstra y conectividad de MST en un contrato común C/Python/UI.
- Hash: escoger claves enteras o una función textual determinista compartida; definir si existe
  rehash y ejecutar exactamente la misma política en C y Python.
- Secuenciales: añadir o retirar las operaciones C faltantes; pila/cola/frente deben mostrar
  snippets compilables; prioridad debe usar la misma selección estable en todas las capas.
- Rojo-negro: eliminación debe conservar `z`, `y`, `x`, padre y hermano mediante identidades
  lógicas y representar el fix-up realmente recorrido.
- Ordenamiento por conteo: rechazar amplitudes de rango que excedan el límite documentado antes de
  reservar memoria, con el mismo error en C, backend y consola.

## P2: fidelidad frame por frame

- ABB, AVL, rojo-negro y heap emitirán snapshots después de cada asignación, rotación, recoloreo,
  append, comparación e intercambio relevante.
- Pila y sublista expondrán temporales, enlaces y liberaciones con identidad lógica.
- Lista circular dibujará el autoenlace del caso unitario.
- Grafos mostrarán distancias, predecesores, visitados, candidatos y union-find según corresponda.
- Ordenamiento incluirá evaluaciones falsas y cuerpos auxiliares transitivos con línea exacta.
- La consola consumirá `console_events`; la validación exigirá continuidad profunda y coherencia
  entre `line_index`, `line_text` y el código fuente.

## Compatibilidad y migración

Los cambios de claves hash, pesos de grafo o serialización de sublistas pueden afectar sesiones
persistidas. Cada contrato se versionará; al cargar datos antiguos se migrarán de forma
determinista o se rechazará el estado con un error accionable. Los endpoints conservarán su forma
salvo que una decisión de contrato requiera un delta expresamente documentado.

## Estrategia de entrega

1. Convertir cada hallazgo en una prueba inicialmente roja.
2. Corregir P0 y ejecutar sanitizers.
3. Corregir P1 por familia, sin mezclar contratos independientes.
4. Corregir P2 sobre el protocolo causal común.
5. Ejecutar matriz completa, 5.000 secuencias deterministas y comparación UI frame a frame.

Cada lote debe cerrar sus pruebas antes de comenzar el siguiente. No se elimina ni suaviza una
aserción de caracterización para hacer pasar una implementación divergente.

## Riesgos

- Elegir un contrato distinto al comportamiento público actual puede romper sesiones: se mitiga
  con versión y migración.
- Trazas más detalladas pueden aumentar tamaño y latencia: se imponen límites y se mide el coste.
- Identidades lógicas incorrectas pueden mezclar nodos con valores duplicados: la identidad nunca
  se deriva exclusivamente del valor.
- Sanitizers pueden descubrir defectos adicionales: se registrarán como hallazgos nuevos y no se
  ocultarán dentro de este alcance.

