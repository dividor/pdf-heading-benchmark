const el=id=>document.getElementById(id);
const colours=['#888','#006ea5','#00806a','#8b4bb1','#bc6405','#c02d65','#604f34'];
let current=DATA.documents.find(d=>d.split==='test')||DATA.documents[0];
let pn=current.review_pages[0]||current.pages[0].number;
const linePage=id=>Number(id.match(/^p(\d+)/)[1]);
function mark(group,box,prediction,index){
 const ns='http://www.w3.org/2000/svg';const rect=document.createElementNS(ns,'rect');
 const colour=prediction?'#e74c22':colours[group.level];
 Object.entries({x:box[0],y:box[1],width:box[2]-box[0],height:box[3]-box[1],fill:colour,'fill-opacity':prediction?0:0.12,stroke:colour,'stroke-width':prediction?1.7:1}).forEach(([k,v])=>rect.setAttribute(k,v));
 if(prediction)rect.setAttribute('stroke-dasharray','4 2');el('overlay').append(rect);
 const text=document.createElementNS(ns,'text');text.setAttribute('x',Math.max(2,box[0]-(prediction?38:22)));text.setAttribute('y',box[1]+9);text.setAttribute('font-size',9);text.setAttribute('fill',colour);text.textContent=(prediction?'M':'H')+group.level;el('overlay').append(text);
}
function drawGroups(groups,prediction){groups.forEach(g=>g.bboxes.forEach((box,i)=>{if(linePage(g.line_ids[i])===pn)mark(g,box,prediction,i);}));}
function page(){
 const p=current.pages.find(p=>p.number===pn);el('page').value=pn;el('image').src=p.image;el('overlay').replaceChildren();el('overlay').setAttribute('viewBox',`0 0 ${p.width} ${p.height}`);
 el('page-title').textContent=`PDF page ${pn} / ${current.total_pages}`;
 const full=current.review_pages.includes(pn);
 el('page-note').textContent=(full?'Fully reviewed page: unmarked lines are ordinary text.':'Partial/context page: only marked positive headings were labelled; other lines are unlabelled.')+(current.split==='test'?' Orange dashed M boxes are selected-model predictions.':' Model predictions are shown only on the fresh test pages.');
 if(el('gold').checked)drawGroups(current.annotations,false);if(el('pred').checked)drawGroups(current.predictions,true);
}
function report(){
 el('report').value=current.id;el('page').replaceChildren();current.pages.forEach(p=>el('page').add(new Option(`${p.number} · ${current.review_pages.includes(p.number)?'full review':current.toc_pages.includes(p.number)?'contents context':'positive labels only'}`,p.number)));
 el('source').href=current.url;el('coverage').textContent=`${current.title} · ${current.language} · ${current.split} · ${current.total_pages} total PDF pages. ${current.review_pages.length} fully reviewed pages; ${current.annotations.length} heading groups. This is not a complete document annotation.`;
 el('count').textContent=`${current.annotations.length} groups; scroll to inspect the full list.`;el('outline').replaceChildren();
 current.annotations.forEach(g=>{const b=document.createElement('button');b.textContent=`H${g.level} · p${g.page} · ${g.text}`;b.style.paddingLeft=`${9+(g.level-1)*12}px`;b.style.borderColor=colours[g.level];b.onclick=()=>{pn=g.page;page();};el('outline').append(b);});
 el('end').textContent=`End of all ${current.annotations.length} recorded groups. Unannotated headings may occur anywhere else in the document.`;page();
}
DATA.documents.forEach(d=>el('report').add(new Option(`${d.id} · ${d.split} · ${d.title}`,d.id)));
el('report').onchange=()=>{current=DATA.documents.find(d=>d.id===Number(el('report').value));pn=current.review_pages[0]||current.pages[0].number;report();};el('page').onchange=()=>{pn=Number(el('page').value);page();};el('gold').onchange=page;el('pred').onchange=page;report();
