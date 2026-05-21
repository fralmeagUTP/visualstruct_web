# Manual de Usuario

Ultima actualizacion: **2026-05-21**.

## 1. Objetivo

El Visualizador Web de Estructuras de Datos permite practicar TAD mediante:

- operaciones interactivas,
- visualizacion del estado interno,
- apoyo didactico con codigo C real de los TAD nuevos (`docs/tads_C`) y fallback de pseudocodigo cuando aplique.

Modulos disponibles:

- Secuencial
- Jerarquico
- Grafos
- Hash

## 2. Requisitos

- Windows 10/11
- Python 3.10+
- Navegador moderno
- Acceso local a `127.0.0.1`

## 3. Instalacion y arranque

Desde `C:\Users\fralm\Desktop\Web_VisualEstruct`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\start_local.bat
```

Abrir:

```text
http://127.0.0.1:5050/
```

## 4. Navegacion

Barra superior:

- Inicio
- Modulo Secuencial
- Modulo Jerarquico
- Modulo Grafos
- Modulo Hash
- Secciones de ayuda

## 5. Flujo de uso

1. Entrar a un modulo.
2. Elegir una estructura.
3. Seleccionar una operacion.
4. Completar inputs.
5. Ejecutar.
6. Revisar resultado en:
   - mensaje didactico,
   - panel visual,
   - estructura/codigo C o pseudocodigo,
   - historial.
7. Usar `Reiniciar` para limpiar el estado de esa estructura.

## 5.1 Controles de ejecucion paso a paso

En secuencial, jerarquico y hash los controles se muestran asi:

- fila superior: `Reproducir`, `Reiniciar`.
- fila inferior: `Anterior paso`, `Siguiente paso`.

Comportamiento esperado:

- `Reproducir`: ejecuta la traza completa automaticamente.
- `Anterior paso`: retrocede una linea/paso en la traza.
- `Siguiente paso`: avanza una linea/paso en la traza.
- `Reiniciar`: limpia el estado de la estructura actual.

En grafos:

- la simulacion esta integrada en `Paso 3: Ejecutar algoritmo`;
- controles: `Reproducir`, `Anterior paso`, `Siguiente paso`;
- `Siguiente paso` avanza linea a linea la traza del algoritmo;
- `Accion actual` indica `Evaluando condicion` o `Aplicando cambio`.

Checkbox comun en todos los modulos:

- `Interpretar codigo paso a paso` activado: reproduce la traza completa.
- `Interpretar codigo paso a paso` desactivado: aplica solo el resultado final.
- Con el checkbox desactivado, `Anterior paso` y `Siguiente paso` quedan deshabilitados.
- En grafos, el resultado final en modo rapido debe coincidir con el ultimo estado visual del modo interpretado
  (mismos resaltados de recorrido, camino minimo o expansion minima).
- En grafos, al desactivar el checkbox se ocultan los controles de navegacion por paso
  (`Anterior paso`, `Siguiente paso`, velocidad, contador y accion actual).

## 6. Modo interprete C

Hay cobertura C para:

- Secuenciales (`stack`, `queue`, `priority_queue`, `linked_list`, `circular_list`, `sublist`)
- Jerarquicas (`abb`, `avl`, `red_black`, `binary_heap`)
- Grafos (`graph`)

Cuando aplica:

- `Estructura del TAD` muestra el `record` C.
- `Codigo C: <Operacion>` muestra funciones C por operacion.
- El historial se presenta como programa principal (`main`) coherente con la sesion.
- `hash_table` tambien usa contrato C (por ejemplo `th_insertar`, `th_buscar`, `th_estadisticas`).

La app no mantiene compatibilidad con nombres legacy de TAD anteriores.

## 6.1 Especificacion obligatoria de simulacion didactica

La simulacion debe representar visualmente la ejecucion real del metodo en C y el efecto sobre la estructura de datos.

Reglas de cumplimiento:

1. El interprete visual debe respetar estructuras de control (`if/else`, ciclos y retornos tempranos); no debe ejecutar ni animar ramas no tomadas.
2. En operaciones mutantes, la animacion debe mostrar al menos estas etapas:
   - estado inicial,
   - creacion de estructura temporal (ej. nodo `aux`),
   - asignaciones intermedias de punteros/enlaces,
   - reasignacion a la estructura principal,
   - estado final.
3. Las estructuras temporales deben verse como elementos separados de la estructura principal hasta el paso de reasignacion.
4. La linea activa de `Codigo C` y el estado visual deben permanecer sincronizados en cada paso.
5. La `Consola C (printf)` debe mostrar los mensajes de la ruta realmente ejecutada, evitando duplicados consecutivos.
6. El `Programa principal (main)` del historial debe ser consistente con las operaciones ejecutadas, con el estado final mostrado y sin redundancia consecutiva innecesaria.
7. Esta especificacion aplica a toda la app y unicamente a los TAD nuevos ubicados en `docs/tads_C`.

## 7. Reglas de entrada

- Secuencial/Jerarquico: valores numericos enteros.
- Grafos:
  - `vertex`, `origin`, `target`, `start`, `end`: enteros.
  - `weight`: numerico (int/float).
  - `directed`: booleano (`true/false`, `1/0`, `si/no`).
- Hash: `key` y `value` como texto.

Si un dato no cumple validacion, la operacion no se ejecuta y se devuelve mensaje de error didactico.

## 8. Funcionalidad por modulo

### 8.1 Secuencial

Incluye operaciones de insercion, eliminacion, busqueda y limpieza para:

- Pila
- Cola
- Cola de prioridad
- Lista enlazada
- Lista circular
- Sublista

### 8.2 Jerarquico

Estructuras:

- ABB
- AVL
- Rojo-Negro
- Monticulo binario

Puntos visuales:

- AVL muestra `balance_factor` por nodo.
- Rojo-Negro renderiza color por nodo (`RED`/`BLACK`).
- Monticulo muestra arreglo y arbol sincronizados.

### 8.3 Grafos

Permite:

- crear grafo dirigido o no dirigido,
- insertar/eliminar vertices y aristas con peso,
- listar vertices/aristas/vecinos,
- ejecutar BFS, DFS, Dijkstra, Bellman-Ford, Prim y Kruskal.

Recomendaciones:

- Prim y Kruskal solo aplican a grafos no dirigidos.
- Dijkstra no acepta pesos negativos; para ese caso usar Bellman-Ford.
- Usa el flujo visual 1) tipo de grafo, 2) construir/editar, 3) ejecutar y depurar paso a paso.
- Si desactivas la interpretacion paso a paso, `Reproducir` aplica directamente el resultado final del algoritmo.

### 8.4 Hash

Permite:

- crear tabla con capacidad inicial,
- insertar/actualizar (`key`, `value`),
- buscar, verificar existencia y eliminar claves,
- listar claves/valores/items,
- ver metricas (`size`, `capacity`, `load_factor`) y colisiones.

## 9. Solucion de problemas

### `ERR_CONNECTION_REFUSED`

1. Confirmar que la consola del servidor siga abierta.
2. Validar URL: `http://127.0.0.1:5050/`.
3. Reiniciar con `.\start_local.bat`.
4. Si persiste, usar:

```powershell
.\run_server_debug.bat
```

### Puerto ocupado

Si `5050` esta ocupado, cerrar procesos Python en ejecucion y volver a iniciar.

## 10. Ejecutar pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
