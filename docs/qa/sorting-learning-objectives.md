# Objetivos de aprendizaje del módulo de ordenamiento

La fuente ejecutable de estos perfiles es `app/domain/sorting/pedagogy.py`. Cada algoritmo declara
un objetivo, conocimientos previos y evidencias observables de dominio. La interfaz debe emplear
estos perfiles sin alterar la traza causal del intérprete.

| Algoritmo | Objetivo conceptual | Evidencia de dominio |
|---|---|---|
| Intercambio | Comparar cada posición con las posteriores | Predice intercambios y explica el prefijo confirmado |
| Selección | Elegir el mínimo del segmento pendiente | Sigue el mínimo provisional y justifica el prefijo |
| Inserción | Insertar una clave en un prefijo ordenado | Identifica hueco, desplazamientos y estabilidad |
| Burbuja | Llevar el mayor al final con comparaciones adyacentes | Explica frontera y terminación temprana |
| Shell | Ordenar subsecuencias con intervalos decrecientes | Forma grupos y explica el intervalo final uno |
| QuickSort | Particionar alrededor de un pivote | Sigue índices y árbol recursivo |
| MergeSort | Dividir y fusionar mediante un auxiliar | Reconstruye divisiones y una fusión estable |
| HeapSort | Construir un max-heap y extraer la raíz | Verifica heap y zona ya ordenada |
| Counting Sort | Reconstruir desde frecuencias | Calcula conteos y relaciona coste con rango |
| Binsort | Comprender urnas y delegación a conteos | Explica delegación y reconstrucción |
| Radix Sort | Ordenar establemente por dígitos y signo | Identifica dígito activo y tratamiento de negativos |

Los conocimientos previos comunes son arreglos, índices, condiciones y ciclos en C. Recursión,
memoria auxiliar, árboles o aritmética posicional se exigen únicamente cuando el método los usa.
