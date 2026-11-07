const extract = require('./export_dom_probe.js');
const mutation = process.argv[2] || 'valid';
const rect = (left,top,width,height) => ({left,top,width,height,right:left+width,bottom:top+height});
function element(id, top, parent=null) {
  const node = {id, tagName:'DIV', hidden:false, parentElement:parent, childNodes:[],
    styles:{display:'block',visibility:'visible',opacity:'1',color:'rgb(0, 0, 0)',fontSize:'16px'},
    box:rect(0,top,500,100), getBoundingClientRect(){return this.box;}};
  if(parent)parent.childNodes.push(node);
  return node;
}
const root=element('wrapper',0);root.box=rect(0,0,500,400);
const group=element('memory-parent',200,root);
const nodes=[element('sorting-visual-state',0,root),element('sorting-pedagogy-narration',100,root),element('sorting-live-memory',200,group)];
for(const node of nodes)node.childNodes.push({nodeType:3,textContent:node.id==='sorting-visual-state'?'Arreglo vacío. Crea o genera datos para iniciar.':'Actual content',box:rect(0,node.box.top,300,19)});
const terminal=element('sorting-live-memory-note',280,nodes[2]);
terminal.box=rect(0,280,500,19);
terminal.childNodes.push({nodeType:3,textContent:'Identificadores simbólicos; no son direcciones reales.',box:rect(0,280,300,19)});
root.querySelectorAll=()=>[group,...nodes,terminal];
global.getComputedStyle=node=>node.styles;
global.document={createRange:()=>({selectNodeContents(node){this.node=node;},getClientRects(){return [this.node.box];}})};
if(mutation==='zero_area')for(const node of [root,group,...nodes,terminal]) {node.box=rect(0,0,0,0);for(const text of node.childNodes)if(text.nodeType===3)text.box=rect(0,0,0,0);}
if(mutation==='missing_memory')root.querySelectorAll=()=>nodes.slice(0,2);
if(mutation==='hidden_terminal')terminal.styles.opacity='0';
if(mutation==='hidden_memory')nodes[2].styles.display='none';
if(mutation==='hidden_narration')nodes[1].styles.visibility='hidden';
if(mutation==='hidden_visual')nodes[0].styles.opacity='0';
if(mutation==='ancestor_opacity')group.styles.opacity='0';
if(mutation==='ancestor_visibility')group.styles.visibility='hidden';
if(mutation==='closed_details'){group.tagName='DETAILS';group.open=false;}
if(mutation==='transparent_text'){nodes[2].styles.color='rgba(0, 0, 0, 0)';terminal.styles.color='rgba(0, 0, 0, 0)';}
if(mutation==='empty_memory'){nodes[2].childNodes=[];terminal.childNodes=[];}
if(mutation==='zero_font')nodes[0].styles.fontSize='0px';
if(mutation==='crop_left')nodes[0].box=rect(-2,0,500,100);
if(mutation==='crop_top')nodes[0].box=rect(0,-2,500,100);
if(mutation==='crop_right')nodes[0].box=rect(0,0,502,100);
if(mutation==='crop_bottom')nodes[2].box=rect(0,200,500,202);
if(mutation==='text_crop')nodes[2].childNodes[0].box=rect(0,399,300,19);
console.log(JSON.stringify(extract(root)));
