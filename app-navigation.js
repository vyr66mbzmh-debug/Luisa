/* Installed-app navigation. Normal browser tabs keep their existing behaviour. */
(()=>{'use strict';
 if(/document-viewer\.html$/.test(location.pathname))return;
 const script=document.currentScript,base=new URL('./',script.src),standalone=()=>matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
 let overlay=null,previousFocus=null,oldOverflow='',closing=false,inerted=[];
 function local(value){try{const u=new URL(value,location.href);return u.origin===base.origin&&u.pathname.startsWith(base.pathname)&&!u.username&&!u.password?u:null;}catch{return null;}}
 function remove(){if(!overlay)return;overlay.remove();overlay=null;for(const [node,wasInert] of inerted)node.inert=wasInert;inerted=[];document.body.style.overflow=oldOverflow;previousFocus?.focus();}
 function close(){if(!overlay||closing)return;closing=true;if(window.history.state?.luisaDocument){window.history.back();}else{remove();closing=false;}}
 function openDocument(value,title='Document'){
  const url=local(value);if(!standalone()||!url||!url.pathname.toLowerCase().endsWith('.pdf'))return false;
  if(overlay)return true;previousFocus=document.activeElement;oldOverflow=document.body.style.overflow;
  const reader=new URL('document-viewer.html',base);reader.searchParams.set('file',url.href);reader.searchParams.set('return',location.href);reader.searchParams.set('title',title);
  overlay=document.createElement('iframe');overlay.src=reader.href;overlay.title=title;overlay.setAttribute('role','dialog');overlay.setAttribute('aria-label',title);overlay.style.cssText='position:fixed;inset:0;width:100%;height:100%;height:100dvh;border:0;background:white;z-index:2147483647';
  inerted=[...document.body.children].map(node=>[node,node.inert]);for(const [node] of inerted)node.inert=true;document.body.append(overlay);document.body.style.overflow='hidden';window.history.pushState({...window.history.state,luisaDocument:true},'',location.href);overlay.focus();return true;
 }
 window.LUISA_NAVIGATION={openDocument};
 addEventListener('popstate',()=>{remove();closing=false;});
 addEventListener('message',e=>{if(e.origin===base.origin&&overlay&&e.source===overlay.contentWindow&&e.data?.type==='luisa-close-document')close();});
 addEventListener('keydown',e=>{if(e.key==='Escape'&&overlay)close();});
 document.addEventListener('click',e=>{if(!standalone()||e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;const a=e.target.closest?.('a[href]');if(!a||a.hasAttribute('download'))return;const u=local(a.href);if(!u)return;if(openDocument(u.href,a.textContent.trim()||'Document')){e.preventDefault();return;}if(/(?:lesson|native)-viewer\.html$/.test(u.pathname)){try{sessionStorage.setItem('luisa-lesson-return',JSON.stringify({viewer:u.pathname,book:u.searchParams.get('book')||'',chapter:u.searchParams.get('chapter')||'1',returnTo:location.href}));}catch{}a.target='_self';}},true);
 if(standalone()&&/(?:lesson|native)-viewer\.html$/.test(location.pathname)){
  const back=document.getElementById('library')||document.querySelector('header a');
  if(back){back.textContent='← Back to library';back.setAttribute('aria-label','Back to library');back.style.minHeight='44px';back.style.display='inline-flex';back.style.alignItems='center';
   back.addEventListener('click',e=>{try{const saved=JSON.parse(sessionStorage.getItem('luisa-lesson-return'));const u=local(saved?.returnTo);if(saved?.viewer===location.pathname&&saved.book===(new URL(location.href).searchParams.get('book')||'')&&saved.chapter===(new URL(location.href).searchParams.get('chapter')||'1')&&u&&u.pathname!==location.pathname){e.preventDefault();location.href=u.href;}}catch{}});
  }
 }
})();
