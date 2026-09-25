# Propuesta: reorganizar el espacio de aprendizaje de Tabla Hash

## Why

La pantalla de Tabla Hash concentra reproducción, predicción, filtros, código, comparación de capacidades y resultados en siete bloques. Esto obliga a desplazarse para conectar función hash, bucket, cadena, memoria dinámica y código C.

Se propone aplicar la experiencia compacta de estructuras secuenciales sin alterar el encadenamiento separado, capacidad fija, operaciones ni traza.

## Inventario real incluido

El módulo tiene una estructura y ruta: `/hash/hash_table`; también expone operar, reiniciar y `/hash/compare-capacities`. Sus operaciones públicas son crear tabla, insertar/actualizar clave-valor con fallo opcional de `malloc`, buscar, verificar existencia, eliminar, listar claves/valores/items, estadísticas, limpiar y destruir.

La representación real usa claves/valores enteros, capacidad fija y encadenamiento separado; no existe resize ni rehash automático.

## What Changes

- Aplicar cinco etapas: Preparar/controlar, Visualizar/ejecutar, Código C, Comprender y Resultados.
- Reunir operación, entradas, Ejecutar operación y Paso a paso; revelar Anterior/Siguiente sólo durante una traza.
- Conservar minimapa, filtro de buckets y Direcciones y campos dentro de la visualización, sin separarlos del estado de la tabla.
- Mostrar en Comprender cálculo hash y normalización, bucket/cadena, punteros, costo, memoria, `malloc`/`free` e invariante.
- Usar funciones C arriba y código a ancho completo debajo; retirar de UI nivel, Ejemplo guiado, Predecir y Comparar capacidades sin eliminar endpoint.
- Reunir consola, historial, TAD y exportaciones en Resultados plegable; TAD estático al abrir.

## Out of Scope

- Cambiar estrategia de colisión, tipos, capacidad fija, política de actualización o semántica de `malloc`/`free`.
- Añadir open addressing, resize, rehash o nuevos tipos de hash.
- Eliminar `/hash/compare-capacities`.
- Añadir pruebas automatizadas.

## Success Criteria

Insertar, buscar o eliminar permite seguir simultáneamente función C, bucket y cadena afectados, salida de consola y frame didáctico, sin overflow global ni representación falsa de enlaces o memoria.
