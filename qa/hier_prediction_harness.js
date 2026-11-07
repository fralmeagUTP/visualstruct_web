'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function extractRange(source,start,end,label) {
 const begin=source.indexOf(start),finish=source.indexOf(end,begin+start.length);
 assert.ok(begin>=0,`${label}: missing start delimiter`);
 assert.equal(source.indexOf(start,begin+start.length),-1,`${label}: ambiguous start delimiter`);
 assert.ok(finish>begin,`${label}: missing end delimiter`);
 const fragment=source.slice(begin,finish);
 new vm.Script(fragment,{filename:`hierarchical.js:${label}`});
 return fragment;
}
function harness(trace,source=fs.readFileSync('static/js/hierarchical.js','utf8')) {
 const nodes={},listeners={};
 function node(){return {value:'',checked:false,disabled:false,textContent:'',innerHTML:'',handlers:{},addEventListener(name,handler){this.handlers[name]=handler;},closest(){return {open:false};}};}
 const document={addEventListener(name,handler){listeners[name]=handler;},getElementById:id=>nodes[id]};
 class Element {closest(){return null;}}
 const context=vm.createContext({window:{},document,Element,HTMLInputElement:class{},HTMLSelectElement:class{},HTMLTextAreaElement:class{}});
 vm.runInContext(source,context);
 for(const key of ['predictionSelect','checkPrediction','hintButton','skipPrediction','predictionFeedback','practiceMode','resetProgress','simStepButton'])context[key]=node();
 for(const key of ['hier-prediction-prompt','hier-open-prediction','hier-prediction-context','h-field-value'])nodes[key]=node();
 let steps=0,seeks=0,metricsWrites=0;
 Object.assign(context,{predictionController:null,predictionTargetKey:'',predictionTraceRef:null,consoleState:{trace},traceCursor:-1,conceptualProgress:{attempts:0,correct:0},operationSelect:{value:'insertar',selectedOptions:[{textContent:'Insertar'}]},currentPedagogyFrame:null,renderConceptualProgress(){metricsWrites++;},practiceCover:{hidden:false},visualContainer:{classList:{remove(){}}},isStepByStepEnabled:()=>true,ensureTraceForCurrentSelection:async()=>true});
 context.tracePlayer={hasTrace:()=>true,seek(){seeks++;throw new Error('Prediction must not seek');},async step(){steps++;context.traceCursor++;context.syncPredictionUI();},prev(){context.traceCursor--;context.syncPredictionUI();}};
 vm.runInContext(extractRange(source,'  predictionController = createHierPredictionController(','  let comparisonRequestVersion =','prediction handlers'),context);
 vm.runInContext(extractRange(source,'  async function stepHierManually(','  prepareButton?.','manual step'),context);
 vm.runInContext(extractRange(source,'  document.addEventListener("keydown",async(event)=>{','  if(window.matchMedia','keyboard'),context);
 return {context,nodes,listeners,Element,counts:()=>({steps,seeks,metricsWrites})};
}
module.exports={extractRange,harness};
