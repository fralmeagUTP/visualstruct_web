"""Independent native oracle for the existing finite graph case inventories.

Native C is downloaded from the app, compiled unchanged, and reports both its
owned result and GrafoEstado. Endpoint tests use normal mode; instruction and
memory fidelity have separate BookSession/native regression suites.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess
from copy import deepcopy
from app import create_app
from app.services.graph_structure_service import GraphStructureService as Service
from app.adapters.graph_adapter import GraphAdapter

def observe(cases, algorithm, output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    client=create_app().test_client();downloads={}
    for structure,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
        for kind,ext in [('source','c'),('header','h')]:
            response=client.get(f'/help/source/{structure}/{kind}');assert response.status_code==200
            (output/f'{stem}.{ext}').write_bytes(response.data)
            downloads[f'{stem}.{ext}']=hashlib.sha256(response.data).hexdigest()
    source='''#include "tad_grafo.h"
#include <stdio.h>
static void emit(int index, ListaArco arcs, GrafoEstado status) {
    printf("RESULT %d {\\"status\\":%d,\\"null\\":%s,\\"arcs\\":[", index, (int)status, arcs == NULL ? "true" : "false");
    int first=1; long long cost=0;
    for (ListaArco p=arcs;p!=NULL;p=p->sig) { printf("%s[%d,%d,%d]",first?"":",",p->origen,p->destino,p->costo); first=0; cost+=p->costo; }
    printf("],\\"cost\\":%lld}\\n",cost);
}
int main(void) {
'''
    for index,case in enumerate(cases):
        source+='{Grafo g=grafo_crear(); GrafoEstado status;\n'
        for vertex in case['v']:source+=f'g=grafo_insertar_vertice(g,{vertex},&status);\n'
        for origin,target,weight in case['e']:
            source+=f'g=grafo_insertar_arco(g,{origin},{target},{weight},&status);\n'
            if not case.get('directed',True) and origin!=target:source+=f'g=grafo_insertar_arco(g,{target},{origin},{weight},&status);\n'
        args='' if algorithm=='kruskal' else f', {case["start"]}'
        if algorithm in {'dijkstra','bellman_ford'}:args+=f', {case["end"]}'
        source+=f'ListaArco result=grafo_{algorithm}(g{args}, &status); emit({index},result,status); grafo_liberar_arcos(&result); grafo_destruir(&g);}}\n'
    source+='return 0;}\n';(output/'observed-main.c').write_text(source,encoding='utf-8')
    compiler=shutil.which('gcc');assert compiler
    executable=output/'native.exe'
    built=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(output/'observed-main.c'),str(output/'tad_grafo.c'),'-o',str(executable)],capture_output=True,text=True,timeout=30)
    (output/'compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    native=subprocess.run([str(executable)],capture_output=True,text=True,timeout=15);assert native.returncode==0,native.stderr
    (output/'native.stdout.log').write_text(native.stdout)
    actual={int(line.split(' ',2)[1]):json.loads(line.split(' ',2)[2]) for line in native.stdout.splitlines() if line.startswith('RESULT ')}
    assert len(actual)==len(cases);rows=[];operation='run_'+algorithm
    for index,case in enumerate(cases):
        history=[];fixture=GraphAdapter()
        setup=[('create_graph',{'directed':case.get('directed',True)})]
        setup += [('insert_vertex',{'vertex':v}) for v in case['v']]
        setup += [('insert_edge',{'origin':a,'target':b,'weight':w}) for a,b,w in case['e']]
        for op,payload in setup:
            # Fixture preparation is not a route/trace assertion. Use the real
            # canonical adapter once per setup call; only the endpoint under
            # test is executed through the full service and replayed below.
            data=fixture.execute(op,payload);assert data['success'],data['message']
            history.append({'operation':op,'payload':deepcopy(payload),'source_contract':'graph-book/v1'})
        before=deepcopy(history);payload={} if algorithm=='kruskal' else {'start':case['start']}
        if algorithm in {'dijkstra','bellman_ford'}:payload['end']=case['end']
        data=Service.execute_operation('graph',operation,payload,history,execution_mode='normal');observed=actual[index];result=data.get('result') or {};ok=observed['status']==0
        differences=[]
        if data['c_status']!=observed['status']:differences.append('status')
        if data['success']!=ok:differences.append('success')
        if algorithm in {'dijkstra','bellman_ford'}:
            path=([case['start']]+[edge[1] for edge in observed['arcs']]) if ok else []
            for key,expected in [('path',path),('path_arcs',observed['arcs']),('reachable',ok),('distance_to_destination',observed['cost'] if ok else None),('has_negative_cycle',observed['status']==4)]:
                if result.get(key)!=expected:differences.append(key)
        else:
            for key,expected in [('mst_edges',observed['arcs']),('connected',ok),('total_weight',observed['cost'] if ok else None)]:
                if result.get(key)!=expected:differences.append(key)
        reloaded=Service.get_view_model('graph',data['history'])
        assert not reloaded.get('suspended',False) and reloaded['visual_state']==data['visual_state']
        retained=sum(row['operation']==operation for row in data['history']);restored=sum(row['operation']==operation for row in reloaded['history'])
        assert data['history'][:-1]==before and data['history'][-1]['source_contract']=='graph-book/v1'
        row={'name':case['name'],'input':case,'native':observed,'backend':{'success':data['success'],'message':data['message'],'result':data.get('result'),'c_status':data['c_status']},'differences':differences,'history_saved':retained,'history_reload':restored,'successful_query_saved':retained,'successful_query_after_reload':restored,'failure_history_recorded':retained==restored==1,'failure_history_unchanged':data['history']==before,'cycle_result_matches_error_spec':observed['status']==4 and not data['success'],'source_contract':'graph-book/v1'}
        rows.append(row);(output/f'case-{index}.json').write_text(json.dumps({'case':case,'native':observed,'row':row,'response':data},ensure_ascii=False,indent=2),encoding='utf-8')
    report={'scope':'finite native graph-book endpoint parity; no instruction claim','cases':len(rows),'downloads_sha256':downloads,'native_strict_c17':True,'rows':rows,'differences_count':sum(bool(r['differences']) for r in rows)}
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report
