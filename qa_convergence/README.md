# QA de convergencia al C del libro

Esta carpeta corresponde a la **segunda copia** de VisualStruct, posterior al
checkpoint de reparación pedagógica. No equivale a la suite histórica mencionada
por el README original. Estado vivo: `INTEGRATION_STATUS.md` y el cambio OpenSpec
`cloud-graph-book-convergence-20261027`.

## Reproducción local
Desde la raíz `app/`, con Python/dependencias y Node ya instalados:

```sh
python -m unittest discover -s qa_convergence -p 'test_*.py' -v
for test in qa_convergence/test_*.js; do node "$test" || exit; done
python qa_convergence/run_non_graph_regressions.py
sh qa_convergence/run_non_graph_node.sh
```

Las regresiones no-grafo necesitan los fixtures vecinos originales `qa_trazas/`,
`qa_frontend_main/`, `scope-insert-baseline/` y `*-baseline.py`. Los dos baselines de ayuda se incluyen en `checkpoint_fixture/`, con hashes
extraídos del ZIP de checkpoint: no dependen de una ruta cloud externa. Los tests nativos
usan GCC disponible, no descargan herramientas ni servicios. La carpeta
`../qa_independent/` contiene oráculos y revisiones distintas del autor; la QA
real de navegador vive en `../qa_ui/` y no queda sustituida por tests DOM.

Los antiguos `qa/test_graph_*` documentan contratos y source hashes previos. Se
preservan como evidencia, **no deben interpretarse como la suite de aceptación de
este nuevo C**. También cambió la extracción textual del viejo handler crear de
`qa/test_real_stdout.js`; el runner no-grafo ejecuta sus casos jerárquicos y deja
los casos grafo a las pruebas de handlers canónicos. Los fallos iniciales de esa
selección quedan registrados; no se eliminan para aparentar verde.

## Semántica importante
- `docs/tads_C/tad_grafo.c/h` deben conservar exactamente los hashes canónicos.
- El servicio usa el intérprete restringido de esas instrucciones. C nativo se
  compila sólo en las comprobaciones externas, no por cada petición web.
- Ocho estados `GrafoEstado`, salida separada para costo y `NULL + GRAFO_OK` válido.
- Una inserción C es atómica. Dos sentidos no dirigidos son llamadas separadas;
  un fallo inverso conserva el primer efecto y se muestra como asimetría real.
- Historial nuevo marcado `graph-book/v1`. Historial anterior/no reconstruible:
  suspensión explícita, exportación sin reinterpretar y restablecimiento confirmado.
- Captura completa hasta 4.000 eventos C/caller más publicación API. Sobre el límite,
  paso rechaza sin escribir; normal devuelve el resultado completo sin traza extensa.
- No se ofrece un main ordinario que simule un historial de inyección QA de malloc.

## Instancia de QA
El puerto5054 usa cookie/cache independientes y
`SESSION_REFRESH_EACH_REQUEST=False`. No comparte estado con5053. Esta opción
impide renovaciones de TTL/cookie en lecturas, además de que las rutas de exportar
no mutan el contenido. No modificar configuraciones de producción ni del original.

La UI y revisión integrada tienen aceptación finita. La primera extracción/rollback
se conserva en ../package-verification-first.json. Antes de aplicar el paquete final,
comprueba su verification.json y hashes: se vuelve a verificar tras el sello.
