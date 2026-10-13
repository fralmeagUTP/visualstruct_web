"""HTTP Hash contracts and unchanged authentic callers under strict C17/Doxygen."""
from pathlib import Path
import shutil,subprocess
import pytest
from tests.test_graph_bfs_documentation import run_doxygen
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-create-insert-instructions-medium'

def test_hash_downloaded_c_h_and_caller_doxygen(client,tmp_path):
    files=[]
    for kind,filename in [('source','tad_tabla_hash.c'),('header','tad_tabla_hash.h')]:
        response=client.get('/help/source/hash_table/'+kind);assert response.status_code==200
        assert response.data==(ROOT/'docs/tads_C'/filename).read_bytes()
        p=tmp_path/filename;p.write_bytes(response.data);files.append(p)
    response=client.get('/help/source/hash_table/main');assert response.status_code==200
    p=tmp_path/'main.c';p.write_bytes(response.data);files.append(p)
    run_doxygen(tmp_path,files)

@pytest.mark.parametrize('case',['downloads','collision_load_gt_one','update_middle','negative_extremes','node_null_repeat'])
def test_hash_actual_downloaded_caller_c17_and_doxygen(case,tmp_path):
    source=E/'downloads/main.c' if case=='downloads' else E/'browser'/case/'main.c'
    assert source.is_file();p=tmp_path/'main.c';p.write_bytes(source.read_bytes())
    for filename in ['tad_tabla_hash.c','tad_tabla_hash.h']:
        shutil.copyfile(E/'downloads'/filename,tmp_path/filename)
    run_doxygen(tmp_path,[p])
    compiler=shutil.which('gcc');assert compiler
    r=subprocess.run([compiler,'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(p),str(tmp_path/'tad_tabla_hash.c'),'-o',str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=30)
    assert r.returncode==0 and not r.stderr,r.stderr
    r=subprocess.run([str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=10)
    assert r.returncode==0 and 'state:3:' in r.stdout
