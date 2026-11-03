'use strict';
// Offline generations are immutable. One metadata write commits a complete download.
const SCOPE=self.registration.scope;
const PREFIX='luisa-offline-v1-'+encodeURIComponent(new URL(SCOPE).pathname)+'-';
const META=PREFIX+'meta';
const key=name=>new URL('__offline/'+name,SCOPE).href;
let mutating=false;
const canonical=url=>{const u=new URL(url,SCOPE);u.search='';u.hash='';if(u.pathname===new URL(SCOPE).pathname)u.pathname+='index.html';else if(!u.pathname.split('/').pop().includes('.'))u.pathname+='.html';return u.href;};
async function read(name){const r=await(await caches.open(META)).match(key(name));return r?r.json():null;}
async function write(name,value){await(await caches.open(META)).put(key(name),new Response(JSON.stringify(value),{headers:{'Content-Type':'application/json'}}));}
function owned(url){const u=new URL(url);return u.origin===new URL(SCOPE).origin&&u.pathname.startsWith(new URL(SCOPE).pathname);}
function safePath(path){if(typeof path!=='string'||path.startsWith('/')||path.includes('\\')||path.split('/').includes('..')||!owned(new URL(path,SCOPE)))throw Error('Invalid download path');return new URL(path,SCOPE).href;}
const hash=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
async function network(path){const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),60000);try{const r=await fetch(safePath(path),{cache:'no-store',headers:{'X-Luisa-Offline':'network'},signal:controller.signal});if(!r.ok)throw Error('Could not download '+path+' ('+r.status+')');const bytes=await r.arrayBuffer();return new Response(bytes,{status:r.status,headers:r.headers});}finally{clearTimeout(timer);}}
async function catalog(){const r=await network('offline-catalogue.json');const d=await r.json();if(d.schemaVersion!==1||!Array.isArray(d.packs)||!Array.isArray(d.shared)||!/^[a-f0-9]{64}$/.test(d.revision))throw Error('Offline downloads are not available for this release.');return d;}
async function available(gen){if(!gen)return false;const names=new Set(await caches.keys());return names.has(gen.shell)&&Object.values(gen.packs).every(p=>names.has(p.cache));}
async function verifyFiles(cacheName,files){if(!(await caches.keys()).includes(cacheName))return false;const c=await caches.open(cacheName);for(const path of files)if(!await c.match(safePath(path)))return false;return true;}
async function status(){const active=await read('active');if(!active)return {active:null,packs:[],error:null};const shellOK=await verifyFiles(active.shell,active.shared);const packs=[];for(const [id,p]of Object.entries(active.packs))packs.push({id,title:p.title,ready:shellOK&&await verifyFiles(p.cache,p.files)});return {active,packs,error:shellOK?null:'Some saved files are missing. Reconnect and download again.'};}
async function download(ids,send,all=false){
 const d=await catalog(),old=await read('active');const selected=new Set([...Object.keys(old?.packs||{}),...(all?d.packs.map(p=>p.id):ids)]);
 const packs=[...selected].map(id=>{const p=d.packs.find(p=>p.id===id);if(!p)throw Error('A previously downloaded chapter is no longer available. The previous copy has been kept.');return p;});
 const files=[...new Set([...d.shared,...packs.flatMap(p=>p.files)])];
 for(const path of files){safePath(path);if(!d.files[path]||!Number.isSafeInteger(d.files[path].bytes)||!/^[a-f0-9]{64}$/.test(d.files[path].sha256))throw Error('Invalid file inventory');}
 const total=files.reduce((n,p)=>n+d.files[p].bytes,0), estimate=await navigator.storage?.estimate?.();
 if(estimate?.quota&&estimate?.usage&&total>estimate.quota-estimate.usage)throw Error('Not enough free storage for a safe download. Free some space and retry; your previous downloads are unchanged.');
 const stamp=d.revision+'-'+crypto.randomUUID(),shell=PREFIX+stamp+'-shell',packNames=Object.fromEntries(packs.map(p=>[p.id,PREFIX+stamp+'-'+encodeURIComponent(p.id)]));
 const staged=[shell,...Object.values(packNames)], shared=new Set(d.shared);let done=0,committed=false;
 try{
  for(const path of files){
   const r=await network(path),bytes=await r.arrayBuffer();
   if(bytes.byteLength!==d.files[path].bytes||await hash(bytes)!==d.files[path].sha256)throw Error('The release changed or a file was incomplete. Retry when online. Previous downloads are unchanged.');
   const names=shared.has(path)?[shell]:packs.filter(p=>p.files.includes(path)).map(p=>packNames[p.id]);
   // Persist full 200 responses, including PDFs; range requests are served below.
   const headers=new Headers(r.headers);headers.delete('content-encoding');headers.delete('transfer-encoding');headers.set('Content-Length',String(bytes.byteLength));
   for(const name of names)await(await caches.open(name)).put(safePath(path),new Response(bytes.slice(0),{status:200,headers}));
   done+=bytes.byteLength;send({type:'progress',done,total,file:path});
  }
  const gen={id:stamp,revision:d.revision,version:d.version,shell,shared:d.shared,packs:Object.fromEntries(packs.map(p=>[p.id,{cache:packNames[p.id],files:p.files,title:p.book+' · '+p.chapter+'. '+p.title}]))};
  // Keep the exact inventory with the snapshot so offline management survives a cold launch.
  await(await caches.open(shell)).put(new URL('offline-catalogue.json',SCOPE),new Response(JSON.stringify(d),{headers:{'Content-Type':'application/json'}}));
  for(const p of packs)if(!await verifyFiles(packNames[p.id],p.files))throw Error('Download verification failed.');
  if(!await verifyFiles(shell,d.shared))throw Error('Shared download verification failed.');
  await write('generation/'+stamp,gen);
  await write('active',gen);
  committed=true;
  send({type:'complete',generation:stamp,status:await status(),catalogue:d});
 }catch(e){if(!committed)for(const name of staged)await caches.delete(name);throw e;}
}
async function remove(id){const old=await read('active');if(!old?.packs[id])return;const packs={...old.packs};delete packs[id];const gen={...old,id:old.id+'-remove-'+crypto.randomUUID(),packs};await write('generation/'+gen.id,gen);await write('active',gen);await cleanup();}
async function cleanup(){
 // Retain snapshots pinned by open windows as well as the active generation.
 const active=await read('active'),keep=new Set([META]);const clients=await self.clients.matchAll({type:'window',includeUncontrolled:true});
 const gens=[active];for(const c of clients){const pin=await read('client/'+c.id);if(pin)gens.push(await read('generation/'+pin));}
 for(const g of gens.filter(Boolean)){keep.add(g.shell);for(const p of Object.values(g.packs))keep.add(p.cache);}
 for(const name of await caches.keys())if(name.startsWith(PREFIX)&&!keep.has(name))await caches.delete(name);
}
// A replacement worker waits until existing windows close; it cannot interrupt a download.
self.addEventListener('install',()=>{});
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('message',e=>{
 const port=e.ports[0];if(!port||!e.source?.url||!owned(e.source.url))return;
 const send=x=>port.postMessage(x);const mutation=['download','remove','cleanup'].includes(e.data?.type);
 const task=async()=>{
  if(mutation&&mutating){send({type:'error',message:'Another download or removal is in progress. Wait for it to finish, then retry.'});return;}
  if(mutation)mutating=true;
  try{switch(e.data?.type){
   case 'status':send({type:'status',...await status()});break;
   case 'catalogue':send({type:'catalogue',catalogue:await catalog()});break;
   case 'download':if(e.data.all!==true&&(!Array.isArray(e.data.ids)||!e.data.ids.length))throw Error('Choose a chapter.');await download(e.data.ids||[],send,e.data.all===true);break;
   case 'remove':await remove(e.data.id);send({type:'status',...await status()});break;
   case 'cleanup':await cleanup();send({type:'status',...await status()});break;
   default:throw Error('Unknown offline request');
  }}catch(error){send({type:'error',message:error.name==='QuotaExceededError'?'Storage is full. Free space and retry. Your previous downloads have been kept.':error.message});}finally{if(mutation)mutating=false;}
 };
 e.waitUntil(task());
});
async function rangeResponse(request,response){
 const range=request.headers.get('Range');if(!range)return response;
 const bytes=await response.arrayBuffer(),m=/^bytes=(\d*)-(\d*)$/.exec(range);
 if(!m||(!m[1]&&!m[2]))return new Response(null,{status:416,headers:{'Content-Range':'bytes */'+bytes.byteLength}});
 let start=m[1]?Number(m[1]):Math.max(0,bytes.byteLength-Number(m[2])),end=m[1]?(m[2]?Math.min(Number(m[2]),bytes.byteLength-1):bytes.byteLength-1):bytes.byteLength-1;
 if(start>end||start>=bytes.byteLength)return new Response(null,{status:416,headers:{'Content-Range':'bytes */'+bytes.byteLength}});
 const headers=new Headers(response.headers);headers.set('Content-Range',`bytes ${start}-${end}/${bytes.byteLength}`);headers.set('Content-Length',String(end-start+1));headers.set('Accept-Ranges','bytes');
 return new Response(bytes.slice(start,end+1),{status:206,headers});
}
async function recovery(){
 if(mutating)throw Error('A download is in progress. Wait for it to finish before repairing the app.');
 mutating=true;let shell,committed=false;
 try{
  const d=await catalog(),id='repair-'+crypto.randomUUID();shell=PREFIX+id;
  const files=['offline.html','offline.js','offline.css','app-navigation.js','manifest.webmanifest','assets/luisa/icon-192.png','assets/luisa/icon-512.png'];
  const c=await caches.open(shell);
  for(const path of files){const r=await network(path),bytes=await r.arrayBuffer();if(!d.files[path]||bytes.byteLength!==d.files[path].bytes||await hash(bytes)!==d.files[path].sha256)throw Error('The app changed during repair. Reconnect and retry.');const headers=new Headers(r.headers);headers.delete('content-encoding');headers.set('Content-Length',String(bytes.byteLength));await c.put(safePath(path),new Response(bytes,{headers}));}
  await c.put(safePath('offline-catalogue.json'),new Response(JSON.stringify(d),{headers:{'Content-Type':'application/json'}}));
  const gen={id,revision:d.revision,version:d.version,shell,shared:files,packs:{}};
  await write('generation/'+id,gen);committed=true;return gen;
 }finally{if(shell&&!committed)await caches.delete(shell);mutating=false;}
}
function repairMessage(message){return new Response('<!doctype html><meta name="viewport" content="width=device-width"><title>Luisa · Repair downloads</title><h1>Saved files need repair</h1><p>'+message+'</p><p>Existing complete downloads are kept.</p><a href="'+new URL('offline.html?repair=1',SCOPE).href+'">Repair downloads while online</a>',{status:503,headers:{'Content-Type':'text/html; charset=utf-8'}});}
async function respond(e){
 const u=new URL(e.request.url),active=await read('active');let gen=active;
 if(e.request.mode==='navigate'&&canonical(u.href)===safePath('offline.html')&&u.searchParams.get('repair')==='1'){
  try{gen=await recovery();if(e.resultingClientId)await write('client/'+e.resultingClientId,gen.id);return(await caches.open(gen.shell)).match(safePath('offline.html'));}
  catch(error){return repairMessage('Reconnect, then retry the repair.');}
 }
 let pinned=e.clientId&&await read('client/'+e.clientId);
 if(pinned)gen=await read('generation/'+pinned)||active;
 if(e.request.mode==='navigate'){
  if(u.searchParams.get('offlineRelease')===active?.id)gen=active;
  if(e.resultingClientId&&gen)await write('client/'+e.resultingClientId,gen.id);
 }
 if(gen){
  const url=canonical(u.href);
  const path=decodeURI(new URL(url).pathname.slice(new URL(SCOPE).pathname.length));
  const candidates=[gen.shell,...Object.values(gen.packs).filter(p=>p.files.includes(path)).map(p=>p.cache)];
  for(const name of candidates){if(!(await caches.keys()).includes(name))continue;const hit=await(await caches.open(name)).match(url);if(hit)return rangeResponse(e.request,hit);}
  if((gen.shared.includes(path)||Object.values(gen.packs).some(p=>p.files.includes(path)))&&e.request.mode==='navigate')return repairMessage('Reconnect to restore the missing saved files.');
  if(gen.shared.includes(path)||Object.values(gen.packs).some(p=>p.files.includes(path)))return new Response('Saved file missing. Reconnect and download this chapter again from Offline downloads.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}});
 }
 try{return await fetch(e.request);}catch(error){
  if(e.request.mode==='navigate')return new Response('<!doctype html><meta name="viewport" content="width=device-width"><title>Luisa · Offline</title><h1>This resource is not downloaded</h1><p>Reconnect to download this chapter. Existing downloads remain available.</p><p><a href="'+new URL('offline.html',SCOPE).href+'">Open offline downloads</a></p>',{status:503,headers:{'Content-Type':'text/html; charset=utf-8'}});
  return new Response('Not downloaded. Reconnect and download this chapter.',{status:503,headers:{'Content-Type':'text/plain'}});
 }
}
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET'||!owned(e.request.url)||e.request.headers.get('X-Luisa-Offline')==='network')return;
 e.respondWith(respond(e));
});
