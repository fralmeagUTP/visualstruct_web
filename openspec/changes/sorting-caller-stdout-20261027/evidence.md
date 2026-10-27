# Evidencia finita de stdout de Ordenamiento

## Resultado y destino

Implementado y verificado únicamente en `C:\Users\fralm\Documents\Codex\2026-10-27\task\visualstruct-syntax-review`. No certifica D:, Docker, VPS ni publicación. C/H canónicos y generador del main permanecen intactos; no se editó frontend ni Hash desde este ownership.

El defecto era que el main real sí imprime durante creación y antes/después del ordenamiento, mientras la traza solo ejecutaba el algoritmo silencioso. El nuevo `app/services/sorting_caller_console.py` usa el AST/VM existente para ejecutar main y los cuerpos reales de `arreglo_valido`/`imprimir_arreglo`. El printf usa el helper compartido `caller_printf.c_printf`, con snprintf real del CRT/libc. No existe formateador Python del arreglo ni compilador en runtime.

Se modificaron también `sorting_structure_service.py` para adjuntar el stdout y `sorting_routes.py` para serializar `console_output` y la traza paginada guardada en GET. Los algoritmos silenciosos consumen sus efectos aceptados como journal de memoria; GET y páginas no vuelven a ordenar. El último cursor agrupa la salida del caller posterior al retorno sin agregar o modificar eventos nativos del TAD.

## Verificación

Quince pruebas nuevas únicas en `tests/test_sorting_caller_stdout.py` pasaron por particiones. No se suman las repeticiones:

- Primera ejecución: **13 passed, 2 failed, 14.65 s** (`focused-tests-initial.log`). Los once algoritmos pasaron contra el stdout del main descargable real compilado con C/H descargados, `gcc -std=c17 -Wall -Wextra -Wpedantic -Werror`. También pasaron rechazo sin nuevo stdout y los controles fuente printf modificado/main silencioso.
- Los dos fallos iniciales fueron un endpoint random mal escrito en la prueba y un campo stdout omitido por la serialización GET existente. Corregidos, el seguimiento dio **1 passed, 1 failed, 13 deselected, 2.42 s** (`focused-integration-final.log`): random con semilla, runs repetidos void/int, C17 y GET sin replay pasaron; apareció además la omisión de la traza guardada en GET.
- Tras serializar condicionalmente esa traza, el único caso paginado dio **1 passed, 14 deselected, 0.60 s** (`focused-paged-final.log`). Entrada pequeña `[128, 0]`; cursor inicial/final, página, GET/reload, historia estable y `SortingAdapter.run` prohibido mediante monkeypatch. Se verificó además la correspondencia de la línea printf con el C real.

La prueba de main modificado demuestra que el evaluador sigue una instrucción printf adicional del programa. La de main silencioso conserva el resultado ordenado pero exige stdout vacío, descartando síntesis desde el estado final.

Coordinación verificó por separado el helper CRT en Linux sin red y con filesystem de contenedor readonly, incluyendo int32, string, float32/double, porcentajes y rechazo de formatos no admitidos. Esa evidencia pertenece a coordinación, no sustituye las pruebas C17 de Ordenamiento.

## Continuidad y límites

Se registró primero propuesta/diseño/spec y el binding de coordinación. La primera guarda rechazó una lista de cinco tareas con el mismo prefijo; se corrigió a un bloque único con pasos y la guarda before pasó. No se usó ese rechazo como autorización para implementar.

El evaluador acepta el main generado y los helpers de impresión del subconjunto actual, no C arbitrario. El ABI de punteros/celdas está documentado en design.md. El journal contiene solo runs aceptados; rechazos no se agregan al main ni al stdout aceptado. Un programa vacío descargable no se ejecuta automáticamente sin creación aceptada. Existe un presupuesto finito de eventos del evaluador; no se ejecutó una prueba de historiales enormes ni una suite global.

La reproducción manual del frontend y GET/páginas están cubiertos por el contrato; no se cambió el endpoint legacy que reconstruye una traza densa cuando se solicita explícitamente una nueva operación `step`. El QA Chromium corresponde al ownership de coordinación. No hubo commit/push/despliegue ni afirmación de CI global verde.
