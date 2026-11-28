'use strict';

const logoDesigns = {
  formation: {label:'Gold pulse'},
  lettering: {label:'Ink sweep'},
  compass: {label:'Compass point'}
};

// Coordinates are in half-size pixels of the original banner. The mask reveals
// its photographed ink, including the serifs, letter spacing and gold separators.
const crestStrokes = [
  {color:'#b88336', start:0, end:1, path:
    'M290 168 L310 168 L320 167.5 L330 166.5 L340 164.5 L350 162.25 L360 159.5 L370 155.75 L380 151.75 L390 147 L400 141.75 L410 135.75 L420 129 L430 122 L440 114.75 L450 107.25 L460 99.75 L470 92.75 L480 85.75 L490 79.25 L500 73.5 L510 68 L520 63.5 L530 59.75 L540 56.25 L550 53.75 L560 51.5 Q572 49.5 581 50 C621 49 653 74 652 117 C652 144 634 164 607 165 C581 165 574 143 584 126 C590 114 607 112 611 124 C616 136 602 141 599 134 C597 130 602 127 605 130 Q607 132 604 133'},
  {color:'#173850', start:.12, end:.83, path:
    'M469.5 179 C469 129 491 90 526 67 C547 54 571 49 591 51 C626 52 654 81 652 121 C650 148 631 164 609 165'},
  {color:'#23435c', start:.49, end:1, path:
    'M595 98.5 C618 97 634 113 653 125 C701 158 738 165 795 165'}
];

const logoBeats = [
  {letter:[337,410],word:[243,324]}, {letter:[424,517],word:[332,483]},
  {letter:[539,573],word:[493,617]}, {letter:[595,655],word:[627,723]},
  {letter:[663,759],word:[733,846]}
];

// Sampled centrelines only control the paper mask. The visible ink is the banner image.
const sideReveals = [
  {origin:[64,271],radius:405,
    path:'M64 271 L75 269.5 90 264.5 105 257.5 120 248 135 237.5 150 225.5 165 213 180 199.5 195 185.5 210 171.5 222 160.5'},
  {origin:[795,172.5],radius:410,
    path:'M795 172.5 L807 185.8 820 202.8 835 220.8 850 237.5 865 252.5 880 262.8 895 267 910 266.5 925 259.5 940 245.2 955 227.5 970 201.8 985 177.8 1000 153.5 1015 132.2 1030 118 1045 107 1060 102.8 1075 104 1085 108'}
];

function mountLogo(frame,design,button,alreadyComplete,onComplete) {
  frame.append(document.getElementById('formation-template').content.cloneNode(true));
  const svg=frame.querySelector('.formation-art');
  const mask=svg.querySelector('#unprinted');
  const clip=svg.querySelector('#current-letter rect');
  const gold=svg.querySelector('.letter-ink');
  const replay=document.getElementById('replay-logo');
  const clamp=n=>Math.min(1,Math.max(0,n));
  const ease=n=>{const t=clamp(n);return t*t*(3-2*t)};
  function add(parent,tag,attrs){
    const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
    for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);
    parent.append(el);return el;
  }
  function path(parent,d,color,width){
    return add(parent,'path',{d,stroke:color,fill:'none','stroke-width':width,
      'stroke-linecap':'round','stroke-linejoin':'round'});
  }
  function trace(el){
    const length=el.getTotalLength();
    el.setAttribute('stroke-dasharray',length+' '+(length+1));
    return {el,length};
  }
  function draw(stroke,fraction){
    stroke.el.style.visibility=fraction<=0?'hidden':'visible';
    stroke.el.setAttribute('stroke-dashoffset',stroke.length*(1-fraction));
  }
  function bead(ink,r){
    return add(svg,'circle',{r,fill:ink,stroke:'#fffaf3','stroke-width':.8});
  }
  function move(pen,pos,opacity){
    pen.setAttribute('cx',pos.x);pen.setAttribute('cy',pos.y);pen.setAttribute('opacity',opacity);
  }

  for(const spec of crestStrokes)path(mask,spec.path,'white',12);
  const crest=crestStrokes.map(spec=>({...spec,stroke:trace(path(mask,spec.path,'black',15))}));
  const words=logoBeats.map(({word:[x,end]})=>add(mask,'rect',{x,y:278,width:end-x,height:26,fill:'white'}));
  const sides=Array.from(svg.querySelectorAll('.side-paper'),(paper,index)=>{
    const spec=sideReveals[index],id='side-reveal-'+index;
    const area=add(svg.querySelector('defs'),'mask',{id,maskUnits:'userSpaceOnUse',x:0,y:0,width:1086,height:362});
    add(area,'rect',{width:1086,height:362,fill:'white'});
    const opening=add(area,'circle',{cx:spec.origin[0],cy:spec.origin[1],r:0,fill:'url(#paper-edge)'});
    path(area,spec.path,'white',12);
    const ink=trace(path(area,spec.path,'black',15));
    paper.setAttribute('mask','url(#'+id+')');
    return {paper,opening,ink,radius:spec.radius};
  });
  const accent=bead('#c18b3a',2.2);
  const duration=7600 / 1.5, period=10000;
  const preference=matchMedia('(prefers-reduced-motion: reduce)');
  let elapsed=alreadyComplete||preference.matches?duration:0;
  let running=!preference.matches, previous=null,request=0, completed=elapsed>=duration;
  function render() {
    const opening=clamp(elapsed/duration);
    for(const c of crest)draw(c.stroke,ease((opening-c.start)/(c.end-c.start)));
    const beat=opening*5;
    words.forEach((word,i)=>{word.style.opacity=1-ease((beat-i)/.82)});
    const i=Math.min(4,Math.floor(beat)),p=clamp(beat-i);
    const [x,end]=logoBeats[i].letter;
    const width=end-x, sweep=design==='lettering';
    clip.setAttribute('x',x);clip.setAttribute('y',180);clip.setAttribute('height',89);
    clip.setAttribute('width',sweep?width*ease(p/.65):width);
    const pulse=Math.sin(Math.PI*p)**2;
    gold.style.opacity=opening===1?0:Math.min(1,pulse*1.55);
    const [startWord,endWord]=logoBeats[i].word;
    move(accent,{x:startWord+6+(endWord-startWord-10)*ease(p),y:303},
      design==='compass'&&opening<1?pulse:0);
    sides.forEach(({paper,opening:aperture,ink,radius},index)=>{
      let fraction,alpha=1;
      if(!completed) {
        fraction=clamp((opening-index*.06)/(index?.90:.86));
      } else {
        // Each turn begins with a finished line, holds, fades, then redraws.
        const phase=(Math.max(0,elapsed-duration-index*period*.5)/period)%1;
        if(phase<.10)fraction=1;
        else if(phase<.25){fraction=1;alpha=1-ease((phase-.10)/.15)}
        else if(phase<.64)fraction=clamp((phase-.25)/.39);
        else fraction=1;
        if(preference.matches&&!running){fraction=1;alpha=1}
      }
      // A fully revealed side is the untouched source image, including every fine guide.
      paper.style.opacity=fraction===1?1-alpha:1;
      const reveal=fraction===1?0:ease(fraction);
      aperture.setAttribute('r',radius*reveal);
      draw(ink,reveal);
    });
  }
  function controls(){
    button.textContent=running?'Pause':'Play';
    replay.hidden=!completed;
  }
  function tick(now){
    if(previous!==null)elapsed+=now-previous;
    previous=now;
    if(!completed&&elapsed>=duration){
      completed=true;onComplete();
      if(preference.matches)running=false;
      controls();
    }
    render();
    if(running)request=requestAnimationFrame(tick);
  }
  function sync(){
    cancelAnimationFrame(request);previous=null;controls();
    if(running&&!document.hidden)request=requestAnimationFrame(tick);
  }
  function reduce(){
    if(preference.matches){elapsed=duration;completed=true;running=false;onComplete();render();sync()}
  }
  button.hidden=false;button.onclick=()=>{running=!running;sync()};
  replay.onclick=()=>{elapsed=0;completed=false;running=true;render();sync()};
  preference.addEventListener('change',reduce);document.addEventListener('visibilitychange',sync);
  render();sync();
  return ()=>{
    cancelAnimationFrame(request);preference.removeEventListener('change',reduce);
    document.removeEventListener('visibilitychange',sync);button.onclick=null;replay.onclick=null;
    replay.hidden=true;svg.remove();
  };
}
