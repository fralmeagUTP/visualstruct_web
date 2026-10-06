"""Canonical pedagogical contract for hierarchical structures."""
from __future__ import annotations
from copy import deepcopy
import re
from typing import Any, Mapping

HIERARCHICAL_FRAME_SCHEMA_VERSION = 1
HIERARCHICAL_STRUCTURES = {"abb", "avl", "red_black", "binary_heap"}
HIERARCHICAL_LEARNING_CATALOG = {
    "abb": {"objective": "Explicar orden, recursión y los tres casos de eliminación.", "prior": ["recursión", "punteros"], "mastery": ["predice la rama", "reconecta el subárbol retornado"]},
    "avl": {"objective": "Relacionar altura y FE con rotaciones LL, RR, LR y RL.", "prior": ["ABB", "altura"], "mastery": ["clasifica el caso", "justifica la rotación"]},
    "red_black": {"objective": "Aplicar reglas de color mediante recoloreos y rotaciones.", "prior": ["ABB", "rotaciones"], "mastery": ["identifica padre/abuelo/tío", "verifica black-height"]},
    "binary_heap": {"objective": "Relacionar índices del arreglo con la propiedad de min-heap.", "prior": ["arreglos", "árbol completo"], "mastery": ["calcula padre/hijos", "predice el intercambio"]},
}

HIERARCHICAL_GUIDED_EXAMPLES: dict[str, list[dict[str, Any]]] = {
 "abb":[
  {"id":"empty","label":"Árbol vacío","seed":[],"operation":"buscar","payload":{"value":7},"lesson":"La recursión termina al encontrar NULL."},
  {"id":"search","label":"Ruta de búsqueda","seed":[10,5,15,7],"operation":"buscar","payload":{"value":7},"lesson":"Cada comparación selecciona exactamente una rama."},
  {"id":"degenerate","label":"ABB degenerado","seed":[10,20,30,40],"operation":"altura","payload":{},"lesson":"Una entrada ordenada puede producir altura lineal."},
  {"id":"delete-leaf","label":"Eliminar hoja","seed":[10,5,15],"operation":"eliminar","payload":{"value":5},"lesson":"Una hoja se libera y retorna NULL."},
  {"id":"delete-one","label":"Eliminar con un hijo","seed":[10,5,3],"operation":"eliminar","payload":{"value":5},"lesson":"El único hijo reemplaza al nodo eliminado."},
  {"id":"delete-two","label":"Eliminar con dos hijos","seed":[10,5,15,12,18],"operation":"eliminar","payload":{"value":15},"lesson":"El sucesor conserva el orden ABB."}],
 "avl":[
  {"id":"ll","label":"Rotación LL","seed":[30,20],"operation":"insertar","payload":{"value":10},"lesson":"Dos descensos izquierdos requieren rotación derecha."},
  {"id":"rr","label":"Rotación RR","seed":[10,20],"operation":"insertar","payload":{"value":30},"lesson":"Dos descensos derechos requieren rotación izquierda."},
  {"id":"lr","label":"Rotación LR","seed":[30,10],"operation":"insertar","payload":{"value":20},"lesson":"Se rota primero el hijo y después el pivote."},
  {"id":"rl","label":"Rotación RL","seed":[10,30],"operation":"insertar","payload":{"value":20},"lesson":"La rotación doble reubica el nodo intermedio."},
  {"id":"delete-balance","label":"Rebalancear al eliminar","seed":[20,10,30,5,15,25,40,3],"operation":"eliminar","payload":{"value":40},"lesson":"La reducción de altura puede propagarse hacia la raíz."}],
 "red_black":[
  {"id":"black-parent","label":"Padre negro","seed":[10],"operation":"insertar","payload":{"value":5},"lesson":"No se requiere ajuste cuando el padre es negro."},
  {"id":"red-uncle","label":"Tío rojo","seed":[10,5,15],"operation":"insertar","payload":{"value":1},"lesson":"Padre y tío se vuelven negros; el abuelo propaga rojo."},
  {"id":"black-uncle-simple","label":"Tío negro: rotación simple","seed":[10,5],"operation":"insertar","payload":{"value":1},"lesson":"El caso exterior usa recoloreo y una rotación."},
  {"id":"black-uncle-double","label":"Tío negro: rotación doble","seed":[10,5],"operation":"insertar","payload":{"value":7},"lesson":"El caso interior se transforma antes del ajuste final."},
  {"id":"propagation","label":"Propagación de recoloreo","seed":[20,10,30,5,15,25,35],"operation":"insertar","payload":{"value":1},"lesson":"El foco puede ascender hasta la raíz."}],
 "binary_heap":[
  {"id":"empty","label":"Heap vacío","seed":[],"operation":"extraer_raiz","payload":{},"lesson":"No existe raíz que extraer."},
  {"id":"single","label":"Único elemento","seed":[7],"operation":"extraer_raiz","payload":{},"lesson":"La extracción deja tamaño cero."},
  {"id":"rise","label":"Ascenso por varios niveles","seed":[20,30,40,50],"operation":"insertar","payload":{"value":5},"lesson":"El nuevo valor compara repetidamente con su padre."},
  {"id":"descent","label":"Descenso al extraer","seed":[1,3,2,8,7,6,5],"operation":"extraer_raiz","payload":{},"lesson":"Se elige el hijo menor en cada nivel."},
  {"id":"tie","label":"Hijos empatados","seed":[1,4,4,8,9],"operation":"extraer_raiz","payload":{},"lesson":"El empate debe seguir el criterio estable del C."}],
}

class HierarchicalFrameValidationError(ValueError): pass

def _flatten(root: Any, depth: int = 0) -> list[dict[str, Any]]:
 if not isinstance(root, Mapping): return []
 value=root.get("value"); node={"id":f"n-{value}","address":f"0xNODE-{value}","value":value,"depth":depth,"height":root.get("height"),"balance":root.get("balance_factor"),"color":root.get("color")}
 return [node,*_flatten(root.get("left"),depth+1),*_flatten(root.get("right"),depth+1)]

def _node_map(state: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
 return {str(node["value"]):node for node in _flatten(state.get("root"))}

def _typed_variables(payload: Mapping[str, Any], before: Mapping[str, Any], after: Mapping[str, Any], active: str | None) -> list[dict[str, Any]]:
 variables=[]
 for name,value in payload.items():
  c_type="int" if isinstance(value,(int,float)) or str(value).lstrip("-").isdigit() else "const char *"
  variables.append({"name":str(name),"type":c_type,"meaning":"Parámetro de operación","previous":value,"value":value,"changed":False})
 if active is not None: variables.append({"name":"nodo_activo","type":"struct Nodo *","meaning":"Raíz local del frame recursivo","previous":f"0xNODE-{active}","value":f"0xNODE-{active}","changed":False})
 for name in ("size","height"):
  old,new=before.get(name),after.get(name)
  if old is not None or new is not None:variables.append({"name":name,"type":"size_t" if name=="size" else "int","meaning":"Tamaño del TAD" if name=="size" else "Altura observada","previous":old,"value":new,"changed":old!=new})
 return variables

def _memory_transition(before: Mapping[str, Any], after: Mapping[str, Any], concept: str) -> dict[str, Any]:
 old,new=_node_map(before),_node_map(after); allocated=[new[key] for key in new.keys()-old.keys()]; freed=[old[key] for key in old.keys()-new.keys()]
 return {"event":concept if concept in {"allocation","free","link"} else "none","objects_before":list(old.values()),"objects_after":list(new.values()),"allocated_objects":allocated,"freed_objects":freed,"null_checked":concept=="compare","null_check_required":concept=="allocation","dangling_references":[],"stable_addresses":True}

def _specific_invariant(structure_id: str, state: Mapping[str, Any], nodes: list[dict[str, Any]], array: list[Any]) -> dict[str, Any]:
 base=_invariant(structure_id,state); evidence=[]
 if structure_id=="abb":
  values=[node["value"] for node in nodes]; evidence=[{"node":node["value"],"lower":"-∞","upper":"+∞","holds":True} for node in nodes]; base["explanation"]="Todo valor del subárbol izquierdo es menor y todo valor del derecho es mayor."; base["ordered_values"]=sorted(values)
 elif structure_id=="avl":
  evidence=[{"node":node["value"],"height":node.get("height"),"balance_factor":node.get("balance"),"holds":node.get("balance") is None or abs(node["balance"])<=1} for node in nodes]; base["explanation"]="Cada nodo conserva orden ABB y factor de equilibrio entre -1 y 1."
 elif structure_id=="red_black":
  evidence=[{"node":node["value"],"color":node.get("color") or "negro","black_height":"verificada por backend","holds":True} for node in nodes]; base["explanation"]="La raíz es negra, no hay dos rojos consecutivos y todos los caminos tienen igual altura negra."; base["rules"]=["raíz negra","hijos de nodo rojo negros","black-height uniforme"]
 else:
  evidence=[{"index":i,"value":value,"parent_index":None if i==0 else (i-1)//2,"holds":i==0 or array[(i-1)//2]<=value} for i,value in enumerate(array)]; base["explanation"]="Es un árbol completo con prioridad parcial: no es un ABB ni un arreglo totalmente ordenado."
 base["evidence_by_node_or_path"]=evidence; return base

def _concept(line: str, debug: Mapping[str, Any]) -> str:
 n=line.lower(); stage=str(debug.get("stage") or "")
 if debug.get("rotation_hint") or "rotar_" in n or "avl_rs" in n:return "rotation"
 if "rbt_color" in n or "recolor" in stage:return "recolor"
 if "intercambiar(" in n:return "swap"
 if "malloc" in n:return "allocation"
 if "free(" in n:return "free"
 if n.lstrip().startswith(("if ","if(","while ","while(")):return "compare"
 if "return" in n:return "return"
 if "altura" in n or "->fe" in n:return "height"
 if re.search(r"\w+\s*=\s*\w+\([^;]*\)",n):return "descend"
 if "->" in n and "=" in n:return "link"
 if stage in {"search","fixup"}:return "descend"
 return "assignment" if "=" in n else "invariant"

def _function_at(lines:list[str],index:int,default:str)->str:
 for row in reversed(lines[:index+1]):
  match=re.search(r"\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{\s*$",row)
  if match and match.group(1) not in {"if","while","for","switch"}:return match.group(1)
 return default

def _substitute_condition(line: str, payload: Mapping[str, Any], active: str | None) -> str:
 result=line.strip()
 for name,value in payload.items():result=re.sub(rf"\b{re.escape(str(name))}\b",str(value),result)
 if active is not None:
  result=result.replace("nodo->valor",str(active)).replace("raiz->valor",str(active)).replace("n->valor",str(active))
 return result

def _branch_for(condition: Mapping[str, Any] | None, payload: Mapping[str, Any], active: str | None) -> str | None:
 if not condition or condition.get("result") is None:return None
 try:
  target=float(payload.get("value")); current=float(active) if active is not None else None
  if current is not None:return "izquierda" if target<current else "derecha" if target>current else "coincidencia"
 except (TypeError,ValueError):pass
 return "cuerpo" if condition.get("result") else "salida/else"

def _invariant(structure_id:str,state:Mapping[str,Any])->dict[str,Any]:
 validation=state.get("validation"); holds=True if validation is None else bool(validation)
 names={"abb":"orden ABB","avl":"orden ABB y |FE| ≤ 1","red_black":"reglas rojo-negro","binary_heap":"forma completa y padre ≤ hijos"}
 evidence=f"validation={validation}, size={state.get('size')}, height={state.get('height','n/a')}"
 return {"name":names[structure_id],"holds":holds,"symbol":"✓" if holds else "✗","evidence":evidence}

def build_hierarchical_frame(*,structure_id:str,operation_name:str,payload:Mapping[str,Any],step:Mapping[str,Any],source_lines:list[str],success:bool)->dict[str,Any]:
 if structure_id not in HIERARCHICAL_STRUCTURES:raise HierarchicalFrameValidationError(structure_id)
 line=str(step.get("line_text") or ""); debug=step.get("debug") if isinstance(step.get("debug"),Mapping) else {}; concept=_concept(line,debug); before=dict(step.get("state_snapshot") or {}); after=dict(step.get("state_after") or {}); idx=int(step.get("line_index") or 0)
 path=[str(v) for v in debug.get("path_keys",[])]; path_index=int(debug.get("path_index",-1)); active=path[path_index] if 0<=path_index<len(path) else None; function=_function_at(source_lines,idx,operation_name); condition=None
 if concept=="compare": condition={"source":line.strip(),"substituted":_substitute_condition(line,payload,active),"result":step.get("condition_result"),"consequence":debug.get("note") or "Solo continúa la ruta registrada"}
 adjustment=deepcopy(debug.get("rotation_hint")) if isinstance(debug.get("rotation_hint"),Mapping) else None
 if adjustment:
  rotation_type=str(adjustment.get("type") or "").upper(); simple_step=None
  if rotation_type in {"LR","RL"}:
   if "izquierda" in line.lower() or "ri(" in line.lower():simple_step="rotación izquierda"
   elif "derecha" in line.lower() or "rd(" in line.lower():simple_step="rotación derecha"
  adjustment={**adjustment,"message":debug.get("rotation_message") or debug.get("note"),"simple_step":simple_step,"sequence":{"LR":["rotación izquierda del hijo","rotación derecha del pivote"],"RL":["rotación derecha del hijo","rotación izquierda del pivote"]}.get(rotation_type,[rotation_type] if rotation_type else [])}
 nodes=_flatten(after.get("root")); array=list(after.get("array") or [])
 variables=_typed_variables(payload,before,after,active)
 action=line.strip() or f"Ejecutar {operation_name}."; case=str((adjustment or {}).get("type") or debug.get("stage") or concept)
 depth=max(0,path_index); stack=[]
 for stack_depth,key in enumerate(path[:depth+1] or ([active] if active is not None else [])):
  stack.append({"function":function,"depth":stack_depth,"parameters":dict(payload),"local_root":key,"local_root_address":f"0xNODE-{key}","return":active if concept=="return" and stack_depth==depth else None,"continuation":"reconectar el subárbol retornado" if concept in {"return","link"} else "siguiente instrucción del llamador"})
 if not stack:stack=[{"function":function,"depth":0,"parameters":dict(payload),"local_root":None,"local_root_address":"NULL","return":step.get("result") if concept=="return" else None,"continuation":"volver al llamador"}]
 branch=_branch_for(condition,payload,active)
 heap_active=debug.get("active_index"); parent=debug.get("parent_index"); children=debug.get("child_indices",[])
 if structure_id=="binary_heap" and heap_active is None and array: heap_active=min(max(path_index,0),len(array)-1)
 roles=deepcopy(debug.get("debug_ids")) if isinstance(debug.get("debug_ids"),Mapping) else {"node":active,"parent":path[path_index-1] if path_index>0 else None,"grandparent":path[path_index-2] if path_index>1 else None,"uncle":None}
 focus={"critical_node":debug.get("unbalanced_key"),"pivot":(adjustment or {}).get("pivot"),"transferred_subtree":(adjustment or {}).get("transferred_subtree"),"red_black_roles":roles,"heap_candidate":debug.get("candidate_index")}
 return {"schema_version":HIERARCHICAL_FRAME_SCHEMA_VERSION,"structure":structure_id,"operation":operation_name,"concept":concept,"case":case,"phase":{"id":f"{operation_name}-{case}","label":case.replace('_',' ').title(),"goal":action},"source":{"line_index":step.get("line_index"),"line_text":line},"condition":condition,"executed_branch":branch,"variables":variables,"call_stack":stack,"nodes":nodes,"array":{"values":array,"active_index":heap_active,"parent_index":parent,"child_indices":children,"valid_region":[i for i in range(len(array)) if i!=heap_active],"index_relations":{"parent":"(i - 1) / 2","left":"2 * i + 1","right":"2 * i + 2"}},"memory":_memory_transition(before,after,concept),"path":{"keys":path,"index":path_index,"active":active,"stage":debug.get("stage"),"bounds":{"lower":"-∞","upper":"+∞"},"successor":debug.get("successor")},"structural_focus":focus,"adjustment":adjustment,"return_propagation":{"active":concept in {"return","link"},"value":active,"reconnects_subtree":concept=="link"},"state_before":before,"state_after":after,"invariant":_specific_invariant(structure_id,after,nodes,array),"narration":{"basic":f"{HIERARCHICAL_LEARNING_CATALOG[structure_id]['objective']} Observa: {action}","intermediate":f"En {operation_name}, el caso «{case}» actúa sobre {active or 'la estructura'} y conserva el invariante indicado.","advanced":f"La función {function} ejecuta «{action}» en profundidad {depth}; solo se representa la ruta emitida por el backend."}}

def validate_hierarchical_frame(frame:Mapping[str,Any],*,source_code:str="")->None:
 required={"schema_version","structure","operation","concept","case","phase","source","condition","variables","call_stack","nodes","array","memory","path","adjustment","state_before","state_after","invariant","narration"}; missing=required.difference(frame)
 if missing:raise HierarchicalFrameValidationError(f"Campos faltantes: {sorted(missing)}")
 if frame["schema_version"]!=HIERARCHICAL_FRAME_SCHEMA_VERSION:raise HierarchicalFrameValidationError("Versión no soportada")
 if set(frame["narration"])!={"basic","intermediate","advanced"}:raise HierarchicalFrameValidationError("Faltan niveles")
 if frame["memory"].get("dangling_references"):raise HierarchicalFrameValidationError("Referencia colgante")
 if source_code and frame["source"].get("line_text"):
  rows=source_code.replace("\r\n","\n").split("\n"); index=frame["source"].get("line_index")
  if not isinstance(index,int) or not 0<=index<len(rows) or rows[index]!=frame["source"]["line_text"]:raise HierarchicalFrameValidationError("Línea C inconsistente")

def hierarchical_frame_schema()->dict[str,Any]:
 return {"$id":"visualestruct://hierarchical/pedagogical-frame/v1","version":HIERARCHICAL_FRAME_SCHEMA_VERSION,"structures":sorted(HIERARCHICAL_STRUCTURES),"levels":["basic","intermediate","advanced"]}
