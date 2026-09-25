# Propuesta: extender la experiencia aprobada de Pila a las estructuras secuenciales

## Why

Pila ya ofrece dos lecturas complementarias del mismo estado: la vista visual
existente y una vista de nodos enlazados que hace explícitos los campos, los
punteros, `NULL` y los nodos auxiliares de cada paso. Las demás pantallas
secuenciales conservan sus visualizaciones actuales, pero no tienen el mismo
contraste entre resultado abstracto y memoria enlazada ni el mismo espacio de
trabajo compacto.

Esta propuesta extiende el patrón aprobado sin sustituir la vista existente ni
cambiar la semántica del TAD, los algoritmos C, las rutas o la traza canónica.

## Módulos reales incluidos

El inventario de adaptadores del proyecto confirma estos módulos hermanos de
Pila:

| Módulo | Operaciones públicas visibles a cubrir | Modelo estructural nuevo |
|---|---|---|
| Cola (`queue`) | `encolar`, `desencolar`, `limpiar` | `delante`, `atras`, nodos `nro`/`sgte` |
| Cola de prioridad (`priority_queue`) | `encolar`, `desencolar`, `frente`, `limpiar` | `delante`, `atras`, nodos `valor`/`prioridad`/`sgte` |
| Lista enlazada (`linked_list`) | inserciones, eliminaciones, búsquedas, posiciones y `limpiar` expuestos por el selector | `HEAD`, nodos `nro`/`sgte`, auxiliares de recorrido y enlace |
| Lista circular (`circular_list`) | insertar inicio/final, eliminar inicio/primero, buscar, invertir y `limpiar` | `HEAD`, `TAIL`, nodos `nro`/`sgte` y cierre `TAIL → HEAD` |
| Sublista (`sublist`) | insertar/eliminar padre o hijo, `hijos_de`, `limpiar` | cadena de padres y cadenas de hijos, con punteros de rama |

No se incluye un módulo Deque: no existe un adaptador ni ruta secuencial para
esa estructura en este repositorio.

## What Changes

- Conservar, sin regresiones, la vista visual que ya existe en cada módulo y
  añadir un conmutador visible entre **Vista actual** y **Nodos y punteros**.
- Implementar la segunda vista con los campos y referencias propios de cada
  TAD; debe hacer explícitos los punteros extremos, enlaces, nodos auxiliares,
  nodos retirados y `NULL` o circularidad según corresponda.
- Conectar ambas vistas al mismo estado canónico y a la traza existente para
  que ejecutar, avanzar, retroceder y completar muestren la misma operación.
- Replicar la presentación aprobada de Pila: preparar y control simplificado,
  visualización y código C simultáneos en escritorio, sin agregar una fila de
  pestañas nueva.
- Normalizar **Relacionar con código C**: checkbox junto a su etiqueta,
  selector de funciones encima del código y ancho útil de lectura.
- Aplicar a todas las pantallas secuenciales la etapa **Resultados de la
  ejecución** plegable: el encabezado y botón Ocultar/Mostrar quedan visibles;
  Consola C, seguimiento, exportaciones y TAD se ocultan o restauran juntos.
- Mostrar **Estructura del TAD** como bloque estático abierto dentro de la
  etapa de resultados, sin `details/summary` ni flecha individual.
- Para Sublista, mantener el diagrama general dentro de su tarjeta: el nodo
  padre se muestra completo y compacto con `PADRE` y `sgte padre`; la
  referencia `hijos` inicia su propia rama. Cada rama de hijos puede
  desplazarse horizontalmente de forma independiente, sin ensanchar el
  diagrama general ni invadir el panel de código C.

## Out of Scope

- Crear un Deque u otro TAD que no exista en el producto.
- Cambiar operaciones, invariantes, código C, endpoints, historial o formatos
  de traza del backend.
- Extender este diseño a árboles, montículos, grafos, hash u ordenamiento.
- Eliminar la visualización actual de cualquiera de las estructuras.

## Success Criteria

En cada módulo incluido, una persona puede seleccionar cualquiera de las
operaciones visibles, ver simultáneamente el código C y el estado, alternar
entre ambos modos visuales sin perder la operación actual, y recorrer una traza
en la que el diagrama estructural cambia solo conforme al frame ejecutado. Los
punteros y campos mostrados representan el estado canónico y la etapa de
resultados se comporta de forma idéntica a Pila.
