'use strict';
const $=id=>document.getElementById(id),library=window.FMQ_LIBRARY;
let current=null,history=[],mode='hidden',stage=0,view='split';
const remembered=new Map(),pools=new Map(),contentCache=new Map();let navigationRevision=0;
const mathMacros={"\\p":"\\mathrm P(#1)",'\\cosec':'\\operatorname{cosec}','\\cosech':'\\operatorname{cosech}','\\sech':'\\operatorname{sech}','\\coth':'\\operatorname{coth}','\\arcosech':'\\operatorname{arcosech}','\\arcsech':'\\operatorname{arcsech}','\\arsech':'\\operatorname{arsech}','\\arcoth':'\\operatorname{arcoth}','\\arsinh':'\\operatorname{arsinh}','\\arcosh':'\\operatorname{arcosh}','\\artanh':'\\operatorname{artanh}','\\Real':'\\operatorname{Re}','\\Imag':'\\operatorname{Im}','\\ssum':'\\sum_{r=1}^{#1}#2','\\arraystretch':'1'};
function renderMath(root){for(const node of root.querySelectorAll('[data-math]'))katex.render(node.dataset.math,node,{displayMode:node.dataset.display==='true',throwOnError:true,strict:'error',macros:{...mathMacros}});}
async function loadSkill(skill){if(contentCache.has(skill.id)){skill.questions=contentCache.get(skill.id);return;}let questions=window.FMQ_CONTENT?.[skill.id];if(!questions){const response=await fetch(new URL('content/'+encodeURIComponent(skill.id)+'.json',document.baseURI));if(!response.ok)throw Error('Unable to load '+skill.code+' ('+response.status+')');questions=await response.json();}if(questions.length!==skill.questions.length||questions.some(q=>!q.question||(!q.reference&&!q.steps?.length)))throw Error('Incomplete skill '+skill.code);contentCache.set(skill.id,questions);skill.questions=questions;}
const key=s=>[s.course,s.book,s.topic,s.skill].join('/');
const isEdexcelOnly=(courseId=current?.course)=>courseId!=='maths-a-level'&&Boolean($('edexcel-only').checked);
function openPrintout(path,title='Question booklet'){if(!path)return;path=library.printDownloads?.[path]||path;if(window.LUISA_NAVIGATION?.openDocument(path,title))return;const link=document.createElement('a');link.href=path;link.target='_blank';link.rel='noopener';link.click();}
function printPath(kind){const r=resolve(current);if(kind==='solutions')return r.skill.solutionsResource;if(r.course.id==='maths-a-level')return kind==='topic'?r.topic.printoutPath:r.skill.printoutPath;if(kind==='topic')return r.topic.edexcelPrintoutPath;return `printouts/${r.book.id}/${r.topic.id}/skills/${r.skill.id}_${r.skill.code==='1.28'?'v03':'v02'}.pdf`;}
function resolve(s={}){
 const course=library.courses.find(x=>x.id===s.course)||library.courses[0];
 const book=course.books.find(x=>x.id===s.book)||course.books[0];
 const topicChoices=isEdexcelOnly(course.id)?book.topics.filter(x=>x.skills.some(y=>y.edexcel)):book.topics;
 const topic=topicChoices.find(x=>x.id===s.topic)||topicChoices[0]||book.topics[0];
 const skillChoices=isEdexcelOnly(course.id)?topic.skills.filter(x=>x.edexcel):topic.skills;
 const skill=skillChoices.find(x=>x.id===s.skill)||skillChoices.find(x=>x.available)||skillChoices[0]||topic.skills[0];
 const state={course:course.id,book:book.id,topic:topic.id,skill:skill.id,question:Math.max(1,Math.min(skill.questions.length,Number(s.question)||1))};
 return {course,book,topic,skill,state};
}
function populate(id,items,selected){$(id).replaceChildren(...items.map(x=>{const o=document.createElement('option');o.value=x.id;o.textContent=x.title;return o;}));$(id).value=selected;}
async function navigate(s,record=true){
 const revision=++navigationRevision,r=resolve(s),next=r.state;
 $('question').setAttribute('aria-busy','true');
 try{if(r.skill.available)await loadSkill(r.skill);}catch(error){console.error('FMQ skill load failed:',error);if(revision!==navigationRevision)return;$('question').textContent='This skill could not be loaded. Please check the prototype folder and try again.';$('question').removeAttribute('aria-busy');return;}
 if(revision!==navigationRevision)return;$('question').removeAttribute('aria-busy');
 if(current){remembered.set(key(current),current.question);if(record&&(key(current)!==key(next)||current.question!==next.question))history.push({...current});}
 current=next;mode='hidden';stage=0;$('edexcel-only').closest('label').hidden=r.course.supportsEdexcelFilter===false;
 populate('course',library.courses,next.course);populate('book',r.course.books,next.book);populate('topic',isEdexcelOnly()?r.book.topics.filter(t=>t.skills.some(s=>s.edexcel)):r.book.topics,next.topic);
 window.FMQ_LESSONS?.update(r);
 const textbookLink=document.getElementById('textbook-view-link');if(textbookLink)textbookLink.href='textbook-view.html#'+new URLSearchParams({course:next.course,book:next.book,fromSkill:next.skill,fromQuestion:String(next.question)});
 $('breadcrumbs').textContent=[r.course.title,r.book.title,r.topic.title].join(' › ');
 $('skilltitle').textContent=`${r.skill.code} ${r.skill.title}`;
 $('print-topic').disabled=!printPath('topic');$('print-skill').disabled=r.course.id==='maths-a-level'&&!r.skill.printoutPath;$('skill-solutions').disabled=!printPath('solutions');
 $('print-topic').setAttribute('aria-label',`Print ${r.topic.title} topic`);$('print-skill').setAttribute('aria-label',`Print ${r.skill.title} skill`);
 const selected=r.skill.questions[next.question-1];$('qtitle').textContent=!r.skill.available?'Awaiting conversion':selected?.reference?'Reference tables':selected?.supplementary?`Additional worked solution ${selected.number}`:`Question ${next.question} of ${r.skill.questionCount}`;
 $('focus-question-number').textContent=$('qtitle').textContent;
 $('skills').replaceChildren(...(isEdexcelOnly()?r.topic.skills.filter(skill=>skill.edexcel):r.topic.skills).map(skill=>{
  const button=document.createElement('button');button.className='skill-button';button.dataset.skill=skill.id;
  if(skill.id===next.skill)button.setAttribute('aria-current','page');
  const code=document.createElement('span');code.className='skill-code';code.textContent=skill.code;
  const title=document.createElement('span');title.textContent=skill.title;
  const count=document.createElement('span');count.className='skill-count';count.textContent=skill.reference?'Reference tables':skill.available?`${skill.questionCount} questions`:'Awaiting conversion';button.disabled=!skill.available;
  button.append(code,title,count);
  button.onclick=()=>{const target={...current,skill:skill.id};target.question=remembered.get(key(target))||1;navigate(target);};return button;
 }));
 $('choose').replaceChildren(...r.skill.questions.map(q=>{const o=document.createElement('option');o.value=q.number;o.textContent=q.reference?'Reference tables':q.supplementary?`Additional solution ${q.number}`:`Question ${q.number}`;return o;}));$('choose').value=next.question;
 const q=r.skill.questions[next.question-1]||{question:'<p>This skill is awaiting LaTeX conversion.</p>',steps:[]};$('question').innerHTML=q.question;$('question').parentElement.scrollTop=0;
 $('solution').innerHTML=q.steps.map((html,i)=>`<div class="solution-step" data-step="${i}">${html}</div>`).join('');$('solution').parentElement.parentElement.scrollTop=0;
 $('previous').disabled=!r.skill.available||(!history.length&&next.question===1);for(const id of ['skip','random','choose','full','hide'])$(id).disabled=!r.skill.available||r.skill.reference;
 const hash=new URLSearchParams({course:next.course,book:next.book,topic:next.topic,skill:next.skill,question:next.question});
 try{window.history.replaceState(null,'','#'+hash);}catch{}
 document.title=`Luisa · ${r.skill.code} · Question ${next.question}`;
 renderMath($('question'));renderMath($('solution'));
 renderSolution();
}
function setView(next){
 view=next;document.body.classList.toggle('focus-view',next!=='split');
 document.body.classList.toggle('view-question',next==='question');document.body.classList.toggle('view-solution',next==='solution');
 for(const name of ['split','question','solution'])$('view-'+name).setAttribute('aria-pressed',String(name===next));
 if(next==='solution'&&mode==='hidden'&&resolve(current).skill.available){mode='full';stage=(resolve(current).skill.questions[current.question-1]?.steps.length||0);renderSolution();}
 window.scrollTo({top:0,behavior:'auto'});
}
function renderSolution(){
 const total=(resolve(current).skill.questions[current.question-1]?.steps.length||0);
 $('solutionempty').textContent=resolve(current).skill.reference?'Reference tables do not have worked solutions.':resolve(current).skill.available?'Choose Reveal next or Show full solution.':'This skill is awaiting LaTeX conversion.';$('solutionempty').hidden=mode!=='hidden';$('solutionclip').hidden=mode==='hidden';$('stepbar').hidden=mode==='hidden';
 for(const [i,node] of [...$('solution').children].entries())node.hidden=mode==='progress'&&i>=stage;
 $('stepcount').textContent=mode==='full'?'Complete solution':`Step ${stage} of ${total}`;
 $('nextstep').disabled=resolve(current).skill.reference||!resolve(current).skill.available||(stage>=total&&mode!=='hidden');$('backstep').disabled=stage===0;$('reset').disabled=stage===0;
}
$('edexcel-only').onchange=()=>navigate({...current});
$('print-topic').onclick=()=>openPrintout(printPath('topic'));
$('print-skill').onclick=()=>openPrintout(printPath('skill'));
$('skill-solutions').onclick=()=>openPrintout(printPath('solutions'),'Skill solutions');
$('course').onchange=()=>navigate({course:$('course').value});
$('book').onchange=()=>navigate({course:current.course,book:$('book').value});
$('topic').onchange=()=>navigate({course:current.course,book:current.book,topic:$('topic').value});
$('choose').onchange=e=>navigate({...current,question:Number(e.target.value)});
$('previous').onclick=()=>history.length?navigate(history.pop(),false):navigate({...current,question:Math.max(1,current.question-1)},false);
$('skip').onclick=()=>navigate({...current,question:current.question%resolve(current).skill.questions.length+1});
$('random').onclick=()=>{
 const k=key(current),count=resolve(current).skill.questionCount;if(count<2)return;let pool=pools.get(k);
 if(!pool?.some(n=>n!==current.question))pool=Array.from({length:count},(_,i)=>i+1).filter(n=>n!==current.question);
 const candidates=pool.filter(n=>n!==current.question),n=candidates[Math.floor(Math.random()*candidates.length)];
 pools.set(k,pool.filter(x=>x!==n));navigate({...current,question:n});
};
$('nextstep').onclick=()=>{
 const total=(resolve(current).skill.questions[current.question-1]?.steps.length||0);
 if(mode==='hidden'){mode='progress';stage=1;}else{mode='progress';stage=Math.min(total,stage+1);}
 renderSolution();const visible=[...$('solution').children].filter(x=>!x.hidden);visible[visible.length-1]?.scrollIntoView({block:'nearest',behavior:'smooth'});
};
$('full').onclick=()=>{mode='full';stage=(resolve(current).skill.questions[current.question-1]?.steps.length||0);renderSolution();};
$('hide').onclick=()=>{mode='hidden';stage=0;renderSolution();};
$('backstep').onclick=()=>{mode='progress';stage=Math.max(0,stage-1);renderSolution();};
$('reset').onclick=()=>{mode='progress';stage=0;renderSolution();};
$('view-split').onclick=()=>{setView('split');if(document.fullscreenElement)document.exitFullscreen();};
document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement)setView('split');});
$('view-question').onclick=()=>enterFocusedFullscreen('question');
$('view-solution').onclick=()=>enterFocusedFullscreen('solution');
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&view!=='split')setView('split');});
window.addEventListener('hashchange',()=>navigate(Object.fromEntries(new URLSearchParams(location.hash.slice(1)))));
$('library-status').textContent=library.availableSkillCount+' of '+library.totalSkillCount+' skills available · '+library.questionCount+' questions';navigate(Object.fromEntries(new URLSearchParams(location.hash.slice(1))),false);
if('serviceWorker' in navigator&&location.protocol!=='file:')navigator.serviceWorker.register('sw.js').catch(()=>{});

async function enterFocusedFullscreen(next){
 setView(next);
 // iPhone browsers without Fullscreen API still show the focused question/solution.
 if(!document.fullscreenElement && document.documentElement.requestFullscreen){
  try{await document.documentElement.requestFullscreen();}catch(error){console.info('Fullscreen unavailable; focused view remains active.');}
 }
}
