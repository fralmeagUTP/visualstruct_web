# Tareas

## 1. Contrato e inventario

- [x] 1.1 Confirmar rutas, adaptadores y operaciones visibles de Cola, Cola de prioridad, Lista enlazada, Lista circular y Sublista.
- [x] 1.2 Documentar para cada operación el estado inicial, frames relevantes, campos C y punteros que debe exponer la vista estructural.
- [x] 1.3 Registrar explícitamente que Deque no forma parte del alcance actual por no existir como módulo del repositorio.

## 2. Armazón compartido de interfaz

- [x] 2.1 Generalizar, sin alterar Pila, el selector accesible Vista actual / Nodos y punteros para los cinco módulos restantes.
- [x] 2.2 Llevar el patrón de disposición y controles simplificados de Pila a los módulos hermanos, conservando sus identificadores y operaciones.
- [x] 2.3 Ajustar el área Relacionar con código C: etiqueta/checkbox, índice de funciones sobre el código y ancho de lectura.
- [x] 2.4 Hacer Resultados de la ejecución plegable en cada módulo, con la etapa completa como única unidad de ocultamiento.
- [x] 2.5 Sustituir el disclosure interno del TAD por un bloque estático siempre abierto dentro de Resultados.

## 3. Vista estructural por TAD

- [x] 3.1 Implementar Cola: nodos `nro`/`sgte`, `delante`, `atras`, `NULL`, `aux` y transiciones de encolar/desencolar/limpiar.
- [x] 3.2 Implementar Cola de prioridad: `valor`, `prioridad`, `sgte`, recorrido de selección, estabilidad y liberación del nodo atendido.
- [x] 3.3 Implementar Lista enlazada: `HEAD`, `nro`, `sgte`, punteros de recorrido, inserciones, eliminaciones, búsquedas y limpieza.
- [x] 3.4 Implementar Lista circular: `HEAD`, `TAIL`, enlace circular, recorridos, inserciones, eliminaciones, inversión y limpieza.
- [x] 3.5 Implementar Sublista: cadena de padres, cadenas de hijos, referencias de rama y aislamiento de cambios por padre.

## 4. Integración con traza

- [x] 4.1 Mapear cada frame de operaciones mutantes a creación, enlace, reasignación, desconexión o liberación visibles.
- [x] 4.2 Mapear operaciones de consulta a recorrido/resaltado sin mutación visual falsa.
- [x] 4.3 Garantizar que anterior, siguiente, ejecutar hasta el final y modo rápido llegan al mismo estado canónico en los dos modos.
- [x] 4.4 Preservar la preferencia de modo por módulo sin persistirla en el historial del TAD.

## 5. Revisión visual y accesibilidad

- [x] 5.1 Revisar en escritorio, tableta y móvil ambos modos para cada módulo incluido.
- [x] 5.2 Revisar etiquetas de punteros/campos, contraste, foco de botones y lectura cuando el diagrama exceda el ancho disponible.
- [x] 5.3 Comprobar manualmente una inserción, una extracción/eliminación, una consulta y limpiar por módulo; verificar la consola, historial y TAD dentro de Resultados.
- [x] 5.4 Confirmar que ocultar Resultados no deja Consola, resumen o TAD visibles por fuera de la etapa y que Mostrar los restaura juntos.

## Evidencia de cierre

- Revisión manual en navegador local: Cola, Cola de prioridad, Lista enlazada,
  Lista circular y Sublista cargan sus dos modos sin error; se verificaron los
  campos `NRO`/`sgte`, `VALOR`/`PRIORIDAD`/`sgte`, `HEAD`, extremos de cola y
  el cierre circular.
- Se recorrió una traza con Siguiente/Paso anterior, se comprobó que el último
  paso usa el snapshot canónico y se revisó la ejecución rápida.
- En Lista circular se abrió y cerró Resultados de la ejecución: Consola C,
  Seguimiento y Estructura del TAD aparecieron y desaparecieron como unidad.
- La revisión responsive cubrió los breakpoints de escritorio, tableta y móvil;
  en Sublista se confirmó que el padre no genera scroll global y que sólo cada
  rama extensa de hijos desplaza horizontalmente su propio carril.
- No se ejecutaron pruebas automatizadas en este cierre; la evidencia anterior
  corresponde a verificación manual y revisión directa de la interfaz.
