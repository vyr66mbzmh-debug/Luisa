'use strict';
(()=>{
const $=id=>document.getElementById(id);let catalogue,snapshot,busy=false,newGeneration;
function savedURL(url){if(!snapshot?.active)return url;const u=new URL(url,location.href);u.searchParams.set('offlineRelease',snapshot.active.id);return u.href;}
const selected=new Set();const mb=n=>(n/1048576).toFixed(1)+' MB';
function request(type,args={},onProgress){return new Promise(async(resolve,reject)=>{
 try{const registration=await navigator.serviceWorker.ready;const worker=registration.active;if(!worker)throw Error('Offline support is not active. Reload while connected.');const channel=new MessageChannel();let timer;
 const resetTimer=()=>{clearTimeout(timer);timer=setTimeout(()=>{channel.port1.close();reject(Error('The download stopped responding. Keep the app open and retry when connected; the previous copy is unchanged.'));},120000);};resetTimer();
 channel.port1.onmessage=e=>{resetTimer();if(e.data.type==='progress'){onProgress?.(e.data);return;}clearTimeout(timer);channel.port1.close();if(e.data.type==='error')reject(Error(e.data.message));else resolve(e.data);};worker.postMessage({type,...args},[channel.port2]);
 }catch(e){reject(e);}
});}
function state(value){busy=value;for(const id of ['download','download-all','refresh','book'])$(id).disabled=value;document.querySelectorAll('input,button.remove').forEach(e=>e.disabled=value);$('download').disabled=value||!selected.size;$('download-all').disabled=value||!catalogue?.packs.length;}
function render(){
 if(!catalogue)return;const filter=$('book').value;const nodes=[];
 for(const p of catalogue.packs.filter(p=>!filter||p.bookId===filter)){
  const saved=snapshot?.packs.find(x=>x.id===p.id),ready=saved?.ready,update=ready&&snapshot.active.revision!==catalogue.revision;
  const card=document.createElement('article');card.className='chapter';const title=document.createElement('h2'),label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=selected.has(p.id);input.disabled=busy;input.setAttribute('aria-label','Select '+p.book+' chapter '+p.chapter);input.onchange=()=>{input.checked?selected.add(p.id):selected.delete(p.id);state(busy);};const text=document.createElement('span');text.textContent=p.book+' · '+p.chapter+'. '+p.title;label.append(input,text);title.append(label);card.append(title);
  const status=document.createElement('p');status.className=ready?'ready':saved?'missing':'';status.textContent=ready?(update?'Ready offline · update available':'Ready offline · v'+snapshot.active.version):saved?'Saved files missing — download again':'Not downloaded';card.append(status);
  const detail=document.createElement('p');detail.className='detail';const bytes=p.files.reduce((sum,f)=>sum+catalogue.files[f].bytes,0);detail.textContent=mb(bytes)+' chapter files. Shared app files and safe replacements of existing downloads are added to the total. '+p.practiceEntries+' practice entries.';card.append(detail);
  if(p.unavailable.length){const missing=document.createElement('p');missing.className='detail';missing.textContent='Not included: '+p.unavailable.join('; ')+'.';card.append(missing);}
  const nav=document.createElement('nav');const library=document.createElement('a');library.href=savedURL((p.chapter==='Additional'?'index.html#':'textbook-view.html#')+new URLSearchParams({course:p.course,book:p.bookId,...(p.chapter==='Additional'?{skill:p.skill,topic:p.topic}:{chapter:p.chapter})}));library.textContent=p.chapter==='Additional'?'Open skill library':'Open chapter';nav.append(library);
  for(const [kind,url]of Object.entries(p.links)){const link=document.createElement('a');link.href=savedURL(url);link.textContent={slides:'Slides',booklet:'Student booklet',solutions:'Solutions',pdf:'Textbook',practice:'Practice Chapter'}[kind];nav.append(link);}
  if(saved){const remove=document.createElement('button');remove.className='remove';remove.textContent='Remove download';remove.disabled=busy;remove.onclick=async()=>{state(true);try{snapshot=await request('remove',{id:p.id});selected.delete(p.id);render();$('status').textContent='Removed from your downloads. Files used by open lessons are retained until those windows close.';}catch(e){$('error').textContent=e.message;}finally{state(false);}};nav.append(remove);}card.append(nav);nodes.push(card);
 }$('chapters').replaceChildren(...nodes);state(busy);
}
function catalogueControls(){
  const allFiles=[...new Set([...catalogue.shared,...catalogue.packs.flatMap(p=>p.files)])];
  const missing=catalogue.packs.filter(p=>p.unavailable.length).length;
  $('all-summary').textContent='Download all includes '+catalogue.packs.length+' chapters across all books (estimated download size: '+mb(allFiles.reduce((n,p)=>n+catalogue.files[p].bytes,0))+'). Includes available slides, booklets, textbooks and practice resources. '+(missing?missing+' chapters have unavailable resources listed below. ':'')+'Extra free space is needed to keep existing downloads during replacement. This downloads the available learning library; it cannot include unpublished or unavailable resources.';
  const prior=$('book').value;$('book').replaceChildren(new Option('All books',''),...[...new Map(catalogue.packs.map(p=>[p.bookId,p.book])).entries()].map(([id,title])=>new Option(title,id)));$('book').value=prior;
}
async function load(online=false){
 $('error').textContent='';state(true);
 try{
  snapshot=await request('status');
  if(online)catalogue=(await request('catalogue')).catalogue;
  else{const r=await fetch('offline-catalogue.json');if(!r.ok)throw Error('Connect to the internet to prepare downloads.');catalogue=await r.json();}
  catalogueControls();
  render();$('status').textContent=snapshot.error||'Choose chapters below. Downloaded chapters remain available without a connection.';
  const estimate=await navigator.storage?.estimate?.();$('storage').textContent=estimate?.quota?'Storage used by this site: '+mb(estimate.usage||0)+'. Estimated space available: '+mb(estimate.quota-(estimate.usage||0))+'.':'';
 }catch(e){$('error').textContent=e.message;}finally{state(false);}
}
$('book').onchange=render;$('refresh').onclick=()=>load(true);
async function downloadSelected(all=false){
 state(true);$('error').textContent='';$('progress').hidden=false;$('progress').value=0;$('status').textContent='Downloading and checking files. Keep Luisa open…';
 try{await navigator.storage?.persist?.();const result=await request('download',{ids:[...selected],all},p=>{$('progress').max=p.total;$('progress').value=p.done;$('status').textContent='Downloaded and checked '+mb(p.done)+' of '+mb(p.total)+'. Keep Luisa open…';});snapshot=result.status;if(result.catalogue){catalogue=result.catalogue;catalogueControls();}newGeneration=result.generation;selected.clear();render();$('status').textContent='Download complete. Open the checked downloads below, then test with Wi-Fi and mobile data off.';$('open-new').hidden=false;}
 catch(e){$('error').textContent=e.message;$('status').textContent='Download incomplete. Previous complete downloads are unchanged.';snapshot=await request('status').catch(()=>snapshot);render();}
 finally{$('progress').hidden=true;state(false);}
}
$('download').onclick=()=>downloadSelected();
$('download-all').onclick=()=>{if(busy||!catalogue)return;selected.clear();for(const p of catalogue.packs)selected.add(p.id);render();downloadSelected(true);};
$('open-new').onclick=()=>{location.href='offline.html?offlineRelease='+encodeURIComponent(newGeneration);};
function connection(){$('connection').textContent=navigator.onLine?'Connection detected. Offline readiness is shown separately for each chapter.':'No connection detected. Use chapters marked Ready offline.';}
window.addEventListener('online',connection);window.addEventListener('offline',connection);connection();
(async()=>{if(!('serviceWorker'in navigator))throw Error('This browser cannot store Luisa for offline use. Open it in a supported browser.');const registration=await navigator.serviceWorker.register('sw.js');if(registration.waiting)throw Error('An app update is waiting. Close all Luisa windows, then reopen Luisa while connected to finish setup. Existing downloads are kept.');await navigator.serviceWorker.ready;await request('cleanup').catch(()=>{});await load();})().catch(e=>{$('error').textContent=e.message;});
})();
