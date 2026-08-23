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
 if n.startswith(("if ","if(","while ","while(","for ","for(")):return "condition"
 if "return" in n:return "return"
 if "->" in n and "=" in n:return "link"
 if "=" in n:return "assignment"
 if "(" in n and ")" in n:return "call"
 return "invariant"

def _items(state:Mapping[str,Any])->list[Any]:
 value=state.get("items"); return list(value) if isinstance(value,list) else []

def _objects(state:Mapping[str,Any])->list[dict[str,Any]]:
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
 if name in {"head","tail","front","back","top","root","aux","actual","anterior"}:return "struct Nodo *"
 if isinstance(value,bool):return "bool"
 if isinstance(value,int) or str(value).lstrip("-").isdigit():return "int"
 return "const char *"

def _expression(line:str)->str:
 match=re.search(r"\b(?:if|while|for)\s*\((.*)\)",line); return match.group(1).strip() if match else line.strip()

def _substitute(expr:str,payload:Mapping[str,Any],before:Mapping[str,Any])->str:
 aliases={"value":"valor","priority":"prioridad","position":"posicion","parent":"padre","child":"hijo","relative":"referencia"}
 values={**_scalars(before),**{str(k):v for k,v in payload.items()}}
 values.update({aliases[k]:v for k,v in payload.items() if k in aliases})
 temporaries=before.get("temporaries") if isinstance(before.get("temporaries"),Mapping) else {}
 for pointer in re.findall(r"\b(aux|actual|anterior|nuevo|p|q|t|lista|cola)\b",expr):
  values[pointer]=f"0xTMP-{pointer}" if pointer in temporaries else None
 result=expr
 for name in sorted(values,key=len,reverse=True):
  rendered="NULL" if values[name] is None else repr(values[name]); result=re.sub(rf"\b{re.escape(name)}\b",rendered,result)
 return result

def _pointers(before:Mapping[str,Any],after:Mapping[str,Any],line:str)->list[dict[str,Any]]:
 names={"head","tail","front","back","top","root","aux","actual","anterior","p","q","t","nuevo"}; names.update(re.findall(r"\b([A-Za-z_]\w*)\s*->",line))
 bt=before.get("temporaries") if isinstance(before.get("temporaries"),Mapping) else {}; at=after.get("temporaries") if isinstance(after.get("temporaries"),Mapping) else {}; rows=[]
 for name in sorted(names):
  old=before.get(name,bt.get(name)); new=after.get(name,at.get(name))
  if old is None and new is None and name not in line:continue
  rows.append({"name":name,"type":"struct Nodo *","previous_target":old,"target":new,"changed":old!=new,"alias":"mismo destino" if old==new and new is not None else None})
 return rows

def _invariant_holds(structure_id:str,state:Mapping[str,Any])->tuple[bool,str]:
 items=_items(state); size=state.get("size"); empty=state.get("empty")
 common=(size in (None,len(items))) and (empty is None or bool(empty)==(len(items)==0))
 if structure_id=="priority_queue" and items:
  expected=min(range(len(items)),key=lambda i:NumberProxy(items[i].get("priority"),i))
  common=common and state.get("out_index",expected)==expected
 if structure_id=="sublist":
  parents=[item.get("parent") for item in items if isinstance(item,Mapping)]; common=common and len(parents)==len(set(map(str,parents)))
 return common, f"size={size}, nodos={len(items)}, empty={empty}"

def NumberProxy(value:Any,fallback:int)->tuple[float,int]:
 try:return (float(value),fallback)
 except (TypeError,ValueError):return (float("inf"),fallback)

def build_sequential_frame(*,structure_id:str,operation_name:str,payload:Mapping[str,Any],step:Mapping[str,Any],success:bool)->dict[str,Any]:
 if structure_id not in SEQUENTIAL_STRUCTURES:raise SequentialFrameValidationError(f"TAD secuencial desconocido: {structure_id}.")
 line=str(step.get("line_text") or ""); concept=_concept(line); before=dict(step.get("state_snapshot") or {}); after=dict(step.get("state_after") or {}); changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
 condition=None
 if concept=="condition":
  expr=_expression(line); result=step.get("condition_result"); consequence="Se ejecuta el cuerpo" if result is True else "Se omite el cuerpo o termina el ciclo" if result is False else "La traza conserva la ruta observada"
  condition={"source":expr,"substituted":_substitute(expr,payload,before),"result":result,"consequence":consequence}
 sb,sa=_scalars(before),_scalars(after); names=list(dict.fromkeys([*payload.keys(),*sb.keys(),*sa.keys()])); variables=[]
 for raw in names:
  name=str(raw); previous=sb.get(name,payload.get(raw)); value=sa.get(name,payload.get(raw)); variables.append({"name":name,"type":_ctype(value,name),"previous":previous,"value":value,"changed":previous!=value,"meaning":"Parámetro de entrada" if raw in payload else "Estado observable del TAD"})
 bh,ah=_objects(before),_objects(after); addresses={o["address"] for o in ah}; freed=[{**o,"status":"freed","allocated":False,"freed":True} for o in bh if o["address"] not in addresses]
 transition="free" if concept=="free" else "allocate" if concept=="allocation" else "link" if concept=="link" else "stable"; action=line.strip() or f"Ejecutar {operation_name}."; invariant_holds,invariant_evidence=_invariant_holds(structure_id,after)
 return {"schema_version":SEQUENTIAL_FRAME_SCHEMA_VERSION,"structure":structure_id,"operation":operation_name,"concept":concept,"phase":{"id":f"{operation_name}-{concept}","label":concept.replace("_"," ").title(),"goal":action},"condition":condition,"variables":variables,"pointers":_pointers(before,after,line),"heap_objects":ah,"heap_transition":{"kind":transition,"before":bh,"after":ah,"freed":freed,"dangling_references":[]},"call_stack":[{"function":str(step.get("function_name") or operation_name),"parameters":dict(payload),"return":step.get("result") if concept=="return" else None,"continuation":"llamador / siguiente instrucción"}],"loop":{"active":line.lstrip().startswith(("while","for")),"condition":_expression(line) if line.lstrip().startswith(("while","for")) else None,"exit":condition["consequence"] if condition and line.lstrip().startswith(("while","for")) else None},"state_changes":changed,"invariant":{"text":_INVARIANTS[structure_id],"holds":invariant_holds,"symbol":"✓" if invariant_holds else "✗","evidence":invariant_evidence},"narration":{"basic":f"{SEQUENTIAL_LEARNING_CATALOG[structure_id]['objective']} Observa: {action}","intermediate":f"En {operation_name}, «{concept}» conecta esta línea con {', '.join(changed) if changed else 'un estado sin cambios visibles'}.","advanced":f"Semántica C: «{action}». Hay {len(bh)} objeto(s) antes y {len(ah)} después; la ruta no ejecutada no aparece."},"source":{"line_index":step.get("line_index"),"line_text":line}}

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
