/* Source-aligned board and student layout. Animation visibility never decides print content. */
(function(root){'use strict';const R=typeof module!=='undefined'?require('./lesson-renderer.js'):root.FMQ_SLIDE_RENDERER;const esc=R.escape;
function flat(xs){return xs.flatMap(s=>[s,...flat(s.children||[])]);}
const {prepare} = typeof module !== 'undefined' ? require('../../../../lesson-controls.js') : root.LUISA_CONTROLS;
function bounds(slide,deck){if(slide.measuredLayout)return{x:0,y:0,w:slide.contentWidth||deck.width,h:slide.contentHeight||deck.height};deck={...deck,width:slide.contentWidth||deck.width};const shapes=slide.shapes.filter(s=>!slide.headerShapes.includes(s.id)&&s.box.x+s.box.w>0&&s.box.y>=55&&s.box.x<deck.width&&s.box.y<(slide.contentHeight||deck.height));
 if(slide.titlePage||!shapes.length)return{x:0,y:0,w:deck.width,h:deck.height};
 let x=Math.max(0,Math.min(...shapes.map(s=>s.box.x))-14),y=Math.min(65,Math.min(...shapes.map(s=>s.box.y))-18),right=Math.min(deck.width,Math.max(...shapes.map(s=>s.box.x+s.box.w))+14),bottom=Math.min(slide.contentHeight||deck.height,Math.max(...shapes.map(s=>s.box.y+s.box.h))+10);
 return {x,y,w:right-x,h:Math.max(100,bottom-y)};}
function render(slide,deck,o={}){const s=prepare(slide,deck),b=bounds(s,deck);let contents;
 if(slide.titlePage){contents=`<div class="chapter-cover" style="width:${deck.width}px;height:${deck.height}px"><h2>${esc(slide.title)}</h2></div>`;}
 else contents=R.render(s,{...deck,width:s.contentWidth||deck.width},o);
 return `<div class="source-slide${slide.titlePage?' title-page':''}${slide.extension?' extension':''}" data-source-slide="${slide.sourceSlide}" style="width:${b.w}px;height:${b.h}px"><div class="source-body" style="position:absolute;left:${-b.x}px;top:${-b.y}px">${contents}</div></div>`;}
 const api={render,prepare,bounds,flat};if(typeof module!=='undefined')module.exports=api;root.FMQ_FAITHFUL=api;
})(typeof window==='undefined'?globalThis:window);
