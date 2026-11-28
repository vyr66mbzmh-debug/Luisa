'use strict';
const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const main = $('#main');
const names = {9:'Shell',10:'Remove',11:'Hundred'};
const assignments = {
  coordinates:['coordinates','Q1–2'],midpoint:['coordinates','Q3–6'],orientation:['coordinates','Q2'],
  substitution:['plotting','After the plotting model'],plotting:['plotting','Q1–5'],plotting2:['plotting','Q1–5, then Q6–11 after gradients and intercepts'],
  gradient:['plotting','Q6–11 after intercepts'],negative:['equation','J–L after the equation model'],fractional:['equation','G–I after the equation model'],
  intercept:['summary','Q1, Q2, Q5, Q6'],equation:['equation','A–L'],sketch:['sketch','Sketch practice'],conversion:['conversion','Q1, then draw and interpret']
};
const sheetNames = {coordinates:'Coordinates and midpoint',plotting:'LIN49',equation:'LIN12',summary:'LIN16',sketch:'Sketches',conversion:'LIN22',check:'Topic check',homework:'LIN01 · Homework'};
const storeKey='luisa-local-scheme-2026-27-v3';
function readStore(){try{return JSON.parse(localStorage.getItem(storeKey)) || {years:{}}}catch{return {years:{}}}}
let records=readStore();
function announce(text){$('#status').textContent=text;setTimeout(()=>{if($('#status').textContent===text)$('#status').textContent=''},2300)}
function persist(){try{localStorage.setItem(storeKey,JSON.stringify(records));return true}catch{announce('Browser storage unavailable');return false}}
function blankClass(name){return {name,taught:{},bookmark:null}}
function yearRecord(n){return records.years[n] ||= {active:'default',classes:{default:blankClass(names[n])}}}
function group(n){const year=yearRecord(n);return year.classes[year.active]}
const fresh = (path='Higher',key='coordinates')=>({path,key,left:0,right:0,practice:false,sheet:'coordinates',question:''});
let state=fresh(), returning=false;
const cycle=()=>LESSON.cycles[state.key];
const route=()=>LESSON.routes[state.path];
const pair=()=>cycle().pairs[state.path];
const options=(values,selected)=>Object.entries(values).map(([key,label])=>`<option value="${esc(key)}" ${key===selected?'selected':''}>${esc(label)}</option>`).join('');
const booklet=(page=1)=>`courses/booklets/Graphs-${state.path}.pdf#page=${page}`;
function nav(parent,label,context){$('#up').href=parent;$('#up').setAttribute('aria-label',label);$('#up').title=label;$('#location').textContent=context;document.title=context||'Mathematics'}
function classSelect(n){const y=yearRecord(n);return `<select class="class-select" aria-label="Teaching class" id="class-select">${options(Object.fromEntries(Object.entries(y.classes).map(([k,c])=>[k,c.name])),y.active)}<option value="new">Add class…</option></select>`}
function modal(title,fields,confirm,save){
 const d=$('#dialog');d.innerHTML=`<form><h2 id="dialog-title">${title}</h2>${fields}<div class="actions"><button class="primary" type="submit">${confirm}</button><button type="button" id="cancel">Cancel</button></div></form>`;
 d.querySelector('form').onsubmit=e=>{e.preventDefault();if(save()!==false)d.close()};d.querySelector('#cancel').onclick=()=>d.close();d.showModal();
}
function bindClass(n){$('#class-select').onchange=e=>{
 const y=yearRecord(n);
 if(e.target.value==='new'){
   e.target.value=y.active;
   modal('Add class','<label>Class name<input id="class-name" required maxlength="60" autofocus></label>','Add',()=>{
     const input=$('#class-name'),name=input.value.trim();if(!name)return false;
     const existing=Object.entries(y.classes).find(([,c])=>c.name.toLowerCase()===name.toLowerCase());
     const id=existing?.[0] || ('c-'+Date.now().toString(36));
     y.classes[id] ||= blankClass(name);y.active=id;persist();render();
   });
 }else{y.active=e.target.value;persist();render()}
}}
let showDetail=false;
function detail(fields){return fields.filter(([,v])=>v).map(([k,v])=>`<div class="detail"><b>${k}</b>${esc(v)}</div>`).join('')}
function activeTopic(n,r,col){return n===9 && col==='main' && r.main.split('\n')[0].trim()==='Graphs'}
function topicCell(n,r,col){
 const val=r[col], ready=activeTopic(n,r,col),id=col+r.row, cls=group(n);
 if(!val)return esc(r[col==='main'?'event':'fmEvent']);
 const label=(n===10 && r.row===41 ? val.replace(/\s*\n\s*/g,' ') : val.split('\n')[0]).trim();
 return `<div class="track"><input type="checkbox" data-topic="${id}" title="Mark taught" aria-label="Taught: ${esc(label)}" ${cls.taught[id]?'checked':''}>${ready?`<a href="#teach/${cls.bookmark?.path||'Higher'}" data-start>${esc(label)}</a>`:`<span class="off" aria-disabled="true">${esc(label)}</span>`}${ready&&cls.bookmark?`<button id="resume" title="${esc(LESSON.cycles[cls.bookmark.key].title)}">Resume</button>`:''}</div>`+
 (ready && cls.bookmark ? `<div class="meta">${esc(cls.bookmark.path)} · ${esc(LESSON.cycles[cls.bookmark.key].title)}${cls.bookmark.question?' · '+esc(cls.bookmark.question):''}</div>` : '')+
 (showDetail?detail(col==='main'?[['Notes',val.includes('\n')?val.slice(val.indexOf('\n')).trim():''],['Textbook',r.details.B],['Specification',r.details.D],['QFT / SEND',r.details.E],['Retrieval',r.details.F],['Further maths reference',n===9?r.details.G:'']]:[['Reference',r.details.G],['Specification',r.details.I],['Retrieval',r.details.J]]):'')
}
function yearView(n){
 nav('#home','Courses',`Year ${n} / ${names[n]}`); const scheme=SCHEMES[n],cls=group(n);
 const topics=scheme.terms.flatMap(t=>t.rows.flatMap(r=>['main','fm'].filter(col=>r[col]).map(col=>({id:col+r.row,ready:activeTopic(n,r,col)}))));
 return `<section class="page"><div class="year-head"><div><h1>${names[n]}</h1><p class="muted">Year ${n} · 2026–27</p></div>${classSelect(n)}</div><div class="overview"><span><b>${topics.filter(t=>t.ready).length} / ${topics.length}</b> lessons ready</span><span><b>${topics.filter(t=>cls.taught[t.id]).length} / ${topics.length}</b> taught</span><label><input type="checkbox" id="details" ${showDetail?'checked':''}> Scheme details</label></div>${scheme.terms.map(t=>`<section class="term"><h2 class="term-title">${esc(t.name)}</h2><table><thead><tr><th class="week">Weeks</th><th>IGCSE Mathematics</th>${n>9?`<th>AQA Further Maths <span class="meta">· ${n===10?'Sets 1–2':'Set 1'}</span></th>`:''}</tr></thead><tbody>${t.rows.map(r=>r.break?`<tr class="event"><td colspan="${n>9?3:2}">${esc(r.break)}</td></tr>`:`<tr><td class="week">${esc(r.weeks)}</td><td>${topicCell(n,r,'main')}</td>${n>9?`<td>${topicCell(n,r,'fm')}</td>`:''}</tr>`).join('')}</tbody></table></section>`).join('')}</section>`
}
function bindYear(n){
 bindClass(n);$('#details').onchange=e=>{showDetail=e.target.checked;render()};
 main.querySelectorAll('[data-topic]').forEach(el=>el.onchange=()=>{group(n).taught[el.dataset.topic]=el.checked;persist();render();main.querySelector(`[data-topic="${el.dataset.topic}"]`)?.focus({preventScroll:true})});
 if($('[data-start]'))$('[data-start]').onclick=()=>{state=fresh(group(n).bookmark?.path||'Higher');returning=true};
 if($('#resume'))$('#resume').onclick=()=>{state={...fresh(),...group(n).bookmark};returning=true;location.hash='teach/'+state.path};
}
function toolbar(){const page=BOOKS[state.path];return `<div class="board-tools"><span>${esc(group(9).name)}</span><select id="path" aria-label="Pathway">${options(Object.fromEntries(Object.keys(LESSON.routes).map(p=>[p,p])),state.path)}</select><select id="cycle" aria-label="Teaching cycle">${options(Object.fromEntries(route().map((k,i)=>[k,(i+1)+'. '+LESSON.cycles[k].title])),state.key)}</select><a class="push" target="_blank" rel="noopener" href="${booklet(page.notes[state.key])}">Notes</a><a target="_blank" rel="noopener" href="${booklet(page.sections.homework)}">Homework</a><button id="bookmark">Bookmark</button></div>`}
function rail(){const i=route().indexOf(state.key);return `<aside class="rail" aria-label="Topic progress">${i+1}/${route().length}<ol aria-hidden="true">${route().map((_,j)=>`<li class="${j===i?'now':j<i?'past':''}"></li>`).join('')}</ol></aside>`}
function table(c){if(!c.table)return '';return `<table class="model-table"><tr><th>x</th>${c.table.xs.map(x=>'<td>'+x+'</td>').join('')}</tr><tr><th>y</th>${c.table.ys.map(y=>'<td>'+(state.left>=c.table.reveal?y:'&nbsp;')+'</td>').join('')}</tr></table>`}
function graph({xmin=-4,xmax=5,ymin=-4,ymax=6,points=[],segments=[],line=null,vertical=null,xName='x',yName='y',description='Coordinate diagram'}){
 const unit=25, x=v=>35+(v-xmin)*unit,y=v=>22+(ymax-v)*unit,w=x(xmax)+25,h=y(ymin)+23;
 const stroke=(a,b,c,d,cls)=>`<line class="${cls}" x1="${x(a)}" y1="${y(b)}" x2="${x(c)}" y2="${y(d)}"/>`;
 let svg=`<svg class="graph" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(description)}"><defs><clipPath id="we-plot"><rect x="${x(xmin)}" y="${y(ymax)}" width="${unit*(xmax-xmin)}" height="${unit*(ymax-ymin)}"/></clipPath></defs>`;
 for(let a=xmin;a<=xmax;a++){svg+=stroke(a,ymin,a,ymax,'grid-line');if(a && !(a%2))svg+=`<text x="${x(a)}" y="${y(0)+16}" text-anchor="middle">${a}</text>`}
 for(let b=ymin;b<=ymax;b++){svg+=stroke(xmin,b,xmax,b,'grid-line');if(b && !(b%2))svg+=`<text x="${x(0)-5}" y="${y(b)+4}" text-anchor="end">${b}</text>`}
 svg+=stroke(xmin,0,xmax,0,'axis-line')+stroke(0,ymin,0,ymax,'axis-line')+`<text x="${x(xmax)+7}" y="${y(0)}">${xName}</text><text x="${x(0)+6}" y="14">${yName}</text><text x="${x(0)-13}" y="${y(0)+17}">0</text><g clip-path="url(#we-plot)">`;
 if(line){const [m,b]=line;svg+=stroke(xmin,m*xmin+b,xmax,m*xmax+b,'plot-line')}
 if(vertical!==null)svg+=stroke(vertical,ymin,vertical,ymax,'plot-line');
 for(const [a,b,c,d] of segments)svg+=stroke(a,b,c,d,'plot-line');
 return svg+'</g>'+points.map(([a,b,label])=>`<circle class="point" cx="${x(a)}" cy="${y(b)}" r="3.7"/>${label?`<text x="${x(a)+6}" y="${y(b)-7}">${label}</text>`:''}`).join('')+'</svg>';
}
function rightGraph(){
 const n=state.right,k=state.key,ix=['Core','Higher','Advanced'].indexOf(state.path);
 if(!n)return '';
 if(k.startsWith('plotting')){
  const [m,b]=ix===2?[3,-4]:k==='plotting'?[2,3]:[3,1];
  if(n<4)return '';
  return graph({ymin:ix===2?-8:-3,ymax:ix===2?2:6,points:[-1,0,1].map(x=>[x,m*x+b]),line:n===5?[m,b]:null});
 }
 if(k==='sketch'){const [m,b,run]=[[-1,2,1],[.5,-1,2],[-1.5,3,2]][ix];return graph({points:(n===1?[0]:[0,run,2*run]).map(x=>[x,m*x+b]),line:n===3?[m,b]:null})}
 if(k==='coordinates'){const pts=[[-2,3,'A/P'],[4,3,'B'],[4,-2,'C']];if(n>=3)pts.push([-2,-2,'D']);return graph({points:pts,segments:n>=3?[[-2,3,4,3],[4,3,4,-2],[4,-2,-2,-2],[-2,-2,-2,3]]:[]})}
 if(k==='conversion'){
  const legs=ix===0?[[12,0,12,8],[12,8,0,8]]:ix===1?[[0,8,12,8],[12,8,12,0],[18,0,18,12],[18,12,0,12]]:[[0,4,6,4],[6,4,6,0]];
  const count=ix===0?n-1:ix===1?(n===3?4:n):(n===1?0:2);
  return graph({xmin:0,xmax:26,ymin:0,ymax:18,xName:'€',yName:'£',line:[2/3,0],segments:legs.slice(0,count),description:'Historical euro and pound conversion with reading guides'});
 }
 if(k==='midpoint')return graph({points:[[-2,-1,'C'],[4,3,'D'],...(n>=3?[[1,1,'M']]:[])],segments:[[-2,-1,4,3]]});
 if(k==='orientation')return graph({points:[[2,-1]],vertical:n>=2?2:null,line:n===3?[0,-1]:null});
 return '';
}
function list(steps,n){return n?`<ol class="steps" aria-live="polite">${steps.slice(0,n).map(s=>'<li>'+s+'</li>').join('')}</ol>`:''}
function plottingModel(){
 const first=state.key==='plotting',m=first?2:3,b=first?4:-1,complete=state.left===cycle().steps.length;
 return graph({xmin:first?-9:-11,xmax:first?9:11,ymin:first?-3:-11,ymax:first?11:9,line:complete?[m,b]:null,points:complete?[-3,-2,-1,0,1,2,3].map(x=>[x,m*x+b]):[],description:'Model coordinate grid for '+cycle().title}).replaceAll('we-plot','model-plot');
}
function drawing(fig,id,tall){return fig?`<div class="drawing ${tall?'tall':''}">${fig}<button class="enlarge" data-enlarge="${id}" aria-label="Enlarge ${id==='left'?'I DO':'WE DO'} graph" title="Enlarge graph">⛶</button></div>`:''}
function enlarge(id){
 const article=main.querySelector(id==='left'?'article:first-child':'article:last-child');
 const svg=article.querySelector('svg').outerHTML.replaceAll('plotclip-','zoom-plotclip-').replaceAll('model-plot','zoom-model-plot').replaceAll('we-plot','zoom-we-plot');
 const d=$('#dialog');d.className='figure-dialog';d.innerHTML=`<div class="side-top"><h2 id="dialog-title">${esc(cycle().title)}</h2><button id="close-figure">Close</button></div><div class="big-figure">${svg}</div>`;d.querySelector('button').onclick=()=>d.close();d.addEventListener('close',()=>{d.className=''}, {once:true});d.showModal();
}
function board(){
 const c=cycle(),p=pair(),left=state.key.startsWith('plotting')?plottingModel():c.frames[state.left-1]||c.initial,right=rightGraph();
 const side=(id,label,question,steps,n,fig,tall=false)=>`<article class="side"><div class="side-top"><h2>${label}</h2><button class="reveal" id="${id}" aria-label="Reveal ${label}" ${n===steps.length?'disabled':''}>Reveal</button></div><p class="question">${question}</p>${id==='left'?table(c):''}${list(steps,n)}${drawing(fig,id,tall)}</article>`;
 return toolbar()+`<section class="lesson"><h1>${esc(c.title)}</h1><div class="layout">${rail()}<div><div class="panes">${side('left','I DO',c.model,c.steps,state.left,left,state.key.startsWith('plotting'))}${side('right','WE DO',p.question,p.steps,state.right,right)}</div><div class="rail-foot"><button id="reset">Reset</button><button id="practice">YOU DO</button><button class="primary" id="next" ${state.key===route().at(-1)?'disabled':''}>Next</button></div></div></div></section>`
}
function practice(){const page=BOOKS[state.path];return toolbar()+`<section class="page"><div class="layout">${rail()}<div><h1>YOU DO</h1><p class="assignment">${sheetNames[assignments[state.key][0]]} · ${assignments[state.key][1]}</p><select aria-label="Worksheet" id="sheet">${options(sheetNames,state.sheet)}</select> <a class="button primary" href="${booklet(page.sections[state.sheet])}" target="_blank" rel="noopener">Open worksheet</a><p>${state.sheet==='homework'?'Shell assignment · Q1, Q2 and Q5':''}</p><div class="actions"><button id="back">Board</button><a href="courses/booklets/Teacher-answer-key.pdf" target="_blank" rel="noopener">Answers</a></div></div></div></section>`}
function bookmark(){modal('Bookmark',`<p>${esc(group(9).name)} · ${esc(cycle().title)}</p><label>Question or next step<input id="question" maxlength="160" value="${esc(state.question)}" placeholder="e.g. LIN49 Q6"></label>`,'Save',()=>{
 state.question=$('#question').value.trim();group(9).bookmark={...state};if(persist())announce('Bookmark saved');
})}
function refresh(focus){render();if(focus)document.getElementById(focus)?.focus({preventScroll:true})}
function reveal(side){
 const max=side==='left'?cycle().steps.length:pair().steps.length;
 if(state[side]>=max)return;
 state[side]++;refresh(state[side]<max?side:(side==='left'?'right':'practice'));
}
function advance(){if(state.left<cycle().steps.length)reveal('left');else if(state.right<pair().steps.length)reveal('right')}
function startingCycle(key,path=state.path){state=fresh(path,key)}
function bindBoard(){
 $('#path').onchange=e=>{const path=e.target.value,k=LESSON.routes[path].includes(state.key)?state.key:LESSON.routes[path][0];startingCycle(k,path);returning=true;location.hash='teach/'+path};
 $('#cycle').onchange=e=>{startingCycle(e.target.value);refresh('cycle')};$('#bookmark').onclick=bookmark;
 if(state.practice){$('#sheet').onchange=e=>{state.sheet=e.target.value;refresh('sheet')};$('#back').onclick=()=>{state.practice=false;refresh('practice')};return}
 main.querySelectorAll('[data-enlarge]').forEach(btn=>btn.onclick=()=>enlarge(btn.dataset.enlarge));
 $('#left').onclick=()=>reveal('left');$('#right').onclick=()=>reveal('right');$('#reset').onclick=()=>{startingCycle(state.key);refresh('left')};
 $('#practice').onclick=()=>{state.practice=true;state.sheet=assignments[state.key][0];refresh('sheet')};
 $('#next').onclick=()=>{startingCycle(route()[route().indexOf(state.key)+1]);refresh('left');window.scrollTo(0,0)};
}
function render(){
 releaseLogo();
 const hash=location.hash.slice(1)||'home';
 if (/^[^&=]+=/u.test(hash)) {
   location.replace('by-skill.html'+location.search+location.hash);
   return;
 }
 const match=/^year(9|10|11)$/.exec(hash);
 document.body.dataset.view=hash==='alevel'?'library':'course';
 if(match){const n=+match[1];main.innerHTML=yearView(n);bindYear(n);return}
 if(hash.startsWith('teach/')){const path=hash.slice(6);if(!LESSON.routes[path]){location.replace('#year9');return}if(state.path!==path)state=fresh(path);nav('#year9','Year 9 scheme of work','Year 9 / Graphs');main.innerHTML=state.practice?practice():board();bindBoard();return}
 if(hash==='graphs'){location.replace('#teach/Higher');return}
 if(hash==='alevel/graphs'){location.replace('#alevel');return}
 if(hash==='alevel'){
   const library='teaching-chapters.html';
   location.replace(library);
   return;
 }
 nav('#home','Courses','');document.body.dataset.view='entrance';mountEntrance();
}
addEventListener('hashchange',e=>{
 const old=new URL(e.oldURL).hash;
 if(location.hash.startsWith('#teach/')&&!returning)state=fresh(location.hash.slice(7));
 returning=false;render();
 if(old.startsWith('#teach/')&&location.hash==='#year9')$('[data-start]')?.scrollIntoView({block:'center'});else window.scrollTo(0,0);
});
document.addEventListener('click',e=>{
 if(!location.hash.startsWith('#teach/')||state.practice||$('#dialog').open||e.target.closest('button,a,input,select,textarea,dialog,label,header,.board-tools')||getSelection()?.toString())return;
 advance();
});
document.addEventListener('keydown',e=>{if(e.code==='Space'&&!e.repeat&&location.hash.startsWith('#teach/')&&!state.practice&&!$('#dialog').open&&!e.target.closest('button,a,input,select,textarea')){e.preventDefault();advance()}});
render();
