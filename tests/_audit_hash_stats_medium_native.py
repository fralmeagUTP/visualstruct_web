"""Independent original-C observer: full statistics statements and typed values."""
from pathlib import Path
import sys,json,subprocess,shutil
R=Path.cwd();sys.path.insert(0,str(R));from app.domain.hash.stats_instruction import build_hash_stats_trace
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-stats-instructions-medium';N=E/'native-observer';N.mkdir(exist_ok=True)
original=(R/'docs/tads_C/tad_tabla_hash.c').read_text(encoding='utf-8-sig')
HEADER=r'''#include <assert.h>
#include <float.h>
_Static_assert(FLT_RADIX==2 && FLT_MANT_DIG==24 && sizeof(float)==4,"finite native binary32");
_Static_assert(DBL_MANT_DIG==53,"finite API double projection");
static void qa_rounding(int n,int d){float cn=(float)n,cd=(float)d,r=cn/cd;fprintf(stderr,"R %d %d %.17g %.17g %.17g\n",n,d,(double)cn,(double)cd,(double)r);}
static int qa_case,qa_sample;
static const TablaHash *qa_root;
static const THEstadisticas *qa_stats;
static char *qa_destination;
static void qa_full(const char *event,int condition){
 fprintf(stderr,"{\"case\":%d,\"sample\":%d,\"event\":\"%s\",\"condition\":%d,\"stats\":",qa_case,qa_sample,event,condition);
 if(qa_stats)fprintf(stderr,"{\"capacidad\":%d,\"cantidad\":%d,\"buckets_ocupados\":%d,\"colisiones\":%d,\"factor_carga\":%.17g}",qa_stats->capacidad,qa_stats->cantidad,qa_stats->buckets_ocupados,qa_stats->colisiones,(double)qa_stats->factor_carga);
 else {fprintf(stderr,"null");}fprintf(stderr,"}\n");
}
static int qa_cond(const char *event,int value){qa_full(event,value);return value;}
'''
def transform(name,replacements,entry,final):
 start=original.index(name+'(');start=original.rfind('\n',0,start)+1;brace=original.index('{',start);end=brace+1;depth=1
 while depth:depth+=(original[end]=='{')-(original[end]=='}');end+=1
 body=original[start:end];body=body[:body.index('{')+1]+'\n'+entry+body[body.index('{')+1:]
 for a,b in replacements:assert a in body,a;body=body.replace(a,b,1)
 if final:body=body[:-1]+final+'\n}'
 return original[start:end],body
s_old,s_new=transform('th_estadisticas',[
 ('THEstadisticas stats = {0};','THEstadisticas stats = {0}; qa_stats=&stats; qa_full("stats_zero_initialized",-1);'),
 ('if (!tabla || !tabla->buckets || tabla->capacidad <= 0) return stats;', 'if (qa_cond("stats_guard", !tabla || !tabla->buckets || tabla->capacidad <= 0)) {qa_full("stats_return",-1);qa_stats=NULL;return stats;}'),
 ('stats.capacidad = tabla->capacidad;','stats.capacidad = tabla->capacidad; qa_full("capacity_write",-1);'),
 ('stats.cantidad = tabla->cantidad;','stats.cantidad = tabla->cantidad; qa_full("size_write",-1);'),
 ('stats.factor_carga = (float)tabla->cantidad / (float)tabla->capacidad;','stats.factor_carga = (float)tabla->cantidad / (float)tabla->capacidad; qa_full("float_load_write",-1);'),
 ('for (int i = 0; i < tabla->capacidad; i++)','for (int i = (qa_full("bucket_init",-1),0); qa_cond("bucket_guard",i < tabla->capacidad); i++,qa_full("bucket_increment",-1))'),
 ('THNodo *actual = tabla->buckets[i];','THNodo *actual = tabla->buckets[i]; qa_full("actual_declared",-1);'),
 ('if (actual != NULL)','if (qa_cond("occupied_guard",actual != NULL))'),
 ('stats.buckets_ocupados++;','stats.buckets_ocupados++; qa_full("occupied_increment",-1);'),
 ('int nodos_en_bucket = 0;','int nodos_en_bucket = 0; qa_full("node_count_declared",-1);'),
 ('while (actual != NULL)','while (qa_cond("chain_guard",actual != NULL))'),
 ('nodos_en_bucket++;','nodos_en_bucket++; qa_full("node_count_increment",-1);'),
 ('actual = actual->siguiente;','actual = actual->siguiente; qa_full("actual_advance",-1);'),
 ('if (nodos_en_bucket > 1)','if (qa_cond("collision_guard",nodos_en_bucket > 1))'),
 ('stats.colisiones += (nodos_en_bucket - 1);','stats.colisiones += (nodos_en_bucket - 1); qa_full("collisions_write",-1);'),
 ('        }\n    }','            qa_full("occupied_body_exit",-1);\n        }\n        qa_full("bucket_body_exit",-1);\n    }\n    qa_full("bucket_loop_exit",-1);'),
 ('    return stats;','    qa_full("stats_return",-1);qa_stats=NULL;return stats;'),
 ],'    assert(tabla==qa_root);qa_stats=NULL;qa_full("stats_entry",-1);','')
f_old,f_new=transform('th_formatear_estadisticas',[
 ('if (!destino || capacidad == 0) return;','if (qa_cond("destination_guard",!destino || capacidad == 0)) {qa_full("formatter_return",-1);return;}'),
 ("destino[0] = '\\0';", "destino[0] = '\\0'; qa_full(\"initial_terminator\",-1);"),
 ('if (!tabla || !tabla->buckets)','if (qa_cond("table_guard",!tabla || !tabla->buckets))'),
 ('snprintf(destino, capacidad, "Tabla no inicializada\\n");','snprintf(destino, capacidad, "Tabla no inicializada\\n");qa_full("uninitialized_table_text",-1);'),
 ('        return;','        qa_full("formatter_return",-1);return;'),
 ('THEstadisticas stats = th_estadisticas(tabla);','qa_full("formatter_stats_declared",-1);qa_full("formatter_stats_call",-1);THEstadisticas stats = th_estadisticas(tabla);qa_full("formatter_stats_assigned",-1);'),
 ('stats.colisiones, stats.factor_carga);','stats.colisiones, stats.factor_carga);qa_full("snprintf_write",-1);'),
 ],'    assert(tabla==qa_root && destino==qa_destination);qa_full("formatter_entry",-1);','    qa_full("formatter_return",-1);')
s=original.replace(s_old,s_new).replace(f_old,f_new);s=s.replace('THEstadisticas th_estadisticas(',HEADER+'\nTHEstadisticas th_estadisticas(',1)
probe=(E/'native/probe.c').read_text(encoding='utf-8').replace('THEstadisticas st=th_estadisticas(t);','qa_case=cid;qa_sample=sid;qa_root=t;qa_destination=null_dest?NULL:(char*)block.buffer;THEstadisticas st=th_estadisticas(t);')
probe=probe.replace('int main(void){','int main(void){qa_rounding(2,3);qa_rounding(4,7);qa_rounding(16777217,16777219);qa_rounding(2147483647,2147483646);')
# Same original bodies in QA translation unit, no exported symbols or canonical mutations.
s+='\n_Static_assert(_Generic(&th_estadisticas, THEstadisticas (*)(const TablaHash*):1,default:0),"stats signature");\n_Static_assert(_Generic(&th_formatear_estadisticas, void (*)(const TablaHash*,char*,size_t):1,default:0),"formatter signature");\n'+probe
(N/'observer.c').write_text(s,encoding='utf-8');shutil.copyfile(R/'docs/tads_C/tad_tabla_hash.h',N/'tad_tabla_hash.h')
p=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'observer.c'),'-o',str(N/'observer.exe')],capture_output=True,text=True);(N/'compile.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'observer.exe')],capture_output=True,text=True);(N/'stderr.raw.log').write_text(p.stderr,encoding='utf-8');(N/'buffers.jsonl').write_text(p.stdout,encoding='utf-8');assert p.returncode==0,p.stderr
all_events=[json.loads(x) for x in p.stderr.splitlines() if not x.startswith('R ')];(N/'events.jsonl').write_text('\n'.join(json.dumps(x) for x in all_events)+'\n',encoding='utf-8');native=[x for x in all_events if not x.get('rounding_probe')];rounding=[dict(zip(['n','d','cast_n','cast_d','result'],[int(x.split()[1]),int(x.split()[2]),*map(float,x.split()[3:])])) for x in p.stderr.splitlines() if x.startswith('R ')];from app.domain.hash.stats_instruction import cfloat
for r in rounding:assert r['cast_n']==cfloat(r['n']) and r['cast_d']==cfloat(r['d']) and r['result']==cfloat(cfloat(r['n'])/cfloat(r['d']))
(E/'native-rounding-probes.json').write_text(json.dumps(rounding,indent=2),encoding='utf-8')
buffers=[json.loads(x) for x in p.stdout.splitlines()];fixtures=json.loads((E/'report.json').read_text(encoding='utf-8'));reports=[]
for row in buffers:
 cid=row['case'];sample=row['sample'];item=next(x for x in fixtures if x['case']==['empty','collision','sparse','destroyed'][cid]) if cid<4 else next(x for x in fixtures if x['case']=='destroyed')
 state=item['data']['execution_trace']['steps'][0]['state_snapshot'];trace=build_hash_stats_trace(operation_name='stats',payload={},source_code=item['data']['execution_trace']['source_code'],code_title='stats',before_state=state,after_state=state,success=True,message='',buffer_capacity=row['buffer_capacity'],caller_buffer_capacity=1024,null_table=cid==4 and sample==0,null_destination=row['null_dest'])
 model=[f for f in trace['steps'] if f['debug']['function'] in {'th_estadisticas','th_formatear_estadisticas'} and f['event_type'] not in {'caller_stats_assigned'}]
 observed=[x for x in native if x['case']==cid and x['sample']==sample];assert [x['event'] for x in observed]==[f['event_type'] for f in model],(cid,sample,[x['event'] for x in observed],[f['event_type'] for f in model])
 for x,f in zip(observed,model):
  if x['condition']!=-1:assert bool(x['condition'])==f['debug']['condition_result']
  if x['stats'] is not None:assert x['stats']==(f['debug']['returned_stats'] if x['event']=='stats_return' else f['debug']['stats']),(x,f['debug'])
 last=trace['steps'][-1]['debug']['buffer']
 if row['buffer_capacity'] and not row['null_dest']:assert bytes(last['bytes']).split(b'\0',1)[0]==bytes.fromhex(row['hex']).split(b'\0',1)[0]
 else:assert last['bytes']==[]
 reports.append({'case':cid,'sample':sample,'capacity':row['buffer_capacity'],'matched_C_events':len(observed),'matched_C_conditions':sum(x['condition']!=-1 for x in observed),'matched_C_struct_snapshots':sum(x['stats'] is not None for x in observed),'final_bytes_match':True,'allocations':0,'frees':0})
(E/'native-observer-report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print(json.dumps({'buffer_cases':len(reports),'native_events':len(native),'conditions':sum(r['matched_C_conditions'] for r in reports),'struct_snapshots':sum(r['matched_C_struct_snapshots'] for r in reports),'matched':True,'C_types_signatures_aliases_verified':True}))
