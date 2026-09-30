# Tareas

## 1. Inventario y contrato de experiencia

- [x] 1.1 Confirmar rutas, adaptadores y operaciones públicas de ABB, AVL, Rojo-Negro y Montículo binario.
- [x] 1.2 Documentar el flujo común, la semántica de Ejecutar operación y Paso a paso, y la conservación de la traza canónica.
- [x] 1.3 Definir el contenido visual mínimo y los invariantes didácticos por estructura jerárquica.

## 2. Armazón común de interfaz

- [x] 2.1 Reorganizar `templates/hierarchical/structure.html` con cinco etapas numeradas sin duplicados.
- [x] 2.2 Unificar operación, entradas y control de ejecución en la primera etapa con controles visibles y compactos.
- [x] 2.3 Mantener Visualizar y ejecutar y Relacionar con código C legibles en paralelo en escritorio y mediante el patrón responsive existente en pantalla estrecha.
- [x] 2.4 Establecer Comprender y Resultados de la ejecución como paneles plegables accesibles.
- [x] 2.5 Hacer que consola C, historial, exportaciones y TAD se oculten/restauren juntos; dejar el TAD estático al abrir Resultados.

## 3. Simplificación de interacción

- [x] 3.1 Implementar Ejecutar operación y Paso a paso, revelando Anterior/Siguiente sólo en el recorrido activo.
- [x] 3.2 Retirar de las cuatro rutas los selectores o paneles visibles de nivel, Ejemplo guiado, Predecir y Comparar conceptos sin cambiar endpoints ni algoritmos.
- [x] 3.3 Garantizar que ocultar, mostrar o cambiar la vista responsive no muta el TAD ni reinicia la posición de traza.
- [x] 3.4 Ajustar etiquetas, foco y anuncios accesibles de botones, pestañas y paneles.

## 4. Visualización didáctica por tipo

- [x] 4.1 Revisar y ajustar ABB para explicar ruta de búsqueda, recorridos y casos de eliminación junto al código C.
- [x] 4.2 Revisar y ajustar AVL para exponer altura, factores de balance y rotaciones sin ocultar el árbol resultante.
- [x] 4.3 Revisar y ajustar Rojo-Negro para que colores, recoloreos, rotaciones e invariantes se expresen también con texto.
- [x] 4.4 Revisar y ajustar Montículo binario para sincronizar arreglo, árbol, índices y desplazamientos de subida/bajada.

## 5. QA visual manual

- [x] 5.1 Revisar manualmente carga, numeración, controles y paneles de ABB, AVL, Rojo-Negro y Montículo binario.
- [x] 5.2 En cada estructura, ejecutar una inserción y una operación característica; confirmar sincronía entre visualización, código C y consola.
- [x] 5.3 Recorrer manualmente una traza con Anterior/Siguiente y comprobar que Ejecutar operación la completa desde el frame actual.
- [x] 5.4 Comprobar plegado conjunto de Resultados y visibilidad estática del TAD en las cuatro rutas.
- [x] 5.5 Revisar el comportamiento de escritorio y el breakpoint responsive disponible, sin ejecutar ni añadir pruebas automatizadas.

## Evidencia de cierre

- Revisión manual local: ABB, AVL, Rojo-Negro y Montículo binario cargaron con
  las cinco etapas numeradas y sin los paneles retirados. Se comprobó ejecución
  directa en ABB, AVL, Rojo-Negro y Montículo; en ABB y Montículo se abrió el
  modo Paso a paso y se verificó el primer frame con Anterior/Siguiente.
- En Rojo-Negro se desplegó Resultados: consola C, historial, exportaciones y
  Estructura del TAD aparecieron dentro de la misma unidad, con el TAD estático.
- Se revisó la disposición de escritorio y el breakpoint responsive existente
  que alterna estructura y código sin alterar los controles. No se ejecutaron
  ni añadieron pruebas automatizadas, conforme a la preferencia del proyecto.
- Ajuste posterior de etapa 3: el selector de funciones C pasó a una franja
  vertical superior y el código ocupa el ancho completo bajo ella. En AVL se
  confirmó el checkbox de documentación y el índice; ABB, Rojo-Negro y
  Montículo binario cargaron el mismo patrón sin desplazamiento lateral global.
