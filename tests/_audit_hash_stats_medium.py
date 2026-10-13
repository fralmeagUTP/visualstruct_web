"""Stats baseline: actual original C and API representations kept distinct."""
from pathlib import Path
import json,sys,subprocess,shutil
R=Path.cwd();sys.path.insert(0,str(R));from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-stats-instructions-medium';N=E/'native';N.mkdir(exist_ok=True)
CASES=[('empty',3,[]),('collision',3,[(1,10),(4,40)]),('sparse',7,[(-7,70),(7,70),(14,-14),(2,2)]),('destroyed',3,[(1,1),(4,4)])]
PREFIX=r'''#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "tad_tabla_hash.h"
_Static_assert(_Generic(((THEstadisticas*)0)->factor_carga,float:1,default:0),"float field");
static void sample(int cid,int sid,const TablaHash*t,size_t cap,int null_dest){
 struct {unsigned char left[16],buffer[1024],right[16];} block;memset(&block,0xA5,sizeof(block));
 THEstadisticas st=th_estadisticas(t);th_formatear_estadisticas(t,null_dest?NULL:(char*)block.buffer,cap);
 for(int j=0;j<16;j++)assert(block.left[j]==0xA5 && block.right[j]==0xA5);
 for(size_t j=cap;j<sizeof(block.buffer);j++)assert(block.buffer[j]==0xA5);
 printf("{\"case\":%d,\"sample\":%d,\"buffer_capacity\":%zu,\"null_dest\":%s,\"capacity\":%d,\"size\":%d,\"occupied\":%d,\"collisions\":%d,\"C_float_load\":%.17g,\"first_byte\":%u,\"hex\":\"",cid,sid,cap,null_dest?"true":"false",st.capacidad,st.cantidad,st.buckets_ocupados,st.colisiones,(double)st.factor_carga,(unsigned)block.buffer[0]);
 for(size_t j=0;j<cap;j++)printf("%02x",(unsigned)block.buffer[j]);printf("\"}\n");
}
'''
# Strict C braces avoid the misleading-indentation defect in an earlier QA harness.
PREFIX=PREFIX.replace('for(size_t j=0;j<cap;j++)printf("%02x",(unsigned)block.buffer[j]);','for(size_t j=0;j<cap;j++){printf("%02x",(unsigned)block.buffer[j]);}')
main='int main(void){'
for cid,(name,cap,pairs) in enumerate(CASES):
 main+='{TablaHash t={0};th_inicializar(&t,'+str(cap)+');assert(t.buckets);'
 for k,v in pairs:main+='assert(th_insertar(&t,'+str(k)+','+str(v)+'));'
 if name=='destroyed':main+='th_destruir(&t);'
 for sid,buffer in enumerate([0,1,2,8,64,512]):main+=f'sample({cid},{sid},&t,{buffer},0);'
 main+='th_destruir(&t);}'
main+='sample(4,0,NULL,64,0);{TablaHash t={0};sample(4,1,&t,64,0);sample(4,2,&t,64,1);}return 0;}'
(N/'probe.c').write_text(PREFIX+main,encoding='utf-8')
for ext in ['c','h']:shutil.copyfile(R/('docs/tads_C/tad_tabla_hash.'+ext),N/('tad_tabla_hash.'+ext))
p=subprocess.run([shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(N/'probe.c'),str(N/'tad_tabla_hash.c'),'-o',str(N/'probe.exe')],capture_output=True,text=True);(N/'compile.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'probe.exe')],capture_output=True,text=True);(N/'native.jsonl').write_text(p.stdout,encoding='utf-8');assert p.returncode==0;native=[json.loads(x) for x in p.stdout.splitlines()];assert len(native)==27
for cid in range(4):
 rows=[r for r in native if r['case']==cid];full=bytes.fromhex(rows[-1]['hex']).split(b'\0',1)[0]
 for row in rows:
  if row['buffer_capacity']:assert bytes.fromhex(row['hex']).split(b'\0',1)[0]==full[:row['buffer_capacity']-1]
  else:assert row['first_byte']==165
app=create_app();app.config['TESTING']=True;report=[];D=E/'callers';D.mkdir(exist_ok=True)
for cid,(case,cap,pairs) in enumerate(CASES):
 c=app.test_client();c.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':cap}})
 for k,v in pairs:c.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 if case=='destroyed':c.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}})
 n=next(r for r in native if r['case']==cid and r['buffer_capacity']==512)
 for repeat in range(2):
  response=c.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}});d=response.get_json();assert response.status_code==200 and d['success'];assert d['result']['capacity']==n['capacity'] and d['result']['size']==n['size'];trace=d['execution_trace'];report.append({'case':case,'repeat':repeat,'pairs':pairs,'created_capacity':cap,'native':n,'API_load_equals_C_float':d['result']['load_factor']==n['C_float_load'],'data':d})
 main=c.get('/help/source/hash_table/main').data;(D/(case+'.c')).write_bytes(main);assert c.get('/help/source/hash_table/main').data==main
(E/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(E/'buffer-report.json').write_text(json.dumps(native,indent=2),encoding='utf-8');print(json.dumps({'native_buffer_calls':27,'API_calls':8,'capacity_size_matches':8,'float_equal':sum(r['API_load_equals_C_float'] for r in report),'caller_stats_calls':[(p.name,p.read_bytes().count(b'th_estadisticas(')) for p in D.glob('*.c')]}))
