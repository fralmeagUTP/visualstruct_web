# Dictamen independiente: prototipo BFS persistente aislado

**ACEPTAR la evidencia de equivalencia finita y el resultado observado; RECHAZAR adopción por incumplimiento del gate<5s.** No es solución vigente ni cierre de rendimiento/global. Canonical: D:/MisProyectos/Web_VisualEstruct. Assignment `coordination-bfs-persistent-prototype-independent-qa-low-20261005`; operación `audit.bfs-persistent-prototype-independent-quality`.

Evidencia propia: offline-checks.json (evidencia local: `openspec/changes/archive/2026-10-13-review-bfs-persistent-isolated-prototype-quality/evidence/independent-review/offline-checks.json`). ZIP6089a03b1a5ef5aca00f7857227d20ba791d3296453d72611190dd05a059b6f6; candidato259b930ab040d67ad4b7abba3d674f1659b21059ecdef72ab4146f4cd87a2725.

## Evidencia verificada sin ejecutar código de producto

-16 IDs únicos coinciden selección/runtime/XML;48 fases setup/call/teardown PASS en events.jsonl original, SHA vinculado751ab017e1ddb958ae4ed5759f4664d2cbffa1fa5fdd0b373d54d1f51c7c2947. Los eventos no están dentro del ZIP; se verifican como dependencia externa explícita. No sumar13casos anteriores ni frames como operaciones nuevas.
-16 funciones de modelo/helper/rechazo son idénticas en AST entre canonical baseline y candidate. SHA, fuentes/diff/modelo y asserts de10 escenarios+6 protocolos se leyeron. Las assertions comparan todos los tipos/orden/claves/campos, wire/expansión, mutación/alias/retirados y request isolation; son más que resultado BFS final. No prueban todas las entradas, llamadas directas a builtins o consumidores mutantes posibles.
-Comparación offline independiente de1.766.832 hojas de los gzip, incluyendo tipos, orden de claves/listas y float.hex: únicamente `history[60].mark_effect.signature` difiere. Traza completa11849pasos igual. SHA y29891205bytes de cada respuesta coinciden con su registro. WholeHTTP y bytes NO son iguales.
-Código canónico _signature incorpora _scope basado en session.sid; el harness copia contenido de sesión a otro cliente, no el SID de servidor. Esto fundamenta que firmas distintas son compatibles con contextos distintos, pero no sustituye revalidación criptográfica individual porSID, que no fue registrada. Se conserva el FAILdeaserciación HTTP completa; no se descarta ni normaliza firma para declarar PASS.

## Rendimiento y cierre

Pareja única guardada: canónico11.728276199981337s; candidato10.4939219999942s. Ahorro1.2343541999871377s=10.524600367009619% observado; ambosFAIL<5s. Baseline primero, candidato después, preparación60POSTs fuera del timer. No se demuestran estabilidad, causalidad del ahorro, pico de memoria o rendimiento en otras formas. Desde10.493922 se necesitaría reducir más del52.35% adicional para bajar de5s; no es extrapolación de viabilidad.

Se cierra la revisión del único prototipo y se acepta la decisión de detenerlo aislado. No se cierra gate5s ni se adopta producto. La evidencia temporal instrumentada anterior (intern+snapshot67.72%) corresponde a otro candidato y no se atribuye al actual.

## Inspección de representación y posible siguiente corrección

La invalidación pernode propaga a todos los padres con guardia seen; publicaciones son valores ordinarios internados separados de wrappers vivos, y generaciones/pool son locales al request. bool/int/float y signo del cero tienen tokens diferentes. Los tests observados acreditan persistencia de snapshots viejos, alias compartidos e hijos intactos. Parent callbacks no se desprenden al eliminar/reemplazar vínculos: retienen propietarios hasta fin de request y pueden propagar invalidaciones a antiguos padres; memoria no fue medida. Los valores publicados dict/list son inmutables por disciplina de uso, no por protección de tipo. No certifica consumidores que los muten ni contenedores vivos cíclicos.

Hay una base de código concreta para **formular**, no adoptar, otra corrección: emit aún copia cuatro mapas pedagógicos por paso (`memory`, `auxiliary`, `traversal`, `invariant`), reconstruye condition/narration y entrega un step nuevo a pool.intern. Una extensión de publicación persistente a esos mapas, preservando todos los campos y orden de registros del codec, es una hipótesis verificable. SnapshotPool ya tiene atajo por identidad de objetos canónicos: no proponer como mejora nueva eliminar una recursión de hijos intactos que ese atajo ya evita. No hay perfil del candidato actual que mida el coste residual ni evidencia para asegurar que esa extensión consiga5s. No es autorización para ejecutar otra variante dentro de esta revisión.

Sí existe una corrección documental/harness concreta para una futura comparación: registrar los contextos SID y verificar cada firma con su propio cuerpo/contexto, sin exigir firmas idénticas entre sesiones distintas ni eliminar campo contractual. No reejecutar la pareja actual; esa carencia no cambia el rechazo de adopción porlatencia. Ninguna modificación local pequeña está demostrada suficiente para cumplir5s.

## Cambios requeridos y límites

Para aceptar la evidencia aislada, ninguno: conservar FAILwholeHTTP y gate5s,16PASS, hashes y respuestas completas. Para una futura adopción hacen falta mejora suficiente en gate autorizado, equivalencia completa con firmas validadas porcontexto y límites de alias/memoria/publicación revisados en su bloque coordinado. No transformar esta lista en campaña implícita ni repetir permiso del prototipo ya autorizado.

Guardas before/after propias exit0;1026 inputs vinculados y ZIP53entradas/52 archivos manifest verificados. Fuentes canónicas1000 y paquetes previos permanecen intactos. Cero nuevas solicitudes, benchmarks, runtime/app imports, tests, profiler o variantes; nada instalado/adoptado y preview5051 intacto. Sólo evidencia y tracker propios modificados.
