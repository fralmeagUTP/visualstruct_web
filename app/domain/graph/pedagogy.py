"""Canonical pedagogical frames and guided examples for graph algorithms."""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Mapping

GRAPH_FRAME_SCHEMA_VERSION = 1
GRAPH_EDGE_POLICY = {"self_loops":"allowed","parallel_edges":"update_existing_weight","neighbor_order":"vertex/edge insertion order"}
GRAPH_ALGORITHMS = {"create_graph","insert_vertex","remove_vertex","insert_edge","remove_edge","run_bfs","run_dfs","run_dijkstra","run_bellman_ford","run_prim","run_kruskal"}
GRAPH_LEARNING_CATALOG = {
 "construction":{"objective":"Relacionar lista de adyacencia, dibujo y memoria C.","prior":["punteros","conjuntos"],"mastery":["distingue arco/arista","justifica grados y enlaces"]},
 "run_bfs":{"objective":"Explicar exploración por niveles mediante una cola FIFO.","prior":["cola","adyacencia"],"mastery":["predice extracción","construye árbol BFS"]},
 "run_dfs":{"objective":"Explicar descenso y backtracking mediante pila o recursión.","prior":["pila","recursión"],"mastery":["predice descenso","explica retorno"]},
 "run_dijkstra":{"objective":"Explicar relajación y cierre con pesos no negativos.","prior":["cola de prioridad","caminos"],"mastery":["calcula relajación","reconstruye predecesores"]},
 "run_bellman_ford":{"objective":"Explicar relajaciones por pasadas y ciclos negativos.","prior":["caminos","ciclos"],"mastery":["predice cambios","detecta ciclo negativo"]},
 "run_prim":{"objective":"Construir un MST desde una frontera mínima.","prior":["árbol","corte"],"mastery":["predice candidata","verifica MST"]},
 "run_kruskal":{"objective":"Construir un MST con aristas ordenadas y Union-Find.","prior":["ordenamiento","conjuntos disjuntos"],"mastery":["predice rechazo","explica union"]},
}

GRAPH_GUIDED_EXAMPLES = [
 {"id":"empty","label":"Grafo vacío","directed":False,"vertices":[],"edges":[],"operation":"run_bfs","payload":{"start":"A"},"lesson":"Una entrada inválida termina sin inventar visitas."},
 {"id":"single","label":"Un solo vértice","directed":False,"vertices":["A"],"edges":[],"operation":"run_bfs","payload":{"start":"A"},"lesson":"La frontera contiene y extrae un único vértice."},
 {"id":"isolated","label":"Vértice aislado","directed":False,"vertices":["A","B","C"],"edges":[["A","B",1]],"operation":"run_bfs","payload":{"start":"C"},"lesson":"El recorrido solo cubre la componente alcanzable."},
 {"id":"disconnected","label":"Grafo desconectado","directed":False,"vertices":["A","B","C","D"],"edges":[["A","B",1],["C","D",1]],"operation":"run_dfs","payload":{"start":"A"},"lesson":"Una ejecución desde A no visita la otra componente."},
 {"id":"cycle","label":"Ciclo","directed":False,"vertices":["A","B","C"],"edges":[["A","B",1],["B","C",1],["C","A",1]],"operation":"run_dfs","payload":{"start":"A"},"lesson":"La marca impide visitar indefinidamente el ciclo."},
 {"id":"dag","label":"DAG","directed":True,"vertices":["A","B","C","D"],"edges":[["A","B",1],["A","C",1],["B","D",1],["C","D",1]],"operation":"run_dfs","payload":{"start":"A"},"lesson":"Un vértice puede tener varios predecesores sin formar ciclo."},
 {"id":"complete","label":"Completo pequeño","directed":False,"vertices":["A","B","C","D"],"edges":[["A","B",1],["A","C",1],["A","D",1],["B","C",1],["B","D",1],["C","D",1]],"operation":"run_bfs","payload":{"start":"A"},"lesson":"El orden de vecinos determina desempates."},
 {"id":"cheap-detour","label":"Ruta indirecta más barata","directed":True,"vertices":["A","B","C"],"edges":[["A","C",10],["A","B",2],["B","C",2]],"operation":"run_dijkstra","payload":{"start":"A","end":"C"},"lesson":"Menor costo no significa menor número de aristas."},
 {"id":"unreachable","label":"Destino inalcanzable","directed":True,"vertices":["A","B","C"],"edges":[["A","B",2]],"operation":"run_dijkstra","payload":{"start":"A","end":"C"},"lesson":"Inalcanzable no equivale a ciclo negativo."},
 {"id":"negative","label":"Peso negativo","directed":True,"vertices":["A","B","C"],"edges":[["A","B",4],["B","C",-2]],"operation":"run_bellman_ford","payload":{"start":"A","end":"C"},"lesson":"Bellman-Ford admite pesos negativos sin ciclo negativo."},
 {"id":"negative-cycle","label":"Ciclo negativo alcanzable","directed":True,"vertices":["A","B","C"],"edges":[["A","B",1],["B","C",-3],["C","B",1]],"operation":"run_bellman_ford","payload":{"start":"A","end":"C"},"lesson":"Una relajación adicional demuestra el ciclo negativo alcanzable."},
 {"id":"negative-cycle-unreachable","label":"Ciclo negativo no alcanzable","directed":True,"vertices":["A","B","C","D"],"edges":[["A","B",1],["C","D",-3],["D","C",1]],"operation":"run_bellman_ford","payload":{"start":"A","end":"B"},"lesson":"Solo los ciclos alcanzables desde el origen afectan sus distancias."},
 {"id":"equal-mst","label":"Varios MST de igual peso","directed":False,"vertices":["A","B","C","D"],"edges":[["A","B",1],["B","C",1],["C","D",1],["D","A",1],["A","C",2]],"operation":"run_kruskal","payload":{},"lesson":"Puede cambiar el conjunto de aristas y conservarse el peso óptimo."},
]

class GraphFrameValidationError(ValueError): pass

def _function_at(lines:list[str],index:int,default:str)->str:
 for row in reversed(lines[:index+1]):
  match=re.search(r"\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{\s*$",row)
  if match and match.group(1) not in {"if","while","for","switch"}:return match.group(1)
 return default

def _concept(line:str,debug:Mapping[str,Any])->str:
 stage=str(debug.get("stage") or "").lower(); normalized=line.lower()
 mapping={"init":"initialize","visit":"discover","extract_min":"extract","relax_edge":"examine","update_distance":"relax","detect_negative_cycle":"negative_cycle","select_edge":"consider","accept_edge":"accept","reject_edge":"reject","union":"union","complete":"return"}
 if stage in mapping:return mapping[stage]
 if "free(" in normalized:return "free"
 if "malloc" in normalized:return "allocation"
 if "encolar" in normalized or "push" in normalized:return "enqueue"
 if "desencolar" in normalized or "pop" in normalized:return "extract"
 if "find" in normalized:return "find"
 if "union" in normalized:return "union"
 if normalized.lstrip().startswith(("if ","if(","while ","while(","for ","for(")):return "condition"
 if "return" in normalized:return "return"
 return "assignment" if "=" in normalized else "examine"

def _objects(state:Mapping[str,Any])->dict[str,dict[str,Any]]:
 result={}
 for node in state.get("nodes",[]) if isinstance(state.get("nodes"),list) else []:
  if isinstance(node,Mapping):
   key=str(node.get("id"));result[f"vertex:{key}"]={"id":key,"kind":"vertex","address":f"0xVERT-{key}"}
 for edge in state.get("edges",[]) if isinstance(state.get("edges"),list) else []:
  if isinstance(edge,Mapping):
   key=f"{edge.get('source')}->{edge.get('target')}";result[f"edge:{key}"]={"id":key,"kind":"edge","address":f"0xEDGE-{key}"}
 return result

def _adjacency(state:Mapping[str,Any])->dict[str,list[dict[str,Any]]]:
 adjacency={str(node.get("id")):[] for node in state.get("nodes",[]) if isinstance(node,Mapping)}
 directed=bool(state.get("directed",False))
 for edge in state.get("edges",[]) if isinstance(state.get("edges"),list) else []:
  if not isinstance(edge,Mapping):continue
  source,target=str(edge.get("source")),str(edge.get("target"));weight=edge.get("weight")
  adjacency.setdefault(source,[]).append({"vertex":target,"weight":weight})
  if not directed and source!=target and not any(item["vertex"]==source for item in adjacency.setdefault(target,[])):adjacency[target].append({"vertex":source,"weight":weight})
 return adjacency

def _degrees(state:Mapping[str,Any],adjacency:Mapping[str,list[dict[str,Any]]])->list[dict[str,Any]]:
 directed=bool(state.get("directed",False));incoming={key:0 for key in adjacency}
 for source,items in adjacency.items():
  for item in items:incoming[str(item["vertex"])]=incoming.get(str(item["vertex"]),0)+1
 return [{"vertex":key,"degree":sum(2 if item["vertex"]==key else 1 for item in items) if not directed else len(items)+incoming.get(key,0),"out_degree":len(items),"in_degree":incoming.get(key,0)} for key,items in adjacency.items()]

def _edge_weight(state:Mapping[str,Any],active_edge:Any)->Any:
 if not isinstance(active_edge,(list,tuple)) or len(active_edge)<2:return None
 for edge in state.get("edges",[]) if isinstance(state.get("edges"),list) else []:
  if isinstance(edge,Mapping) and ((str(edge.get("source"))==str(active_edge[0]) and str(edge.get("target"))==str(active_edge[1])) or (not state.get("directed",False) and str(edge.get("source"))==str(active_edge[1]) and str(edge.get("target"))==str(active_edge[0]))):return edge.get("weight")
 return None

def build_graph_frame(*,operation_name:str,payload:Mapping[str,Any],step:Mapping[str,Any],source_lines:list[str],success:bool)->dict[str,Any]:
 line=str(step.get("line_text") or "");debug=step.get("debug") if isinstance(step.get("debug"),Mapping) else {};progress=debug.get("graph_progress") if isinstance(debug.get("graph_progress"),Mapping) else {};before=step.get("state_snapshot") or {};after=step.get("state_after") or {};index=int(step.get("line_index") or 0);concept=_concept(line,debug);function=_function_at(source_lines,index,operation_name)
 distances={str(k):v for k,v in (progress.get("distances") or {}).items()};previous={str(k):v for k,v in (progress.get("previous") or {}).items()};visited={str(v) for v in progress.get("visited",[])};selected=progress.get("selected");candidates=[str(v) for v in progress.get("candidates",[])];active_edges=progress.get("edges") or [];active_edge=progress.get("active_edge") or (active_edges[-1] if active_edges else None)
 vertices=[]
 for node in after.get("nodes",[]) if isinstance(after.get("nodes"),list) else []:
  node_id=str(node.get("id"));status="closed" if node_id in visited else "active" if node_id==str(selected) else "frontier" if node_id in candidates else "undiscovered";vertices.append({"id":node_id,"status":status,"distance":distances.get(node_id),"predecessor":previous.get(node_id)})
 auxiliary_kind={"run_bfs":"queue","run_dfs":"recursive_stack","run_dijkstra":"priority_queue","run_bellman_ford":"edge_passes","run_prim":"frontier","run_kruskal":"union_find"}.get(operation_name,"adjacency")
 auxiliary_items=list(progress.get("queue") or candidates) if auxiliary_kind=="queue" else list(progress.get("stack") or progress.get("nodes") or []) if auxiliary_kind=="recursive_stack" else candidates if auxiliary_kind in {"priority_queue","frontier"} else [{"vertex":key,"parent":value,"rank":(progress.get("ranks") or {}).get(key),"root":(progress.get("roots") or {}).get(key)} for key,value in (progress.get("parents") or {}).items()] if auxiliary_kind=="union_find" else list(progress.get("edge_order") or progress.get("nodes") or [])
 condition=None
 if concept=="condition":condition={"source":line.strip(),"substituted":line.strip(),"result":step.get("condition_result"),"consequence":debug.get("note") or "Solo continúa la rama registrada"}
 is_algorithm=operation_name.startswith("run_");large_graph=len(after.get("nodes") or [])+len(after.get("edges") or [])>120
 old,new=({}, {}) if is_algorithm else (_objects(before),_objects(after));allocated=[new[key] for key in new.keys()-old.keys()];freed=[old[key] for key in old.keys()-new.keys()]
 adjacency={} if large_graph else _adjacency(after);degrees=[] if large_graph else _degrees(after,adjacency);weight=_edge_weight(after,active_edge)
 invariant_names={"run_bfs":"cola FIFO y descubierto único","run_dfs":"pila y finalización coherentes","run_dijkstra":"distancia cerrada definitiva","run_bellman_ford":"relajaciones por pasada","run_prim":"frontera mínima acíclica","run_kruskal":"componentes distintas y orden de peso"};holds=bool(after.get("validation",True))
 variables=[{"name":str(k),"type":"int" if isinstance(v,(int,float)) else "Vertice","previous":v,"value":v,"changed":False,"meaning":"Parámetro de operación"} for k,v in payload.items()]
 for node_id in sorted(set(distances)|set(previous)):variables.append({"name":f"dist[{node_id}]","type":"double","previous":distances.get(node_id),"value":distances.get(node_id),"changed":False,"meaning":f"Distancia tentativa; predecesor={previous.get(node_id)}"})
 case=str(debug.get("stage") or concept);action=line.strip() or f"Ejecutar {operation_name}."
 relaxation=None
 if isinstance(active_edge,(list,tuple)) and len(active_edge)>=2 and operation_name in {"run_dijkstra","run_bellman_ford"}:
  source,target=str(active_edge[0]),str(active_edge[1]);source_distance=distances.get(source);old_distance=progress.get("old_distance",distances.get(target));candidate=progress.get("candidate_distance");candidate=candidate if candidate is not None else (None if source_distance is None or weight is None else source_distance+weight);relaxation={"source":source,"target":target,"weight":weight,"old_distance":old_distance,"candidate":candidate,"success":progress.get("relaxation_succeeded",concept=="relax"),"new_distance":distances.get(target),"predecessor":previous.get(target),"expression":f"dist[{target}] > dist[{source}] + {weight}"}
 weight=progress.get("edge_weight",weight)
 return {"schema_version":GRAPH_FRAME_SCHEMA_VERSION,"algorithm":operation_name,"concept":concept,"case":case,"phase":{"id":f"{operation_name}-{case}","label":case.replace('_',' ').title(),"goal":action},"source":{"line_index":step.get("line_index"),"line_text":line},"condition":condition,"variables":variables,"call_stack":[{"function":function,"depth":max(0,len(progress.get("stack") or progress.get("nodes") or [])-1) if operation_name=="run_dfs" else 0,"parameters":dict(payload),"active_vertex":selected,"continuation":"siguiente instrucción ejecutada"}],"auxiliary":{"kind":auxiliary_kind,"items":auxiliary_items,"selected":selected,"candidates":candidates,"iteration":progress.get("iteration") or debug.get("iteration"),"operation":"extract" if concept=="extract" else "insert" if concept in {"discover","enqueue"} else "inspect"},"vertices":vertices,"active_edge":{"from":str(active_edge[0]),"to":str(active_edge[1]),"weight":weight} if isinstance(active_edge,(list,tuple)) and len(active_edge)>=2 else None,"table":{"distances":distances,"previous":previous,"visited":sorted(visited),"rows":vertices},"relaxation":relaxation,"representation":{"directed":bool(after.get("directed",False)),"adjacency":adjacency,"degrees":degrees},"traversal":{"tree_edges":list(progress.get("tree_edges") or progress.get("edges") or []),"discovery_order":list(progress.get("nodes") or []),"active":selected,"component":progress.get("component",0)},"memory":{"objects_before":list(old.values()),"objects_after":list(new.values()),"allocated":allocated,"freed":freed,"null_checked":concept=="condition","dangling_references":[]},"state_before":before,"state_after":after,"invariant":{"name":invariant_names.get(operation_name,"representación consistente"),"holds":holds,"symbol":"✓" if holds else "✗","evidence":debug.get("note") or f"vertices={len(vertices)}, active_edge={active_edge}"},"narration":{"basic":f"{GRAPH_LEARNING_CATALOG.get(operation_name,GRAPH_LEARNING_CATALOG['construction'])['objective']} Observa: {debug.get('note') or action}","intermediate":f"El concepto «{concept}» usa {auxiliary_kind} y conserva el invariante indicado.","advanced":f"La función {function} ejecuta «{action}»; el frame procede de la ruta registrada por el backend."}}

def validate_graph_frame(frame:Mapping[str,Any],*,source_code:str="")->None:
 required={"schema_version","algorithm","concept","phase","source","condition","variables","call_stack","auxiliary","vertices","active_edge","table","memory","state_before","state_after","invariant","narration"};missing=required.difference(frame)
 if missing:raise GraphFrameValidationError(f"Campos faltantes: {sorted(missing)}")
 if frame["schema_version"]!=GRAPH_FRAME_SCHEMA_VERSION:raise GraphFrameValidationError("Versión no soportada")
 if set(frame["narration"])!={"basic","intermediate","advanced"}:raise GraphFrameValidationError("Faltan niveles")
 if frame["memory"].get("dangling_references"):raise GraphFrameValidationError("Referencia colgante")
 if source_code and frame["source"].get("line_text"):
  rows=source_code.replace("\r\n","\n").split("\n");idx=frame["source"].get("line_index")
  if not isinstance(idx,int) or not 0<=idx<len(rows) or rows[idx]!=frame["source"]["line_text"]:raise GraphFrameValidationError("Línea C inconsistente")

def graph_frame_schema()->dict[str,Any]:
 return {"$id":"visualestruct://graph/pedagogical-frame/v1","version":GRAPH_FRAME_SCHEMA_VERSION,"levels":["basic","intermediate","advanced"],"algorithms":sorted(GRAPH_ALGORITHMS)}
