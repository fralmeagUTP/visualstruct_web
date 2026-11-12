"""Released scripts retain exact, independently declared cache identities."""
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

import pytest

# 52dcec05 explicitly advanced these seven scripts to 20261111graph2.
# Graph subsequently advanced through scope1 (4521915) to mst1 (8186a4f).
# The authorized organic-growth release advances graph and graph_layout together.
# Do not derive expectations from templates: stale URLs must fail this check.
EXPECTED_SCRIPT_VERSIONS = {
    'interpreter_runtime.js': '20261111graph2',
    'counting_runtime.js': '20261111graph2',
    'sequential.js': '20261111graph2',
    'hierarchical.js': '20261111graph2',
    'graph.js': '20261112organic1',
    'graph_layout.js': '20261112organic1',
    'hash.js': '20261111graph2',
    'sorting.js': '20261111graph2',
}


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.urls.extend(value for key, value in attrs if key == 'src')


def _assert_script_versions(urls):
    selected = []
    for name, version in EXPECTED_SCRIPT_VERSIONS.items():
        matches = [url for url in urls if urlsplit(url).path.endswith('/js/' + name)]
        assert len(matches) == 1, f'{name}: expected exactly one script URL'
        url = matches[0]
        assert parse_qs(urlsplit(url).query).get('v') == [version], name
        selected.append(url)
    return selected


def test_updated_scripts_have_fresh_cache_identity(client):
    response = client.get('/')
    assert response.status_code == 200
    parser = Scripts()
    parser.feed(response.get_data(as_text=True))
    for url in _assert_script_versions(parser.urls):
        assert client.get(url).status_code == 200


@pytest.mark.parametrize('name', list(EXPECTED_SCRIPT_VERSIONS))
@pytest.mark.parametrize('bad_query', ['', '?v=20261106qa1', '?v=unapproved'])
def test_script_cache_identity_rejects_missing_old_and_unapproved_versions(name, bad_query):
    urls = ['/static/js/' + script + '?v=' + version
            for script, version in EXPECTED_SCRIPT_VERSIONS.items()]
    index = list(EXPECTED_SCRIPT_VERSIONS).index(name)
    urls[index] = '/static/js/' + name + bad_query
    with pytest.raises(AssertionError, match=name.replace('.', r'\.')):
        _assert_script_versions(urls)


def test_graph_cache_identity_rejects_previous_scope_release():
    urls = ['/static/js/' + script + '?v=' + version
            for script, version in EXPECTED_SCRIPT_VERSIONS.items()]
    urls[list(EXPECTED_SCRIPT_VERSIONS).index('graph.js')] = '/static/js/graph.js?v=20261111scope1'
    with pytest.raises(AssertionError, match=r'graph\.js'):
        _assert_script_versions(urls)
