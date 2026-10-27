# Ejemplo local de tarea persistida
Este change muestra el contexto de una tarea real en HTML. No modifica el núcleo cerrado, aplicación o auditoría; no ejecuta gates/agentes ni certifica estados.

Desde raíz canónica:
```
python -B openspec/changes/adopt-local-role-documentation-example/build_example.py --config openspec/changes/adopt-local-role-documentation-example/workflow.json --task example-code --output openspec/changes/adopt-local-role-documentation-example/artifact/index.html
python -B -m unittest discover -s openspec/changes/adopt-local-role-documentation-example/checks -p test_example.py -v
```
Abrir artifact/index.html como archivo local después del rol visual. JSON embebido es fotografía de generación, no sigue cambios futuros; leer perfil/instrucción actuales para trabajar. El generador valida campos/ID y conserva texto como datos, no ejecuta contenido HTML del JSON.

Rol specifications: spec/escenarios y acceptance-plan. Rol code: generador/pruebas. Rol visual: CSS, teclado, foco, responsive y capturas finitas Chromium. Autor común con transferencia secuencial; QA independiente existente al final. Las tareas quedan pending, no closed, hasta revisión genuina. No motor distribuido ni red/servicios/API pagada. LOW.
