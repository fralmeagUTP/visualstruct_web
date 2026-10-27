# Mantener extremos de arcos ante fallo de reserva
Por qué: fault malloc1/2 en grafo vacío y1 con un extremo previo produce arco cuyo extremo no existe. Cuatro de30 escenarios nativos fallan invariante.
Qué: no crear/actualizar arco si un extremo sigue ausente tras intentar crearlos. Mantener retornoGrafo y creación parcial de vértices ya documentada; no prometer atomicidad completa.
