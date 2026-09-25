# Diseño: ciclo de ejecución y reproducción de TAD secuenciales

## Estados de la interfaz

Cada página secuencial mantiene dos conceptos independientes:

1. **Estado canónico del TAD:** el estado persistido en sesión y modificado solo
   por una respuesta exitosa de `POST /operate`.
2. **Traza preparada:** la representación efímera de una única ejecución exitosa,
   con cursor navegable y una clave derivada de estructura, operación, entrada y
   revisión de ejecución.

La revisión de ejecución evita que una traza de una operación anterior se tome
por una nueva operación solo porque tienen el mismo valor de entrada.

## Transiciones

| Acción | Llamada mutante | Estado canónico | Traza/cursor |
|---|---:|---|---|
| Ejecutar operación, modo rápido | Sí, una | pasa al resultado final | no navega traza |
| Ejecutar operación, paso a paso | Sí, una | registra la operación | carga una traza nueva al inicio |
| Preparar | No | sin cambio | restablece el cursor al inicio |
| Reproducir | No | sin cambio | anima desde el cursor o inicio preparado |
| Anterior/Siguiente/Inicio/Final/Repetir | No | sin cambio | navega únicamente la traza cargada |
| Reiniciar estructura | Sí, endpoint de reset | vacía el TAD | invalida la traza |

## Reglas de interacción

- El envío normal del formulario es equivalente a **Ejecutar operación**; no es
  un atajo para reproducir una ejecución previa.
- Si no hay traza preparada, los controles de Preparar, Reproducir y navegación
  se deshabilitan o informan que primero debe ejecutarse la operación en modo
  paso a paso.
- Al cambiar estructura, operación o datos, la traza deja de ser compatible y
  queda invalidada. Esto nunca borra ni revierte el estado canónico.
- Una consulta no mutante puede ejecutarse como nueva operación, pero no cambia
  el historial. Aun así, sus controles de reproducción siguen siendo solo
  visuales.
- Las respuestas con error no cargan una traza nueva ni alteran el cursor de la
  última ejecución válida.

## Cobertura de estructuras

El mismo controlador se aplica a `stack`, `queue`, `priority_queue`,
`linked_list`, `circular_list` y `sublist`; las diferencias de formulario u
operación quedan encapsuladas en los metadatos del adapter, no en el contrato de
controles.
