"""Contrato pedagógico canónico de los seis TAD secuenciales."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Mapping

SEQUENTIAL_FRAME_SCHEMA_VERSION = 2
SEQUENTIAL_STRUCTURES = {"stack", "queue", "priority_queue", "linked_list", "circular_list", "sublist"}
SEQUENTIAL_LEARNING_CATALOG: dict[str, dict[str, Any]] = {
 "stack":{"objective":"Explicar LIFO y las reasignaciones de TOP.","prior":["punteros","malloc/free"],"mastery":["predice TOP","explica apilar y desapilar"]},
 "queue":{"objective":"Explicar FIFO y la coordinación de FRONT y BACK.","prior":["punteros","extremos"],"mastery":["predice el frente","resuelve la transición unitaria"]},
 "priority_queue":{"objective":"Distinguir orden de llegada de selección estable por prioridad.","prior":["cola","comparación"],"mastery":["sigue el candidato","resuelve empates"]},
 "linked_list":{"objective":"Mantener conectividad desde HEAD al insertar, buscar y eliminar.","prior":["nodos","enlaces"],"mastery":["sigue actual/anterior","evita perder nodos"]},
 "circular_list":{"objective":"Conservar el enlace último→primero y terminar recorridos con seguridad.","prior":["lista enlazada","ciclos"],"mastery":["verifica el cierre","explica la condición de salida"]},
 "sublist":{"objective":"Gestionar padres e hijos sin alterar ramas ajenas.","prior":["listas","doble nivel de punteros"],"mastery":["identifica propiedad","demuestra aislamiento"]},
}
_INVARIANTS = {
 "stack":"TOP identifica el único extremo de entrada y salida; el orden observable es LIFO.",
 "queue":"FRONT alcanza BACK; se inserta por BACK y se retira por FRONT; vacía implica ambos NULL.",
 "priority_queue":"Los enlaces conservan llegada y la selección usa prioridad con desempate estable.",
 "linked_list":"Todos los nodos son alcanzables exactamente una vez desde HEAD.",
 "circular_list":"El último nodo enlaza al primero y el recorrido termina al volver al inicio.",
 "sublist":"Cada hijo pertenece a un padre y las ramas no activas permanecen sin cambios.",
}

# Cada ejemplo prepara el estado exclusivamente mediante operaciones públicas reales.
SEQUENTIAL_GUIDED_EXAMPLES: dict[str,list[dict[str,Any]]] = {
 "stack":[
  {"id":"empty","label":"Vacío: desapilar","kind":"empty","seed":[],"operation":"desapilar","payload":{},"lesson":"La guarda evita leer TOP cuando es NULL."},
  {"id":"one","label":"Un elemento","kind":"one","seed":[["apilar",{"value":10}]],"operation":"desapilar","payload":{},"lesson":"TOP avanza y el nodo retirado se libera."},
  {"id":"lifo","label":"Secuencia LIFO","kind":"several","seed":[["apilar",{"value":10}],["apilar",{"value":20}],["apilar",{"value":30}]],"operation":"desapilar","payload":{},"lesson":"El último insertado, 30, sale primero."},
  {"id":"repeated","label":"Valores repetidos","kind":"repeated","seed":[["apilar",{"value":7}],["apilar",{"value":7}]],"operation":"desapilar","payload":{},"lesson":"Valores iguales ocupan reservas distintas."}],
 "queue":[
  {"id":"empty","label":"Vacío: desencolar","kind":"empty","seed":[],"operation":"desencolar","payload":{},"lesson":"FRONT y BACK permanecen NULL."},
  {"id":"fifo","label":"Secuencia FIFO","kind":"several","seed":[["encolar",{"value":10}],["encolar",{"value":20}],["encolar",{"value":30}]],"operation":"desencolar","payload":{},"lesson":"El primer insertado, 10, sale primero."},
  {"id":"extremes","label":"Único a vacío","kind":"extremes","seed":[["encolar",{"value":5}]],"operation":"desencolar","payload":{},"lesson":"Al retirar el único nodo cambian ambos extremos."}],
 "priority_queue":[
  {"id":"tie","label":"Empate de prioridad","kind":"repeated","seed":[["encolar",{"value":10,"priority":2}],["encolar",{"value":20,"priority":2}],["encolar",{"value":30,"priority":1}]],"operation":"desencolar","payload":{},"lesson":"El empate conserva el orden de llegada."},
  {"id":"empty","label":"Cola vacía","kind":"empty","seed":[],"operation":"desencolar","payload":{},"lesson":"No existe candidato seleccionable."}],
 "linked_list":[
  {"id":"not-found","label":"Valor no encontrado","kind":"not_found","seed":[["insertar_final",{"value":4}],["insertar_final",{"value":8}]],"operation":"buscar_elemento","payload":{"value":99},"lesson":"El recorrido llega a NULL sin alterar enlaces."},
  {"id":"invalid","label":"Posición inválida","kind":"invalid","seed":[["insertar_final",{"value":4}]],"operation":"insertar_posicion","payload":{"value":9,"position":8},"lesson":"La guarda rechaza el índice fuera del rango."},
  {"id":"repeated","label":"Eliminar repetidos","kind":"repeated","seed":[["insertar_final",{"value":3}],["insertar_final",{"value":3}],["insertar_final",{"value":5}]],"operation":"eliminar_repetidos","payload":{"value":3},"lesson":"Cada coincidencia se desconecta y libera."}],
 "circular_list":[
  {"id":"circularity","label":"Una vuelta completa","kind":"several","seed":[["insertar_final",{"value":1}],["insertar_final",{"value":2}],["insertar_final",{"value":3}]],"operation":"buscar_posiciones","payload":{"value":9},"lesson":"El ciclo termina al volver a HEAD, no en NULL."},
  {"id":"one","label":"Único nodo circular","kind":"one","seed":[["insertar_final",{"value":1}]],"operation":"eliminar_inicio","payload":{},"lesson":"HEAD y TAIL se anulan al liberar el único nodo."}],
 "sublist":[
  {"id":"isolation","label":"Aislamiento de ramas","kind":"several","seed":[["insertar_padre",{"parent":1}],["insertar_padre",{"parent":2}],["insertar_hijo",{"parent":1,"child":11}],["insertar_hijo",{"parent":2,"child":21}]],"operation":"insertar_hijo","payload":{"parent":1,"child":12},"lesson":"Cambiar el padre 1 no altera la rama del padre 2."},
  {"id":"not-found","label":"Padre no encontrado","kind":"not_found","seed":[["insertar_padre",{"parent":1}]],"operation":"insertar_hijo","payload":{"parent":99,"child":4},"lesson":"No se crea un hijo huérfano."}],
}

class SequentialFrameValidationError(ValueError): pass

def _concept(line:str)->str:
 n=line.lower().lstrip()
 if "malloc" in n or "calloc" in n:return "allocation"
 if "free(" in n:return "free"
 if n.startswith(("if ","if(","while ","while(","} while ","} while(","for ","for(")):return "condition"
 if "return" in n:return "return"
 if "->" in n and "=" in n:return "link"
 if "=" in n:return "assignment"
 if "(" in n and ")" in n:return "call"
 return "invariant"

def _items(state:Mapping[str,Any])->list[Any]:
 value=state.get("items"); return list(value) if isinstance(value,list) else []

def _objects(state:Mapping[str,Any])->list[dict[str,Any]]:
 if state.get("sublist_delete_model"):
  return [{"id":node["id"],"address":f"0x{node['id']}","status":node["status"],"allocated":True,"freed":False,"fields":{"nro":node["value"],"sgte":node["next"],**({"sub":node["sub"]} if node["kind"]=="parent" else {})}} for node in state.get("heap_nodes",[])]
 if (state.get("clear_model") or state.get("delete_model") or state.get("search_model") or state.get("insert_model") or state.get("circular_insert_model")):
  return [{"id":node["id"],"address":f"0x{node['id']}","status":node["status"],"allocated":True,"freed":False,"fields":{("valor" if state.get("circular_insert_model") else "nro"):node["value"],"sgte":node["next"]}} for node in state.get("heap_nodes",[])]
 out=[]; seen:dict[str,int]={}
 for i,item in enumerate(_items(state)):
  fields=deepcopy(item) if isinstance(item,dict) else {"value":item}
  signature=json.dumps(fields,sort_keys=True,ensure_ascii=False,default=str); seen[signature]=seen.get(signature,0)+1
  token=hashlib.sha1(signature.encode("utf-8")).hexdigest()[:6].upper(); address=f"0xN-{token}-{seen[signature]}"
  out.append({"id":address.replace("0x", ""),"address":address,"status":"linked","allocated":True,"freed":False,"fields":fields})
 temporaries=state.get("temporaries")
 if isinstance(temporaries,Mapping):
  for name,value in temporaries.items():
   fields=deepcopy(value) if isinstance(value,Mapping) else {"value":value}; allocated=bool(fields.pop("allocated",False))
   out.append({"id":str(name),"address":f"0xTMP-{name}","status":"temporary","allocated":allocated,"freed":False,"fields":fields})
 return out

def _scalars(state:Mapping[str,Any])->dict[str,Any]:
 return {str(k):v for k,v in state.items() if k not in {"items","temporaries","title","kind"} and not isinstance(v,(dict,list))}

def _ctype(value:Any,name:str)->str:
 if name in {"head","tail","front","back","top","root","aux","actual","anterior","prev","next","siguiente","objetivo","objetivoPrev","delante","atras","p","q","t","lista","ant","temp","nuevo","cabeza","cola","curr","old_head","nodo"}:return "CPNodo *" if name in {"objetivo","objetivoPrev","delante","atras"} else "struct Nodo *"
 if isinstance(value,bool):return "bool"
 if isinstance(value,int) or str(value).lstrip("-").isdigit():return "int"
 return "const char *"

def _expression(line:str)->str:
 match=re.search(r"\b(?:if|while|for)\s*\((.*)\)",line); return match.group(1).strip() if match else line.strip()

def _substitute(expr:str,payload:Mapping[str,Any],before:Mapping[str,Any],structure_id:str="")->str:
 if structure_id=="sublist" and before.get("sublist_delete_model"):
  frames=before.get("sublist_frames",[])
  active=frames[-1] if frames else {"parameters":{},"locals":{}}
  values={**active["parameters"],**active["locals"]}
  nodes={node["id"]:node for node in before.get("heap_nodes",[])}
  result=expr
  if values.get("lista")=="&sublista":result=re.sub(r"\*\s*lista\b",str(before["head"]),result)
  if "lista_hijos" in values:result=re.sub(r"\*\s*lista_hijos\b",str(before["sub_head"]),result)
  for pointer in ("actual","anterior","padre","next"):
   node=nodes.get(values.get(pointer))
   if node:
    for member,key in (("nro","value"),("sgte","next"),("sub","sub")):
     if key in node:result=re.sub(rf"\b{pointer}\s*->\s*{member}\b",str(node[key]),result)
   elif values.get(pointer)=="NULL" and expr.startswith("padre == NULL ||"):
    result=result.replace("padre->sub", "no evaluado por cortocircuito")
  for name in sorted(values,key=len,reverse=True):
   result=re.sub(rf"\b{re.escape(name)}\b",str(values[name]),result)
  return result
 aliases={"value":"valor","priority":"prioridad","position":"posicion","parent":"padre","child":"hijo","relative":"referencia"}
 values={**_scalars(before),**{str(k):v for k,v in payload.items()}}
 values.update({aliases[k]:v for k,v in payload.items() if k in aliases})
 temporaries=before.get("temporaries") if isinstance(before.get("temporaries"),Mapping) else {}
 for pointer in re.findall(r"\b(aux|actual|anterior|prev|next|siguiente|objetivo|objetivoPrev|nuevo|p|q|t|lista|cola|cabeza|curr|old_head|nodo)\b",expr):
  values[pointer]=f"0xTMP-{pointer}" if pointer in temporaries else before.get(pointer)
 result=expr
 if before.get("insert_model") and "position" in payload:values["pos"]=payload["position"]
 linked_parameter=structure_id=="linked_list" and (before.get("clear_model") or before.get("delete_model") or before.get("insert_model") or bool(re.search(r"\*\s*lista\b",expr)))
 if linked_parameter:
  # lista is a valid pointer to the caller's head variable, even when *lista
  # is NULL. Resolve dereference before substituting the parameter name.
  result=re.sub(r"\*\s*lista\b",str(before.get("head",before.get("lista","NULL"))),result)
  values["lista"]="&cabeza"
  if before.get("delete_model") or before.get("insert_model"):
   nodes={node["id"]:node for node in before.get("heap_nodes",[])}
   for pointer in ("p","ant","q","temp","t"):
    node=nodes.get(before.get(pointer))
    if node:
     for member,key in (("nro","value"),("sgte","next")):
      result=re.sub(rf"\b{pointer}\s*->\s*{member}\b",str(node[key]),result)
 if structure_id=="linked_list" and before.get("search_model"):
  node=next((node for node in before.get("heap_nodes",[]) if node["id"]==before.get("q")),None)
  if node:
   result=re.sub(r"\bq\s*->\s*nro\b",str(node["value"]),result)
 if structure_id=="circular_list" and before.get("circular_insert_model"):
  values["lista"]="&lc"
  for member in ("cabeza","cola","cantidad"):
   result=re.sub(rf"\blista\s*->\s*{member}\b",str(before[member]),result)
  nodes={node["id"]:node for node in before.get("heap_nodes",[])}
  for pointer in ("nodo","nuevo","actual","anterior","prev","curr","next","old_head"):
   node=nodes.get(before.get(pointer))
   if node:
    for member,key in (("valor","value"),("sgte","next")):
     result=re.sub(rf"\b{pointer}\s*->\s*{member}\b",str(node[key]),result)
 if structure_id=="priority_queue":
  values.update(cola="&cp", valor="&valor", prioridad="&prioridad")
  for member in ("delante","atras","cantidad"):
   target=before.get(member)
   if target is None:
    items=_items(before); target=len(items) if member=="cantidad" else (("N1" if member=="delante" else f"N{len(items)}") if items else "NULL")
   result=re.sub(rf"\bcola\s*->\s*{member}\b",str(target),result)
  ids=before.get("node_ids") or [f"N{i+1}" for i in range(len(_items(before)))]
  nodes=dict(zip(ids,_items(before)))
  for temporary in temporaries.values():
   if isinstance(temporary,Mapping) and temporary.get("node_id"):nodes[temporary["node_id"]]=temporary
  for pointer in ("actual","objetivo"):
   item=nodes.get(before.get(pointer),{})
   for member,key in (("prioridad","priority"),("valor","value")):
    if key in item:result=re.sub(rf"\b{pointer}\s*->\s*{member}\b",str(item[key]),result)
 if structure_id=="queue":
  # Public operations pass a valid queue address, including empty queues.
  # Resolve member accesses before replacing pointer names.
  values["q"]="&cola"
  for member in ("delante","atras"):
   target=before.get(member)
   if target is None:
    items=_items(before)
    target=("N1" if member=="delante" else f"N{len(items)}") if items else "NULL"
   result=re.sub(rf"\bq\s*->\s*{member}\b",str(target),result)
 for name in sorted(values,key=len,reverse=True):
  rendered=(str(values[name]) if (structure_id=="circular_list" and before.get("circular_insert_model") and name in {"lista","cabeza","cola","nuevo","nodo","actual","anterior","destino","prev","curr","next","old_head"}) or (structure_id=="linked_list" and (before.get("clear_model") or before.get("delete_model") or before.get("insert_model")) and name in {"lista","q","head","p","ant","temp","t"}) or (linked_parameter and name=="lista") or (structure_id=="linked_list" and before.get("search_model") and name in {"lista","q","head"}) else "&cola" if structure_id=="queue" and name=="q" else "NULL" if values[name] is None else repr(values[name]))
  result=re.sub(rf"\b{re.escape(name)}\b",rendered,result)
 return result

def _pointers(before:Mapping[str,Any],after:Mapping[str,Any],line:str,structure_id:str="")->list[dict[str,Any]]:
 names={"head","tail","front","back","top","root","aux","actual","anterior","prev","next","siguiente","objetivo","objetivoPrev","p","q","t","ant","temp","lista","nuevo","delante","atras","cabeza","cola","curr","old_head","nodo","destino"}; names.update(re.findall(r"\b([A-Za-z_]\w*)\s*->",line))
 bt=before.get("temporaries") if isinstance(before.get("temporaries"),Mapping) else {}; at=after.get("temporaries") if isinstance(after.get("temporaries"),Mapping) else {}; rows=[]
 for name in sorted(names):
  old=before.get(name,bt.get(name)); new=after.get(name,at.get(name))
  clear=structure_id=="linked_list" and (before.get("clear_model") or after.get("clear_model") or before.get("delete_model") or after.get("delete_model") or before.get("insert_model") or after.get("insert_model"))
  if clear and name=="lista":old=new="&cabeza"
  if clear and name=="q" and old is None and new is None:continue
  if before.get("delete_model") and not after.get("delete_model") and name in {"p","ant","q","temp","lista"} and old is not None:new="fuera de ámbito"
  if before.get("insert_model") and not after.get("insert_model") and name in {"lista","q","t"}:new="fuera de ámbito"
  if before.get("search_model") and not after.get("search_model") and name in {"lista","q"}:new="fuera de ámbito"
  if structure_id=="circular_list" and before.get("circular_insert_model") and not after.get("circular_insert_model") and name in {"lista","nuevo","nodo","actual","anterior","destino","prev","curr","next","old_head"}:new="fuera de ámbito"
  if structure_id=="circular_list" and before.get("circular_insert_model") and name=="nodo" and old is not None and new is None:new="fuera de ámbito"
  if structure_id=="queue" and name=="q":old=new="&cola"
  if structure_id=="priority_queue" and name=="cola":old=new="&cp"
  if structure_id=="queue" and name=="aux" and "q->atras = aux" in line and new is None:
   # The final trace snapshot omits local scope, but this assignment event
   # still observes aux before cola_encolar returns to its caller.
   new=before.get("aux") or f"N{len(_items(after))}"
  if structure_id=="queue" and name=="aux" and isinstance(old,Mapping) and new is not None:
   # Publishing a node does not assign a different value to local aux.
   old=new
  if old is None and new is None and name not in line:continue
  rows.append({"name":name,"type":"int *" if structure_id=="circular_list" and name=="destino" else ("Tlista *" if name=="lista" else "Tlista") if clear else "Tlista" if structure_id=="linked_list" and (before.get("search_model") or after.get("search_model")) else ("ColaPrioridad *" if name=="cola" else "CPNodo *") if structure_id=="priority_queue" else (("const ListaCircular *" if before.get("circular_search_model") or after.get("circular_search_model") else "ListaCircular *") if name=="lista" else "LCirNodo *") if structure_id=="circular_list" and (before.get("circular_insert_model") or after.get("circular_insert_model")) else "struct Cola *" if structure_id=="queue" and name=="q" else "struct NodoCola *" if structure_id=="queue" else "struct Nodo *","previous_target":old,"target":new,"changed":old!=new,"alias":"mismo destino" if old==new and new is not None else None})
 return rows

def _invariant_holds(structure_id:str,state:Mapping[str,Any])->tuple[bool,str]:
 items=_items(state); size=state.get("size"); empty=state.get("empty")
 common=(size in (None,len(items))) and (empty is None or bool(empty)==(len(items)==0))
 if structure_id=="circular_list" and state.get("circular_insert_model"):
  live={node["id"] for node in state.get("heap_nodes",[])}
  safe=all(node["next"] in live|{"NULL","sin inicializar"} for node in state.get("heap_nodes",[]))
  safe=safe and state.get("cabeza") in live|{"NULL"} and state.get("cola") in live|{"NULL"}
  return safe and size==state.get("cantidad"), f"cantidad C={state.get('cantidad')}; alcanzables={len(items)}; cola->sgte={state.get('cola_sgte')}; ciclo termina en {state.get('cycle_target')}. El anillo completo y el contador se restauran al concluir la operación."

 if structure_id=="priority_queue" and items:
  expected=min(range(len(items)),key=lambda i:NumberProxy(items[i].get("priority"),i))
  common=common and (state.get("scan_complete") is False or state.get("candidate_detached") is True or state.get("out_index",expected)==expected)
 if structure_id=="sublist":
  # Parent values are data, not identities: C permits duplicates and each
  # allocated Nodo remains a distinct parent. Validate identity uniqueness.
  ids=[item.get("id") for item in items if isinstance(item,Mapping)]
  common=common and len(ids)==len(items) and len(ids)==len(set(map(str,ids)))
 return common, f"size={size}, nodos={len(items)}, empty={empty}"

def NumberProxy(value:Any,fallback:int)->tuple[float,int]:
 try:return (float(value),fallback)
 except (TypeError,ValueError):return (float("inf"),fallback)

def build_sequential_frame(*,structure_id:str,operation_name:str,payload:Mapping[str,Any],step:Mapping[str,Any],success:bool)->dict[str,Any]:
 # HTML fields arrive as strings, but validated linked-list inputs execute as C ints.
 if structure_id in {"linked_list","circular_list"}:
  payload=dict(payload)
  for name in ("value","position"):
   if name in payload:
    try:payload[name]=int(payload[name])
    except (TypeError,ValueError):pass
 if structure_id not in SEQUENTIAL_STRUCTURES:raise SequentialFrameValidationError(f"TAD secuencial desconocido: {structure_id}.")
 line=str(step.get("line_text") or ""); concept=_concept(line); before=dict(step.get("state_snapshot") or {}); after=dict(step.get("state_after") or {}); changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
 normalized_line=line.lower()
 clear_exit=structure_id=="linked_list" and operation_name in {"limpiar","eliminar_elemento","eliminar_repetidos","buscar_elemento","insertar_inicio","insertar_final","lista_insertar_elemento"} and line.strip()=="}"
 if structure_id=="circular_list" and operation_name in {"limpiar","invertir"} and line.strip()=="}":clear_exit=True
 if structure_id=="sublist" and operation_name in {"eliminar_padre","limpiar"} and line.strip()=="}" and before.get("active_function") in {"destruir_hijos","sublista_destruir"}:clear_exit=True
 if clear_exit:concept="return"
 condition=None
 if concept=="condition":
  expr=_expression(line); result=step.get("condition_result"); consequence="Se ejecuta el cuerpo" if result is True else "Se omite el cuerpo o termina el ciclo" if result is False else "La traza conserva la ruta observada"
  condition={"source":expr,"substituted":_substitute(expr,payload,before,structure_id),"result":result,"consequence":consequence}
 sb,sa=_scalars(before),_scalars(after); names=list(dict.fromkeys([*payload.keys(),*sb.keys(),*sa.keys()])); variables=[]
 for raw in names:
  name=str(raw); previous=sb.get(name,payload.get(raw)); value=sa.get(name,payload.get(raw)); variables.append({"name":name,"type":_ctype(value,name),"previous":previous,"value":value,"changed":previous!=value,"meaning":"Parámetro de entrada" if raw in payload else "Estado observable del TAD"})
 if structure_id=="linked_list" and operation_name in {"limpiar","eliminar_elemento","eliminar_repetidos","buscar_elemento"}:
  for variable in variables:
   if variable["name"]=="lista":
    if operation_name in {"eliminar_elemento","eliminar_repetidos"} and not after.get("delete_model"):variable["value"]="fuera de ámbito"
    variable.update(type="Tlista *",meaning="Parámetro: dirección de la variable cabeza del llamador (&cabeza es una dirección simbólica).")
   elif variable["name"]=="head":
    variable.update(type="Tlista",meaning="Cabeza del llamador; HEAD es una etiqueta didáctica, no otra variable C." if operation_name=="buscar_elemento" else "Valor de *lista; HEAD es una etiqueta didáctica, no otra variable C.")
   elif variable["name"] in {"q","p","ant","temp"}:
    if operation_name in {"eliminar_elemento","eliminar_repetidos"} and not after.get("delete_model") and variable["name"] in {"p","ant","q","temp"}:variable["value"]="fuera de ámbito"
    variable.update(type="Tlista",meaning="Alias local; tras free su valor es indeterminado y no se lee.")
 if structure_id=="linked_list" and operation_name=="buscar_elemento":
  for variable in variables:
   if variable["name"] in {"lista","q"}:
    variable.update(type="Tlista",meaning="Puntero pasado por valor; lista conserva la cabeza, q recorre sin modificar enlaces.")
   if variable["name"] in {"i","encontrado"}:
    variable.update(type="int",meaning="Posición actual desde 1." if variable["name"]=="i" else "Bandera entera: 1 si hubo coincidencia, 0 inicialmente.")
   if variable["name"] in {"lista","q","i","encontrado"} and not after.get("search_model"):
    variable["value"]="fuera de ámbito"
 if structure_id=="linked_list" and operation_name in {"insertar_inicio","insertar_final","lista_insertar_elemento"}:
  for variable in variables:
   if variable["name"]=="lista":variable.update(type="Tlista *",meaning="Dirección de la cabeza del llamador; no es NULL aunque la cadena esté vacía.")
   elif variable["name"] in {"head","q","t"}:variable.update(type="Tlista",meaning="Identidad estable de nodo; asignar un enlace no libera memoria.")
   elif variable["name"]=="i":variable.update(type="int",meaning="Posición base actual desde 1.")
   if variable["name"] in {"lista","q","t","i"} and not after.get("insert_model"):variable["value"]="fuera de ámbito"
 if structure_id=="circular_list" and operation_name in {"insertar_inicio","insertar_final","eliminar_inicio","buscar_posiciones","eliminar_primero","limpiar","invertir"}:
  for variable in variables:
   if variable["name"]=="lista":variable.update(type="ListaCircular *",meaning="Dirección del TAD del llamador; &lc no es NULL aunque cabeza sea NULL.")
   elif variable["name"] in {"cabeza","cola","nuevo","nodo"}:variable.update(type="LCirNodo *",meaning="Identidad estable; nodo pertenece al constructor y nuevo al llamador.")
   elif variable["name"]=="actual":variable.update(type="LCirNodo *",meaning="Alias local del nodo retirado; desconectar no libera la reserva. Después de free, su valor es indeterminado y no se lee.")
   elif variable["name"]=="anterior":variable.update(type="LCirNodo *",meaning="Alias del predecesor circular; comparte reserva con actual cuando hay un solo nodo. Si se libera esa reserva, su valor es indeterminado.")
   elif variable["name"] in {"size","cantidad"}:variable.update(type="int",meaning="Campo cantidad real de C; puede diferir de los nodos alcanzables durante la publicación.")
   elif variable["name"]=="reachable_count":variable.update(type="int",meaning="Conteo didáctico de identidades alcanzables, no una variable C.")
   if variable["name"] in {"lista","nuevo","nodo","actual","anterior","destino","encontrados","pos","capacidad","prev","curr","next","old_head"} and not after.get("circular_insert_model"):variable["value"]="fuera de ámbito"
   if variable["name"]=="nodo" and "nodo" in before and "nodo" not in after:variable["value"]="fuera de ámbito"
 if structure_id=="circular_list" and operation_name in {"limpiar","invertir"}:
  for variable in variables:
   if variable["name"] in {"actual","next","prev","curr","old_head"}:variable.update(type="LCirNodo *",meaning="Alias local de una reserva estable; los enlaces cambian solo en sus escrituras C. Una reserva liberada no se vuelve a leer.")
 if structure_id=="circular_list" and operation_name=="buscar_posiciones":
  for variable in variables:
   if variable["name"]=="lista":variable.update(type="const ListaCircular *",meaning="Dirección de un TAD válido; la búsqueda no modifica sus nodos.")
   elif variable["name"]=="destino":variable.update(type="int *",meaning="Arreglo del llamador para posiciones desde 1; no es un nodo de la lista.")
   elif variable["name"]=="actual":variable.update(type="LCirNodo *",meaning="Alias que recorre el anillo una vuelta sin modificar enlaces ni liberar nodos.")
   elif variable["name"] in {"encontrados","pos","capacidad"}:variable.update(type="int",meaning="Coincidencias totales, posición desde 1 o capacidad del arreglo del llamador.")
 memory_state=None
 if structure_id=="linked_list" and operation_name in {"eliminar_elemento","eliminar_repetidos"}:
  memory_state=deepcopy(after if after.get("delete_model") else before)
  if not after.get("delete_model"):
   memory_state.update({key:deepcopy(value) for key,value in after.items()})
   
   for local in ("p","ant","q","temp"):memory_state.pop(local,None)
   memory_state["scope_ended"]=True
 if structure_id=="linked_list" and operation_name=="buscar_elemento":
  memory_state=deepcopy(after if after.get("search_model") else before)
  if not after.get("search_model"):
   memory_state.update({key:deepcopy(value) for key,value in after.items()})
   for local in ("q","i","encontrado"):memory_state.pop(local,None)
   memory_state["scope_ended"]=True
 if structure_id=="linked_list" and operation_name in {"insertar_inicio","insertar_final","lista_insertar_elemento"}:
  memory_state=deepcopy(after if after.get("insert_model") else before)
  if not after.get("insert_model"):
   memory_state.update({key:deepcopy(value) for key,value in after.items()})
   for local in ("q","t","i"):memory_state.pop(local,None)
   memory_state["scope_ended"]=True
 if structure_id=="circular_list" and operation_name in {"insertar_inicio","insertar_final","eliminar_inicio","buscar_posiciones","eliminar_primero","limpiar","invertir"}:
  memory_state=deepcopy(after if after.get("circular_insert_model") else before)
  if not after.get("circular_insert_model"):
   memory_state.update({key:deepcopy(value) for key,value in after.items()})
   for local in ("nuevo","nodo","actual","anterior","destino","encontrados","pos","capacidad","prev","curr","next","old_head"):memory_state.pop(local,None)
   memory_state["scope_ended"]=True
 bh,ah=_objects(before),_objects(after); addresses={o["address"] for o in ah}; freed=[{**o,"status":"freed","allocated":False,"freed":True} for o in bh if o["address"] not in addresses]
 # En apilar, aux no se libera: el mismo nodo pasa de temporal a enlazado al
 # publicar *p = aux. La diferencia estructural no debe convertirse en free.
 if structure_id=="stack" and "*p = aux" in line:
  freed=[]
 # En desapilar, aux es un alias del TOP retirado. La liberación ocurre solo
 # en free(aux), aunque ya no pertenezca a la cadena alcanzable desde *p.
 if structure_id=="stack" and "free(aux)" in line:
  value=before.get("aux_value")
  freed=[{"id":"aux","address":"0xTMP-aux","status":"freed","allocated":False,"freed":True,"fields":{"nro":value}}]
 if structure_id=="queue" and any(token in line for token in ("q->delante = aux", "q->atras->sgte = aux", "q->atras = aux")):
  freed=[]
 if structure_id=="queue" and "free(aux)" in line:
  value=before.get("aux_value")
  freed=[{"id":"aux","address":"0xTMP-aux","status":"freed","allocated":False,"freed":True,"fields":{"nro":value}}]
 if structure_id=="priority_queue":
  if any(token in normalized_line for token in ("cola->delante = objetivo->sgte", "objetivoprev->sgte = objetivo->sgte", "cola->delante = next")):
   # Unlinking only removes reachability; the allocation stays live until free.
   freed=[]
  if any(token in normalized_line for token in ("cola->delante = nuevo", "cola->atras->sgte = nuevo")):
   # Publishing the temporary node transfers ownership into the live chain.
   freed=[]
  if "free(objetivo)" in line or "free(aux)" in line:
   temporary_name="objetivo" if "free(objetivo)" in line else "aux"
   temporary=before.get("temporaries",{}).get(temporary_name,{})
   fields={key:value for key,value in temporary.items() if key!="allocated"}
   freed=[{"id":temporary_name,"address":f"0xTMP-{temporary_name}","status":"freed","allocated":False,"freed":True,"fields":fields}]
 # En listas, q se integra a la cadena; no se libera al desaparecer de la
 # zona temporal. p/temp solo se consideran liberados en su free explícito.
 if structure_id=="linked_list" and ("*lista = q" in line or "t->sgte = q" in line):
  freed=[]
 if structure_id=="linked_list" and "free(q)" in line:
  value=before.get("temporaries",{}).get("q",{}).get("nro",before.get("removed_value"))
  freed=[{"id":"q","address":"0xTMP-q","status":"freed","allocated":False,"freed":True,"fields":{"nro":value}}]
 if structure_id=="linked_list" and ("free(p)" in line or "free(temp)" in line):
  value=before.get("removed_value", before.get("freed_p"))
  freed=[{"id":"p" if "free(p)" in line else "temp","address":"0xTMP-p","status":"freed","allocated":False,"freed":True,"fields":{"nro":value}}]
 if structure_id=="circular_list":
  if any(token in normalized_line for token in ("anterior->sgte = actual->sgte", "lista->cabeza = actual->sgte", "lista->cabeza = next", "lista->cabeza = null")):
   # Rewiring roots or links only disconnects a node; the next free releases it.
   freed=[]
  if "free(actual)" in normalized_line:
   value=before.get("actual_value", before.get("freed_node"))
   freed=[{"id":"actual","address":"0xTMP-actual","status":"freed","allocated":False,"freed":True,"fields":{"valor":value}}]
 if structure_id=="sublist":
  if any(token in normalized_line for token in ("*lista = actual->sgte", "anterior->sgte = actual->sgte", "padre->sub = actual->sgte", "previo->sgte = actual->sgte", "*lista_hijos = next", "*lista = next")):
   # A pointer update only detaches a node; the following C free releases it.
   freed=[]
  if "free(actual)" in normalized_line:
   temporary=before.get("temporaries",{}).get("actual",{}) if isinstance(before.get("temporaries"),Mapping) else {}
   detached=before.get("detached_parent") if isinstance(before.get("detached_parent"),Mapping) else {}
   if temporary.get("kind")=="child":
    fields={"nro":temporary.get("value")}
    object_id="actual"
   elif detached:
    fields={"nro":detached.get("parent"),"children":list(detached.get("children") or [])}
    object_id=detached.get("id","actual")
   else:
    fields={}
    object_id="actual"
   freed=[{"id":object_id,"address":f"0xTMP-{object_id}","status":"freed","allocated":False,"freed":True,"fields":fields}]
 if structure_id=="linked_list" and operation_name=="limpiar":
  # Heap membership tracks allocation, not merely root reachability. No
  # inferred free on unlinking or local-scope exit; only the explicit C call.
  freed=[]
  if "free(q)" in line:
   freed_id=after.get("freed_q")
   freed=[{**obj,"status":"freed","allocated":False,"freed":True} for obj in bh if obj["id"]==freed_id]
 if structure_id=="linked_list" and operation_name in {"eliminar_elemento","eliminar_repetidos"}:
  ah=_objects(memory_state)
  freed=[]
  if "free(p)" in line or "free(temp)" in line:
   freed_id=after.get("freed_temp") if "free(temp)" in line else after.get("freed_p")
   freed=[{**obj,"status":"freed","allocated":False,"freed":True} for obj in bh if obj["id"]==freed_id]
 if structure_id=="linked_list" and operation_name=="buscar_elemento":
  ah=_objects(memory_state)
  freed=[]
 if structure_id=="linked_list" and operation_name in {"insertar_inicio","insertar_final","lista_insertar_elemento"}:
  ah=_objects(memory_state)
  freed=[]
  if "free(q)" in line:
   freed=[{**obj,"status":"freed","allocated":False,"freed":True} for obj in bh if obj["id"]==after.get("freed_q")]
 if structure_id=="circular_list" and operation_name in {"insertar_inicio","insertar_final","eliminar_inicio","buscar_posiciones","eliminar_primero","limpiar","invertir"}:
  ah=_objects(memory_state)
  freed=[]  # Publication and scope exit do not release any allocation.
  if operation_name in {"eliminar_inicio","eliminar_primero","limpiar"} and line.strip()=="free(actual);":
   freed=[{**obj,"status":"freed","allocated":False,"freed":True} for obj in bh if obj["id"]==after.get("freed_actual")]

 transition="free" if concept=="free" else "allocate" if concept=="allocation" else "link" if concept=="link" else "stable"; action=("Finaliza la función: termina el ámbito de los locales; los nodos restantes no se liberan." if clear_exit else line.strip() or f"Ejecutar {operation_name}."); invariant_holds,invariant_evidence=_invariant_holds(structure_id,after)
 loop_line=line.lstrip().startswith(("while","for","} while"))
 frame={"schema_version":SEQUENTIAL_FRAME_SCHEMA_VERSION,"structure":structure_id,"operation":operation_name,"concept":concept,"phase":{"id":f"{operation_name}-{concept}","label":concept.replace("_"," ").title(),"goal":action},"condition":condition,"memory_state":memory_state,"variables":variables,"pointers":_pointers(before,after,line,structure_id),"heap_objects":ah,"heap_transition":{"kind":transition,"before":bh,"after":ah,"freed":freed,"dangling_references":[]},"call_stack":[{"function":str(step.get("function_name") or operation_name),"parameters":({"lista":"&cabeza","valor":payload.get("value"),**({"pos":payload.get("position")} if operation_name=="lista_insertar_elemento" else {})} if structure_id=="linked_list" and operation_name in {"insertar_inicio","insertar_final","lista_insertar_elemento"} else {"lista":before.get("head","NULL"),"valor":payload.get("value")} if structure_id=="linked_list" and operation_name=="buscar_elemento" else {"lista":"&cabeza",**({"valor":payload.get("value")} if operation_name in {"eliminar_elemento","eliminar_repetidos"} else {})} if structure_id=="linked_list" and operation_name in {"limpiar","eliminar_elemento","eliminar_repetidos","buscar_elemento"} else {"lista":"&lc","valor":payload.get("value")} if structure_id=="circular_list" and operation_name in {"insertar_inicio","insertar_final","eliminar_inicio","buscar_posiciones","eliminar_primero","limpiar","invertir"} else dict(payload)),"return":step.get("result") if concept=="return" else None,"continuation":"llamador / siguiente instrucción"}],"loop":{"active":loop_line,"condition":_expression(line) if loop_line else None,"exit":condition["consequence"] if condition and loop_line else None},"state_changes":changed,"invariant":{"text":("HEAD alcanza la cadena; reservas temporales aún no publicadas permanecen vivas hasta publicación o free." if structure_id=="linked_list" and operation_name in {"limpiar","eliminar_elemento","eliminar_repetidos","insertar_inicio","insertar_final","lista_insertar_elemento"} else _INVARIANTS[structure_id]),"holds":invariant_holds,"symbol":"✓" if invariant_holds else "✗","evidence":invariant_evidence},"narration":{"basic":f"{SEQUENTIAL_LEARNING_CATALOG[structure_id]['objective']} Observa: {action}","intermediate":f"En {operation_name}, «{concept}» conecta esta línea con {', '.join(changed) if changed else 'un estado sin cambios visibles'}.","advanced":f"Semántica C: «{action}». Hay {len(bh)} objeto(s) antes y {len(ah)} después; la ruta no ejecutada no aparece."},"source":{"line_index":step.get("line_index"),"line_text":line}}
 if structure_id=="circular_list" and operation_name in {"insertar_inicio","insertar_final","eliminar_inicio","buscar_posiciones","eliminar_primero","limpiar","invertir"}:
  caller={"function":"lcir_"+operation_name,"parameters":{"lista":"&lc","valor":payload.get("value")},"return":(line.strip()=="return true;") if not after.get("circular_insert_model") else None,"continuation":"llamador / siguiente instrucción"}
  if operation_name=="eliminar_inicio":caller["parameters"]={"lista":"&lc"}
  if operation_name in {"limpiar","invertir"}:caller.update(function="lcir_destruir" if operation_name=="limpiar" else "lcir_invertir",parameters={"lista":"&lc"});caller["return"]=None
  if operation_name=="buscar_posiciones":
   caller["parameters"]={"lista":"&lc","valor":payload.get("value"),"destino":"&posiciones","capacidad":before.get("capacidad")}
   caller["return"]=(before.get("encontrados",0) if line.strip()=="return encontrados;" else 0) if not after.get("circular_insert_model") else None

  if operation_name in {"eliminar_inicio","eliminar_primero","limpiar"}:frame["heap_transition"]["indeterminate_locals"]=[{"name":name,"former_allocation":after.get("freed_actual"),"status":"indeterminado; no se lee"} for name in ("actual","anterior","next") if after.get(name)=="indeterminado (liberado)"]
  frame["call_stack"]=[caller]
  if after.get("active_function")=="lcir_crear_nodo":
   frame["call_stack"].append({"function":"lcir_crear_nodo","parameters":{"valor":payload.get("value")},"return":None,"continuation":"asignar resultado a nuevo al retornar"})
  frame["invariant"]["text"]="Las identidades y enlaces representan cada escritura C; el anillo completo y cantidad se restablecen al terminar."
 if structure_id=="sublist" and operation_name in {"eliminar_hijo","eliminar_padre","limpiar","hijos_de","insertar_padre","insertar_hijo"} and (after.get("sublist_delete_model") or before.get("sublist_delete_model")):
  if not after.get("sublist_delete_model"):
   canonical=after
   after=deepcopy(before)
   for name in ("lista","padre","actual","anterior","next","lista_hijos","owner_parent","sub_head","valor_padre","valor_hijo","destino","capacidad","usados","nuevo","valor"):
    after.pop(name,None)
   after.update(canonical,sublist_frames=[],active_function="llamador",scope_ended=True)
   if line.strip() in {"return true;","return false;"}:after["returned"]=line.strip()=="return true;"
   if literal_return:=re.fullmatch(r"return (-?\d+);",line.strip()):after["returned"]=int(literal_return.group(1))
   if line.strip()=="return nuevo;":after["returned"]=before["sublist_frames"][-1]["locals"]["nuevo"]
   if line.strip()=="return NULL;":after["returned"]="NULL"
  memory=deepcopy(after)
  frame["memory_state"]=memory
  bh,ah=_objects(before),_objects(after)
  freed=[{**obj,"status":"freed","allocated":False,"freed":True} for obj in bh if line.strip()=="free(actual);" and obj["id"]==after.get("freed_actual")]
  frame.update(heap_objects=ah)
  frame["heap_transition"].update(before=bh,after=ah,freed=freed)
  bframes=before.get("sublist_frames",[]);aframes=after.get("sublist_frames",[])
  ba=bframes[-1] if bframes else {"function":"llamador","parameters":{},"locals":{}}
  aa=aframes[-1] if aframes else {"function":"llamador","parameters":{},"locals":{}}
  bv={**ba["parameters"],**ba["locals"]};av={**aa["parameters"],**aa["locals"]}
  names=list(dict.fromkeys([*bv,*av]))
  def pointer_type(name,fn):
   if name=="lista_hijos":return "Sublista **"
   if name=="destino":return "int *"
   if name=="padre" and fn=="sublista_copiar_hijos":return "const Nodo *"
   if name=="actual" and fn=="sublista_copiar_hijos":return "const Sublista *"
   if name=="lista" and fn in {"sublista_eliminar_padre_primero","sublista_destruir","sublista_insertar_padre_final"}:return "Nodo **"
   return "Sublista *" if name in {"actual","anterior","next","nuevo"} and fn in {"sublista_eliminar_hijo_primero","destruir_hijos","crear_hijo","sublista_insertar_hijo_final"} else "Nodo *"
  # A caller suspended during a helper call keeps its own live locals.
  # Key by C function scope and name, so both actual variables remain distinct.
  def scoped_values(frames):
   return {(entry["function"],name):(value,name in entry["parameters"]) for entry in frames for name,value in {**entry["parameters"],**entry["locals"]}.items()}
  previous=scoped_values(bframes);current=scoped_values(aframes)
  keys=list(dict.fromkeys([*previous,*current]))
  frame["variables"]=[];frame["pointers"]=[]
  for scope,name in keys:
   old=previous.get((scope,name),(None,False))[0]
   value,param=current.get((scope,name),("fuera de ámbito",False))
   ctype=pointer_type(name,scope) if name in {"lista","padre","actual","anterior","next","lista_hijos","destino","nuevo"} else "int"
   status="fuera de ámbito" if (scope,name) not in current else "activo" if scope==aa["function"] else "suspendido durante llamada"
   frame["variables"].append({"name":name,"type":ctype,"previous":old,"value":value,"changed":old!=value,"scope":scope,"scope_state":status,"meaning":"Parámetro C pasado por valor" if param else "Alias local; indeterminado tras free, no se lee" if ctype.endswith("*") else "Escalar local C; su actualización no modifica enlaces"})
   if name in {"lista","padre","actual","anterior","next","lista_hijos","destino","nuevo"}:
    frame["pointers"].append({"name":name,"type":ctype,"previous_target":old,"target":value,"previous_scope":scope,"scope":scope,"scope_state":status,"changed":old!=value,"alias":"mismo destino" if old==value else None})
  exiting=line.strip().startswith("return ") or clear_exit
  frame["call_stack"]=deepcopy(bframes if exiting else aframes)
  frame["call_stack_after"]=deepcopy(aframes)
  if frame["call_stack"] and exiting:
   frame["call_stack"][-1]["return"]=None if clear_exit else after.get("returned")
  if line.strip().startswith("Nodo *padre = sublista_buscar_padre("):
   complete="padre" in aa["locals"]
   frame["concept"]="assignment" if complete else "call"
   frame["call_phase"]="completed" if complete else "enter"
   frame["narration"]["basic"]="La llamada termina y asigna su resultado a padre." if complete else "Entra a la búsqueda; padre aún no tiene un valor asignado."
  if line.strip().startswith("return sublista_eliminar_hijo_primero("):
   complete=not aframes
   frame["concept"]="return" if complete else "call"
   frame["call_phase"]="completed" if complete else "enter"
   frame["narration"]["basic"]="Retorna al llamador el bool producido por el auxiliar." if complete else "Entra al auxiliar de eliminación; aún no retorna al llamador."
   if not complete and frame["call_stack"]:frame["call_stack"][-1]["return"]=None
  if line.strip().startswith("return sublista_copiar_hijos("):
   complete=not aframes
   frame["concept"]="return" if complete else "call"
   frame["call_phase"]="completed" if complete else "enter"
   if not complete and frame["call_stack"]:frame["call_stack"][-1]["return"]=None
   frame["narration"]["basic"]="Retorna la cantidad realmente copiada; la estructura permanece intacta." if complete else "Entra al auxiliar de copia; aún no se han escrito los siguientes elementos del destino."
  if line.strip()=="destruir_hijos(&actual->sub);":
   # The source line is revisited after the helper's closing-brace event.
   complete=step.get("state_snapshot",{}).get("helper_completed",False)
   frame["concept"]="call";frame["call_phase"]="completed" if complete else "enter"
   frame["narration"]["basic"]="Finaliza la liberación de hijos; el padre sigue vivo hasta su free." if complete else "Entra al auxiliar con la dirección del campo sub; actual del padre permanece en su propio ámbito."
  if operation_name=="hijos_de" and line.strip() in {"destino[usados] = actual->nro;","usados++;"}:
   frame["concept"]="assignment"
   frame["narration"]["basic"]="Copia el valor del hijo actual a destino[usados]; todavía no incrementa usados ni cambia nodos." if line.strip().startswith("destino[") else "Incrementa usados después de la escritura; no modifica el heap ni añade otra copia."
   frame["narration"]["intermediate"]="Copia nro del hijo actual al arreglo destino. usados conserva su valor hasta la próxima instrucción; ninguna reserva o enlace cambia." if line.strip().startswith("destino[") else "Incrementa el contador escalar usados. La posición del destino ya se escribió en el paso anterior; este incremento no escribe otra posición ni modifica la estructura."
   frame["narration"]["advanced"]="Copia un int de actual->nro a destino[usados]. No asigna punteros ni modifica el heap; la reserva del hijo sigue viva y usados aún no se incrementa." if line.strip().startswith("destino[") else "Incrementa únicamente el int local usados tras completar la copia. No cambia actual ni los enlaces; el avance del alias actual ocurre en una instrucción posterior."
  if operation_name in {"insertar_padre","insertar_hijo"}:
   text=""
   if line.strip() in {"nuevo = crear_padre(valor_padre);","nuevo = crear_hijo(valor_hijo);"}:
    complete=aa["locals"].get("nuevo") not in {None,"sin inicializar"}
    frame["concept"]="assignment" if complete else "call";frame["call_phase"]="completed" if complete else "enter"
    text="El constructor ya retornó; ahora asigna su puntero a nuevo del llamador. La reserva sigue sin publicarse." if complete else "Entra al constructor. nuevo del llamador sigue sin inicializar y conserva su propio ámbito."
   elif line.strip().startswith("return sublista_insertar_hijo_final("):
    complete=not aframes;frame["concept"]="return" if complete else "call";frame["call_phase"]="completed" if complete else "enter"
    if not complete and frame["call_stack"]:frame["call_stack"][-1]["return"]=None
    text="Retorna el bool real del auxiliar de inserción." if complete else "Entra al auxiliar de inserción del primer padre encontrado; todavía no retorna."
   elif "malloc(sizeof(" in line:
    frame["concept"]="allocation";text="malloc reserva memoria sin inicializar nro, sgte ni sub. El nuevo nodo aún no pertenece a la cadena alcanzable."
   elif line.strip()=="nuevo->nro = valor;":
    frame["concept"]="assignment";text="Inicializa solo el int nro del nodo reservado. Los campos de puntero no se inicializan en esta instrucción."
   elif line.strip() in {"nuevo->sgte = NULL;","nuevo->sub = NULL;"}:
    text="Inicializa únicamente este campo de puntero en NULL. La reserva todavía no se ha publicado en la estructura."
   elif line.strip()=="return nuevo;":text="Retorna el puntero al nodo vivo; salir del ámbito no libera la reserva."
   elif line.strip() in {"*lista = nuevo;","actual->sgte = nuevo;","padre->sub = nuevo;"}:frame["concept"]="link";text="Publica el nodo ya inicializado mediante esta única asignación de enlace; conserva las demás reservas y ramas."
   if text:frame["narration"]={level:text for level in ("basic","intermediate","advanced")}
  frame["phase"].update(id=f"{operation_name}-{frame['concept']}",label=frame["concept"].replace("_"," ").title())
  frame["heap_transition"]["kind"]="free" if freed else "allocate" if frame["concept"]=="allocation" else "link" if line.strip() in {"padre->sub = actual->sgte;","anterior->sgte = actual->sgte;","*lista = nuevo;","actual->sgte = nuevo;","padre->sub = nuevo;"} else "stable"
  frame["heap_transition"]["indeterminate_locals"]=[{"name":name,"former_allocation":after.get("freed_actual"),"scope":aa["function"],"status":"indeterminado; no se lee"} for name,value in av.items() if value=="indeterminado (liberado)"]
  live={node["id"] for node in after.get("heap_nodes",[])}
  safe=all(node["next"] in live|{"NULL","sin inicializar"} and (node["kind"]!="parent" or node["sub"] in live|{"NULL","sin inicializar"}) for node in after.get("heap_nodes",[]))
  frame["invariant"].update(text="Cada reserva conserva identidad y propiedad; desconectar un hijo no lo libera. Solo free elimina la reserva; las demás ramas y todos los padres permanecen vivos.",holds=safe,symbol="✓" if safe else "✗",evidence=f"{len(live)} reservas vivas; raíz {after.get('head')}; ámbito {aa['function']}")
  if operation_name=="eliminar_padre":frame["invariant"]["text"]="Desconectar el padre no lo libera. Su reserva vive mientras se liberan sus hijos; free del padre ocurre al terminar el auxiliar. Las demás ramas conservan identidades y enlaces."
  if operation_name=="limpiar":frame["invariant"]["text"]="Cada padre permanece vivo mientras se liberan sus hijos. Después se actualiza la raíz y se libera ese padre; el cierre del ámbito no añade liberaciones."
  if operation_name=="hijos_de":frame["invariant"]["text"]="La consulta no cambia reservas ni enlaces. Cada escritura copia solo el valor del hijo actual al destino; usados aumenta en la instrucción siguiente."
  if operation_name in {"insertar_padre","insertar_hijo"}:frame["invariant"]["text"]="Cada reserva conserva identidad. malloc no inicializa campos; la cadena solo incorpora el nodo en la instrucción de publicación, después de inicializarlo."
 return frame


def validate_sequential_frame(frame:Mapping[str,Any],*,source_code:str="")->None:
 required={"schema_version","structure","operation","concept","phase","condition","variables","pointers","heap_objects","heap_transition","call_stack","loop","state_changes","invariant","narration","source"}; missing=sorted(required.difference(frame))
 if missing:raise SequentialFrameValidationError(f"Frame secuencial incompleto: {', '.join(missing)}.")
 if frame["schema_version"]!=SEQUENTIAL_FRAME_SCHEMA_VERSION:raise SequentialFrameValidationError("Versión no soportada.")
 if set(frame["narration"])!={"basic","intermediate","advanced"}:raise SequentialFrameValidationError("Faltan niveles.")
 if frame["heap_transition"].get("dangling_references"):raise SequentialFrameValidationError("Referencia a memoria liberada.")
 if source_code:
  rows=source_code.replace("\r\n","\n").split("\n"); index=frame["source"].get("line_index"); text=frame["source"].get("line_text"); unresolved=index is None or not text
  if not unresolved and (not isinstance(index,int) or not 0<=index<len(rows) or rows[index]!=text):raise SequentialFrameValidationError("La línea C no coincide con el frame.")

def sequential_frame_schema()->dict[str,Any]:
 return {"$id":"visualestruct://sequential/pedagogical-frame/v2","version":SEQUENTIAL_FRAME_SCHEMA_VERSION,"structures":sorted(SEQUENTIAL_STRUCTURES),"levels":["basic","intermediate","advanced"]}
