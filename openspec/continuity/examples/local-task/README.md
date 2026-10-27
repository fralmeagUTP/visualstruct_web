# Muestra local aceptada
artifact/index.html y style.css son copias exactas del ejemplo aceptado por QA; abrir HTML como archivo local. source-profile.json conserva fotografía de generación, no autorización actual: rutas/owners/next_step impresos son datos históricos. El núcleo rechaza el change archivado como tarea activa.

Desde raíz:
```
python -B openspec/continuity/examples/local-task/build_example.py --config openspec/continuity/examples/local-task/source-profile.json --task example-code --output openspec/continuity/examples/local-task/artifact/regenerated.html
python -B -m unittest discover -s openspec/continuity/examples/local-task/checks -p test_example.py -v
```
Generador estándar admite otro perfil/task explícito para fotografía, pero no ejecuta/valida gates ni agentes. Para trabajo real seguir ../../USAGE.md y registrar nueva tarea aprobada. Mantener original index.html; usar salida distinta al regenerar.

QA original, capturas y perfiles cerrados viven en archive/2026-10-02-adopt-local-role-documentation-example. example-archive.json de continuidad traduce prefijo antiguo a archivo; fuentes de los checks visuales originales conservan contexto fechado y no son comandos activos después de moverlas. No WCAG completa ni aislamiento OS.
