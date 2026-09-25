# Tareas

## 1. Inventario y contrato

- [x] 1.1 Confirmar rutas/fases, operaciones públicas, algoritmos y endpoint de comparación del único módulo `graph`.
- [x] 1.2 Documentar estados, auxiliares e invariantes visibles para construcción, BFS, DFS, caminos mínimos y MST.

## 2. Espacio de trabajo común

- [x] 2.1 Reorganizar las cuatro fases en cinco etapas numeradas sin duplicados.
- [x] 2.2 Compactar tipo, operación/algoritmo, entradas y controles en Preparar y controlar.
- [x] 2.3 Implementar Ejecutar operación y Paso a paso con Anterior/Siguiente contextual.
- [x] 2.4 Mantener lienzo/leyenda y Código C simultáneos en escritorio; conservar alternativa responsive.
- [x] 2.5 Disponer el índice de funciones sobre Código C, mantener checkbox y eliminar scroll lateral global; cada línea C conserva su formato y usa scroll horizontal local cuando excede el ancho.

> Nota transversal: la regla se implementa en el componente compartido `didactic-code`; por ello también cubre paneles de código de estructuras secuenciales, jerárquicas, Hash, ordenamiento y guías, sin iniciar tareas funcionales de sus OpenSpec.

## 3. Paneles y pedagogía

- [x] 3.1 Retirar de la UI nivel, Ejemplo guiado, Predecir y Comparar sin tocar endpoints ni algoritmos.
- [x] 3.2 Hacer Comprender plegable y mostrar auxiliares/fuentes de evidencia por algoritmo.
- [x] 3.3 Hacer Resultados plegable como unidad y convertir TAD en contenido estático.
- [x] 3.4 Evitar overflow de tablas de vértices, distancias o conjuntos mediante tarjetas con ancho mínimo cero y scroll local.

## 4. QA manual

- [x] 4.1 Revisar visualmente Construcción, Recorridos, Camino mínimo y Expansión mínima.
- [x] 4.2 Ejecutar construcción, BFS/DFS, un camino mínimo y un MST; contrastar lienzo, código, consola y Comprender.
- [x] 4.3 Recorrer una traza por algoritmo y comprobar que Siguiente/Anterior y ejecución final conservan el estado canónico.
- [x] 4.4 Revisar escritorio, breakpoint responsive, plegado de Resultados y accesibilidad básica, sin pruebas automatizadas.
