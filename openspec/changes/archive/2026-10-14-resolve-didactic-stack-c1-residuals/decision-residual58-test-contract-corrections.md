# Correcciones de pruebas, no producto

El borrador inserir_elemento pos1/relative0 esperaba[1,2,3]. Fallo nuevo devuelve[2,1,3]. Ccanónico docs/tads_C/tad_lista.c declara explícitamente pos==1 insertaalinicio;valorrelative no seconsulta enesarama. Python tad_lista.py también retorna antes de consultardesplazamiento. Corregir sóloesperado a[2,1,3] conserva contratoC,no evitaunbug inventandoesperado. La descripción genérica "después" deladapter resulta imprecisa para pos1:hallazgo textual pendiente,fuera modificación deproducto eneste bloque. Borrador/fallo anteriores retenidos,no borrarlos.

clear_graph fallóporleer metadata.directed. GraphAdapter.to_visual_state publica directed enraízvisual_state ymetadata sólocounts/is_empty. Corregir sólo ruta deaserción,no reducir comprobación dirigida ni limpiar. Test/fixtureanteriores respaldados enevidence,residuoslogs preservados. Retest sóloestos2casos porcorrección nueva verificable;ningún bloqueo consumido allímite/campaña repetida.
