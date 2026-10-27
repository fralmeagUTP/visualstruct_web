import copy
import unittest
from app.services.structure_service import StructureService

class PositionBoundsTests(unittest.TestCase):
    def test_new_c_position_and_relative_rejected_before_body(self):
        history=StructureService.execute_operation('linked_list','insertar_final',{'value':7},[])['history']
        for operation in ['lista_insertar_elemento','insertar_posicion','insertar_elemento','eliminar_posicion']:
            for field in (['position','relative'] if operation=='insertar_elemento' else ['position']):
                for bad in [-2147483649,2147483648]:
                    with self.subTest(operation=operation,field=field,bad=bad):
                        payload={'value':3,'position':1,'relative':0};payload[field]=bad
                        r=StructureService.execute_operation('linked_list',operation,payload,copy.deepcopy(history))
                        self.assertFalse(r['success'])
                        if field=='position':self.assertIn('32 bits',r['message'])
                        self.assertEqual(r['history'],history)
                        self.assertFalse(r['execution_trace']['execution_started'])
                        self.assertEqual(r['execution_trace']['steps'],[])
    def test_optional_relative_preserves_existing_default(self):
        history=StructureService.execute_operation('linked_list','insertar_final',{'value':7},[])['history']
        for suffix in [{},{'relative':None},{'relative':''},{'relative':'  '},{'relative':0.0}]:
            with self.subTest(payload=suffix):
                result=StructureService.execute_operation('linked_list','insertar_elemento',{'value':3,'position':1,**suffix},copy.deepcopy(history))
                self.assertTrue(result['success'],result['message'])
                self.assertEqual(result['history'][-1]['payload'],{'value':3,'position':1,**suffix})

    def test_representable_positions_keep_native_contract(self):
        for pos in [-2147483648,2147483647,1]:
            r=StructureService.execute_operation('linked_list','insertar_posicion',{'value':7,'position':pos},[])
            self.assertNotIn('32 bits',r['message'])
    def test_legacy_position_history_preserved_not_replayed_as_c(self):
        history=[{'operation':'insertar_posicion','payload':{'value':7,'position':2147483648}}]
        view=StructureService.get_view_model('linked_list',copy.deepcopy(history))
        self.assertEqual(view['history'],history)
        r=StructureService.execute_operation('linked_list','insertar_final',{'value':3},copy.deepcopy(history))
        self.assertFalse(r['success']);self.assertEqual(r['history'],history)
        self.assertEqual(r['execution_trace']['steps'],[])

if __name__=='__main__':unittest.main()
