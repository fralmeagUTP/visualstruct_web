# Revision independiente: formato ColaPrioridad — 2026-10-07

Veredicto: ACEPTADO focalmente: un archivo, una asercion.

32 hashes del manifiesto final coinciden. Manifiesto inicial conservado; C/H y Python formatter mantienen sus3 hashes originales. AST independiente: al revertir la unica asercion nueva, archivo completo identico al before. Copy used==2, valores[11,22], prioridades[2,1], input/capacidad120 y cleanup contar==0 intactos.

El contrato de conformidad observable C/Python y consultas secuenciales no mutantes se respeta. C cp_encolar agrega al final sin ordenar por prioridad. cp_formatear nativo conserva orden de enlaces, prefix "frente -> ", cada valor "%d(p=%d)" y separador " | ", sin salto final ni stdout; la capacidad120 permite todo este texto. Por tanto resultado exacto "frente -> 11(p=2) | 22(p=1)" deriva de la semantica C, no de copiar una salida Python arbitraria. El formatter Python reproduce esos limites/separadores. El indice [0]=11 antiguo no corresponde a la fuente C vigente. Igualdad de texto completo exige tambien segundo elemento, prioridad, orden y separadores: fortalece el substring anterior.

XML mismosID test_tad_cola_prioridad_copy_and_format: baseline1FAIL, final1PASS; guardas/workers2GiB120s conservados. No se repitio el test ni bateria. Este caso no certifica todas las capacidades/truncaciones/vacios ni todo PQ.

Sortinginventory, ABB/RN y E2E son contexto no reabierto y siguen sus propias decisiones. No publicacion ni cambios de producto/contratos/indice. Before/after propios conservados.
