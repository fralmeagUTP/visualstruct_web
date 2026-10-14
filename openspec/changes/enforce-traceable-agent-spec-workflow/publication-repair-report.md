# Reparación de publicación: inputs de pruebas y pipeline existente

Este trabajo implementa únicamente la reparación de portabilidad autorizada para actualizar GitHub/VPS. **enforce-traceable-agent-spec-workflow sigue propuesta pendiente de visto bueno: no se implementan sus requisitos ni se activan roles, hooks o controles de registro/publicación.**

## Cambio concreto
Los34errores de colección provenían de Playwright/Pillow ausentes,12lecturas de11inputs excluidos yCANDIDATE_OUT. Coverage añadía colisión de ejemplo. Se fijan dependencias de testing observadas, se suministran inputs históricos exactos conSHA en un paquete comprimido y se usan lectores explícitos hacia copias temporales. Las fuentes originales y sesiones permanecen intactas. Los26C publicados equivalen alcanónico tras CRLF/LF solamente; se verifica el contenido real antes de compatibilidad de hashes históricos. No se normalizan instrucciones ni espacios ni se admiten cambios decontenido.

Se conservan las funciones API/nativas en unit/integration. Los506E2E existentes corresponden a500Chromium generales repartidos4x125,1caso Graph dedicado y5Firefox dedicados. Ningún caso se elimina por esta partición. ElJPEG antes condicionado por URL usa servidor privado. Cada ejecución escribe sus propios resultados sin sobrescribir evidencia histórica. Triggers, max-parallel2, gates de cobertura, C17/sanitizers, secretos/permisos y protección de rama conservan política previa.

Cuatro assertions jerárquicas heredadas count==0 se alinean a count==1 deeducación restaurada aprobada. Navegación/teclado/responsive permanecen. Cambios de lectura:101de102módulos conAST equivalente tras quitar wrappers/markers; excepción declaradaJPEG elimina dependencia depreviewexterno. Las otras correcciones declaradas son contexto temporal delcandidato, identidad del ejemplo ycontrato de reparto CI.

## Evidencia y límites
-29checks reales de paquete/disposición/reparto/sanitización:PASS,13.48s pytest,95MiB pico Job,120s/2GiB aplicados. No sumar corridas solapadas.
-Recolección de5586noE2E en snapshot previo a6checks nuevos:exit0,18.73s pytest,159MiB pico. Posteriormente la prueba de reparto recoge125de500generales; no es ejecución debrowser.
-1713inputs comprimidos enaprox18.1MB; hashes yprocedencia en tests/fixtures/published-audit-inputs/manifest.json. Losinputs son expectativas/observaciones históricas reales, no una campaña nueva ni certificado universal/ABI/LSan.
-E2E delcommit anterior effda1c:Graph yFirefox PASS,Chromium general FAIL en2oráculos heredados. Coordinación confirmó independientemente losjobs116003318811/116003319246/116003319258 a18:44UTC. C17/sanitizers PASS;unit/coverage fallaron durantecollection.
-Hash26C y3904sesiones originalespreservado enD. Paquete ylectores no modifican producto niC.
-El nuevo commit requiereCI real completo; estoschecks locales no lo sustituyen. VPS permanece pendiente deCIverde ylo ejecuta otra tarea. No se repiten campañas originales consumidas ni se atribuye QA humana nueva inexistente.

Detalle de34errores:ci-portability-diagnosis.md. Evidencia local: evidence/publication-pipeline-final-checks,resultadosdecolección,portable-source-equivalence.json,C-line-ending-portability-proof.json ymanifiestodepreservación. Loslogs ylas asignaciones activas permanecen locales.
