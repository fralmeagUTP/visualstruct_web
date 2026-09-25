# Diseño: experiencia compacta para Tabla Hash

## Flujo de pantalla

```
1. Preparar y controlar la ejecución
   operación + entradas + Ejecutar operación + Paso a paso [Anterior | Siguiente]
2. Visualizar y ejecutar       3. Relacionar con código C
   tabla, minimapa, filtros         funciones arriba y código debajo
4. Comprender (plegable)
5. Resultados de la ejecución (plegable)
```

Ejecutar operación aplica una operación nueva o completa la traza a medio recorrer; Paso a paso revela navegación contextual. Filtros de buckets y direcciones sólo cambian presentación, nunca tabla, historial ni posición de traza.

## Contrato didáctico por operación

| Operación | Estado y transición visual requerida |
|---|---|
| Crear/destruir/limpiar | capacidad, arreglo `buckets`, inicialización a `NULL`, liberación de nodos/arreglo y estado final |
| Insertar | `h(k)`, residuo C y normalización, bucket, recorrido, actualización o creación, `malloc`, campos y enlace final |
| Buscar/contiene | bucket, comparaciones y nodos visitados sin mutar enlaces |
| Eliminar | recorrido, anterior/actual, bypass, `free` y cadena final |
| Listas/estadísticas | consulta sin cambios; cantidad, capacidad, factor de carga, colisiones y longitud máxima reales |

Una colisión se representa como cadena en el bucket correcto; `NULL`, direcciones, nodo nuevo o liberado sólo aparecen cuando el frame los justifica.

### Frames permitidos

Cada instrucción interpretada entrega un frame de esquema `hash-pedagogical-frame/v1` con: origen C (`source`), cálculo y normalización (`hash`), condición ejecutada, variables, punteros, cadena examinada, distribución/costo, transición de memoria, estados antes/después e invariante. Las consultas sólo pueden resaltar bucket, cadena y comparaciones; insertar puede reflejar `malloc`, inicialización y enlace; eliminar puede reflejar `anterior`/`actual`, bypass y `free`; limpiar y destruir pueden reflejar liberación de nodos o del arreglo. Ningún frame debe inventar `rehash`, resize, punteros o ramas que la instrucción C no ejecutó.

## Código, overflow y resultados

Código usa patrón vertical: checkbox junto al título, funciones arriba y bloque C debajo a ancho completo. Cadenas extensas se desplazan sólo dentro de su bucket; minimapa y tabla no provocan scroll horizontal global. Resultados agrupa consola, historial, exportaciones y TAD estático.

## Responsive y accesibilidad

- En escritorio tabla y código se muestran lado a lado; en pantalla estrecha las pestañas existentes conservan la traza.
- Buckets y tarjetas usan `min-width: 0`; campos o direcciones largas se ajustan o desplazan sólo dentro de su carril.
- Colisión, creación, actualización y liberación se nombran además de usar color.
