"""Build a standalone documentation snapshot from local role-task JSON."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def render(config: dict, task_id: str) -> str:
    tasks=config.get('tasks')
    if not isinstance(tasks,dict) or task_id not in tasks:
        raise ValueError('Unknown task ID')
    task=tasks[task_id]
    for field in ['objective','role','owner','next_step']:
        if not isinstance(task.get(field),str) or not task[field].strip():
            raise ValueError('Invalid task field: '+field)
    paths=task.get('allowed_paths')
    if not isinstance(paths,list) or not paths or not all(isinstance(p,str) and p.strip() for p in paths):
        raise ValueError('Invalid allowed_paths')
    snapshot={'task_id':task_id,**{field:task[field] for field in ['objective','role','owner','allowed_paths','next_step']}}
    raw=json.dumps(snapshot,ensure_ascii=False,sort_keys=True)
    for character,code in [('<','003c'),('>','003e'),('&','0026')]:
        raw=raw.replace(character,chr(92)+'u'+code)
    html='''<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'unsafe-inline'; connect-src 'none'; img-src 'none'; font-src 'none'; base-uri 'none'">
<title>Una tarea, contexto visible</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip-link" href="#main">Saltar al contexto de la tarea</a>
<header><p class="eyebrow">MANUAL LOCAL DEL ARNES</p><h1>Una tarea, contexto visible</h1>
<p>Recupera el objetivo, responsable y siguiente paso desde una fuente persistida.</p></header>
<main id="main" tabindex="-1"><p class="notice" role="note">Fotografia documental: no certifica aprobacion, cierre ni evidencia vigente. No ejecuta gates o agentes.</p>
<section aria-labelledby="task-title"><h2 id="task-title">Contexto de la tarea</h2><p id="task-id"></p>
<div class="grid"><article><h3>Objetivo</h3><p id="objective"></p></article>
<article><h3>Rol y propietario</h3><p id="role"></p><p id="owner"></p></article>
<article><h3>Rutas permitidas</h3><ul id="paths"></ul></article>
<article><h3>Siguiente paso</h3><p id="next-step"></p></article></div></section>
<section aria-labelledby="source-title"><h2 id="source-title">Fuente de la muestra</h2>
<p>Consulta los archivos actuales y la instruccion vigente antes de trabajar. Esta vista conserva los datos de cuando fue generada.</p>
<button type="button" id="toggle-json" aria-expanded="false" aria-controls="raw-json">Mostrar datos JSON</button>
<pre id="raw-json" hidden tabindex="0"></pre></section>
<p class="limits">Sin red ni servicios. La coordinacion real mantiene propiedad y QA independiente; un registro no impone aislamiento del sistema operativo.</p>
</main><footer>Ejemplo local de documentacion. Aplicacion, auditoria y preview5051 quedan fuera.</footer>
<script id="snapshot" type="application/json">__SNAPSHOT__</script>
<script>
'use strict';
const task=JSON.parse(document.getElementById('snapshot').textContent);
for(const [id,key] of [['task-id','task_id'],['objective','objective'],['role','role'],['owner','owner'],['next-step','next_step']]){
 document.getElementById(id).textContent=task[key];
}
for(const path of task.allowed_paths){const item=document.createElement('li');item.textContent=path;document.getElementById('paths').appendChild(item);}
document.getElementById('raw-json').textContent=JSON.stringify(task,null,2);
const button=document.getElementById('toggle-json');
button.addEventListener('click',()=>{const expanded=button.getAttribute('aria-expanded')==='true';button.setAttribute('aria-expanded',String(!expanded));document.getElementById('raw-json').hidden=expanded;button.textContent=expanded?'Mostrar datos JSON':'Ocultar datos JSON';});
</script></body></html>
'''
    return html.replace('__SNAPSHOT__',raw)

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--task',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        content=render(json.loads(args.config.read_text(encoding='utf-8-sig')),args.task)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(content,encoding='utf-8')
        print('Local documentation written: '+str(args.output))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(str(exc))
        return 2

if __name__=='__main__':raise SystemExit(main())
