"""RBT collector reads exact semantic stdout from the real console publisher."""
import json
from pathlib import Path
import shutil
import subprocess
import pytest
from _rbt_stdout_reader import RBT_STDOUT_READER

@pytest.mark.parametrize('stdout,missing', [
    ('', False),
    ('  repeat\nrepeat\n \t', False),
    ('(sin salida printf en esta ruta)', False),
    ('', True),
])
def test_rbt_stdout_reader_with_real_publisher(stdout, missing):
    node = shutil.which('node')
    assert node, 'Node is required for this renderer contract'
    renderer = Path(__file__).resolve().parents[1] / 'static/js/console-history.js'
    script = r"""
const fs=require('fs');global.window={};
eval(fs.readFileSync(process.argv[1],'utf8'));
const input=JSON.parse(process.argv[2]);
const el={dataset:{},textContent:'',style:{},scrollTop:0,scrollLeft:0,scrollHeight:0,clientHeight:0,
 hasAttribute(name){return name==='data-console-copy' && Object.prototype.hasOwnProperty.call(this.dataset,'consoleCopy');}};
window.ConsoleHistory.publish(el,input.stdout);
const read=eval('('+input.reader+')');
if(input.missing)delete el.dataset.consoleCopy;
try{process.stdout.write(JSON.stringify({value:read(el)}));}
catch(error){process.stdout.write(JSON.stringify({error:error.message}));}
"""
    run = subprocess.run([node, '-e', script, str(renderer), json.dumps({'stdout': stdout, 'missing': missing, 'reader': RBT_STDOUT_READER})], capture_output=True, text=True, timeout=10, check=True)
    result = json.loads(run.stdout)
    if missing:
        assert result == {'error': 'Missing data-console-copy'}
    else:
        assert result == {'value': {'stdout': stdout, 'stdoutDisplay': stdout if stdout != '' else '(sin salida printf en esta ruta)'}}
