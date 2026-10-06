"""Application rejection is not a native C deletion invocation."""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

def build_rbt_delete_rejection_trace(trace,before_state,after_state):
    assert before_state==after_state
    source='/* Solicitud rechazada por la aplicacion: rbt_eliminar NO fue invocado. */\n\n'+trace['source_code'];lines=source.splitlines()
    step={'step_index':0,'line_index':0,'line_text':lines[0],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':deepcopy(before_state),'state_after':deepcopy(after_state),'debug':{'stage':'application_precondition_rejected'}}
    ped=build_hierarchical_frame(structure_id='red_black',operation_name='eliminar',payload=trace['payload'],step=step,source_lines=lines,success=False)
    ped.update(concept='compare',case='application_precondition_rejected',phase={'id':'application_precondition_rejected','label':'Rechazo antes del TAD','goal':lines[0]},condition=None,variables=[],call_stack=[],return_propagation={'active':False,'value':None,'reconnects_subtree':False},instruction_event={'phase':'application_precondition_rejected','C_invoked':False,'return':None},memory={'event':'none','objects_before':[],'objects_after':[],'allocated_objects':[],'freed_objects':[],'dangling_references':[]},memory_state=deepcopy(before_state))
    ped['narration']={k:'El rechazo pertenece a la aplicacion, no a una ejecucion de C: no hay malloc, escritura, printf ni retorno del TAD. El codigo restante es referencia.' for k in ['basic','intermediate','advanced']};validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped
    trace.update(source_code=source,steps=[step],application_precondition_rejected=True);return trace

