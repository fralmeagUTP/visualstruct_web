# Main de ordenamiento: propuesta minima concreta

La UI sigue sin mostrar ni generar main. Este bloque implementa solo la semantica por instruccion de Intercambio; el prototipo no constituye un caller real del producto ni cierra C-SORT-MAIN-01.

## Integracion propuesta

Usar el historial aceptado por el servidor, en orden, en la quinta seccion ya existente («Resultados de ejecucion»). Dentro del historial plegable, mostrar un pre de clase didactic-history-main con el programa C y la indicacion de compilar con el C/H descargado. No agregar una sexta seccion, acciones de ejecucion, endpoints ni un segundo historial. Un cambio de modo o retroceso conserva el mismo programa cronologico; GET y la recarga lo reconstruyen sin ejecutar operaciones historicas.

El servidor debe persistir los valores materializados de cada generate_random_array. La semilla Python no puede sustituirse por rand de C. Las creaciones manuales usan los enteros ya validados. Cada creacion escribe el mismo arreglo automatico int arreglo[80] y cambia n; cada run exitoso posterior llama al TAD sobre el estado corriente y usa imprimir_arreglo para producir el resultado. Se conservan dos runs iguales. Fallos, navegacion y efectos historicos invalidos no se convierten en llamadas C. Intercambio retorna void; no se inventa un codigo de retorno. INT_MIN/INT_MAX usan macros del C/H. El arreglo pertenece al main y sale de scope al retornar, sin malloc/free.

Para los otros diez metodos se necesita un bloque de integracion separado que respete sus firmas reales, especialmente los cuatro retornos int y sus fallos. Este prototipo rechaza runs de esos metodos, en lugar de atribuirles soporte no verificado.

## Prototipo revisable, fuera de la UI

sorting-main-minimal-prototype.py contiene build_main(history, materialized_random). Los valores aleatorios son un argumento explicito; su ausencia no se rellena con otra secuencia. El historial y sus array_effect deben coincidir cronologicamente antes de emitir llamadas. Tres programas y sus entradas/salidas estan en evidence/visible-sorting-intercambio-instructions/main-prototype: manual_repeated, recreate_negative, random_materialized. Se compilaron con gcc -std=c17 -Wall -Wextra -Wpedantic -Werror, junto al C descargado por HTTP. Las salidas reales coinciden con los estados de las operaciones aceptadas; Doxygen del main/C/H no emitio advertencias. Son tres programas de propuesta, no tres mains mostrados por el producto.

## Criterio de cierre futuro

Asignacion fina y guarda propias para integrar el main. Capturar el programa realmente mostrado tras creacion manual/aleatoria, dos runs, recreacion y recarga; compilar sus bytes C17 con C/H HTTP, observar ownership y verificar Doxygen. Confirmar que el historial fallido y el replay no agregan llamadas y que se conservan las cinco secciones. No ejecutar esa ampliacion como parte del cierre Intercambio.
