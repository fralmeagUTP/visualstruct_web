# Auditoría didáctica de árbol rojo-negro

Se verificaron inserciones con rotación simple, doble y recoloreo, además de una
secuencia de eliminaciones con fix-up. El oráculo C expone colores en preorden,
raíz negra, black-height, orden BST y ausencia de enlaces rojo-rojo por snapshot.

| Área | Resultado |
|---|---|
| Estado final de rotaciones LL/RR/LR/RL | Aprobado |
| Estado final de recoloreo | Aprobado |
| Invariantes RN tras inserción/eliminación | Aprobado en el oráculo C |
| Momento visual de los recoloreos | Fallido (`RBT-001`, alta) |
| Ruta y ramas de eliminación | Fallido (`RBT-002`, alta) |
| Estados intermedios del fix-up de eliminación | Fallido (`RBT-002`, alta) |

El backend alcanza estados finales válidos, pero la interpretación paso a paso
anticipa cambios de color en inserción y presenta control de flujo falso durante
la eliminación. La tarea queda auditada con ambos defectos abiertos.
