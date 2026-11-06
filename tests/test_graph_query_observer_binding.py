"""The query observer imports the approved shared oracle without executing UI."""
from importlib import reload
from unittest.mock import patch
from _book_graph_browser_contract import COLLECT, assert_browser_row, decoded_body, main_text


def test_query_observer_uses_shared_contract_without_ast_scraping_or_browser_start():
    with patch('werkzeug.serving.make_server', side_effect=AssertionError('Import must not start a server')):
        import _graph_query_browser_contract_observer as observer
        reload(observer)
    assert observer.COLLECT is COLLECT
    assert observer.assert_browser_row is assert_browser_row
    assert observer.decoded_body is decoded_body
    assert observer.main_text is main_text
