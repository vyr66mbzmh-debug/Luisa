window.luisaPrintPanel = async function({item,edition}) {
  const css = Array.from(document.querySelectorAll('link[rel=stylesheet]'),e=>e.href);
  const overview = document.querySelector('#slide-content .luisa-overview');
  if (overview) return {html:overview.outerHTML,width:1200,height:760,css};
  const activity = document.querySelector('#slide-content .ch14');
  if (!activity) throw Error('Expected an activity on '+item.chapterKey+' '+item.slide);
  const student = edition==='student', n=item.slide;
  // The worked teaching sequences stay on paper in both editions. Independent
  // exercise slots and table answers remain writable in the student edition.
  if(!student || [22,46,47,48,49].includes(n)) FMQ_TEST.revealAll();
  const copy=activity.cloneNode(true);
  copy.dataset.panel=n;
  if(n===5 && student) copy.querySelector('.slot').classList.remove('open');
  if(n===8) {
    const image = new Image();
    image.className='paper-geogebra';
    image.alt='Exponential gradient and its tangent for the GeoGebra activity';
    image.src=item.poster||new URL('resources/pure-year-1/native/assets/ch14-8-geogebra.png',location.href).href;
    const frame=copy.querySelector('.frame-viewport,.frame');
    if(!frame)throw Error('Missing original GeoGebra diagram');
    frame.replaceWith(image);
  }
  if(n===28) {
    if(!copy.dataset.proof)throw Error('Missing change-of-base proof');
    copy.querySelector('.proof').innerHTML=copy.dataset.proof;
  }
  if(n===49 && student) for(const plot of copy.querySelectorAll('[data-blank-graph]')) {
    const template=plot.querySelector('template.print-grid');
    if(!template)throw Error('Missing model axes');
    plot.replaceChildren(template.content.cloneNode(true));
  }
  for(const slot of copy.querySelectorAll('.slot')) {
    const work=slot.querySelector('.working'), control=slot.querySelector('.cover');
    if(slot.classList.contains('open')) {control.remove();continue;}
    const blank=work.querySelector('[data-blank-src]');
    if(blank) {
      const img=new Image();img.src=new URL(blank.dataset.blankSrc,location.href).href;
      img.alt='Labelled grid for the sketch';img.className='pencil-grid';
      work.replaceChildren(img);work.style.visibility='visible';control.remove();
    } else {
      work.replaceChildren();
      const label=document.createElement('span');label.className='paper-cue';
      label.textContent=control.textContent;control.replaceWith(label);
    }
  }
  copy.querySelectorAll('.controls,.power-tracer,button.choice,template').forEach(e=>e.remove());
  return {html:copy.outerHTML,width:1200,height:805,css};
};
