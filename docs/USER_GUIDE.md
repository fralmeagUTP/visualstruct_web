# Manual de Usuario

Ultima actualizacion: **2026-05-12**.

## 1. Objetivo

El Visualizador Web de Estructuras de Datos permite practicar TAD mediante:

- operaciones interactivas,
- visualizacion del estado interno,
- apoyo didactico con codigo C real o pseudocodigo.

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

En los paneles de simulacion se usa el texto `Ejecucion paso a paso` y los controles se muestran asi:

- fila superior: `Reproducir`, `Reiniciar`.
- fila inferior: `Anterior paso`, `Siguiente paso`.

Comportamiento esperado:

- `Reproducir`: ejecuta la traza completa automaticamente.
- `Anterior paso`: retrocede una linea/paso en la traza.
- `Siguiente paso`: avanza una linea/paso en la traza.
- `Reiniciar`: limpia el estado de la estructura actual.

## 6. Modo interprete C

Hay cobertura C para:

- Secuenciales (`stack`, `queue`, `priority_queue`, `linked_list`, `circular_list`, `sublist`)
- Jerarquicas (`abb`, `avl`, `red_black`, `binary_heap`)
- Grafos (`graph`)

Cuando aplica:

- `Estructura del TAD` muestra el `record` C.
- `Codigo C: <Operacion>` muestra funciones C por operacion.
- El historial se presenta como programa principal (`main`) coherente con la sesion.

Para `hash_table` se usa principalmente pseudocodigo didactico.

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
