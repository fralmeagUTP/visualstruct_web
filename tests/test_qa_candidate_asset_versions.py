"""The revised visible copy and Hash wire decoder must not reuse UX asset URLs."""
from html.parser import HTMLParser

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.urls.extend(value for key,value in attrs if key=='src')

def test_updated_scripts_have_fresh_cache_identity(client):
    response=client.get('/');assert response.status_code==200
    parser=Scripts();parser.feed(response.get_data(as_text=True))
    names=['interpreter_runtime.js','counting_runtime.js','sequential.js','hierarchical.js','graph.js','hash.js','sorting.js']
    for name in names:
        url=next(url for url in parser.urls if '/js/'+name+'?' in url)
        assert 'v=20261106qa1' in url
        assert client.get(url).status_code==200
