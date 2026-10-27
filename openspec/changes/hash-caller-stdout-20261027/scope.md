# Hash caller stdout — alcance vigente

Autorización delegada por coordinación el 2026-10-27: diagnosticar y corregir stdout de Hash cuando su main real imprime, en la copia integrada visualstruct-syntax-review. Sólo backend/generador Hash y pruebas nuevas Hash. Preservar C/H originales, los cambios de grafo, sintaxis y presentación integrados. No publicar, commit, push ni desplegar. Sorting pertenece a otro agente.

Cada salida visible debe provenir de printf del caller efectivamente ejecutado o interpretado, compartir fuente con el main y coincidir con ejecución nativa C17. No se fabrican mensajes de dominio como stdout ni se agregan printf indiscriminados a void.
