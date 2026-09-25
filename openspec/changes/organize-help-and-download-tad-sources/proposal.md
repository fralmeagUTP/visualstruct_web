# Propuesta: organizar Ayuda y descargar fuentes C de los TAD

## Why

La Ayuda y el Manual describen controles de versiones anteriores en varios módulos y no dan acceso directo al código C completo que respalda cada TAD. Esto dificulta que el estudiante pase de la explicación y visualización a la lectura o compilación del material fuente.

## What Changes

- Reorganizar el Manual de uso y las cinco portadas de Ayuda alrededor del flujo actual: elegir módulo, preparar datos, ejecutar o recorrer por pasos, leer código/resultado y consultar material fuente.
- Añadir a la ayuda específica de cada TAD una tarjeta accesible para descargar el `.c` canónico completo y su `.h` asociado.
- Atender las seis estructuras secuenciales, los cuatro TAD jerárquicos, Grafo, Tabla Hash y Ordenamiento.
- Exponer las descargas exclusivamente desde una lista permitida de archivos en `docs/tads_C`; no se aceptarán rutas de archivo provenientes de la URL.
- Informar dependencias reales: el TAD Grafo requiere también el TAD Cola para compilar los recorridos que usan una cola.

## Out of Scope

- Modificar algoritmos, trazas, datos de sesión o las pantallas de visualización.
- Presentar un fragmento de operación como si fuera un programa C completo.
- Empaquetar ejecutables, crear un ZIP o descargar archivos arbitrarios del servidor.

## Success Criteria

Cada ayuda específica enlaza al `.c` canónico del TAD que se está estudiando, ofrece su encabezado y aclara dependencias. El Manual y las portadas de Ayuda describen el flujo vigente sin depender de etiquetas de controles obsoletas.
