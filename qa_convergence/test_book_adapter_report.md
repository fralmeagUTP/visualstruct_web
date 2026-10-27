# Adaptador canónico del libro — 2026-10-27

Alcance: `app/adapters/graph_adapter.py`, nuevo `app/domain/graph/book_application.py` y pruebas propias. Sólo copia `visualstruct_convergencia_libro_20261027/app`. Canon C/H y copia previa intactos.

## Implementación
- `execute` ya no ejecuta algoritmos Python anteriores: una `BookSession` por operación y llamadas públicas reales.
- Validación int32 y límite educativo15 antes de ejecutar. RNG puro existente materializa comandos y conserva semilla real.
- Grafo no dirigido: segunda llamada sólo si la primera devolvió GRAFO_OK; fallo inverso conserva efectos reales sin rollback. Todas llamadas quedan registradas.
- Estado serializado desde `graph_after` HEAD hacia almacenamiento insertion-order; estructuras enlazadas sólo reconstruyen esa proyección, no recalculan algoritmos.
- Listas retornadas mantienen orden C. Propias se copian como resultado de aplicación y liberan explícitamente por funciones C canónicas; prestadas no se liberan.
- Resultados incluyen c_status/c_status_name/c_return/output/ownership. NULL+OK es válido; costo inexistente retorna0 y no inicializa salida. Rutas/totales se derivan únicamente de listas C reales; no se inventa tabla de distancias completa.
- Callback opcional `_book_callback` transmite también cleanup. `_last_book_execution` conserva calls compactas, fuente única, snapshot final y resultado; no acumula transitions/raw snapshots al no solicitar traza.
- Visual conserva arcos reales completos `c_arcs` y `asymmetric_pairs`; la combinación gráfica de inversos iguales no elimina esta evidencia.

## Verificación
`PYTHONPATH=. ../../visualstruct_prueba_local/.venv/bin/python -m unittest qa_convergence.test_book_adapter qa_convergence.test_book_main_native qa_convergence.test_book_main_help -v`

7 grupos adaptador: cobertura19 operaciones; comparación directa motor de16; orden/estado; fallo primera llamada vs inversa; todas reservas alcanzablesBFS; marcas preservadas y sin fuga; estados0..6 alcanzados en integración (RANGO7 cubierto por motor, no fingido aquí); consulta0/ausente; selfpathNULL+OK; total3e9; MSTdesconectado sin bosque; callback/cleanup; monkeypatch prohibiendo algoritmosviejos; rechazo preejecución sin mutación. Además10 grupos main/guía previos, incluidos26 mainsC17 estrictos.

Resultado reproducible: `book_adapter_tests.log`. Gateafter: `book_adapter_gate_after.json`.

## Límites
Estas pruebas son integración directa Python, no aprobación GUI/endpoints/sesiones. Oráculo nativo del motor y revisión independiente separados. No se afirma que todo GrafoEstado sea alcanzable mediante interfaz limitada15. UI aún debe adaptar presentación de estados nuevos, fuente íntegra y asimetría. No se desplegó ni reinició servidor.
