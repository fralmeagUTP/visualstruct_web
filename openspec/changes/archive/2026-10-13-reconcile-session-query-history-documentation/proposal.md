# Reconciliar descripción de historial cronológico existente

## Why
La spec session-state prohíbe todas las consultas aunque servicios y decisiones aceptadas ya conservan consultas seleccionadas. Es una contradicción documental.

## What Changes
Reescribir íntegramente Historial de operaciones por estructura; aclarar replay sin redispatch y el escenario de consulta del intervalo de checkpoints. La tabla reproduce las políticas actuales por módulo.

## Scope
Sólo expediente documental dedicado. No modificar producto, almacenamiento, semántica ni canónicos antes de aceptación coordinada. No certifica otros requisitos existentes de checkpoints o rendimiento. Purpose canónico deberá sustituir «historial de operaciones mutantes» por «historial cronológico de ejecuciones registradas según módulo» únicamente al adoptar.
