"""Fresh downloadable contracts and actual generated caller ownership."""
from pathlib import Path
import hashlib,json,subprocess,shutil,re
import pytest

from scripts.test_tool_paths import resolve_doxygen
DOXYGEN=Path(resolve_doxygen())

from scripts.published_test_inputs import audit_input_path
def run_doxygen(target,inputs):
    warning=target/'warnings.log';cfg=target/'Doxyfile'
    cfg.write_text('\n'.join(['INPUT = '+' '.join('"'+p.as_posix()+'"' for p in inputs),'OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warning.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
    p=subprocess.run([str(DOXYGEN),str(cfg)],capture_output=True,text=True,timeout=30)
    assert p.returncode==0 and audit_input_path(warning).read_text(encoding='utf-8')=='',(p.stderr,audit_input_path(warning).read_text(encoding='utf-8'))

def test_bfs_fresh_download_contracts_and_manual(client,tmp_path):
    files=[];hashes={}
    for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
        for kind,ext in [('source','c'),('header','h')]:
            response=client.get('/help/source/'+tad+'/'+kind);assert response.status_code==200
            p=tmp_path/(stem+'.'+ext);p.write_bytes(response.data);files.append(p);hashes[p.name]=hashlib.sha256(response.data).hexdigest()
    for ext in ['c','h']:
        graph=(audit_input_path(tmp_path/('tad_grafo.'+ext))).read_text(encoding='utf-8-sig')
        assert 'O(V*(V+E))' in graph and 'dato valido' in graph and 'lista parcial' in graph
        assert 'no normaliza otro valor a 1' in graph and 'el caller libera cada nodo' in graph
        queue=(audit_input_path(tmp_path/('tad_cola.'+ext))).read_text(encoding='utf-8-sig')
        assert 'void no comunica exito' in queue and '-1 tambien es un dato valido' in queue
    root=Path(__file__).resolve().parents[1]
    for file in ['docs/USER_GUIDE.md','docs/qa/graph-teacher-guide.md']:
        guide=(audit_input_path(root/file)).read_text(encoding='utf-8');assert 'O(V*(V+E))' in guide and 'dos llamadas iguales consecutivas' in guide and 'sin inyectar esos fallos' in guide
    run_doxygen(tmp_path,files)
    (tmp_path/'download-review.json').write_text(json.dumps({'hashes':hashes,'doxygen_warnings':0,'symbols_reviewed':['grafo_bfs','grafo_desmarcar','grafo_marcar_vertice','grafo_marcado_vertice','grafo_sucesores','cola_encolar','cola_desencolar'],'algorithm_tokens':'comment-only changes guarded at apply','limits':['No allocation-failure injection or whole-file semantic documentation closure']},indent=2),encoding='utf-8')

@pytest.mark.parametrize('case',[1,3,4,5,6,7,8,9])
def test_bfs_actual_browser_main_ownership_and_doxygen(tmp_path,case):
    # This is an immutable artifact from the completed actual-browser run; fail
    # explicitly if absent, rather than regenerate a different synthetic caller.
    root=Path(__file__).resolve().parents[1]
    evidence=root/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-bfs-instruction-review/browser-artifacts'
    source=evidence/('case-'+str(case))/'main.c';assert audit_input_path(source).is_file(),source
    main=audit_input_path(source).read_text(encoding='utf-8');(tmp_path/'main.c').write_text(main,encoding='utf-8')
    assert main.count('= grafo_bfs(')==2 and main.count('free(rec_')==2
    run_doxygen(tmp_path,[tmp_path/'main.c'])
    for stem in ['tad_grafo','tad_cola']:
        for ext in ['c','h']:(tmp_path/(stem+'.'+ext)).write_bytes((audit_input_path(root/'docs/tads_C'/(stem+'.'+ext))).read_bytes())
    # Count every source and caller allocation/free without reading retired
    # pointers. Student program statements are retained; only observation added.
    header='#include <stddef.h>\nvoid *owned_malloc(size_t);\nvoid owned_free(void*);\n'
    (tmp_path/'ownership.h').write_text(header,encoding='utf-8')
    observer=r'''
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
static void *ptrs[4096];static int live[4096],total,allocations,frees;
void *owned_malloc(size_t size){void *p=malloc(size);if(p){assert(total<4096);ptrs[total]=p;live[total++]=1;allocations++;}return p;}
void owned_free(void *p){if(p){int found=0;for(int i=0;i<total;i++){if(live[i]&&ptrs[i]==p){live[i]=0;found=1;break;}}assert(found);frees++;}free(p);}
static void ownership_done(void){for(int i=0;i<total;i++){assert(live[i]==0);}assert(allocations==frees);printf("OWNERSHIP %d %d 0\n",allocations,frees);}
#define free owned_free
'''
    owned=observer+main.replace('    return 0;','    ownership_done();\n    return 0;');(tmp_path/'owned-main.c').write_text(owned,encoding='utf-8')
    compiler=shutil.which('gcc');assert compiler
    objects=[]
    for stem in ['tad_grafo','tad_cola']:
        obj=tmp_path/(stem+'.o');p=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-include',str(tmp_path/'ownership.h'),'-Dmalloc=owned_malloc','-Dfree=owned_free','-c',str(tmp_path/(stem+'.c')),'-o',str(obj)],capture_output=True,text=True,timeout=30);assert p.returncode==0 and not p.stderr,p.stderr;objects.append(obj)
    exe=tmp_path/'owned-main.exe';p=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'owned-main.c'),*map(str,objects),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert p.returncode==0 and not p.stderr,p.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
    m=re.search(r'^OWNERSHIP (\d+) (\d+) 0$',run.stdout,re.M);assert m and m[1]==m[2]
    (tmp_path/'ownership-review.json').write_text(json.dumps({'case':case,'allocations':int(m[1]),'frees':int(m[2]),'live':0,'strict_c17':True,'actual_main_doxygen_warnings':0,'main_sha256':hashlib.sha256(audit_input_path(source).read_bytes()).hexdigest()},indent=2),encoding='utf-8')
