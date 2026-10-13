"""DFS downloaded documentation and actual browser caller ownership."""
from pathlib import Path
import hashlib,json,subprocess,shutil,re
import pytest
from test_graph_bfs_documentation import run_doxygen

def test_dfs_fresh_download_contracts_and_manual(client,tmp_path):
    files=[]
    for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
        for part,ext in [('source','c'),('header','h')]:
            response=client.get('/help/source/'+tad+'/'+part);assert response.status_code==200
            p=tmp_path/(stem+'.'+ext);p.write_bytes(response.data);files.append(p)
    for ext in ['c','h']:
        code=(tmp_path/('tad_grafo.'+ext)).read_text(encoding='utf-8-sig')
        assert 'si falta, conserva las marcas previas' in code
        assert 'No desmarca ni comprueba que actual estuviera sin visitar' in code
        assert 'El resultado usa nodos nuevos con marcado=0' in code
        assert 'Cada frame libera su lista' in code
    root=Path(__file__).resolve().parents[1]
    for fn in ['docs/USER_GUIDE.md','docs/qa/graph-teacher-guide.md']:
        guide=(root/fn).read_text(encoding='utf-8')
        assert 'DFS comprueba primero' in guide and 'recursión real' in guide
        assert 'sin volver a ejecutar consultas' in guide and 'historial antiguo' in guide
        assert 'ocho casos de navegador registrados' in guide
    run_doxygen(tmp_path,files)
@pytest.mark.parametrize('case',[1,3,4,5,6,7,8,9,'context'])
def test_dfs_actual_browser_main_ownership_and_doxygen(tmp_path,case):
    # This is an immutable artifact from the completed actual-browser run; fail
    # explicitly if absent, rather than regenerate a different synthetic caller.
    root=Path(__file__).resolve().parents[1]
    evidence=root/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-dfs-history-context-low/browser-artifacts'
    source=evidence/('case-'+str(case))/'main.c';assert source.is_file(),source
    main=source.read_text(encoding='utf-8');(tmp_path/'main.c').write_text(main,encoding='utf-8')
    expected_calls=3 if case=='context' else 2
    assert main.count('= grafo_dfs(')==expected_calls and main.count('free(rec_')==expected_calls
    run_doxygen(tmp_path,[tmp_path/'main.c'])
    for stem in ['tad_grafo','tad_cola']:
        for ext in ['c','h']:(tmp_path/(stem+'.'+ext)).write_bytes((root/'docs/tads_C'/(stem+'.'+ext)).read_bytes())
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
    (tmp_path/'ownership-review.json').write_text(json.dumps({'case':case,'allocations':int(m[1]),'frees':int(m[2]),'live':0,'strict_c17':True,'actual_main_doxygen_warnings':0,'main_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
