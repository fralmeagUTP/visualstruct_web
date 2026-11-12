# Design

Public graph methods accept only their inputs. Diagnostics remain private to C and are observed by the visualizer; generated caller code uses the same minimal API. The normal execution fast path retains all mutations and event accounting.

Graph capacity is centrally 30. Layout work is bounded for larger graphs, and dense-edge label placement is cached. This is not a guarantee of readability or constant latency for every density; the 4,000-event trace budget is unchanged.

Results live outside diagram pan/zoom and use natural height. Hash/sorting retain their existing result sections. Internal DOM transfers are distinguished from genuine redraws, and practice-mode concealment is preserved.

The result cell received by the caller is distinct from the last function return. A void printing helper does not replace the displayed TAD result. Rendering uses safe per-frame snapshots, including retired-identity warnings; reverse navigation does not leak future values.
