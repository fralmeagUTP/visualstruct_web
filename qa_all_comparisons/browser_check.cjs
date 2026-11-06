/* Finite browser acceptance for the isolated all-comparisons change.
   Run with VISUALSTRUCT_PYTHON and PLAYWRIGHT_MODULE pointing to existing runtimes. */
const {spawn} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const output = path.join(__dirname, 'evidence'); fs.mkdirSync(output, {recursive:true});
const server = spawn(process.env.VISUALSTRUCT_PYTHON || 'python', ['-u', '-c', `
from app import create_app
from app.config import Config
from werkzeug.serving import make_server
import tempfile
class PrivateConfig(Config):
    TESTING = True
    APP_ENV = 'testing'
    SESSION_COOKIE_NAME = 'all_comparisons_test'
    SESSION_CACHE_DIR = tempfile.mkdtemp(prefix='all-comparisons-sessions-')
app = create_app(PrivateConfig)
server = make_server('127.0.0.1', 0, app, threaded=True)
print(server.server_port, flush=True)
server.serve_forever()
`], {cwd:root, stdio:['ignore','pipe','pipe']});
let stderr=''; server.stderr.on('data', chunk => stderr += chunk);
const basePromise = new Promise((resolve,reject) => {
  server.stdout.once('data', chunk => resolve('http://127.0.0.1:'+String(chunk).trim()));
  server.once('error',reject);
  server.once('exit',code => reject(new Error('Server exited '+code+' '+stderr)));
});
let browser;
const structures={abb:'abb',avl:'avl','red-black':'red_black',heap:'binary_heap'};
const expectedNames={abb:'Árbol Binario de Búsqueda',avl:'Árbol AVL',red_black:'Árbol Rojo-Negro',binary_heap:'Montículo Binario (min-heap)'};
(async()=>{
  const base=await basePromise;
  browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || '/usr/bin/chromium',headless:true});
  const context=await browser.newContext({viewport:{width:1366,height:1000}});
  const page=await context.newPage(); page.setDefaultTimeout(7000);
  const errors=[], posts=[]; page.on('pageerror',error=>errors.push(String(error))); page.on('request',request=>{if(request.method()==='POST') posts.push(request.url());});
  async function openPanel(){
    if(await page.locator('#hier-understand-toggle').getAttribute('aria-expanded')==='false') await page.click('#hier-understand-toggle');
    const summary=page.locator('details.hier-learning-disclosure > summary').filter({hasText:/^Comparar$/});
    await summary.focus(); await summary.press('Space');
    assert.equal(await summary.evaluate(el=>el.parentElement.open),true);
  }
  async function run(kind, values='9, 3, 7'){
    await page.selectOption('#hier-compare-kind',kind); await page.fill('#hier-compare-values',values);
    const responsePromise=page.waitForResponse(response=>response.url().endsWith('/hierarchical/compare'));
    await page.click('#hier-compare-run'); const response=await responsePromise;
    await page.waitForFunction(()=>!document.querySelector('#hier-compare-run').disabled);
    return response.json();
  }
  const cases=[];
  for(const [alias,sid] of Object.entries(structures)){
    await page.goto(base+'/hierarchical/'+sid); await openPanel();
    assert.equal(await page.locator('#hier-compare-kind option').count(),17);
    assert((await page.locator('#hier-compare-kind').inputValue()).startsWith(alias+'-'));
    const before=await page.evaluate(()=>window.HIER_VIEW_MODEL.visual_state);
    for(const [otherAlias,otherSid] of Object.entries(structures)){
      if(otherAlias===alias) continue;
      const kind=alias+'-'+otherAlias, data=await run(kind);
      assert.deepEqual(data.sides.map(side=>side.structure),[sid,otherSid]);
      assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),2);
      const initial=await page.locator('#hier-compare-grid').innerText(), n=posts.length;
      await page.click('#hier-compare-next'); assert.notEqual(await page.locator('#hier-compare-grid').innerText(),initial);
      await page.click('#hier-compare-prev'); assert.equal(await page.locator('#hier-compare-grid').innerText(),initial);
      assert.equal(posts.length,n); cases.push(kind);
    }
    const kind=alias+'-all', data=await run(kind);
    assert.equal(data.sides[0].structure,sid); assert.equal(new Set(data.sides.map(side=>side.structure)).size,4);
    assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),4);
    for(const step of [2,3]){
      await page.click('#hier-compare-next');
      const steps=await page.locator('#hier-compare-grid .hier-compare-card').allTextContents(); assert(steps.every(text=>text.includes('Paso: '+step)));
    }
    assert.equal(await page.locator('#hier-compare-next').isDisabled(),true);
    assert.deepEqual(await page.evaluate(()=>window.HIER_VIEW_MODEL.visual_state),before);
    cases.push(kind);
    if(alias==='abb') await page.locator('#hier-compare-grid').screenshot({path:path.join(output,'abb-against-all.png')});
  }
  await run('traversals'); assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),3);
  assert.equal(await page.locator('#hier-compare-next').isDisabled(),true);
  assert.equal(await page.locator('#hier-compare-prev').isDisabled(),true);
  await run('heap-all','7'); assert.equal(await page.locator('#hier-compare-next').isDisabled(),true);
  await run('heap-all','7, 7'); assert.match(await page.locator('#hier-compare-conclusion').innerText(),/sin duplicados/);
  assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),0);
  assert.equal(await page.locator('#hier-compare-next').isDisabled(),true);
  await run('heap-all'); await page.fill('#hier-compare-values','11, 2');
  assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),0);
  assert.equal(await page.locator('#hier-compare-input').innerText(),'');
  await run('heap-all'); await page.selectOption('#hier-compare-kind','abb-avl');
  assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),0);
  // Response race: an aborted old request must not revive a superseded selection.
  let pendingRoute;
  await page.route('**/hierarchical/compare',route=>{pendingRoute=route;});
  await page.click('#hier-compare-run');
  assert.equal(await page.locator('#hier-compare-run').isDisabled(),true);
  const count=posts.length; await page.evaluate(()=>document.querySelector('#hier-compare-run').click()); assert.equal(posts.length,count);
  await page.selectOption('#hier-compare-kind','avl-all');
  assert.equal(await page.locator('#hier-compare-run').isDisabled(),false);
  await pendingRoute.continue().catch(()=>{}); await page.unroute('**/hierarchical/compare');
  await page.waitForTimeout(100);
  assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),0);
  await run('avl-all'); assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),4);
  const disclosure=page.locator('details.hier-learning-disclosure').filter({has:page.locator('#hier-compare-grid')});
  await disclosure.locator('summary').click(); await disclosure.locator('summary').click();
  assert.equal(await page.locator('#hier-compare-grid .hier-compare-card').count(),4);
  await page.setViewportSize({width:390,height:844});
  const overflow=await page.evaluate(()=>({width:innerWidth,body:document.documentElement.scrollWidth}));
  assert(overflow.body<=overflow.width,JSON.stringify(overflow));
  await page.locator('#hier-compare-grid').screenshot({path:path.join(output,'all-comparisons-mobile.png')});
  assert.equal(await page.locator('input[type=range]').count(),0);
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'browser-results.json'),JSON.stringify({cases,traversals:true,singleValue:true,invalidInput:true,manualNavigation:true,sessionViewPreserved:true,staleResponseDiscarded:true,repeatedClickPrevented:true,changeInvalidation:true,disclosureReopen:true,mobile:overflow,jsErrors:errors,chromium:browser.version()},null,2)+'\n');
  console.log('PASS: 12 directed pairs, 4 all views, traversal/validation/navigation/race checks.');
})().catch(error=>{console.error(error); process.exitCode=1;}).finally(async()=>{if(browser) await browser.close();server.kill('SIGTERM');});
