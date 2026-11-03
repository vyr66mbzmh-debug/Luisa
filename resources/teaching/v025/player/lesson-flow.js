/* Reflow reviewed text exercises; answer covers share their working container. */
(function(root){
function render(slide,deck,o){
 const R=root.FMQ_SLIDE_RENDERER, shapes=new Map(root.FMQ_FAITHFUL.flat(root.FMQ_FAITHFUL.prepare(slide,deck).shapes).map(s=>[s.id,s]));
 const shape=id=>{const s=shapes.get(id);if(!s)throw Error('Missing flow shape '+id);return R.shape(s,o)};
 return '<div class="lesson-flow">'+slide.flowLayout.map(row=>'<section class="flow-row'+(row.cover?' flow-answer':'')+(row.theory?' flow-theory':'')+'">'+(row.label?'<div class="flow-label">'+shape(row.label)+'</div>':'')+'<div class="flow-body">'+row.body.map(shape).join('')+'</div>'+(row.cover?shape(row.cover):'')+'</section>').join('')+'</div>';
}
root.FMQ_FLOW={render};
})(window);
