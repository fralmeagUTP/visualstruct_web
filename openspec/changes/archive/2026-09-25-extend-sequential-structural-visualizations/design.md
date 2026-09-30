# Diseño: laboratorio secuencial con dos modos visuales

## Patrón de pantalla compartido

Se conserva el patrón aprobado de Pila para cada estructura:

```
1. Preparar y controlar la ejecución
   operación + entradas + Ejecutar operación + Paso a paso

2. Visualizar y ejecutar             3. Relacionar con código C
   [Vista actual | Nodos y punteros]    selector de función
   estado / diagrama estructural         código resaltado

4. Comprender (plegable)
5. Resultados de la ejecución (plegable)
   consola C + seguimiento + TAD abierto + exportaciones
```

No se crea otra fila de pestañas. En móvil se conserva el mecanismo responsive
ya existente para alternar el área principal, mientras el conmutador de modo
visual permanece dentro de la etapa 2.

## Estado y sincronización

Ambos modos reciben el mismo `visual_state` canónico. La vista estructural no
reconstruye ni muta el TAD: transforma el estado y los metadatos de la traza en
una representación didáctica. Cuando una operación dispone de frames de
simulación, estos aportan temporalmente `aux`, nodo pendiente, nodo retirado,
enlace y liberación; al final se presenta exactamente el estado final recibido
del backend. Para operaciones no mutantes, la vista debe resaltar el recorrido
sin inventar cambios de puntero.

El selector de vista guarda solamente la preferencia de presentación por
estructura en la sesión del navegador; no forma parte del historial ni altera
la traza.

## Diagramas por estructura

| Módulo | Referencias y campos | Reglas visuales durante la traza |
|---|---|---|
| Cola | `delante`, `atras`; `nro`, `sgte` | creación de `aux`, enlace desde atrás, caso primera/última extracción y `NULL` en cola vacía |
| Cola de prioridad | `delante`, `atras`; `valor`, `prioridad`, `sgte` | recorrido para elegir prioridad, estabilidad en empates y desconexión del objetivo |
| Lista enlazada | `HEAD`; `nro`, `sgte` | recorrido `actual`/`anterior`, inserción por posición, bypass de enlaces y `free` |
| Lista circular | `HEAD`, `TAIL`; `nro`, `sgte` | el último enlace se dibuja como `TAIL → HEAD`; las operaciones no deben mostrar `NULL` como cierre de la cadena |
| Sublista | `HEAD` de padres, `hijos`; campos de padre/hijo y enlaces de rama | resaltar solo la rama seleccionada, manteniendo las demás sin cambios |

## Matriz operativa y contrato de frames

Esta matriz completa el contrato documental de cada operación visible. Un
**inicio** es el estado canónico que debe entregarse a ambos modos de vista;
los **frames** son los únicos cambios temporales que la representación puede
mostrar. Una consulta no crea ni libera nodos.

| TAD y operaciones | Inicio e invariantes a exponer | Frames estructurales y campos C |
|---|---|---|
| **Cola**: `encolar` | Vacía: `delante = atras = NULL`; no vacía: ambos extremos alcanzables y `atras->sgte = NULL`. | Crear `aux { nro, sgte = NULL }`; en cola vacía asignar ambos extremos a `aux`; en otro caso `atras->sgte = aux`, después `atras = aux`. Mostrar `nro`, `sgte`, `delante`, `atras`, `aux` y `NULL`. |
| **Cola**: `desencolar` | La salida corresponde a `delante`; una cola unitaria obliga a anular ambos extremos. | `aux = delante`; `delante = delante->sgte`; si queda vacía, `atras = NULL`; nodo retirado y `free(aux)`. |
| **Cola**: `frente`, `final` y `limpiar` | Las consultas no mutan. Limpiar termina con ambos extremos `NULL`. | Consulta: resaltar respectivamente el primer o último nodo. Limpiar: recorrido y liberación ordenada de cada nodo, luego extremos `NULL`. |
| **Cola de prioridad**: `encolar` | La cadena conserva orden de llegada; prioridad y selección son conceptos distintos. | Crear `aux { valor, prioridad, sgte }`; recorrer candidatos de prioridad sin reordenar físicamente la llegada salvo que el backend canónico lo indique. Mostrar candidato, comparación, desempate estable y enlace final. |
| **Cola de prioridad**: `desencolar`, `frente`, `limpiar` | El frente lógico es el primer candidato de prioridad mínima; los empates conservan llegada. | Desencolar resalta recorrido de selección, desconecta/libera solo el candidato elegido. `frente` resalta sin mutar. Limpiar libera todos los nodos y deja `delante/atras = NULL` si esos extremos forman parte del estado adaptado. |
| **Lista enlazada**: `insertar_inicio`, `insertar_final`, `insertar_elemento` | `HEAD` alcanza todos los nodos una vez; el último `sgte = NULL`. La posición visible es base 1. | Crear `aux { nro, sgte }`; usar `actual` y, cuando aplique, `anterior`; enlazar primero `aux->sgte`, luego el puntero de entrada. Inicio cambia `HEAD`; final sigue hasta `NULL`; por posición muestra guarda y recorrido. |
| **Lista enlazada**: `buscar_elemento`, `mostrar` | No hay cambio de enlaces ni de tamaño. | Resaltar `actual` y las posiciones visitadas, incluida salida por `NULL`; reproducir sólo las salidas C correspondientes. |
| **Lista enlazada**: `eliminar_elemento`, `eliminar_repetidos`, `limpiar` | Tras cada eliminación, todos los nodos restantes siguen alcanzables desde `HEAD`. | Mostrar `anterior`, `actual`, bypass `anterior->sgte = actual->sgte`, nodo desconectado y `free`. Para limpiar, repetir hasta `HEAD = NULL`; actualizar cola si el adaptador la expone. |
| **Lista circular**: `insertar_inicio`, `insertar_final` | Vacía: `HEAD = TAIL = NULL`; no vacía: `TAIL->sgte = HEAD`. | Crear `aux`; mantener el cierre circular en cada frame. Inicio reasigna `HEAD` y luego `TAIL->sgte`; final enlaza el antiguo `TAIL`, mueve `TAIL` y restituye `TAIL->sgte = HEAD`. Nunca dibujar el cierre como `NULL`. |
| **Lista circular**: `eliminar_inicio`, `eliminar_primero` | El recorrido termina al volver a `HEAD`; caso unitario anula ambos extremos. | Resaltar nodo objetivo, conservar su siguiente antes de desconectarlo, actualizar `HEAD` o el `sgte` anterior y siempre restaurar el cierre. Mostrar nodo liberado sólo durante el frame de `free`. |
| **Lista circular**: `buscar_posiciones`, `invertir`, `limpiar` | Buscar completa como máximo una vuelta y no muta. | Buscar resalta una vuelta; invertir muestra reasignación de cada `sgte` y el intercambio `HEAD/TAIL`; limpiar libera una vuelta completa y concluye con `HEAD = TAIL = NULL`. |
| **Sublista**: `insertar_padre`, `eliminar_padre` | `HEAD` apunta a `P1` o `NULL`; cada padre tiene `sgte padre` y una rama de hijos independiente. | Insertar crea padre con sublista vacía. Eliminar resalta sólo ese padre, recorre/libera primero sus hijos y después el padre; ninguna otra rama cambia. |
| **Sublista**: `insertar_hijo`, `eliminar_hijo`, `hijos_de` | Cada hijo pertenece a un único padre; las ramas no seleccionadas permanecen sin cambios. | Buscar primero el padre; después crear/recorrer/desconectar un hijo `Hn.m { HIJO, sgte }`. `hijos_de` resalta el recorrido de esa rama sin mutarla. Los rótulos deben preservar `PADRE`, `sgte padre`, `hijos`, `HIJO`, `sgte` y `NULL`. |
| **Sublista**: `limpiar` | El resultado es `HEAD = NULL`. | Liberar una rama de hijos por vez y luego su padre; el estado final no conserva referencias de ramas retiradas. |

### Geometría obligatoria de Sublista

La geometría no es semántica del TAD, pero es necesaria para no falsear sus
relaciones. La fila del padre contiene sólo `PADRE` y `sgte padre`, con ancho
compacto y completo dentro de la tarjeta. La etiqueta `hijos → Hn.1/NULL`
inicia el carril de esa rama. Los carriles de hijos conservan sus nodos
`HIJO`/`sgte` y tienen desplazamiento horizontal independiente; el lienzo
general no debe adquirir desplazamiento horizontal por la rama más larga. Las
ramas de padres se apilan verticalmente con separación suficiente y el modo
móvil conserva la misma propiedad.

## Resultados y TAD

La implementación reutiliza el patrón de panel plegable de Comprender. El
botón agrega o quita la clase de panel colapsado sobre la etapa completa,
nunca sobre bloques individuales. Así, al ocultar desaparecen Consola C,
seguimiento, estructura del TAD y exportaciones; el título y el botón se
mantienen accesibles. Dentro de una etapa abierta, el TAD se renderiza como una
sección estática con encabezado, no como `details`.

## Accesibilidad y responsive

- El selector de modo usa botones con `aria-pressed` y una etiqueta de grupo.
- Los nodos exponen etiquetas textuales para punteros, campos y `NULL`; el
  color de un frame no es el único medio de comunicar pendiente, activo o
  liberado.
- El diagrama puede desplazarse horizontalmente solo cuando no quepa; no
  comprime los nombres de campos ni oculta los extremos.
- La vista actual sigue siendo la predeterminada al visitar una estructura por
  primera vez.
