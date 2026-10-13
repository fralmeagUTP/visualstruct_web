# Prioridad limpiar: propuesta MEDIUM acotada tras baseline LOW

Propuesta para coordinación; esta fase LOW no implementa producto.

1. Motor exclusivo cp_vaciar: caller ColaPrioridad vivo; parámetro y aux/next con tipo CPNodo*, scope/init exactos; next guarda identidad del sucesor, front avanza conservando aux original vivo desconectado; rear=NULL antes último free; aux indeterminado despuésfree con máscara/fields históricos separados; cantidad decrece despuésfree; aux=next revalida; retorno void explícito cierra sólo callee. Respetar todas condiciones reales, sin contrato numérico nuevo ni rama falsa cantidad>0 inventada.
2. Persistir última traza preparar/reload ligada a historial actual sin redispatch; invalidar por mutación/reset exitosos pertinentes. Conservar limpiarduplicado y reinserción en historial real.
3. Main DOM exclusivo Prioridad: C17 vigente, comprobar retorno real cp_encolar antes anunciar aplicado; ante0 cp_vaciar+return1, sin mensaje falso. Finalcleanup y Doxygen @file/main/@return documentados. Mantener llamadas históricas originales y contratos actuales.
4. UI exclusiva cleanup: inicial sin locales futuros/línea, caller persistente; alias next y nodo desconectado con identidad estable, aux indeterminado separado de historia, variables y máscaras coherentes, return sin callee. Ambas vistas y vuelta exacta, cinco secciones existentes.
5. Verificación: conservar22IDs y resolver10rojos, nuevas regresiones sólo si aportan cobertura; comparar153eventos/41conditions completos con observador seguro existente. Ocho UI calls2views forward/back, cuatro recargas exactas; cuatro mains DOM C17,8ownership/8NULL faultsreturn1no false success,6Doxinputs4documentedmains; recursos finitos y hashes protegidos. No ABI/OOM real/arbitrary depth/globalclosure.

Pedir MEDIUM acotado según coordinación; terminar checkpoint y devolver LOW para consolidación finita. No reabrir Pila/Cola limpiar, Hash/Sorting, ni cambiar C/H/RN/Grafos/publicar.
