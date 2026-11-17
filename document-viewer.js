const $=id=>document.getElementById(id),base=new URL('./',location.href),params=new URLSearchParams(location.search);
function local(value,pdf=false){try{const u=new URL(value,base);if(u.origin!==base.origin||!u.pathname.startsWith(base.pathname)||u.username||u.password||!['http:','https:'].includes(u.protocol)||(pdf&&!u.pathname.toLowerCase().endsWith('.pdf')))return null;return u;}catch{return null;}}
const target=local(params.get('file')||'',true),back=local(params.get('return')||'./');
if(target){$('original').href=target.href;$('original').hidden=false;$('save').href=target.href;$('save').download=decodeURIComponent(target.pathname.split('/').pop());$('save').hidden=false;}
$('return').href=back?.href||base.href;
$('return').onclick=e=>{if(window.parent!==window){e.preventDefault();window.parent.postMessage({type:'luisa-close-document'},base.origin);}};
$('title').textContent=params.get('title')||'Document';document.title=$('title').textContent+' · Luisa';
const scroller=document.querySelector('main'), sheets=[];
let pdf, current=1, zoom=1, observer, frame, busy=false;
const nearby=new Set();
function updatePage(){
  let low=0, high=sheets.length-1;
  const top=scroller.getBoundingClientRect().top+16;
  while(low<high){
    const mid=(low+high)>>1;
    if(sheets[mid].node.getBoundingClientRect().bottom<=top) low=mid+1;
    else high=mid;
  }
  current=low+1;
  if(document.activeElement!==$('page')) $('page').value=current;
  $('previous').disabled=current<=1;
  $('next').disabled=current>=sheets.length;
}
function scrollToPage(index,x=0,y=0){
  const sheet=sheets[index];
  if(!sheet)return;
  const box=sheet.node.getBoundingClientRect(), host=scroller.getBoundingClientRect();
  scroller.scrollBy(box.left-host.left+x-12,box.top-host.top+y-12);
  updatePage();
}
async function follow(dest){
  if(typeof dest==='string') dest=await pdf.getDestination(dest);
  if(!Array.isArray(dest))return;
  const index=Number.isInteger(dest[0])?dest[0]:await pdf.getPageIndex(dest[0]);
  const page=await pdf.getPage(index+1), sheet=sheets[index];
  const vp=page.getViewport({scale:sheet.node.clientWidth/page.getViewport({scale:1}).width});
  let x=0,y=0;
  const [left,, ,top]=page.view;
  switch(dest[1]?.name){
    case 'XYZ': [x,y]=vp.convertToViewportPoint(dest[2]??left,dest[3]??top);break;
    case 'FitH': case 'FitBH': [x,y]=vp.convertToViewportPoint(left,dest[2]??top);break;
    case 'FitV': case 'FitBV': [x,y]=vp.convertToViewportPoint(dest[2]??left,top);break;
    case 'FitR': [x,y]=vp.convertToViewportPoint(dest[2],dest[5]);break;
  }
  scrollToPage(index,Math.max(0,x),Math.max(0,y));
}
function linkLayer(annotations,vp){
  const layer=document.createElement('div');
  layer.className='links';
  for(const item of annotations){
    if(item.subtype!=='Link'||!item.rect)continue;
    const a=document.createElement('a');
    if(item.dest){
      a.href='#';
      a.onclick=e=>{e.preventDefault();follow(item.dest).catch(reportError);};
    }else if(item.url){
      let url;try{url=new URL(item.url);}catch{continue;}
      if(!['https:','http:','mailto:','tel:'].includes(url.protocol))continue;
      a.href=url.href;a.target='_blank';a.rel='noopener noreferrer';
    }else continue;
    a.setAttribute('aria-label',item.contentsObj?.str||item.titleObj?.str||(item.dest?'Go to linked passage':a.href));
    const [x1,y1]=vp.convertToViewportPoint(item.rect[0],item.rect[1]);
    const [x2,y2]=vp.convertToViewportPoint(item.rect[2],item.rect[3]);
    Object.assign(a.style,{left:100*Math.min(x1,x2)/vp.width+'%',top:100*Math.min(y1,y2)/vp.height+'%',width:100*Math.abs(x2-x1)/vp.width+'%',height:100*Math.abs(y2-y1)/vp.height+'%'});
    layer.append(a);
  }
  return layer;
}
function reportError(error){
  $('status').textContent='This page could not be displayed. Open the original PDF to continue.';
  console.error(error);
}
function discard(s){
  s.revision++;
  s.task?.cancel();
  for(const c of s.node.querySelectorAll('canvas')){c.width=c.height=0;}
  s.node.replaceChildren();s.ready=false;
}
async function paint(s){
  const revision=s.revision, page=await pdf.getPage(s.number);
  if(s.revision!==revision)return;
  const vp=page.getViewport({scale:s.node.clientWidth/page.getViewport({scale:1}).width});
  const ratio=Math.min(devicePixelRatio||1,2,Math.sqrt(4500000/(vp.width*vp.height)));
  const canvas=document.createElement('canvas');
  canvas.width=Math.ceil(vp.width*ratio);canvas.height=Math.ceil(vp.height*ratio);
  canvas.setAttribute('aria-label','Page '+s.number);
  s.task=page.render({canvasContext:canvas.getContext('2d'),viewport:vp,transform:[ratio,0,0,ratio,0,0]});
  try{
    await s.task.promise;
    const annotations=await page.getAnnotations({intent:'display'});
    if(s.revision!==revision)return;
    const details=document.createElement('details'),summary=document.createElement('summary');
    summary.textContent='Page text';details.append(summary);
    details.ontoggle=async()=>{
      if(!details.open||details.lastChild!==summary)return;
      const text=await page.getTextContent(), para=document.createElement('p');
      para.textContent=text.items.map(i=>(i.str||'')+(i.hasEOL?'\n':' ')).join('');
      details.append(para);
    };
    s.node.replaceChildren(canvas,linkLayer(annotations,vp),details);s.ready=true;
  }finally{s.task=null;if(!canvas.isConnected)canvas.width=canvas.height=0;}
}
async function processNearby(){
  if(busy)return;
  busy=true;
  try{
    while(true){
      const s=[...nearby].filter(s=>!s.ready).sort((a,b)=>Math.abs(a.number-current)-Math.abs(b.number-current))[0];
      if(!s)break;
      try{await paint(s);}catch(error){if(error.name!=='RenderingCancelledException'){s.ready=true;reportError(error);}}
    }
  }finally{busy=false;}
}
function size(s){
  const width=Math.max(100,scroller.clientWidth-26)*zoom;
  s.node.style.width=width+'px';s.node.style.height=width*s.aspect+'px';
}
function layout(nextZoom){
  if(!sheets.length)return;
  const s=sheets[current-1], rect=s.node.getBoundingClientRect();
  const offset=(scroller.getBoundingClientRect().top+12-rect.top)/rect.height;
  zoom=nextZoom;
  for(const sheet of sheets){size(sheet);if(sheet.ready||nearby.has(sheet))discard(sheet);}
  scrollToPage(s.number-1,0,offset*s.node.clientHeight);
  $('smaller').disabled=zoom<=.5;$('larger').disabled=zoom>=3;
  processNearby();
}
$('page').onblur=updatePage;
$('previous').onclick=()=>scrollToPage(current-2);
$('next').onclick=()=>scrollToPage(current);
$('page').onchange=()=>{const n=Math.max(1,Math.min(sheets.length,Math.trunc(Number($('page').value))||1));$('page').value=n;scrollToPage(n-1);};
$('smaller').onclick=()=>layout(Math.max(.5,zoom-.25));
$('larger').onclick=()=>layout(Math.min(3,zoom+.25));
scroller.addEventListener('scroll',()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(updatePage);},{passive:true});
let resize;
addEventListener('resize',()=>{clearTimeout(resize);resize=setTimeout(()=>layout(zoom),150);});
try{
  if(!target)throw Error('Invalid document address');
  const pdfjs=await import('./vendor/pdfjs/pdf.min.js');
  pdfjs.GlobalWorkerOptions.workerSrc=new URL('vendor/pdfjs/pdf.worker.min.js',base).href;
  pdf=await pdfjs.getDocument({url:target.href,docBaseUrl:target.href,cMapUrl:new URL('vendor/pdfjs/cmaps/',base).href,cMapPacked:true,standardFontDataUrl:new URL('vendor/pdfjs/standard_fonts/',base).href,wasmUrl:new URL('vendor/pdfjs/wasm/',base).href,isEvalSupported:false}).promise;
  observer=new IntersectionObserver(entries=>{
    for(const entry of entries){
      const s=sheets[Number(entry.target.dataset.page)-1];
      if(entry.isIntersecting)nearby.add(s);
      else if(nearby.delete(s))discard(s);
    }
    processNearby();
  },{root:scroller,rootMargin:'400px 0px'});
  const first=(await pdf.getPage(1)).getViewport({scale:1});
  for(let number=1;number<=pdf.numPages;number++){
    const node=document.createElement('section');
    node.className='sheet';node.dataset.page=number;node.setAttribute('aria-label','Page '+number+' of '+pdf.numPages);
    const s={number,node,aspect:first.height/first.width,revision:0,ready:false,task:null};
    sheets.push(s);size(s);$('paper').append(node);observer.observe(node);
  }
  $('status').textContent='';$('count').textContent='of '+pdf.numPages;$('page').max=pdf.numPages;
  for(const id of ['page','smaller','larger'])$(id).disabled=false;
  const initialPage=Number(new URLSearchParams(target.hash.slice(1)).get('page'));
  if(Number.isInteger(initialPage)&&initialPage>0)scrollToPage(Math.min(initialPage,pdf.numPages)-1);
  updatePage();
  // Measure mixed-size pages without allocating off-screen bitmaps.
  for(const s of sheets.slice(1)){
    const vp=(await pdf.getPage(s.number)).getViewport({scale:1}), aspect=vp.height/vp.width;
    if(Math.abs(s.aspect-aspect)>.0001){s.aspect=aspect;size(s);}
  }
}catch(error){
  $('status').textContent='This document could not be opened. If you are offline, check the document in Offline downloads.';
  console.error(error);
}
addEventListener('keydown',e=>{if(e.key==='Escape'){$('return').click();e.preventDefault();}if(e.key==='Tab'&&parent!==window){const controls=[...document.querySelectorAll('a[href],button:not(:disabled),input:not(:disabled),summary')].filter(n=>!n.closest('[hidden]'));const i=controls.indexOf(document.activeElement);if(e.shiftKey&&(i<=0)){e.preventDefault();controls.at(-1)?.focus();}else if(!e.shiftKey&&(i<0||i===controls.length-1)){e.preventDefault();controls[0]?.focus();}}});
$('return').focus();
