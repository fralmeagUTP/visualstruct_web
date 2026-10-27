"""Independent native-C oracle for the shipped sorting TAD (no source edits)."""
import ctypes
import random
import subprocess
import tempfile
import unittest
from pathlib import Path
from app.adapters.sorting_adapter import SortingAdapter
from app.services.c_code_service import CCodeService

class NativeSortingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='visualstruct-native-')
        root=Path(__file__).resolve().parents[1]
        lib=Path(cls.tmp.name)/'sorting.so'
        subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-shared','-fPIC',str(root/'docs/tads_C/tad_ordenamiento.c'),'-o',str(lib)],check=True,capture_output=True,text=True)
        cls.lib=ctypes.CDLL(str(lib))
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_native_and_simulator_agree(self):
        rng=random.Random(27102026)
        cases=[[3,1,2],[-3,0,-1],[2,2,1],[7],[rng.randint(-10,10) for _ in range(7)]]
        sources=CCodeService.get_structure_data('sorting_array')['operations']
        for meta in SortingAdapter().get_supported_algorithms():
            function=getattr(self.lib,meta['c_function'])
            function.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.c_size_t]
            returns_status=meta['id'] in {'mergesort','counting_sort','binsort','radixsort'}
            function.restype=ctypes.c_int if returns_status else None
            for values in cases:
                with self.subTest(algorithm=meta['id'],values=values):
                    native=(ctypes.c_int*len(values))(*values)
                    result=function(native,len(values))
                    if returns_status:self.assertEqual(result,1)
                    self.assertEqual(list(native),sorted(values))
                    adapter=SortingAdapter();adapter.create_array(values);adapter.select_algorithm(meta['id'])
                    simulated=adapter.run('step_by_step',source_code=sources[meta['id']])
                    self.assertEqual(simulated['result']['array'],list(native))

if __name__=='__main__':unittest.main(verbosity=2)
