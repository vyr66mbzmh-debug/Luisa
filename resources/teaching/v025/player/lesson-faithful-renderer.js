/* Source-aligned board and student layout. Animation visibility never decides print content. */
(function(root){'use strict';const R=typeof module!=='undefined'?require('./lesson-renderer.js'):root.FMQ_SLIDE_RENDERER;const esc=R.escape;
function flat(xs){return xs.flatMap(s=>[s,...flat(s.children||[])]);}
function prepare(slide,deck){let copy=JSON.parse(JSON.stringify(slide));copy.shapes=copy.shapes.filter(s=>!copy.headerShapes.includes(s.id));
 function style(shapes){for(const s of shapes){delete s.printFallback;delete s.webStage;const t=s.text;if(t){for(const p of t.paragraphs){delete p.webStage;for(const r of p.parts)delete r.fontFamily;}if(s.cover){s.fill='#d6e5f5';s.line={color:'#6383a4',width:1.5};s.text={...t,anchor:'ctr',paragraphs:[{align:'ctr',fontSize:32,color:'#173b60',parts:[{type:'text',text:s.coverLabel||'?',fontSize:32}]}]};}}
 if(s.cover){s.text={insets:[4,4,4,4],anchor:'ctr',wrap:true,paragraphs:[{align:'ctr',fontSize:30,color:(copy.vectorRebuilt||copy.measuredLayout)?'#173b60':'#fff',parts:[{type:'text',text:s.coverLabel||'?',fontSize:30}]}]};} if(s.children)style(s.children);}}
 style(copy.shapes);return copy;}
function bounds(slide,deck){if(slide.measuredLayout)return{x:0,y:0,w:slide.contentWidth||deck.width,h:slide.contentHeight||deck.height};deck={...deck,width:slide.contentWidth||deck.width};const shapes=slide.shapes.filter(s=>!slide.headerShapes.includes(s.id)&&s.box.x>=0&&s.box.y>=55&&s.box.x<deck.width&&s.box.y<(slide.contentHeight||deck.height)&&s.box.w<deck.width);
 if(slide.titlePage||!shapes.length)return{x:0,y:0,w:deck.width,h:deck.height};
 let x=Math.max(0,Math.min(...shapes.map(s=>s.box.x))-14),y=Math.min(65,Math.min(...shapes.map(s=>s.box.y))-18),right=Math.min(deck.width,Math.max(...shapes.map(s=>s.box.x+s.box.w))+14),bottom=Math.min(slide.contentHeight||deck.height,Math.max(...shapes.map(s=>s.box.y+s.box.h))+10);
 return {x,y,w:right-x,h:Math.max(100,bottom-y)};}
function render(slide,deck,o={}){const s=prepare(slide,deck),b=bounds(s,deck);let contents;
 if(slide.titlePage){contents=`<div class="chapter-cover" style="width:${deck.width}px;height:${deck.height}px"><h2>${esc(slide.title)}</h2></div>`;}
 else contents=R.render(s,{...deck,width:s.contentWidth||deck.width},o);
 return `<div class="source-slide${slide.titlePage?' title-page':''}${slide.extension?' extension':''}" data-source-slide="${slide.sourceSlide}" style="width:${b.w}px;height:${b.h}px"><div class="source-body" style="position:absolute;left:${-b.x}px;top:${-b.y}px">${contents}</div></div>`;}
 const api={render,prepare,bounds,flat};if(typeof module!=='undefined')module.exports=api;root.FMQ_FAITHFUL=api;
})(typeof window==='undefined'?globalThis:window);
