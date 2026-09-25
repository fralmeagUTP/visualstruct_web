# Tareas

## 1. Contrato y alcance

- [x] 1.1 Inventariar los controles y rutas que ejecutan o navegan trazas en las seis estructuras secuenciales.
- [x] 1.2 Documentar la máquina de estados de ejecución, preparación y reproducción, incluidos modo rápido, paso a paso, errores y reinicio.
- [x] 1.3 Confirmar que el contrato no modifica la semántica C ni los adapters de cada TAD.

## 2. Interfaz y accesibilidad

- [x] 2.1 Añadir **Ejecutar operación** a la plantilla compartida de estructuras secuenciales.
- [x] 2.2 Reorganizar y etiquetar los controles para distinguir ejecutar, preparar, reproducir y navegación.
- [x] 2.3 Actualizar estados habilitado/deshabilitado, foco, títulos y mensajes accesibles cuando no exista traza preparada.
- [x] 2.4 Conservar la disposición utilizable en escritorio y móvil.

## 3. Controlador de ejecución

- [x] 3.1 Implementar una ruta de cliente exclusiva para **Ejecutar operación** que siempre cree una nueva solicitud al backend.
- [x] 3.2 Hacer que el envío del formulario use esa misma ruta de ejecución real.
- [x] 3.3 Versionar o identificar cada traza por ejecución para impedir que entradas iguales reutilicen una traza previa.
- [x] 3.4 Mantener modo rápido como aplicación de resultado final y modo paso a paso como carga de traza nueva.
- [x] 3.5 Conservar intacto el historial para consultas no mutantes y respuestas fallidas.

## 4. Reproducción sin mutación

- [x] 4.1 Cambiar Preparar para que solo posicione la traza compatible al inicio.
- [x] 4.2 Cambiar Reproducir para que solo anime una traza preparada, sin solicitudes de operación.
- [x] 4.3 Restringir Inicio, Anterior, Siguiente, Final y Repetir a la navegación visual de la traza cargada.
- [x] 4.4 Invalidar de forma segura la traza al cambiar entrada, operación o reiniciar la estructura.
- [x] 4.5 Presentar una explicación didáctica clara cuando se intente reproducir sin una ejecución preparada.

## 5. Regresión funcional por TAD

- [x] 5.1 Pila: verificar dos `apilar` consecutivos con el mismo valor y dos `desapilar` consecutivos contra el estado real.
- [x] 5.2 Cola y cola de prioridad: verificar inserciones repetidas, extracciones sucesivas y conservación de FIFO/prioridad.
- [x] 5.3 Lista enlazada y circular: verificar inserciones/eliminaciones repetidas, posiciones y circularidad.
- [x] 5.4 Sublista: verificar inserciones repetidas de padres/hijos y eliminaciones sucesivas sobre el estado actual.
- [x] 5.5 Verificar operaciones de consulta y errores sin mutación de historial ni reproducción accidental.

## 6. Pruebas y cierre

- [x] 6.1 Añadir pruebas unitarias del controlador para asegurar que Reproducir y navegación no emiten `POST /operate`.
- [x] 6.2 Añadir pruebas E2E para ejecutar-preparar-reproducir y para ejecutar repetidamente la misma entrada.
- [x] 6.3 Validar equivalencia entre el estado final paso a paso y modo rápido para cada estructura.
- [x] 6.4 Ejecutar la suite relevante, revisar accesibilidad y documentar los resultados.
- [x] 6.5 Actualizar las especificaciones afectadas y validar el cambio OpenSpec.
- [x] 6.6 Mostrar el estado canónico final inmediatamente después de Ejecutar, sin confundirlo con el primer frame de la traza.
