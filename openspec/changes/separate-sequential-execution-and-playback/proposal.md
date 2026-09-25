# Propuesta: separar ejecución y reproducción en estructuras secuenciales

## Why

En el módulo de estructuras secuenciales, una misma acción de la interfaz puede
reutilizar una traza ya cargada en vez de iniciar una nueva operación contra el
estado actual. Esto es didácticamente incorrecto: al apilar dos veces el mismo
valor deben existir dos nodos, y al ejecutar `desapilar` repetidamente debe
retirarse un nodo real en cada ejecución. Reproducir una traza anterior no puede
simular una nueva mutación.

El problema afecta a Pila, Cola, Cola de Prioridad, Lista Enlazada, Lista
Circular y Sublista. Se necesita un contrato de interacción explícito que separe
la mutación del TAD de la navegación visual de una traza ya creada.

## What Changes

- Añadir el control **Ejecutar operación** a todas las páginas de estructuras
  secuenciales.
- Definir tres acciones con responsabilidades no solapadas:
  - **Ejecutar operación** siempre envía una nueva operación al backend contra
    el estado actual y obtiene su resultado o su traza.
  - **Preparar** posiciona al inicio la traza de la última ejecución compatible;
    nunca muta el TAD.
  - **Reproducir** anima exclusivamente una traza preparada; nunca llama al
    endpoint de operación ni altera historial, sesión o estado interno.
- Convertir Anterior, Siguiente, Inicio, Final y Repetir en navegación
  estrictamente visual de la traza preparada.
- Mantener el modo rápido: Ejecutar aplica el resultado final; en modo paso a
  paso deja disponible la traza para preparar y reproducir.
- Actualizar mensajes, estados deshabilitados y accesibilidad para explicar qué
  acción falta cuando no hay una traza disponible.
- Añadir pruebas de regresión para duplicados, operaciones repetidas, navegación
  y preservación del historial de las seis estructuras.

## Out of Scope

- Cambiar los algoritmos C o las operaciones públicas de los TAD.
- Cambiar el comportamiento de módulos jerárquicos, grafos, hash u ordenamiento.
- Persistir trazas entre sesiones del navegador.

## Success Criteria

Cada clic en **Ejecutar operación** representa exactamente una nueva llamada al
backend. Preparar, Reproducir y cualquier control de navegación no generan
llamadas mutantes. Una pila permite apilar valores duplicados en ejecuciones
sucesivas; las operaciones de extracción sucesivas consumen elementos distintos
del estado actual. Las seis estructuras presentan el mismo contrato y las pruebas
automatizadas demuestran que el historial y el estado final coinciden con la
cantidad de ejecuciones reales.
