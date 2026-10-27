"""Compile actual main copy payloads, without whitespace/source normalization.
Run qa/frontend_main_audit.py first to generate the local operation fixtures.
"""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
subprocess.run(['node','qa_classroom_v1/test_raw_main_copy.js'],cwd=ROOT,check=True)
pairs=dict(zip(['queue','priority_queue','linked_list','circular_list','sublist','abb','avl','red_black','binary_heap'],['cola','cola_prioridad','lista','lista_circular','sublista','abb','avl','rojo_negro','monticulo_binario']))
for key,tad in pairs.items():
 out=ROOT/'qa_classroom_v1/raw_main'/key
 subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'docs/tads_C'),str(out.with_suffix('.c')),str(ROOT/f'docs/tads_C/tad_{tad}.c'),'-o',str(out)],check=True,capture_output=True)
 subprocess.run([str(out)],check=True,capture_output=True)
print('PASS 9 exact main copy payloads compile C17-Werror and execute')
