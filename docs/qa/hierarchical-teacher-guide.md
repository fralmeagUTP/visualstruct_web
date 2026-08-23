# Guía docente: estructuras jerárquicas

## Propósito

Usar ABB, AVL, árbol rojo-negro y min-heap para que el estudiante conecte la ejecución real de C con forma, memoria, costo e invariantes. La visualización es evidencia de la traza, no una animación independiente.

## Secuencia sugerida

1. **ABB y recursión:** insertar `30, 20, 10, 25`; predecir cada rama y dibujar la pila. Contrastar una entrada balanceada con `10, 20, 30, 40, 50`.
2. **Eliminación ABB:** practicar hoja, un hijo y dos hijos. Pedir que el estudiante señale sucesor, `free` y enlace que recibe el retorno.
3. **AVL:** ejecutar LL, RR, LR y RL. Antes de revelar, calcular alturas y FE. En rotaciones dobles identificar los dos pasos simples.
4. **Rojo-negro:** identificar nodo, padre, abuelo y tío; predecir recoloreo o rotación. Verificar las tres reglas y black-height por camino.
5. **Heap:** vincular `A[i]` con padre e hijos. Comparar con ABB para discutir prioridad parcial frente a orden de búsqueda.
6. **Recorridos:** sincronizar inorden, preorden y postorden con la pila recursiva; explicar cuándo se visita el nodo.

## Preguntas de discusión

- ¿Qué instrucción C causa el cambio visual y qué puntero se modifica?
- ¿Qué rama no se ejecutó y por qué no aparece en la traza?
- ¿El invariante está conservado o temporalmente en reparación?
- ¿Qué ocurriría con la altura al usar una entrada ordenada?
- ¿Por qué un heap no permite buscar como un ABB?

## Ejercicios

- Construir una entrada que active cada rotación AVL.
- Eliminar un nodo ABB con dos hijos y registrar el sucesor y las reconexiones.
- Encontrar un caso rojo-negro con tío rojo y otro con tío negro.
- Insertar un mínimo al final de un heap y predecir todos sus índices.
- Exportar el resumen JSON y justificar cada frame señalado por el docente.

## Rúbrica (0–3 por criterio)

| Criterio | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Semántica C | No relaciona código/estado | Reconoce líneas | Explica punteros o recursión | Justifica causalmente cada cambio |
| Invariante | No lo identifica | Lo enuncia | Aporta evidencia parcial | Verifica todos los nodos/caminos |
| Predicción | No predice | Predice sin justificar | Justifica con una regla | Anticipa caso, ajuste y resultado |
| Comparación | Confunde estructuras | Enumera diferencias | Relaciona forma y costo | Argumenta con la misma entrada |
| Comunicación | Respuesta ausente | Vocabulario impreciso | Explicación comprensible | Explicación rigurosa y reproducible |

Puntuación sugerida: 12–15 dominio, 8–11 en progreso, 0–7 requiere refuerzo.
