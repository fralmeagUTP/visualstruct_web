"""The revised visible copy and Hash wire decoder must not reuse UX asset URLs."""
from html.parser import HTMLParser
from urllib.parse import urlsplit, parse_qs
import pytest

EXPECTED_VERSIONS = {
    'interpreter_runtime.js': '20261106qa1',
    'counting_runtime.js': '20261106qa1',
    'sequential.js': '20261106ci2',
    'hierarchical.js': '20261106ci2',
    'classroom_view.js': '20261106ci2',
    'graph.js': '20261106qa1',
    'hash.js': '20261106qa1',
    'sorting.js': '20261106qa1',
}

def assert_asset_versions(urls):
    for name, version in EXPECTED_VERSIONS.items():
        matching = [url for url in urls if urlsplit(url).path == '/static/js/' + name]
        assert len(matching) == 1, name
        assert parse_qs(urlsplit(matching[0]).query) == {'v': [version]}, name

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.urls.extend(value for key,value in attrs if key=='src')

def test_updated_scripts_have_fresh_cache_identity(client):
    response=client.get('/');assert response.status_code==200
    parser=Scripts();parser.feed(response.get_data(as_text=True))
    assert_asset_versions(parser.urls)
    for name in EXPECTED_VERSIONS:
        url=next(url for url in parser.urls if '/js/'+name+'?' in url)
        assert client.get(url).status_code==200

@pytest.mark.parametrize('mutation', ['old_sequential', 'old_classroom', 'unknown_version', 'duplicate', 'missing'])
def test_asset_version_gate_rejects_stale_or_ambiguous_delivery(mutation):
    urls = ['/static/js/' + name + '?v=' + version for name, version in EXPECTED_VERSIONS.items()]
    target = next(i for i, url in enumerate(urls) if '/sequential.js?' in url)
    if mutation == 'old_sequential':
        urls[target] = '/static/js/sequential.js?v=20261106qa1'
    elif mutation == 'old_classroom':
        target = next(i for i, url in enumerate(urls) if '/classroom_view.js?' in url)
        urls[target] = '/static/js/classroom_view.js?v=20261105ux1'
    elif mutation == 'unknown_version':
        urls[target] += 'unexpected'
    elif mutation == 'duplicate':
        urls.append(urls[target])
    else:
        urls.pop(target)
    with pytest.raises(AssertionError):
        assert_asset_versions(urls)
