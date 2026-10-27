'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test');
const source=fs.readFileSync(process.argv[2] || 'static/js/interpreter_runtime.js','utf8');
function runtimeFixture(throws=false){
 const urls=[],revoked=[],timers=[],clicks=[],anchors=[];
 const window={setTimeout:(fn,ms)=>{timers.push({fn,ms});return timers.length;},clearTimeout:()=>{},atob:s=>Buffer.from(s,'base64').toString('binary')};
 const document={readyState:'loading',addEventListener:()=>{},body:{appendChild:a=>{a.attached=true;}},createElement:()=>{const a={attached:false,click(){assert.equal(this.attached,true);if(throws)throw Error('download refused');clicks.push(this.href);},remove(){this.attached=false;}};anchors.push(a);return a;}};
 const URL={createObjectURL:blob=>{urls.push(blob);return `blob:qa/${urls.length}`;},revokeObjectURL:url=>revoked.push(url)};
 const context={window,document,URL,Blob,Uint8Array};vm.runInNewContext(source.includes('downloadJpg: triggerDataUrlDownload') ? source : source.replace('    exportVisualStateAsJpg,', '    exportVisualStateAsJpg, downloadJpg: triggerDataUrlDownload,'),context);
 return {api:window.InterpreterRuntime,urls,revoked,timers,clicks,anchors};
}
test('JPG download uses attached blob anchor, exact JPEG bytes/MIME and delayed cleanup',async()=>{
 const f=runtimeFixture();f.api.downloadJpg('data:image/jpeg;base64,/9j/2Q==','capture.jpg');
 assert.equal(f.urls.length,1);assert.equal(f.urls[0].type,'image/jpeg');assert.deepEqual([...new Uint8Array(await f.urls[0].arrayBuffer())],[255,216,255,217]);
 assert.deepEqual(f.clicks,['blob:qa/1']);assert.equal(f.anchors[0].download,'capture.jpg');assert.equal(f.anchors[0].attached,false);
 assert.equal(f.revoked.length,0);assert.equal(f.timers[0].ms,60000);f.timers[0].fn();assert.deepEqual(f.revoked,['blob:qa/1']);
});
test('download failure releases blob and anchor immediately',()=>{
 const f=runtimeFixture(true);assert.throws(()=>f.api.downloadJpg('data:image/jpeg;base64,/9j/2Q==','x.jpg'),/refused/);assert.deepEqual(f.revoked,['blob:qa/1']);assert.equal(f.anchors[0].attached,false);
});
test('invalid image output is not downloaded',()=>{const f=runtimeFixture();assert.throws(()=>f.api.downloadJpg('data:image/png;base64,AA=='),/JPG valido/);assert.equal(f.urls.length,0);});
function imageFixture(mode){
 const images=[],timers=new Map();let number=0;
 class Image{constructor(){images.push(this);}set src(value){this._src=value;if(value&&mode==='load')queueMicrotask(()=>this.onload?.());if(value&&mode==='error')queueMicrotask(()=>this.onerror?.());}get src(){return this._src;}}
 const context={Image,window:{setTimeout:fn=>{timers.set(++number,fn);return number;},clearTimeout:id=>timers.delete(id)},Promise,Error};
 const begin=source.indexOf('  function loadImageFromSource('),end=source.indexOf('  async function renderSvgMarkupToJpegDataUrl(',begin);
 vm.createContext(context);vm.runInContext(source.slice(begin,end)+';this.load=loadImageFromSource;',context);
 return{load:context.load,images,timers};
}
test('image onload resolves and clears timer/listeners',async()=>{const f=imageFixture('load');const image=await f.load('data:svg');assert.equal(image,f.images[0]);assert.equal(f.timers.size,0);assert.equal(image.onload,null);assert.equal(image.onerror,null);});
test('image onerror rejects and releases source/timer',async()=>{const f=imageFixture('error');await assert.rejects(f.load('data:svg'),/cargar/);assert.equal(f.images[0].src,'');assert.equal(f.timers.size,0);});
test('image with no event has finite timeout and releases resources',async()=>{const f=imageFixture('never');const promise=f.load('data:svg');assert.ok(f.timers.size>0,'missing finite image-load timeout');const rejection=assert.rejects(promise,/5 segundos/);[...f.timers.values()][0]();await rejection;assert.equal(f.images[0].src,'');assert.equal(f.timers.size,0);});
function rasterFixture(failures){
 const revoked=[],sources=[],progress=[];let attempts=0;
 const begin=source.indexOf('  async function renderSvgMarkupToJpegDataUrl('),end=source.indexOf('  async function exportVisualStateAsJpg(',begin);
 const context={Blob,URL:{createObjectURL:()=> 'blob:svg',revokeObjectURL:url=>revoked.push(url)},encodeURIComponent,
  loadImageFromSource:async url=>{sources.push(url);return{};},drawImageToJpegDataUrl:()=>{if(attempts++<failures)throw Error('raster failed');return 'data:image/jpeg;base64,/9j/2Q==';}};
 vm.createContext(context);vm.runInContext(source.slice(begin,end)+';this.render=renderSvgMarkupToJpegDataUrl;',context);
 return{render:()=>context.render('<svg/>',10,20,.9,1,m=>progress.push(m)),revoked,sources,progress};
}
test('raster prefers self-contained data SVG and revokes blob after fallback',async()=>{const f=rasterFixture(1);assert.match(await f.render(),/^data:image\/jpeg/);assert.match(f.sources[0],/^data:image\/svg/);assert.equal(f.sources[1],'blob:svg');assert.deepEqual(f.revoked,['blob:svg']);assert.ok(f.progress.includes('Creando JPG...'));});
test('raster failure always releases intermediate URL',async()=>{const f=rasterFixture(2);await assert.rejects(f.render(),/raster failed/);assert.deepEqual(f.revoked,['blob:svg']);});
