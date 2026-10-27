# Ejecución mínima propuesta, NO autorizada todavía

Docker local listo29.6.2. Imagen existente gcc:14 Linux/amd64, fija sha256:468b5b959b5f4025724d8549f45550c6ad38a32474733cbf130f8f2c1bc80805. Ningún pull ni contenedor nuevo ejecutados;6servicios existentes preservados. No se confirma toolchain interno hasta ejecución.

Solicitar dos bloques nuevos: Pila ASan y Pila UBSan, solo copia observadora validada y controlC de evidence/stack-native-pilot-final (sin montar repo/.env/sesiones). Contenedores propios con --pull=never --network=none --memory=2g --memory-swap=2g --cpus=1 --pids-limit=64 --read-only y tmpfs/tmp256MiB; inputsololectura y carpeta propia/results. Supervisor host120s mata/detiene SOLO nombre/ID propio al límite; nunca detener daemon/otros servicios. CompilarC17 -Wall -Wextra -Wpedantic -Werror -fno-omit-frame-pointer -g, sanitizadores separados, nominal y mallocNULLinyectado; comparar stdout/control,21eventos y ciclo de vida. Registrar versióngcc/imagen/sourceSHA/sanitizerlogs/status. ASan detect_leaks=0 conserva reservaLSan; no certificar fugas por ausencia de reporte. No ejecutar26bloques/13familias ni casos aceptados sin eventos nuevos. No Bellman900 ni UB intencional.

Estos dosbloques demuestran únicamente pilotoLinuxPila; matriz instrumentada original completa sigue pendiente de eventos/estadospor familia y casos explícitos.
