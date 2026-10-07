# Source admission

Validate required native functions/helpers and supported statement layout before constructing SortingInterpreter. Read canonical mapping for comparison only; never fill absent source. Detect preprocessing after trigraph replacement, line splicing and comment removal; no macro/conditional evaluation. Service uses actual C provider on run/step/compare and preserves prior accepted state on source errors. General C compiler support is outside this contract.
