"""Independent instrumented original C: byte writes and used-counter transitions."""
from pathlib import Path
import json,subprocess,shutil,sys
R=Path.cwd();sys.path.insert(0,str(R))
from app.domain.hash.listing_instruction import build_hash_listing_trace
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-listings-instructions-medium';N=E/'native-observer';N.mkdir(exist_ok=True)
original=(R/'docs/tads_C/tad_tabla_hash.c').read_text(encoding='utf-8-sig')
header=r'''
static int qa_case,qa_sample;
static void qa_write(const char *tag,const char *destino,size_t cap,size_t used,int count){
 fprintf(stderr,"{\"case\":%d,\"sample\":%d,\"event\":\"%s\",\"capacity\":%zu,\"used\":%zu,\"written\":%d,\"hex\":\"",qa_case,qa_sample,tag,cap,used,count);
 for(size_t j=0;destino[j];j++)fprintf(stderr,"%02x",(unsigned char)destino[j]);
 fprintf(stderr,"\"}\n");
}
'''
full_header = r'''
static void qa_full(const char *event){fprintf(stderr,"{\"case\":%d,\"sample\":%d,\"event\":\"%s\",\"full\":true}\n",qa_case,qa_sample,event);}
static int qa_condition(const char *event,int value){qa_full(event);return value;}
'''
def transform(name, replacements, entry, endevent):
 start=original.index(name+'(');start=original.rfind('\n',0,start)+1
 brace=original.index('{',start);depth=1;end=brace+1
 while depth:
  depth+=(original[end]=='{')-(original[end]=='}');end+=1
 text=original[start:end]
 text=text[:text.index('{')+1]+'\n    qa_full("'+entry+'");'+text[text.index('{')+1:]
 for old,new in replacements:
  assert old in text,old;text=text.replace(old,new,1)
 text=text[:-1]+'    qa_full("'+endevent+'");\n}'
 return original[start:end],text
helper_old,helper_new=transform('th_append_text',[
 ('va_list args;','va_list args; qa_full("args_declared");'),
 ('int escritos;','int escritos; qa_full("written_declared");'),
 ('if (destino == NULL || usado == NULL || *usado >= capacidad)', 'if (qa_condition("append_guard", destino == NULL || usado == NULL || *usado >= capacidad))'),
 ('return;','qa_full("append_return"); return;'),
 ('va_start(args, fmt);','va_start(args, fmt); qa_full("va_start");'),
 ('va_end(args);','qa_write("vsnprintf_write",destino,capacidad,*usado,escritos); qa_full("vsnprintf_write"); va_end(args); qa_full("va_end");'),
 ('if (escritos < 0)','if (qa_condition("encoding_guard", escritos < 0))'),
 ('if ((size_t)escritos >= capacidad - *usado)','if (qa_condition("truncation_guard", (size_t)escritos >= capacidad - *usado))'),
 ('*usado = capacidad;','*usado = capacidad; qa_write("used_saturated",destino,capacidad,*usado,escritos); qa_full("used_saturated");'),
 ('*usado += (size_t)escritos;','*usado += (size_t)escritos; qa_write("used_advanced",destino,capacidad,*usado,escritos); qa_full("used_advanced");'),
 ],'append_entry','append_return')
format_old,format_new=transform('th_formatear',[
 ('if (!destino || capacidad == 0) return;', 'if (qa_condition("destination_guard", !destino || capacidad == 0)) {qa_full("formatter_return"); return;}'),
 ("destino[0] = '\\0';", "destino[0] = '\\0'; qa_full(\"initial_terminator\");"),
 ('if (!tabla || !tabla->buckets)','if (qa_condition("table_guard", !tabla || !tabla->buckets))'),
 ('snprintf(destino, capacidad, "Tabla no inicializada\\n");','snprintf(destino, capacidad, "Tabla no inicializada\\n"); qa_full("uninitialized_table_text");'),
 ('        return;','        qa_full("formatter_return"); return;'),
 ('size_t usado = 0;','size_t usado = 0; qa_full("used_declared");'),
 ('for (int i = 0; i < tabla->capacidad && usado < capacidad; i++)','for (int i = (qa_full("bucket_init"),0); qa_condition("bucket_guard", i < tabla->capacidad && usado < capacidad); i++,qa_full("bucket_increment"))'),
 ('th_append_text(destino, capacidad, &usado, "[%d] -> ", i);','qa_full("append_call"); th_append_text(destino, capacidad, &usado, "[%d] -> ", i);'),
 ('THNodo *actual = tabla->buckets[i];','THNodo *actual = tabla->buckets[i]; qa_full("actual_declared");'),
 ('while (actual != NULL && usado < capacidad)','while (qa_condition("chain_guard", actual != NULL && usado < capacidad))'),
 ('th_append_text(destino, capacidad, &usado, "(%d:%d) -> ", actual->clave, actual->valor);','qa_full("append_call"); th_append_text(destino, capacidad, &usado, "(%d:%d) -> ", actual->clave, actual->valor);'),
 ('actual = actual->siguiente;','actual = actual->siguiente; qa_full("actual_advance");'),
 ('if (usado < capacidad)','if (qa_condition("null_label_guard", usado < capacidad))'),
 ('th_append_text(destino, capacidad, &usado, "NULL\\n");','qa_full("append_call"); th_append_text(destino, capacidad, &usado, "NULL\\n");'),
 ('        }\n    }','        }\n        qa_full("bucket_body_exit");\n    }\n    qa_full("bucket_loop_exit");'),
 ],'formatter_entry','formatter_return')
s=original.replace(helper_old,helper_new).replace(format_old,format_new)
s=s.replace('static void th_append_text(',header+full_header+'\nstatic void th_append_text(',1)
# Same translation unit grants QA visibility without exporting anything in C/H.
probe=(E/'native/probe.c').read_text(encoding='utf-8').replace('memset(&block,0xA5,sizeof(block));','qa_case=cid;qa_sample=sample_id;memset(&block,0xA5,sizeof(block));')
source=s+'\n_Static_assert(_Generic(&th_formatear, void (*)(const TablaHash *,char *,size_t):1,default:0),"formatter types");\n_Static_assert(_Generic(&th_append_text, void (*)(char *,size_t,size_t *,const char *,...):1,default:0),"helper types");\n'+probe
(N/'observer.c').write_text(source,encoding='utf-8');shutil.copyfile(R/'docs/tads_C/tad_tabla_hash.h',N/'tad_tabla_hash.h')
p=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'observer.c'),'-o',str(N/'observer.exe')],capture_output=True,text=True);(N/'compile.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'observer.exe')],capture_output=True,text=True);assert p.returncode==0;(N/'events.jsonl').write_text(p.stderr,encoding='utf-8');(N/'buffers.jsonl').write_text(p.stdout,encoding='utf-8')
all_events=[json.loads(x) for x in p.stderr.splitlines()];native=[x for x in all_events if 'used' in x];full_events=[x for x in all_events if x.get('full')];buffers=[json.loads(x) for x in p.stdout.splitlines()];fixtures=json.loads((E/'report.json').read_text(encoding='utf-8'));reports=[]
for row in buffers:
 cid=row['case'];sample=row['sample'];null=cid==4 and sample==0
 item=next((x for x in fixtures if x['case']==['empty','mixed','extremes','sparse'][cid]),None) if cid<4 else fixtures[0]
 state=item['data']['execution_trace']['steps'][0]['state_snapshot']
 if cid==4 and sample!=0:state={'metadata':{'capacity':0,'size':0},'buckets':[],'kind':'hash_table'}
 trace=build_hash_listing_trace(operation_name='items',payload={},source_code=item['data']['execution_trace']['source_code'],code_title='th_formatear',before_state=state,after_state=state,success=True,message='',buffer_capacity=row['capacity'],null_table=null,null_destination=row['null_destination'],caller_buffer_capacity=4096)
 observed=[x for x in native if x['case']==cid and x['sample']==sample]
 modeled=[]
 for f in trace['steps']:
  d=f['debug']
  if f['event_type'] in {'vsnprintf_write','used_saturated','used_advanced'}:
   count=d['variables']['th_append_text.escritos']['value'];hextext=bytes(d['buffer']['bytes']).split(b'\0',1)[0].hex()
   modeled.append({'case':cid,'sample':sample,'event':f['event_type'],'capacity':row['capacity'],'used':d['used'],'written':count,'hex':hextext})
 assert observed==modeled,(cid,sample,observed,modeled)
 full_native=[x['event'] for x in full_events if x['case']==cid and x['sample']==sample]
 full_model=[f['event_type'] for f in trace['steps'] if f['event_type'] not in {'buffer_declared','formatter_call'}]
 assert full_native==full_model,(cid,sample,full_native,full_model)
 last=trace['steps'][-1]['debug']['buffer'];raw=bytes.fromhex(row['hex']);expected=raw.split(b'\0',1)[0]
 if row['capacity'] and not row['null_destination']:assert bytes(last['bytes']).split(b'\0',1)[0]==expected
 if cid==4 and not row['null_destination']:
  assert trace['steps'][-1]['line_text'].strip()=='return;'
 assert all(not f['console'] for f in trace['steps']);assert all(f['state_after']==state for f in trace['steps'])
 reports.append({'case':cid,'sample':sample,'capacity':row['capacity'],'matched_native_events':len(observed),'matched_full_instruction_events':len(full_native),'modeled_frames':len(trace['steps']),'final_bytes_match':True,'allocations':0,'frees':0})
(E/'native-observer-report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print(json.dumps({'same_buffer_cases':len(reports),'native_write_counter_events':len(native),'all_instruction_events':len(full_events),'matched':True,'C17_type_assertions':2}))
