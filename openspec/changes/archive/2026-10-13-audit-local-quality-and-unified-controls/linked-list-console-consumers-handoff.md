# Lista console consumers: focal reproduction and blocked repair

Canonical D execution; assignment coordination-linked-list-console-consumers-low-20261007; operation audit.linked-list-console-consumers.

Two selected tests reproduce FAIL (pytest 0.70s; supervisor exit1, 1.531s). Worker verified Windows Job hard2GiB before app imports; cap120s. No broader suites or engine changes.

Obsolete expectations: successful search must still evaluate `if (!encontrado)` while skipping its printf body; repeated deletion emits its confirmation before the closing void scope frame. Existing matching printf counts, intermediate deletion states and three free(temp) assertions pass before the obsolete assertion fails.

Real contract defect: native lista_buscar_elemento prints `\n Encontrado en la posicion %d\n`; frames5/15 instead emit strings ending in 1/3 without final LF. Native lista_eliminar_repetidos prints `\n\n Valores eliminados..\n`; frame29 emits that message without final LF, followed by frame30 scope end. Source and actual chunks are frozen in console-contract-findings.json and original traces. No native execution/UB needed: discrepancy is literal bytes.

Do not update consumers to bless missing LF. Tests and tad_lista.c remain byte-identical to pre-block copies. No product modifications. Repair requires coordination of exact previously closed emitter blocks and corresponding reopen decision/authorization; this consumer assignment explicitly excludes reopening engines. Next step: authorize narrow printf console emitter repair, then adjust guard/chronology consumers and add negative controls for byte truncation, duplicate/late emission and wrongly executed not-found body. Independent QA remains pending; no closure claim.

Accepted Sorting/Radix, hierarchical and Apilar lots are preserved; no commit/push/deploy attempts. Prior automatic review publication rejections remain untouched.
