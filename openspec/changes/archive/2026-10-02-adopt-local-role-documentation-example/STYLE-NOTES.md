# Decisiones de diseño local
Objetivo: separar contexto (tarjetas) y fuente/limitaciones, con jerarquía legible. Fondo cálido, texto azul oscuro y advertencia ámbar: no usar verde de aprobado ni barra global de avance, porque no hay certificación de estado.
Responsive: dos columnas a escritorio; una bajo640px; rutas largas con wrapping. Controles48px, foco3px contrastado, skip-link y botón JSON nativo con aria-expanded/aria-controls. Estilo local sin fuentes/iconos externos.
Verificación autor: Chromium headless file:// con red externa bloqueada, teclado/DOM/overflow y capturas1280x900 y390x844. Inspección visual de capturas antes de entrega. Es muestra local, no WCAG completa, screenreader real o UI de aplicación. QA independiente pendiente.

## Inspección ejecutada
Autor inspeccionó capturas desktop/mobile con JSON oculto y abierto: jerarquía y rutas legibles, una columna móvil, sin recortes; foco del botón visible y JSON envuelto. Contraste del texto principal medido en DOM12.10:1; botón13.63:1. Cuatro capturas bajo evidence/example-visual. La primera prueba de inyección reutilizó una página con globals ya declarados y falló en el checker; se aisló fixture en página nueva sin relajar el assert. Generador no cambió por ese fallo. Resultado final: cero errores JS/peticiones externas observadas. No se atribuye revisión independiente ni screenreader/WCAG global.

Reproducir desde raíz:
```
python -B openspec/changes/adopt-local-role-documentation-example/evidence/example-visual/check_visual.py
```
El checker escribe sólo sus resultados/capturas locales y usa Chromium ya instalado; no descarga navegadores ni inicia servidor.

## Límite encontrado y alternativa acotada
El núcleo cerrado sólo lee fuentes UTF-8; registrar PNG directamente en deliverables produjo rechazo de decodificación, conservado en gate-verify-binary-rejection.log. Se mantienen capturas con image-hashes.json y check_image_integrity.py, texto enlazado al task. Ejecutar checker de PNG antes de verify/QA. Un cambio aislado de PNG NO invalida automáticamente el gate del núcleo si no cambia el manifiesto; no se promete esa garantía. No modificar núcleo para resolverlo en este piloto.
```
python -B openspec/changes/adopt-local-role-documentation-example/evidence/example-visual/check_image_integrity.py
```

QA independiente puede usar --output-dir openspec/changes/adopt-local-role-documentation-example/evidence/independent-review/visual para no sobrescribir capturas/resultados del autor. Sólo se permite salida bajo evidence del mismo change.
