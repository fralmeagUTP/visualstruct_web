# DFS baseline preparation — not verified

Current operation: `graph.dfs`. This document registers the next algorithm after BFS recorded-case closure. No DFS native, browser or semantic tests were executed in this preparation. Global tasks remain 13/22; DFS is not signed off.

## Source inventory and risks to test

Actual downloadable `docs/tads_C/tad_grafo.c` implements `grafo_dfs`, `grafo_dfs_recursivo` and static `grafo_agregar_recorrido`. Dependencies include vertex existence, clearing/setting/querying marks and successor-list allocation. Unlike BFS, DFS checks vertex existence before clearing marks: do not copy the BFS rejection order into DFS.

Recursive calls share the output-list storage through `ListaVertice *recorrido`; each frame owns its successor-list allocations and frees them while returning. Result nodes are separately allocated, initially unmarked, and caller-owned. Audit publication of partial links, suspended parent frames and allocation lifetimes against native observations. Static source inspection identifies these review targets; it does not establish frontend correctness.

## Next bounded work

1. Read current service/domain/trace/frontend DFS paths and exact downloaded function bodies; record source hashes and contracts before instrumentation.
2. Reuse the safe native observation architecture, not BFS outcomes: empty/missing start, singleton, negative IDs including -1, cycle, diamond, disconnected graph, adjacency order and repeated execution. Record finite cases and distinct observations without implying all paths.
3. Compare native instruction order, branch outcomes, calls/returns, aliases, marks, successor ownership and result publication against before/after visualization, highlighted line and console. Verify forward/back replay in each existing representation without additional operation POSTs.
4. Verify successful DFS history/reload and actual generated caller C: computed output, owned-result cleanup and compilation. Do not infer this from BFS tests.
5. Review DFS public/helper Doxygen contracts and manual consistency individually; update only verified ledger symbols.

Allocation-failure injection, larger-graph performance, other graph algorithms and global final regression remain separate pending work. Hash and Rojo-Negro validator decisions remain unchanged. Request bounded higher reasoning only for a demonstrated difficult semantic case.

## Reusable evidence, not DFS proof

See `evidence/visible-graph-bfs-low-closure/README.md` for the completed BFS harness and its limits. BFS is recorded-closed and must not be reopened merely to start DFS.


## Subsequent authorized LOW execution
The original preparation above is historical. Current assignment coordination-graph-dfs-execution-low-20261002 executed the contract baseline and fixes; see evidence/visible-graph-dfs-contract-low/README.md. DFS instruction conformance remains OPEN; next bounded case is graph-dfs-instruction-review-plan.md.
