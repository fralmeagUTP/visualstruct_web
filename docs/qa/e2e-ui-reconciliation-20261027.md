# Conciliación finita E2E de la entrega

Los cuatro fallos iniciales siguientes se reprodujeron localmente con Chromium headless y un servidor Flask efímero. No se controló el Chrome del usuario, Docker5050 ni el VPS.

| Caso | Observación real | Comprobación conservada o ampliada |
| --- | --- | --- |
| Panel C e historial de grafos | El título contiene `Código C canónico del libro` y `tad_grafo.c`. | Título canónico, función de inserción, historial `main` y panel desplazable. |
| Controles del intérprete hash | Restablecer exige confirmación y devuelve un estado explícito de tabla restablecida. | Aceptación del diálogo de datos sintéticos, POST de reset, HTTP200, éxito, historial vacío y navegación siguiente/anterior. |
| MST, teclado y tamaño móvil | La inserción de arco informa `grafo_insertar_arco`; no usa el mensaje histórico «arista insertada». | Preparación sin resultado futuro, navegación de toda la traza, función C final, Prim, teclado y control disponible a 390 px. |
| Contexto educativo AVL móvil | El resumen utiliza lenguaje docente («llamador equivalente», «no hay resultado futuro»). | Evento backend `caller_enter`, explicación visible, pestañas código/visual y conservación del cursor. |

Tras conciliar las expectativas con esos contratos, los cuatro casos pasaron: **4 passed in 115.99s**. Ninguno se eliminó ni marcó para omitir. Estas correcciones no cambian código de producto ni C/H.

El caso de algoritmos por fases conserva la comprobación estricta del nuevo campo `execution_mode=step`, el historial y estado tras cada operación. La navegación manual usa el número finito de pasos declarado por la traza canónica, en lugar del límite histórico fijo de 2000. Cada avance sigue esperando un cambio de cursor y la terminación exige el control deshabilitado.

La ejecución completa de BFS, Dijkstra y Prim por fases también pasó: **1 passed in 317.82s**. Verificó cada avance manual y, tras cada algoritmo, el estado final de la respuesta, la vista visible, el historial y las solicitudes emitidas por UI. En conjunto, los cinco casos que fallaban inicialmente pasan localmente.

La partición complementaria del archivo detectó cuatro expectativas adicionales de presentación. La ubicación de los controles de Pila se comprueba ahora inmediatamente antes del espacio de clase. Los botones de exportación de Hash y Ordenamiento se alcanzan abriendo sus contenedores reales de Resultados, mediante los `summary` visibles, en vez de un índice histórico de panel.

Para JPG se mantiene un desbordamiento real en una ventana móvil a escala nativa. La exportación normaliza zoom y restricciones de pantalla; por ello se verifica la escena realmente enviada al rasterizador: ocho vértices completos, texto del bloque de resultado idéntico, metadatos del grafo y dimensiones que cubren el `viewBox` nativo. El JPEG se decodifica y sus dimensiones coinciden con las declaradas. Esta prueba final pasó: **1 passed in 61.33s**.

## Resultado local por particiones

- Cuatro casos inicialmente fallidos: **4 passed**.
- BFS, Dijkstra y Prim por fases: **1 passed**.
- Casos complementarios sin modificaciones adicionales: **20 passed**.
- Pila compacta y exportación Hash/Ordenamiento: **3 passed**.
- JPG con escena completa y decodificación real: **1 passed**.

Los **29 casos** de `test_ui_playwright_e2e.py` quedan cubiertos por esas ejecuciones. Los fallos iniciales y las iteraciones de geometría se conservan en logs locales; no se eliminó ningún caso para conseguir el resultado.

También pasan las dos consultas de vecinos de `test_graph_neighbors_native_and_DOM_regression.py`: **2 passed, 1 deselected in 21.34s**. El caso deseleccionado es el oráculo nativo, verificado por separado por su propietario. Los dos casos que abren navegador tienen ahora marcador `e2e` y permanecen en la suite de navegador. Verifican memoria y ámbitos en ambos sentidos, distinción entre instrucciones C y límites del caller, ningún POST durante replay/reload y coincidencia exacta entre `main.c` del DOM y HTTP. La consulta y su liberación pertenecen al historial canónico `graph-book/v1`.

Estas pruebas locales son finitas y se ejecutaron por particiones. No sustituyen el CI del commit publicado.
