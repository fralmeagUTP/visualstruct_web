# Hash two consumers: author handoff, pending independent QA

Canonical D project. Assignment coordination-hash-two-consumers-low-20261008; operation audit.hash-two-consumers. Only original HASH-001 capacity3 keys1,4,7 and goldenHash capacity5 insert1->1; no closed native/UI block repeated.

Before:2 FAIL. HASH-001 mistook comments saying No rehash for executable resizing. Corrected source check strips comments before rejecting executable realloc/rehash/capacity assignment in insertion; additionally checks original count3 and collision chain7,4,1. Historical failed/high finding unchanged. Golden expected18 but canonical C reaches19 steps: helper call and caller assignment separate. Only Hash count18->19; every other golden byte and original fixture preserved.

After:20 PASS in0.91s:2 original IDs plus18 pure controls (2 positive,16 negative). Bounded C-derived oracle checks exact reached lines/order/source indices, masks0/1/3/7, separate key/value/next writes, allocation/free counters, link/count chronology, fixed capacity and before/after sizes. Negative controls reject dropped/reordered steps, source mismatch, premature mask/write/count, corrupt values/links, allocation/free/capacity/snapshot and executable resizing. This is a bounded consumer oracle, not a universal ownership proof. Runs guarded before, hard Windows Job2GiB before imports and120s supervisor; logs retained.

Before/after captured service responses byte-identical. C/H/product and historical finding unchanged; all other shared-file function bodies and golden bytes preserved. Protected manifest chain verified read-only; prior accepted/pending evidence retained. No QA registration/acceptance/publication, engine change, broad test or remote CI rerun. Balance27 accepted/26 author-corrected pending independent QA/13 other pending; original remote66 failures unchanged/not recomputed. Next: independent review of exact lot, then coordinator assigns next bounded pending group.

Evidence: evidence/visible-hash-two-consumers-low/ (XML/logs/responses, preservation, inventory, input binding).
