# Diseño

Un módulo compartido tokeniza C dentro de lectores PRE y CODE usando nodos de texto, nunca innerHTML con el código. Recolorea el interior de filas existentes sin reemplazar filas ni sus atributos, selección de línea o navegación. Conserva rawCode y el desplazamiento. Un MutationObserver limitado a cambios de contenido detecta reemplazos, incluida ampliación o pestañas; una caché por nodos/texto evita ciclos propios y trabajo al cambiar sólo clases de navegación. La salida de consola permanece texto de salida.

Comprobar inventario inicial de las trece estructuras y ayudas de las cinco familias; operaciones reales y paso siguiente/anterior en cada familia; main/TAD dinámicos, reset, pestañas, ampliación/cierre, fuente copiada/descargada, escape, scroll y ausencia de bucles. Las capturas son de una instancia de prueba con datos sintéticos, no del Docker del usuario.
