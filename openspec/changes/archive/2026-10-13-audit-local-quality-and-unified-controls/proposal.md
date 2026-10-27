> Implementación autorizada por el usuario el 2026-09-30. La identificación de borrador y el gate siguientes conservan el contexto de revisión inicial; estado actual: auditoría en curso, sin cierre QA.

# Auditoría local integral y controles uniformes

**Estado: BORRADOR — pendiente de revisión y aprobación del usuario.**
Proyecto destino autorizado: `D:\MisProyectos\Web_VisualEstruct`, revisión local `ba53ba7c0bcebaf7a4938328ebf4c863f19eadab`, Desktop-FM, 2026-09-30. Inspección inicial: checkout de tarea `83c3c96fc17cabed85fddaf95e39b46bb19ff80b`; su evidencia histórica no sustituye validación pendiente del destino. Las 108 piezas OpenSpec preexistentes coinciden textualmente normalizando finales de línea/BOM. Se preservan cambios locales de QA.

## Why
Una suite verde no demuestra toda la funcionalidad ni la fidelidad de cada paso C. Se necesita evidencia trazable de operaciones, controles, documentación y archivos descargados. Pila es la referencia de presentación. Su plantilla declara once botones en el bloque de ejecución y CSS con `overflow-x:auto` en el menú; el conteo NO significa que estén simultáneamente visibles. La captura de Pila revisada por el agente principal muestra cuatro controles. Las observaciones estáticas y capturas aportadas no son validación dinámica del checkout.

## What Changes
1. Auditar todos los módulos y opciones reales mediante una matriz de requisitos, casos y evidencia.
2. Comparar C ejecutado, implementación Python, traza, consola y visualización, incluidos estados intermedios. Auditar sección 2, Visualizar y ejecutar, por instrucción en vista individual y nodos enlazados, adelante/atrás, con estado antes/después y resaltado inequívoco. Explicar instrucciones sin efecto estructural sin fabricar mutaciones.
3. Auditar Doxygen de `.c/.h` efectivamente entregados por la aplicación y la exactitud del manual y ayudas.
4. Uniformar el menú superior y eliminar su desplazamiento horizontal sin recortar enlaces ni ocultar información inaccesiblemente.
5. Simplificar cada TAD integrando captura de datos y controles según operación, estado y modo. Pila aporta cuatro controles visibles de referencia: **Ejecutar operación**, **Cerrar paso a paso**, **Paso anterior** y **Siguiente paso**. Mantener el control de activar/cerrar modo paso a paso y mostrar navegación solo cuando esté activo. Otros TAD pueden necesitar cinco controles u otros propios: se justifican y prueban, sin imponer un número fijo ni eliminar botones por su conteo en fuente.
6. Reconciliar compromisos OpenSpec abiertos y archivados, preservando semántica y contenido pedagógico vigente.

## Scope
13 estructuras: stack, queue, priority_queue, linked_list, circular_list, sublist, abb, avl, red_black, binary_heap, graph, hash_table y sorting_array. Todos los algoritmos y operaciones registrados, rutas, ayudas, manual, descargas C/H, exportaciones, sesiones, historial, reset, comparaciones y opciones de aprendizaje. Inventario generado desde código real; ninguna opción se considera cubierta por mera pertenencia a un módulo.

## Approval gate and phases
Ahora: inspección de solo lectura y redacción. Después de aprobación explícita: iniciar servidor local en Desktop-FM, comprobar HTTP/puerto y comunicar URL accesible desde su navegador; identificar capacidad visual; establecer línea base; auditar; implementar los cambios UI/documentales aprobados; verificar revisión final y entregar informe. No se ha iniciado servidor ni ejecutado validación funcional en esta fase.

## Out of Scope
Hostinger, despliegue, merge, push, cambios de algoritmos/contratos no aprobados, borrar trabajo previo o debilitar pruebas. Defectos semánticos mayores se documentarán y consultarán antes de modificar su diseño.

## Success Criteria
Inventario completo sin filas silenciosamente omitidas; evidencia por caso; límites explícitos; diferencias C de severidad alta/crítica resueltas dentro de autorización o identificadas como bloqueantes. Menú sin scroll horizontal en todas las estructuras; modo rápido oculta navegación; modo paso a paso conserva equivalencia final y navegación sin remutaciones. Doxygen y manual coherentes con bytes descargados. Suite final y cobertura con resultados reales y comparación de base, sin convertir porcentajes en garantía de corrección total.

## Assumptions awaiting review
- Desktop objetivo 1366×768 y 1920×1080; tableta 768×1024 y móvil 390×844. El menú debe envolver naturalmente sus enlaces y herramientas en filas accesibles a anchos estrechos, conservando orden y estilo uniforme; nunca scroll horizontal, clipping ni simple ocultación de la barra.
- Scroll interno de código largo/tablas se permite cuando aporta acceso al contenido; el requisito elimina scroll indebido del menú y desbordamiento global. No se elimina scroll necesario de toda página móvil.
- Ejecutar en paso a paso prepara la traza al inicio; los pasos son manuales. Desactivar el modo lleva al resultado final de la misma ejecución sin nueva mutación. Activarlo de nuevo recupera esa traza si existe.
- Mostrar únicamente controles pertinentes a operación/estado/modo; conservar capacidades necesarias, con divulgación progresiva cuando corresponda. Excepciones específicas de cada TAD se documentan y verifican; no se exige exactamente cuatro botones en todas las pantallas.
- Las tres referencias fueron inspeccionadas visualmente por el agente principal: la primera muestra barra horizontal y extremos recortados; la segunda, navegación en negrita con reflujo natural, Manual en otra fila y checkbox a la derecha sin barra; la tercera, preparación y cuatro controles de Pila con pasos deshabilitados sin traza. Son evidencia aportada, no QA dinámico del checkout. Las dos primeras tienen anchos distintos: no se atribuye causalidad solo a su comparación.
