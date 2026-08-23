# Diseño pedagógico del módulo de ordenamiento

## Principios

1. **Correspondencia:** cada explicación debe estar vinculada al estado y a la línea C real.
2. **Progresión:** el estudiante controla cuánto detalle recibe.
3. **Segmentación:** una acción conceptual por frame, con agrupación por fase.
4. **Señalización:** color, texto, icono y posición comunican el mismo significado.
5. **Aprendizaje activo:** las preguntas predictivas son opcionales y nunca bloquean la exploración.
6. **Reversibilidad:** avanzar y retroceder recupera exactamente estado, variables y pila.
7. **Comparabilidad:** métricas empíricas y complejidad teórica se presentan como conceptos distintos.

## Arquitectura de la pantalla

La pantalla se divide en cinco regiones coordinadas:

1. **Preparar:** entrada manual/aleatoria, ejemplos guiados y selección de algoritmo.
2. **Visualizar:** arreglo y representación específica del método.
3. **Comprender:** objetivo de fase, condición evaluada, explicación y variables.
4. **Relacionar con C:** código, pila de llamadas, parámetros y retornos.
5. **Reflexionar:** predicción, métricas, invariante y comparación.

En escritorio, Visualizar y Código permanecen visibles simultáneamente. En pantallas estrechas se
usan pestañas con encabezado fijo y se conserva el paso al cambiar de pestaña.

## Niveles didácticos

### Básico

- Lenguaje natural, arreglo, símbolos y objetivo de la fase.
- Oculta detalles de punteros y comentarios extensos.
- Tamaño recomendado: 5–8 elementos.

### Intermedio

- Añade índices, rangos, condiciones, ciclos, variables principales e invariantes.

### Avanzado

- Añade C completo, pila de llamadas, punteros, temporales, estados transitorios, auxiliares,
  recursión y métricas completas.

El nivel cambia la presentación, nunca la ejecución ni la secuencia causal.

## Modelo de frame pedagógico

Cada frame amplía el contrato de traza con:

```json
{
  "concept": "comparison|branch|call|return|assignment|swap|phase",
  "phase": {"id": "bubble-pass", "label": "Pasada 2", "goal": "..."},
  "condition": {"expression": "8 > 3", "result": true, "consequence": "..."},
  "variables": [{"name": "j", "value": 2, "changed": true, "meaning": "..."}],
  "call_stack": [{"function": "ordenar_burbuja", "parameters": {"n": 5}}],
  "invariant": {"text": "El sufijo [4..4] está ordenado", "indices": [4]},
  "narration": {"basic": "...", "intermediate": "...", "advanced": "..."}
}
```

Los campos se generan desde eventos del intérprete; el frontend no deduce ramas ni analiza C.

## Visualización específica por algoritmo

| Algoritmo | Representación principal |
|---|---|
| Intercambio | pareja fija `i,j`, comparación y permuta |
| Selección | mínimo provisional, candidato y prefijo confirmado |
| Inserción | clave separada, hueco y desplazamientos |
| Burbuja | pasada, comparación adyacente y frontera del sufijo |
| Shell | `gap` y subsecuencias coloreadas/etiquetadas |
| QuickSort | pivote copiado, `i/j`, particiones y árbol de llamadas |
| MergeSort | árbol de división, arreglo auxiliar y fusión por segmentos |
| HeapSort | arreglo y árbol heap sincronizados, zona heap/ordenada |
| Counting Sort | dominio de valores, frecuencias y reconstrucción |
| Binsort | delegación explícita y representación de urnas/conteos |
| Radix Sort | signo, dígito activo y buckets 0–9 |

## Representación numérica

Las barras usan un eje cero. Los negativos crecen a la izquierda y los positivos a la derecha.
La longitud comunica magnitud; la posición respecto al eje comunica signo. El valor textual
siempre permanece visible.

## Evaluación formativa

Las preguntas se insertan antes de ramas, intercambios y cambios de fase. El estudiante puede:

- elegir una predicción;
- solicitar una pista;
- continuar sin responder;
- ver explicación inmediata;
- repetir el mismo concepto con otra entrada.

Sólo se guardan aciertos y conceptos durante la sesión; no se almacenan datos personales.

## Comparador

El comparador ejecuta dos algoritmos sobre una copia idéntica e inmutable de la entrada. Puede
sincronizarse por paso o por evento conceptual. Presenta métricas observadas y una ficha teórica:
mejor/promedio/peor caso, memoria, estabilidad e in-place. Nunca infiere complejidad asintótica a
partir de una sola ejecución.

## Accesibilidad

- Ningún significado depende sólo del color.
- Símbolos: `C` comparación, `I` intercambio, `P` pivote, `✓` confirmado, `A` auxiliar.
- Controles operables por teclado y foco visible.
- Región `aria-live` breve para cambios; narración extensa consultable bajo demanda.
- Pausa automática si el usuario solicita reducción de movimiento.

## Estrategia de pruebas

- Contratos unitarios para frames pedagógicos de cada concepto.
- Golden traces por algoritmo y caso representativo.
- Propiedades: reversibilidad, continuidad y ausencia de inferencias del frontend.
- Playwright en tres anchos de pantalla y tres niveles didácticos.
- Pruebas de teclado, roles, nombres accesibles y contraste.
- Pruebas de comparación con entrada idéntica y métricas separadas de teoría.
