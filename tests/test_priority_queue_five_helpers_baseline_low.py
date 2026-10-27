"""Permanent red baseline against immutable observed native helper results."""
from pathlib import Path
import json
import pytest
from app.domain.sequential import tad_cola_prioridad as raw
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-five-helpers-baseline-low'
from scripts.published_test_inputs import audit_input_path
ROWS=json.loads((audit_input_path(E/'report.json')).read_text(encoding='utf-8'))
@pytest.mark.parametrize('row',ROWS,ids=[r['ID'] for r in ROWS])
def test_priority_helper_matches_native(row):
    cfg=row['fixture']; nodes=[raw.CPNodo(v,p) for v,p in cfg['nodes']]
    for i in range(len(nodes)-1):nodes[i].sgte=nodes[i+1]
    mode=cfg['mode'];q=raw.ColaPrioridad(nodes[0] if nodes and mode!=3 else None,nodes[-1] if nodes and mode!=2 else None,cfg['count']);arg=None if mode==1 else q
    method=row['method'];cap=cfg['capacity'];nv=cfg['NULL_values_or_dest'];np=cfg['NULL_priorities'];values=[123456]*6;priorities=[654321]*6;dest=['Z'*129]
    before=[(n.valor,n.prioridad,n.sgte) for n in nodes];roots=(q.delante,q.atras,q.cantidad)
    if method=='cp_inicializar':raw.cp_inicializar(arg);actual={'return':None,'roots_count':[int(q.delante is None),int(q.atras is None),q.cantidad]}
    elif method in ['cp_vacia','cp_contar']:actual={'return':int(getattr(raw,method)(arg))}
    elif method=='cp_copiar_items':actual={'return':raw.cp_copiar_items(arg,None if nv else values,None if np else priorities,cap),'values':values,'priorities':priorities}
    else:raw.cp_formatear(arg,None if nv else dest,cap);actual={'return':None,'text':None if cap==0 or nv else dest[0]}
    assert [(n.valor,n.prioridad,n.sgte) for n in nodes]==before
    if method!='cp_inicializar':assert (q.delante,q.atras,q.cantidad)==roots
    expected={k:v for k,v in row['native'].items() if k!='buffer_bytes'}
    assert actual==expected
