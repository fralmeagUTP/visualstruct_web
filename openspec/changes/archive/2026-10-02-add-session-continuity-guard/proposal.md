# Continuidad verificable de sesiones
Estado: implementación autorizada por «Necesito que me ayudes a solucionar el problema del Open spec» y delegación de coordinación del2026-10-02. Registra autorización recibida; no autentica conversación desde Git.

## Why
Estados dispersos/contratos canónicos antiguos permiten repetir bloques cerrados y confundir C:/D:. Persistir documentos necesita recuperación obligatoria.

## What Changes
AGENTS raíz, índice de fuentes sin estado manual duplicado, checkpoint UTC/SHA, guarda de identidad/bloques/evidencia/reapertura y pruebas aisladas. Reconciliación histórica con diferencias y decisiones explícitas.

## Scope
Tooling/instrucciones propios. Sin código funcional, preview, suites de aplicación ni archivos de auditoría concurrente. Sin dependencias/despliegue. Python3.10/OpenSpec1.6.0 instalados; formato de deltas existente.

## Success Criteria
Proyecto incorrecto, bloque desconocido, evidencia ausente, checkpoint obsoleto y reapertura sin registro fallan. Conteo se deriva de tasks; cada cierre declara alcance/fuente. Ambigüedades semánticas quedan rastreadas.
