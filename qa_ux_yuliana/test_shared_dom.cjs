/* Actual frontend initialization in a DOM emulator. Not browser/layout/pixel QA. */
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const {JSDOM, VirtualConsole} = require(process.env.JSDOM_MODULE || 'jsdom');
const root = path.resolve(__dirname, '..');
const fixtureDir = process.argv[2];
assert(fixtureDir, 'Pass the directory produced by capture_dom_fixtures.py');
const routes = JSON.parse(fs.readFileSync(path.join(fixtureDir, 'routes.json')));
async function load(name, route) {
  const errors = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error.message));
  const dom = new JSDOM(fs.readFileSync(path.join(fixtureDir, `${name}.html`), 'utf8'), {
    url: `https://example.invalid${route}`, runScripts:'outside-only', pretendToBeVisual:true, virtualConsole
  });
  const w = dom.window, d = w.document;
  w.scrollTo = () => {}; w.HTMLElement.prototype.scrollIntoView = () => {};
  // Use window-owned timers so closing a DOM cancels queued paint callbacks.
  w.requestAnimationFrame = callback => w.setTimeout(()=>callback(Date.now()),0);
  w.cancelAnimationFrame = id => w.clearTimeout(id);
  w.fetch = async () => { throw new Error('Unexpected network request in initialization test'); };
  w.confirm = () => false;
  for (const link of [...d.querySelectorAll('link[rel="stylesheet"]')]) {
    const style = d.createElement('style');
    style.textContent = fs.readFileSync(path.join(root, new URL(link.href).pathname), 'utf8');
    link.replaceWith(style);
  }
  for (const script of [...d.scripts]) {
    const source = script.src ? fs.readFileSync(path.join(root, new URL(script.src).pathname), 'utf8') : script.textContent;
    w.eval(source);
  }
  await new Promise(resolve => w.setTimeout(resolve, 25));
  assert.deepEqual(errors, [], `${name}: JavaScript initialization errors`);
  return {w,d,dom};
}
async function checkModules() {
  let modules = 0;
  for (const [name, route] of Object.entries(routes)) {
    const {w,d,dom} = await load(name, route);
    const code = d.querySelector('#seq-code-region,#hier-code-region,#sorting-code-region,#graph-code-region,#hash-code-region');
    const toggle = d.getElementById('didactic-mode-switch');
    assert.equal(d.documentElement.dataset.didacticMode, 'visual', name);
    assert.equal(w.getComputedStyle(code).display, 'none', `${name}: code hidden by default`);
    const visual = d.querySelector('.classroom-visual');
    assert.notEqual(w.getComputedStyle(visual).display, 'none', `${name}: visual stays available`);
    for (const full of [true,false,true,false]) {
      toggle.checked=full; toggle.dispatchEvent(new w.Event('change', {bubbles:true}));
      assert.equal(d.documentElement.dataset.didacticMode, full?'full':'visual', name);
      assert.equal(w.localStorage.getItem('didactic-mode'), full?'full':'visual', name);
      assert.equal(w.getComputedStyle(code).display==='none', !full, `${name}: repeat toggle`);
    }
    for (const panel of d.querySelectorAll('.classroom-results,.classroom-memory')) {
      assert(panel.classList.contains('didactic-technical'), `${name}: technical wrapper retained`);
      assert.equal(w.getComputedStyle(panel).display, 'none', `${name}: memory/result wrapper hidden`);
    }
    assert.equal(d.querySelectorAll('.code-navigation-help').length, 1, `${name}: one navigation hint`);
    const functions = [...d.querySelectorAll('[class$="function-index"] button, .seq-function-index button, .hier-function-index button, .sorting-function-index button, .graph-function-index button, .hash-function-index button')];
    if (functions.length) {
      toggle.checked=true; toggle.dispatchEvent(new w.Event('change'));
      const activeBefore = functions.filter(n=>n.classList.contains('is-active')).map(n=>n.textContent);
      functions.at(-1).click();
      assert(functions.at(-1).classList.contains('is-code-consulted'), `${name}: consulted function marked`);
      assert.deepEqual(functions.filter(n=>n.classList.contains('is-active')).map(n=>n.textContent), activeBefore, `${name}: execution marker unchanged`);
    }
    if (name==='stack') {
      const prepare = d.querySelector('.seq-prepare'), controls = d.querySelector('.seq-execute');
      assert.equal(prepare.nextElementSibling, controls, 'Pila controls immediately follow preparation in DOM');
      assert(controls.compareDocumentPosition(d.querySelector('.sequential-primary-workspace')) & w.Node.DOCUMENT_POSITION_FOLLOWING);
      assert.equal(d.querySelectorAll('#seq-sim-execute').length, 1, 'Pila controls not duplicated');
    }
    dom.window.close(); modules++;
  }
  console.log(`PASS ${modules} actual route/script initializations, repeated mode toggles, technical wrappers, navigation markers and Pila DOM order. No layout/pixel claim.`);
}
async function checkBatches() {
  const batches = JSON.parse(fs.readFileSync(path.join(fixtureDir,'batches.json')));
  for (const [name, operation] of [['stack','desapilar'],['stack','limpiar'],['queue','encolar']]) {
    const {w,d,dom} = await load(name, routes[name]);
    const sent=[];
    w.fetch = async (url, options) => {
      sent.push(JSON.parse(options.body));
      assert(sent.length<=3, 'No duplicate or unexpected fourth operation');
      return {ok:true,json:async()=>structuredClone(batches[name][sent.length-1])};
    };
    const select=d.querySelector('#operation-select');
    select.value=operation; select.dispatchEvent(new w.Event('change',{bubbles:true}));
    const values=d.querySelector('#multiple-values'); values.value='10,20,30';
    values.dispatchEvent(new w.Event('input',{bubbles:true}));
    assert.match(d.querySelector('#multiple-preview').textContent,/No ejecuta la operación individual/);
    d.querySelector('#multiple-load').click();
    const deadline=Date.now()+5000;
    while(!d.querySelector('#multiple-status').textContent.includes('Completado') && Date.now()<deadline) await new Promise(r=>w.setTimeout(r,5));
    assert.match(d.querySelector('#multiple-status').textContent,/Completado: 3 de 3/);
    assert.equal(select.value,operation,'Restores original individual operation');
    assert.equal(sent.length,3);
    assert.deepEqual(sent.map(item=>item.payload.value),['10','20','30']);
    if (operation==='encolar') {
      assert.equal(d.querySelector('input[name="value"]').value,'','Last batch value cannot be accidentally reused');
      d.querySelector('#seq-sim-execute').click();
      await new Promise(r=>w.setTimeout(r,10)); assert.equal(sent.length,3,'Empty new value sends no mutation');
    }
    const before=JSON.stringify(w.SEQ_VIEW_MODEL.visual_state);
    d.querySelector('#multiple-load').click();
    await new Promise(r=>w.setTimeout(r,10));
    assert.equal(sent.length,3,'Late duplicate batch click ignored');
    assert.equal(JSON.stringify(w.SEQ_VIEW_MODEL.visual_state),before);
    dom.window.close();
  }
  console.log('PASS real frontend batch flows: Pila Desapilar/Limpiar selection retained, Cola fresh input required, exact 3 calls and duplicate-click prevention. Backend responses generated with isolated Flask clients.');
}
async function checkBatchTerminals() {
  for (const terminal of ['done','stopped','failed','uncertain']) {
    const dom = new JSDOM('<form><select name="operation"><option value="encolar">Encolar</option><option value="limpiar" selected>Limpiar</option></select><input name="value" value="old"></form>',{runScripts:'outside-only',url:'https://example.invalid/'});
    const w=dom.window,d=w.document,form=d.querySelector('form'),select=d.querySelector('select'),field=d.querySelector('input');
    w.eval(fs.readFileSync(path.join(root,'static/js/multiple_input.js'),'utf8'));
    let cursor=-1,calls=0;
    const player={pause(){},hasTrace(){return true},getTotalSteps(){return 2},getCursor(){return cursor},isAtEnd(){return cursor===1},seek(i){cursor=i},reset(){cursor=-1},async step(){cursor++},prev(){cursor--},async play(){cursor=1}};
    const adapter={model:{id:'queue',visual_state:{}},form,player,isBusy:()=>false,sync(){},select(value){select.value=value},async execute(value){calls++;field.value=String(value);return terminal==='failed'?{success:false,message:'Known rejection'}:terminal==='uncertain'?null:{success:true}}};
    const q=w.MultipleInput.mount(adapter),values=d.querySelector('#multiple-values');values.value='10,20';values.dispatchEvent(new w.Event('input'));
    d.querySelector('#multiple-step').click();await new Promise(r=>w.setTimeout(r,0));
    if(terminal==='stopped')q.stop();
    if(terminal==='done')while(q.state().active)await q.next();
    assert.equal(q.state().phase,terminal);
    if(terminal==='uncertain') {
      assert.equal(select.value,'encolar');assert(select.disabled,'Uncertain outcome remains locked until reconciliation');
      assert.equal(d.querySelector('#multiple-reconcile').hidden,false);
      await q.start([20],'normal');assert.equal(calls,1,'No retry for uncertain outcome');
    } else {
      assert.equal(select.value,'limpiar',`${terminal}: restores original selection`);
      assert.equal(field.value,'',`${terminal}: no reusable last batch value`);
      assert.equal(select.disabled,false);
      assert.equal(d.querySelector('#multiple-load').disabled,true,'Must edit list before another batch');
    }
    dom.window.close();
  }
  console.log('PASS batch terminal DOM states: done, stopped, failed restore selection/clear value; uncertain outcome locks and never retries.');
}
module.exports={load};
if(require.main===module)checkModules().then(checkBatches).then(checkBatchTerminals).catch(error=>{console.error(error);process.exitCode=1});
