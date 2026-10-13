"""The didactic operation list matches the actual seven visible list methods."""
import re,json
from app.services.help_service import HelpService

def test_linked_guide_operations_match_actual_visible_menu(client):
    page=client.get('/sequential/linked_list');assert page.status_code==200
    bootstrap=re.search(r'window.SEQ_VIEW_MODEL = (.*?);</script>',page.data.decode(),re.S);assert bootstrap
    model=json.loads(bootstrap.group(1))
    actual={op['name'] for op in model['operations'] if not op.get('hidden')}
    expected={'insertar_inicio','insertar_final','lista_insertar_elemento','buscar_elemento','eliminar_elemento','eliminar_repetidos','limpiar'}
    assert actual==expected
    assert set(HelpService.get_structure_help('linked_list')['supported_operations'])==expected
    guide=client.get('/help/sequential/linked_list');assert guide.status_code==200
    for name in ['lista_insertar_inicio','lista_insertar_final','lista_insertar_elemento','lista_buscar_elemento','lista_eliminar_elemento','lista_eliminar_repetidos','lista_limpiar']:
        assert name.encode() in guide.data
    for kind in ['source','header']:
        data=client.get('/help/source/linked_list/'+kind);assert data.status_code==200
        text=data.data.decode('utf-8-sig');assert re.search(r'void\s+lista_buscar_elemento\(Tlista\s+lista,\s*int\s+valor\)',text)
        assert 'lista_invertir' not in text
