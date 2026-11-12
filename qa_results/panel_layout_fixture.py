"""Build a self-contained browser fixture using production CSS/controller, no network."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
css='\n'.join((ROOT/'static/css'/n).read_text() for n in ['styles.css','contextual_help.css','classroom_view.css'])
controller=(ROOT/'static/js/classroom_view.js').read_text()
html='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Resultados completos · prueba local</title><style>'''+css+'''</style><body><main class="container"><h1>Resultados completos · prueba local</h1><p>Prueba aislada de presentación con CSS/controlador reales. No ejecuta algoritmos.</p><button id="practice">Alternar práctica</button><button id="redraw">Redibujar</button><div id="root" class="graph-primary-workspace"><section id="visual"><h3>Visualizar y ejecutar</h3><div id="stage"></div></section><section id="code-panel"><h3>Código C</h3><pre id="code">int main(void) {\n  return 0;\n}</pre></section></div><section id="output"><h3>Consola C</h3><pre id="console"></pre></section></main><script>'''+controller+'''
const stage=document.getElementById('stage'),visual=document.getElementById('visual');
function paint(){stage.innerHTML='<svg viewBox="0 0 700 350" role="img" aria-label="Grafo de prueba"><circle cx="90" cy="80" r="25" fill="#d6e5f8"/><circle cx="500" cy="200" r="25" fill="#d6e5f8"/><path d="M115 80L475 200" stroke="#2165a5"/><text x="80" y="85">13</text><text x="495" y="205">30</text></svg><details open class="hier-traversal-summary"><summary>Recorrido completo</summary><p>'+Array.from({length:30},(_,i)=>i+1).join(' → ')+'</p></details><p class="hier-current-result">Contrato C: GRAFO_OK (0): Correcto. Retorno C registrado. Lista propia: el caller conserva el contenido y libera los nodos después de recibirlos. Camino mínimo Dijkstra: '+Array.from({length:30},(_,i)=>i+1).join(' → ')+'</p>';}
paint();document.getElementById('console').textContent=Array.from({length:35},(_,i)=>'Salida '+i+': '+Array.from({length:30},(_,j)=>j+1).join(' -> ')).join('\\n');
const view=ClassroomView.mount({root:document.getElementById('root'),visual,stage,code:document.getElementById('code'),key:'test',results:[{label:'Consola C (printf)',panel:document.getElementById('output'),code:document.getElementById('console')}]});
document.getElementById('practice').onclick=()=>stage.classList.toggle('hier-practice-hidden');document.getElementById('redraw').onclick=paint;
</script></body></html>'''
Path('/tmp/visualstruct-panel-fixture.html').write_text(html)
