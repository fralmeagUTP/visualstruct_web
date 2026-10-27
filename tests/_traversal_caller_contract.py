"""Fresh callers for historical traversal intents; no historical UI claim."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
from app.services.graph_main_service import build_graph_main
from scripts.published_test_inputs import audit_input_path
from _book_traversal_oracle import CASES

TRACK=r'''
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
static long live,allocations,frees;
void *owned_malloc(size_t n){void *p=malloc(n);if(p){live++;allocations++;}return p;}
void *owned_calloc(size_t n,size_t s){void *p=calloc(n,s);if(p){live++;allocations++;}return p;}
void owned_free(void *p){if(p){assert(live>0);live--;frees++;}free(p);}
__attribute__((destructor)) static void check(void){assert(live==0&&allocations==frees);printf("OWNERSHIP %ld %ld 0\\n",allocations,frees);}
'''

def canonical_history(case,algorithm):
    record=CASES[case if isinstance(case,int) else 3]
    history=[{'operation':'create_graph','payload':{'directed':True}}]
    history += [{'operation':'insert_vertex','payload':{'vertex':v}} for v in record['vertices']]
    history += [{'operation':'insert_edge','payload':{'origin':a,'target':b,'weight':1}} for a,b in record['edges']]
    starts=[record['start']]*2 if case!='context' else [1,3,1]
    history += [{'operation':'run_'+algorithm,'payload':{'start':start}} for start in starts]
    return history,len(starts)

def validate_caller(root,tmp_path,algorithm,case,archived_source,run_doxygen):
    archived=audit_input_path(archived_source)
    assert archived.is_file(),archived_source
    historical_hash=hashlib.sha256(archived.read_bytes()).hexdigest()
    history,count=canonical_history(case,algorithm);main=build_graph_main(history)
    assert main.count('= grafo_'+algorithm+'(')==count
    assert main.count('grafo_liberar_vertices(&lista_')==count
    assert 'GrafoEstado estado_' in main and 'grafo_destruir(&g)' in main
    source=tmp_path/'main.c';source.write_text(main,encoding='utf-8')
    run_doxygen(tmp_path,[source])
    for ext in ['c','h']:(tmp_path/('tad_grafo.'+ext)).write_bytes((root/'docs/tads_C'/('tad_grafo.'+ext)).read_bytes())
    (tmp_path/'ownership.c').write_text(TRACK,encoding='utf-8')
    compiler=shutil.which('gcc');assert compiler
    common=[compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(tmp_path)]
    obj=tmp_path/'graph.o';exe=tmp_path/'main.exe'
    commands=[common+['-Dmalloc=owned_malloc','-Dcalloc=owned_calloc','-Dfree=owned_free','-c',str(tmp_path/'tad_grafo.c'),'-o',str(obj)],common+[str(source),str(tmp_path/'ownership.c'),str(obj),'-o',str(exe)]]
    for command in commands:
        result=subprocess.run(command,capture_output=True,text=True,timeout=45);assert result.returncode==0,result.stderr
    result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15);assert result.returncode==0,result.stderr
    match=re.search(r'OWNERSHIP (\d+) (\d+) 0',result.stdout);assert match and match[1]==match[2]
    (tmp_path/'ownership-review.json').write_text(json.dumps({'case':case,'historical_artifact_sha256':historical_hash,'fresh_canonical_caller_sha256':hashlib.sha256(main.encode()).hexdigest(),'current_caller_is_browser_evidence':False,'strict_c17':True,'allocations':int(match[1]),'frees':int(match[2]),'live':0,'doxygen_warnings':0}),encoding='utf-8')
