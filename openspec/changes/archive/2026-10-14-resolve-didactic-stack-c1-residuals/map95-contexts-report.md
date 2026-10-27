# Resultado del bloque de 95 candidatos

Se añadieron 24 vínculos de fuente. El registro pasa de 143 vínculos y 232 pendientes a 167 vínculos y 208 pendientes. Los vínculos reutilizan seis funciones de prueba existentes; no equivalen a 24 pruebas ejecutadas.

| Categoría | Vínculos nuevos | Alcance |
|---|---:|---|
| Algoritmos | 9 | SortingAdapter: entrada 5,1,4,2,3 y resultado [1,2,3,4,5], con fixture C real. Prueba unitaria; no endpoint ni UI. |
| Operaciones | 10 | Seis consultas inorden/validar tras inserciones y borrado; dos rechazos de insertar inválido con history[]; cinco extracciones heap con resultado agregado [1,1,3,7,9]; Prim con peso3. |
| Fases | 4 | GET parametrizado, HTTP200 e identificador de fase renderizado. |
| Ruta | 1 | La misma parametrización de cuatro fases. No sumar estos casos dos veces. |

Los 24 vínculos registran función, línea, hash, parámetros, setup, ruta/operación, esperado y alcance en bindings-map95/app-executable-bindings.json. La relación de SortingAdapter con POST /api/ordenamiento/run es contractual: el caso unitario no llama al endpoint. El rechazo de insertar inválido no demuestra inserción nominal. El renderizado de fase no demuestra ejecución de algoritmo.

Se conservan los 14 contextos compartidos: doce requisitos de algoritmo por fase comparten seis backends; dos reset-button pertenecen a páginas distintas. shared14-review.json enlaza el caso backend y el caso de renderizado disponibles, indicando por qué no bastan para acreditar la interacción en esa fase. Ningún requisito eliminado ni exclusión/ausencia certificada.

Quedan 71 de los 95 candidatos sin cadena completa: doce algoritmos graph, cuatro controles,49operaciones y seis rutas. classification95.json conserva sus IDs y acciones pendientes. Los otros137pendientes permanecen intactos. El siguiente bloque deberá resolver helpers, parámetros y aserciones correlacionadas de un grupo concreto; reutilizar evidencia vigente de campañas consumidas antes de considerar ejecución focal.

Verificación: gate sin errores; tres pruebas focales del verificador de fuente pasan (0,984s de supervisor;38,27MiB; límites120s/2GiB). Cero pruebas de producto ejecutadas y cero nuevas aceptaciones. Fuente, ejecución y aceptación permanecen separadas. No Docker, campañas, commit, push ni despliegue. Evidencia previa preservada.
