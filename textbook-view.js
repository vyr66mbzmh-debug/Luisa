'use strict';
const mathMacros={"\\p":"\\mathrm P(#1)",'\\cosec':'\\operatorname{cosec}','\\cosech':'\\operatorname{cosech}','\\sech':'\\operatorname{sech}','\\coth':'\\operatorname{coth}','\\arcosech':'\\operatorname{arcosech}','\\arcsech':'\\operatorname{arcsech}','\\arsech':'\\operatorname{arsech}','\\arcoth':'\\operatorname{arcoth}','\\arsinh':'\\operatorname{arsinh}','\\arcosh':'\\operatorname{arcosh}','\\artanh':'\\operatorname{artanh}','\\Real':'\\operatorname{Re}','\\Imag':'\\operatorname{Im}','\\ssum':'\\sum_{r=1}^{#1}#2','\\arraystretch':'1'};
const $=id=>document.getElementById(id);let catalogue,state={},pool=[],selected=null,steps=[],shown=0,revision=0;const cache=new Map();
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function options(id,items,value){$(id).replaceChildren(...items.map(x=>{const o=document.createElement('option');o.value=x.id;o.textContent=x.title;return o;}));$(id).value=value;}
function hash(s){return '#'+new URLSearchParams(Object.entries(s).filter(([,v])=>v!==undefined&&v!==null&&v!==''));}
function skillURL(r){const sk=catalogue.skills[r.skill];return './'+hash({course:sk.course,book:sk.book,topic:sk.topic,skill:r.skill,question:r.question});}
function bookURL(b){return './'+hash({course:b.course,book:b.id});}
function renderMath(root){for(const node of root.querySelectorAll('[data-math]'))katex.render(node.dataset.math,node,{displayMode:node.dataset.display==='true',throwOnError:true,strict:'error',macros:{...mathMacros}});}
function matches(r,b,ch,sub){return r.targets.some(t=>t.book===b&&t.chapter===ch&&(!sub||t.subtopics.includes(sub)));}
function renderResource(r){const a=document.createElement('a');a.className='resource-link';a.textContent=r.title;if(r.url&&r.access==='available'){a.href=r.url;}else{a.setAttribute('aria-disabled','true');a.title='Not yet uploaded';}return a;}
function change(patch){const s={...state,...patch};location.hash=hash(s);}
function render(){
 const input=Object.fromEntries(new URLSearchParams(location.hash.slice(1)));const from=input.fromSkill&&catalogue.questions.find(r=>r.skill===input.fromSkill&&String(r.question)===input.fromQuestion);
 const course=catalogue.courses.find(c=>c.id===input.course)||catalogue.courses[0];let book=catalogue.books.find(b=>b.id===input.book&&b.course===course.id)||catalogue.books.find(b=>b.course===course.id);
 let chapter=book.chapters.find(c=>c.id===input.chapter)||book.chapters[0];
 // A unique match can be opened directly. For multiple matches offer all destinations explicitly.
 if(from&&!input.chapter&&from.targets.length===1){const t=from.targets[0];book=catalogue.books.find(b=>b.id===t.book);chapter=book.chapters.find(c=>c.id===t.chapter);}
 const sub=chapter.subtopics.some(s=>s.id===input.subtopic)?input.subtopic:'';
 state={course:book.course,book:book.id,chapter:chapter.id,subtopic:sub};if(input.fromSkill){state.fromSkill=input.fromSkill;state.fromQuestion=input.fromQuestion;}
 options('course',catalogue.courses,book.course);options('book',catalogue.books.filter(b=>b.course===book.course),book.id);options('chapter',book.chapters.map(c=>({id:c.id,title:`${c.id}. ${c.title}`})),chapter.id);options('subtopic',[{id:'',title:'Whole chapter'},...chapter.subtopics.map(s=>({id:s.id,title:`${s.id} ${s.title}`}))],sub);
 $('breadcrumbs').textContent=[catalogue.courses.find(c=>c.id===book.course).title,book.title].join(' › ');$('chapter-title').textContent=`Chapter ${chapter.id}: ${chapter.title}`;
 $('resources').replaceChildren(...chapter.resources.filter(r=>['slides','pdf','booklet'].includes(r.type)).map(renderResource));
 $('additional-resources').replaceChildren(...chapter.resources.filter(r=>!['slides','pdf','booklet'].includes(r.type)&&(!sub||!r.subtopics?.length||r.subtopics.includes(sub))).map(renderResource));
 const all=catalogue.questions.filter(r=>matches(r,book.id,chapter.id,''));pool=all.filter(r=>matches(r,book.id,chapter.id,sub));
 const reviewed=all.filter(r=>r.mapping==='question-reviewed').length;
 $('coverage').textContent=all.length ? `${all.length} practice entries · ${reviewed} individually mapped`+(all.length>reviewed?` · ${all.length-reviewed} grouped by skill, awaiting individual review.`:". Further mapping is in progress.") : "Practice mapping is pending. Chapter resources are listed below as they become available.";
 $('chapter-choices').hidden=!input.fromSkill;
 if(input.fromSkill){
  $('chapter-choices').replaceChildren();const p=document.createElement('p');p.style.margin='0';
  p.textContent=from?(from.targets.length>1?'This question relates to more than one chapter. Choose where to study it:':'Showing the textbook chapter for your selected question.'):'Your selected question has not yet been mapped to an Edexcel chapter. Your original question remains available in skill view.';
  $('chapter-choices').append(p);
  if(from)for(const t of from.targets){const b=catalogue.books.find(b=>b.id===t.book),ch=b.chapters.find(c=>c.id===t.chapter),a=document.createElement('a');a.href=hash({course:b.course,book:b.id,chapter:ch.id,entry:from.id});a.textContent=`${b.title} · ${ch.id}. ${ch.title}`;$('chapter-choices').append(a);}
  if(catalogue.skills[input.fromSkill]){const a=document.createElement('a');a.href=skillURL({skill:input.fromSkill,question:Number(input.fromQuestion)||1});a.textContent='Return to original question';$('chapter-choices').append(a);}
 }
 $('browse-skills').href=bookURL(book);$('skill-view').href=input.fromSkill&&catalogue.skills[input.fromSkill]?skillURL({skill:input.fromSkill,question:Number(input.fromQuestion)||1}):bookURL(book);
 const wanted=input.entry||(from?.targets.length===1?from.id:null);let record=pool.find(r=>r.id===wanted);let group=record?.skill||(pool.some(r=>r.skill===input.group)?input.group:pool[0]?.skill);
 const groups=[...new Set(pool.map(r=>r.skill))];options('practice-skill',groups.map(id=>({id,title:catalogue.skills[id].title})),group);
 const questions=pool.filter(r=>r.skill===group);record=record||questions[0];
 options('question-select',questions.map(r=>({id:r.id,title:r.label})),record?.id);
 const empty=!record;$('empty').hidden=!empty;$('panels').hidden=empty;$('practice-selection').hidden=empty;
 $('empty-message').textContent=sub?'No individually mapped questions are available for this subtopic yet. Choose Whole chapter for broader practice, or use the chapter resources above.':'The chapter is ready to browse, but its eligible practice questions have not yet been mapped. Available teaching slides, book chapters and handouts remain accessible above.';
 if(record){state.entry=record.id;state.group=group;showQuestion(record,questions);}else{revision++;selected=null;}
 // Keep incoming context until the user changes selection, so multi-chapter choices remain recoverable.
 if(input.fromSkill){state.fromSkill=input.fromSkill;state.fromQuestion=input.fromQuestion;}
 window.history.replaceState(null,'',hash(state));
}
async function showQuestion(record,questions){
 const token=++revision;selected=record;shown=0;steps=[];$('question').classList.remove('load-error');$('question').textContent='Loading question…';$('solution').replaceChildren();$('solution-hint').hidden=false;$('solution-hint').textContent='Choose Reveal next or Show full solution.';for(const id of ['reveal','show-all','hide'])$(id).disabled=true;
 const index=questions.indexOf(record);$('previous').disabled=index===0;$('next').disabled=index===questions.length-1;
 $('previous').onclick=()=>change({entry:questions[index-1].id,fromSkill:'',fromQuestion:''});$('next').onclick=()=>change({entry:questions[index+1].id,fromSkill:'',fromQuestion:''});
 $('question-title').textContent=record.label;$('original-question').href=skillURL(record);if(!state.fromSkill)$('skill-view').href=skillURL(record);
 $('mapping-status').textContent=record.mapping==='question-reviewed'?'Individually mapped to this chapter'+(record.targets.find(t=>matches(record,t.book,t.chapter,'')&&t.book===state.book&&t.chapter===state.chapter)?.subtopics.length?' and subtopic.':'.'):'Chapter-level practice group. Individual question and subtopic mapping is pending.';
 try{
  let data=cache.get(record.skill);if(!data){const response=await fetch(`content/${encodeURIComponent(record.skill)}.json`);if(!response.ok)throw Error('Question file unavailable');data=await response.json();cache.set(record.skill,data);}
  if(token!==revision)return;const q=data[record.question-1];if(!q?.question)throw Error('Question not found');
  $('question').innerHTML=q.question;renderMath($('question'));steps=q.steps||[];
  for(const id of ['reveal','show-all','hide'])$(id).disabled=!steps.length;
  if(!steps.length)$('solution-hint').textContent=q.reference?'This is a reference entry.':'No worked solution is available for this entry.';
 }catch(error){if(token!==revision)return;$('question').textContent='This question could not be loaded. Please reload or open it in skill view.';$('question').classList.add('load-error');console.error(error);}
}
function solution(){const container=$('solution');container.replaceChildren();for(const step of steps.slice(0,shown)){const div=document.createElement('div');div.className='solution-step';div.innerHTML=step;container.append(div);}renderMath(container);$('solution-hint').hidden=shown>0;$('reveal').disabled=shown>=steps.length;$('show-all').disabled=shown>=steps.length;$('hide').disabled=shown===0;}
$('reveal').onclick=()=>{shown=Math.min(shown+1,steps.length);solution();};$('show-all').onclick=()=>{shown=steps.length;solution();};$('hide').onclick=()=>{shown=0;solution();};
$('course').onchange=()=>{location.hash=hash({course:$('course').value});};$('book').onchange=()=>{location.hash=hash({course:state.course,book:$('book').value});};$('chapter').onchange=()=>{location.hash=hash({course:state.course,book:state.book,chapter:$('chapter').value});};$('subtopic').onchange=()=>change({subtopic:$('subtopic').value,entry:'',group:'',fromSkill:'',fromQuestion:''});$('practice-skill').onchange=()=>change({group:$('practice-skill').value,entry:'',fromSkill:'',fromQuestion:''});$('question-select').onchange=()=>change({entry:$('question-select').value,fromSkill:'',fromQuestion:''});
fetch('textbook-catalogue.json').then(r=>{if(!r.ok)throw Error('Catalogue unavailable');return r.json();}).then(data=>{catalogue=data;render();window.addEventListener('hashchange',render);}).catch(error=>{$('chapter-title').textContent='The textbook catalogue could not be loaded. Please reload.';console.error(error);});
