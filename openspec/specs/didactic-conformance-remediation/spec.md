# didactic-conformance-remediation Specification

## Purpose
Validación existente de continuidad profunda/rebase y línea fuente del motor de trazas. Esta consolidación parcial incorpora únicamente el requisito verificado; no certifica fidelidad C global ni cierre de29hallazgos. Las otras obligaciones históricas y sus bloqueos se conservan en openspec/changes/archive/2026-10-02-reconcile-verified-historical-trace-contract/reconciliation.md.
## Requirements
### Requirement: Traza continua y fuente verificable
El motor MUST comprobar continuidad profunda entre pasos, MUST validar la línea resaltada contra el
código cargado y MUST exigir un evento explícito para cualquier reinicio o cambio de base.

#### Scenario: discontinuidad entre pasos
- **GIVEN** dos pasos consecutivos sin evento de `rebase`
- **WHEN** `after_state` del primero difiere de `before_state` del segundo
- **THEN** la traza se rechaza antes de entregarse al frontend

#### Scenario: línea resaltada inválida
- **GIVEN** un `line_index` fuera de rango o un `line_text` distinto de la línea normalizada
- **WHEN** se valida la traza
- **THEN** la traza se rechaza con localización del paso inconsistente

