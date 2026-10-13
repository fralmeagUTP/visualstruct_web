# Diseño documental

Separar ejecución explícita, mutación estructural y restauración. Preservar políticas heterogéneas: Hash no registra consultas; RN False válido sí. GET no redispatcha consultas retenidas, pero metadatos/validación interna y efectos almacenados siguen permitidos. No journal nuevo. El delta conserva obligaciones ajenas de checkpoint íntegramente y sólo aclara la cláusula que equiparaba posición cronológica a mutaciones. Su implementación global no se certifica aquí.

Fuentes numeradas y SHA: manifest C1 20261004. Revisión propia es estática, sin nueva ejecución técnica y sin independencia.
