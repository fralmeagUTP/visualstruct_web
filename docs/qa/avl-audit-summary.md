# Auditoría didáctica de AVL

Se ejecutaron casos independientes de rotación LL, RR, LR y RL, además de una
eliminación que provoca rebalanceo. El oráculo C confirmó las raíces esperadas
`20`, `20`, `20`, `20` y `10`, junto con orden BST, balance y enlaces padre-hijo.

| Área | Resultado |
|---|---|
| Inserción y rotaciones LL/RR | Aprobado en el estado final |
| Inserción y rotaciones LR/RL | Fallido en estados intermedios (`AVL-001`, alta) |
| Eliminación con rebalanceo | Aprobado en el estado final |
| Invariantes BST, balance y enlaces | Aprobado en cada snapshot del oráculo |
| Alturas y factores durante rotaciones dobles | Fallido (`AVL-001`, alta) |

La visualización de una rotación doble no representa el resultado de la primera
rotación simple. Por ello, aunque el estado final coincide con C, la secuencia
didáctica muestra un salto falso respecto de las instrucciones realmente
ejecutadas. La tarea queda auditada con el defecto abierto y reproducible.
