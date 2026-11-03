/* The same measured typography is used for board display and printed lessons. */
(function(root){
function fit(container){
 const records={};
 for(const text of container.querySelectorAll('.lesson-text')){
  const nodes=[...text.querySelectorAll('.lesson-paragraph,.lesson-paragraph>span')],original=nodes.map(e=>({e,font:parseFloat(e.style.fontSize)||0,min:parseFloat(e.style.minHeight)||0}));
  const set=f=>original.forEach(({e,font,min})=>{if(font)e.style.fontSize=font*f+'px';if(min)e.style.minHeight=min*f+'px';});
  const fits=()=>{const h=[...text.children].reduce((a,e)=>a+e.offsetHeight,0);return h<=text.clientHeight+.5&&text.scrollWidth<=text.clientWidth+1;};
  let factor=1; if(!fits()){let lo=.15,hi=1;for(let n=0;n<11;n++){const mid=(lo+hi)/2;set(mid);if(fits())lo=mid;else hi=mid;}factor=lo;set(factor);}
  const id=text.parentElement.dataset.shape;(records[id]??={}).textScale=factor;
 }
 for(const text of container.querySelectorAll('.lesson-image-tex')){
  const start=parseFloat(text.style.fontSize)||24;const set=f=>text.style.fontSize=start*f+'px';
  const fits=()=>text.scrollWidth<=text.clientWidth+1&&text.scrollHeight<=text.clientHeight+1;
  let lo=.10,hi=1;set(1);if(!fits()){for(let n=0;n<12;n++){const mid=(lo+hi)/2;set(mid);if(fits())lo=mid;else hi=mid;}set(lo);}else lo=1;
  const id=text.closest('[data-shape]').dataset.shape;((records[id]??={}).imageFonts??=[]).push(start*lo);
 }
 return records;
}
root.FMQ_FIT=fit;
})(window);
