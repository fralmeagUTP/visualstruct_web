"""Finite sorting/API regression suite; run from project root with unittest."""
import json
import tempfile
import unittest
from app import create_app
from app.config import Config
from app.adapters.sorting_adapter import SortingAdapter

class SortingRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache = tempfile.TemporaryDirectory(prefix='visualstruct-qa-')
        class TestConfig(Config):
            TESTING = True
            SESSION_CACHE_DIR = cls.cache.name
        cls.app = create_app(TestConfig)
    @classmethod
    def tearDownClass(cls):
        cls.cache.cleanup()
    def setUp(self):
        self.client = self.app.test_client()
    def post(self, endpoint, data):
        return self.client.post('/api/ordenamiento/' + endpoint, json=data)
    def test_unknown_algorithm_is_validation_not_server_error(self):
        original = self.post('create-array', {'values':'3,1,2'}).get_json()
        for endpoint in ['run', 'step', 'algorithm']:
            with self.subTest(endpoint=endpoint):
                response = self.post(endpoint, {'algorithm_id':'inexistente', 'mode':'step_by_step', 'cursor':-1, 'direction':'next'})
                self.assertEqual(response.status_code,400)
                data=response.get_json()
                self.assertFalse(data['success'])
                self.assertEqual(data['history'], original['history'])
                self.assertEqual(data['visual_state']['items'],[3,1,2])
        self.assertEqual(self.post('run',{'algorithm_id':'burbuja','mode':'fast'}).status_code,200)
    def test_c_int_extremes_and_counting_range_rejection(self):
        for meta in SortingAdapter().get_supported_algorithms():
            for values in ([2147483647,-2147483648,0],[-2147483648,-2147483647,-2147483648]):
                with self.subTest(algorithm=meta['id'],values=values):
                    self.assertEqual(self.post('create-array',{'values':values}).status_code,200)
                    response=self.post('run',{'algorithm_id':meta['id'],'mode':'step_by_step'})
                    rejected=meta['id'] in {'counting_sort','binsort'} and max(values)-min(values)>1000000
                    self.assertEqual(response.status_code,400 if rejected else 200)
                    self.assertEqual(response.get_json()['visual_state']['items'],values if rejected else sorted(values))

    def test_all_algorithms_both_modes(self):
        for algorithm in SortingAdapter().get_supported_algorithms():
            name=algorithm['id']
            for values in ([3,1,2], [2,2,1], [-3,0,-1], [7]):
                results=[]
                for mode in ('fast','step_by_step'):
                    with self.subTest(algorithm=name,values=values,mode=mode):
                        self.assertEqual(self.post('create-array',{'values':values}).status_code,200)
                        response=self.post('run',{'algorithm_id':name,'mode':mode})
                        self.assertEqual(response.status_code,200,response.get_json())
                        result=response.get_json()
                        self.assertEqual(result['visual_state']['items'],sorted(values))
                        self.assertEqual(result['result']['array'],sorted(values))
                        if mode == 'step_by_step':
                            trace=result['execution_trace']
                            steps=trace['steps']
                            self.assertGreater(len(steps), 1)
                            self.assertEqual(steps[0]['state_snapshot']['items'], values)
                            self.assertEqual(steps[-1]['state_after']['items'], sorted(values))
                            source=trace['source_code'].splitlines()
                            for index, step in enumerate(steps):
                                self.assertTrue(step.get('pedagogy'), (name,index,'missing pedagogy'))
                                self.assertTrue(step['state_after'].get('trace_action'), (name,index,'missing explanation'))
                                if step['line_index'] is not None:
                                    self.assertGreaterEqual(step['line_index'],0)
                                    self.assertLess(step['line_index'],len(source))
                                    self.assertEqual(step['line_text'],source[step['line_index']])
                                if index:
                                    self.assertEqual(step['state_snapshot']['items'], steps[index-1]['state_after']['items'])
                        results.append(result['visual_state']['items'])
                self.assertEqual(results[0],results[1])

if __name__ == '__main__': unittest.main(verbosity=2)
