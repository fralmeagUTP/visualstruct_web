# Change: Validar y endurecer el módulo de ordenamiento

## Por qué

El módulo ofrece once algoritmos como interpretaciones didácticas de C, pero necesita una
validación exhaustiva y reproducible que cubra entradas reales, opciones de ejecución,
fidelidad de trazas, navegación, errores y equivalencia entre el estado visual y el resultado C.

## Qué cambia

- Se define una matriz de pruebas para los once métodos y todas las operaciones del módulo.
- Se contrasta resultado, multiconjunto, traza, línea C, auxiliares, métricas y estado visual.
- Se validan límites de `int` C, entradas inválidas, generación aleatoria y rangos costosos.
- Se corrigen las divergencias descubiertas y se conservan como pruebas de regresión.
- Se publica un informe con entradas, resultados observados, correcciones y evidencia final.

## Impacto

- Capacidades afectadas: `sorting-visualizer`, `c-code-interpreter`, `visual-playback-ui`.
- Código afectado: dominio/adaptador/servicio/rutas de ordenamiento, extracción de C,
  frontend del visualizador y pruebas.
