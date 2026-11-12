## ADDED Requirements

### Requirement: Minimal educational graph API
Graph insertion, neighbor queries, BFS, DFS, Dijkstra, Bellman-Ford, Prim and Kruskal SHALL be callable without public diagnostic-state arguments.
#### Scenario: Standalone C program
- GIVEN the public graph header and student example
- WHEN compiled as strict C17
- THEN it uses only minimal inputs and releases owned results, not borrowed graph lists.

### Requirement: Bounded graph capacity
The application SHALL accept 30 vertices and reject a 31st without changing graph or history.
#### Scenario: Persisted boundary graph
- GIVEN a saved graph of 30 vertices
- WHEN reloaded and another vertex is requested
- THEN all existing data remain and the request is rejected.

### Requirement: Complete readable results
Result text SHALL remain accessible without a small nested scrollbar and without inheriting diagram pan or zoom.
#### Scenario: Redraw and practice
- GIVEN a result transferred from the diagram into its result panel
- WHEN the mutation observer runs or practice concealment changes
- THEN internal transfers do not erase the result and concealed answers stay concealed.

### Requirement: Explicit graph returns
The UI SHALL distinguish the current received TAD result cell from the most recent function return.
#### Scenario: Printed borrowed list
- GIVEN a nonempty graph-list return followed by a void printing helper
- WHEN moving forward or backward through its trace
- THEN the received list and void return are labeled separately, without future values.

### Requirement: Yellow minimum spanning tree
Prim and Kruskal SHALL highlight accepted MST edges in yellow and keep other edges blue with a textual legend.
#### Scenario: Final MST and trace navigation
- GIVEN a completed MST or intermediate accepted-edge set
- WHEN displayed or revisited
- THEN precisely those accepted edges are highlighted.
