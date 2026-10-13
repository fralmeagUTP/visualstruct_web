"""Offline proposal only: a minimal chronological caller for Intercambio history."""
from pathlib import Path
import json,sys,subprocess,shutil
ROOT=Path(__file__).resolve().parents[3]

def build_main(history,materialized_random=None):
 materialized_random=materialized_random or {};current=None;lines=['/** @file main.c',' * @brief Prototipo fuera de la UI: caller cronologico de Intercambio.',' */','#include <stddef.h>','#include <limits.h>','#include "tad_ordenamiento.h"','/** @brief Reproduce creaciones y llamadas aceptadas; arreglo automatico, sin ownership heap.',' * @return 0 al terminar.',' */','int main(void) {','    int arreglo[80] = {0};','    size_t n = 0;']
 def checked(values):
  if isinstance(values,str):values=[int(v.strip()) for v in values.split(',')]
  if not isinstance(values,list) or not 1<=len(values)<=80 or any(type(v) is not int or not -2147483648<=v<=2147483647 for v in values):raise ValueError('Valores no materializados int32/1..80')
  return list(values)
 def literal(value):return 'INT_MIN' if value==-2147483648 else 'INT_MAX' if value==2147483647 else str(value)
 for index,entry in enumerate(history):
  op=entry['operation'];payload=entry['payload']
  if op in ['create_array','generate_random_array']:
   current=checked(payload['values'] if op=='create_array' else materialized_random[index]);lines.append(f'    n = {len(current)};')
   lines.extend(f'    arreglo[{i}] = {literal(v)};' for i,v in enumerate(current));lines.append('    imprimir_arreglo(arreglo, n);')
  elif op=='select_algorithm':
   lines.append('    /* Seleccion de algoritmo: la llamada posterior expresa el metodo. */')
  elif op=='run':
   effect=entry.get('array_effect',{})
   if current is None or payload.get('algorithm_id')!='intercambio' or effect.get('schema')!=1 or effect.get('input')!=current or effect.get('output')!=sorted(current):raise ValueError('Historial fuera del prototipo Intercambio o efecto inconsistente')
   lines.extend(['    ordenar_intercambio(arreglo, n);','    imprimir_arreglo(arreglo, n);']);current=effect['output']
  else:raise ValueError('Operacion no aceptada en este prototipo')
 lines.extend(['    return 0;','}']);return '\n'.join(lines)+'\n'

if __name__=='__main__':
 sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
 from app import create_app
 from test_graph_bfs_documentation import run_doxygen
 out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True);app=create_app();rows=[]
 scenarios={'manual_repeated':[('create-array',{'values':[3,1,2]}),('run',{'algorithm_id':'intercambio','mode':'fast'}),('run',{'algorithm_id':'intercambio','mode':'fast'})],'recreate_negative':[('create-array',{'values':[7]}),('run',{'algorithm_id':'intercambio','mode':'fast'}),('create-array',{'values':[-3,0,-1,0]}),('run',{'algorithm_id':'intercambio','mode':'step_by_step'})],'random_materialized':[('random-array',{'size':4,'min_value':-5,'max_value':5,'seed':42}),('run',{'algorithm_id':'intercambio','mode':'fast'}),('run',{'algorithm_id':'intercambio','mode':'fast'})]}
 for name,operations in scenarios.items():
  target=out/name;target.mkdir(exist_ok=True);client=app.test_client();expected=[];materialized={}
  for route,payload in operations:
   d=client.post('/api/ordenamiento/'+route,json=payload).get_json();assert d['success'],d;expected.append(d['visual_state']['items'])
   if route=='random-array':materialized[len(d['history'])-1]=list(d['visual_state']['items'])
  main=build_main(d['history'],materialized);(target/'main.c').write_text(main,encoding='utf-8');(target/'history.json').write_text(json.dumps({'history':d['history'],'materialized_random':materialized},ensure_ascii=False,indent=2),encoding='utf-8')
  for kind,ext in [('source','c'),('header','h')]:r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;(target/('tad_ordenamiento.'+ext)).write_bytes(r.data)
  run_doxygen(target,[target/'main.c',target/'tad_ordenamiento.c',target/'tad_ordenamiento.h'])
  cc=shutil.which('gcc');assert cc;p=subprocess.run([cc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(target/'tad_ordenamiento.c'),'-o',str(target/'main.exe')],capture_output=True,text=True);(target/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  p=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=10);(target/'stdout.log').write_text(p.stdout);assert p.returncode==0;actual=[json.loads(line) for line in p.stdout.splitlines()];assert actual==expected,(name,actual,expected)
  rows.append({'case':name,'strict_C17':True,'doxygen_warnings':0,'native_printed_arrays':actual,'matches_saved_chronology':True,'heap_ownership':'stack array; Intercambio has no allocator calls','actually_displayed_UI_main':False})
 (out/'report.json').write_text(json.dumps({'rows':rows,'scope':'offline proposal only, not a product main; other10 excluded'},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rows,ensure_ascii=False))
