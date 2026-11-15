// Three studies for the opening Pure Year 1 overview. Topic text comes from the deck.
window.LuisaOverview = (() => {
  const groups = [
    null,
    [[[0,3],'indices'],[[1,2],'factor'],[[4],'surd']],
    [[[0,1],'quadratic'],[[2,3],'vertex'],[[4,5],'roots']],
    [[[0,1],'intersect'],[[2],'interval'],[[3],'region']],
    [[[0],'cubic'],[[1],'intersect'],[[2],'translate']],
    [[[0],'line'],[[1],'perpendicular'],[[2,3],'triangle']],
    [[[0],'circle'],[[1,2],'tangentCircle'],[[3],'circumcircle']],
    [[[0,1],'division'],[[2],'factor'],[[3],'proof']],
    [[[0],'pascal'],[[1,2],'binomial'],[[3],'estimate']],
    [[[0],'triangle'],[[1],'height'],[[2],'sine']],
    [[[0,1],'unitCircle'],[[2],'sine'],[[3],'trigRoots']],
    [[[0],'vectors'],[[1],'vectorLength'],[[2,3],'displacement']],
    [[[0],'tangent'],[[1],'derivative'],[[2,3],'vertex']],
    [[[0],'antiderivative'],[[1],'area'],[[2,3],'signedArea']],
    [[[0],'exponential'],[[1],'logarithm'],[[2],'fit']]
  ];
  const formulae = {
    indices:'a^m a^n=a^{m+n}',factor:'x^2-1=(x-1)(x+1)',surd:'\\sqrt{12}=2\\sqrt{3}',
    division:'P(x)=(x-a)Q(x)+r',proof:'n(n+1)\\equiv0\\pmod 2',
    pascal:'\\begin{gathered}1\\quad2\\quad1\\\\1\\quad3\\quad3\\quad1\\end{gathered}',
    binomial:'(1+x)^n=\\sum_{r=0}^n {n\\choose r}x^r',estimate:'(1+x)^n\\approx1+nx',
    derivative:'x^n\\longmapsto nx^{n-1}',antiderivative:'2x\\longmapsto x^2+C'
  };
  const math = tex => katex.renderToString(tex,{throwOnError:true,trust:false});
  function illustration(kind) {
    if (formulae[kind]) return '<div class="study-equation">'+math(formulae[kind])+'</div>';
    const vx=x=>110+34*x, vy=y=>76-20*y;
    const pts = a => a.map(([x,y])=>vx(x).toFixed(2)+','+vy(y).toFixed(2)).join(' ');
    const path=(a,attrs='')=>'<polyline points="'+pts(a)+'" '+attrs+'/>';
    const line=(a,b,attrs)=>path([a,b],attrs);
    const dot=(x,y)=>'<circle cx="'+vx(x)+'" cy="'+vy(y)+'" r="3.1" class="study-dot"/>';
    const curve=(f,l=-2.9,h=2.9,attrs='')=>path(Array.from({length:91},(_,i)=>{const x=l+(h-l)*i/90;return[x,f(x)]}),attrs);
    const axes=line([-3,0],[3,0],'class="study-axis"')+line([0,-1.8],[0,3.4],'class="study-axis"');
    const disk='<circle cx="103" cy="58" r="42"/>';
    const arrow=(a,b)=>line(a,b,'marker-end="url(#arrow-'+kind+')"');
    const triangle=path([[-2.3,-.8],[1.9,-.8],[.7,2.65],[-2.3,-.8]]);
    const gold='class="study-alt"';
    let drawing=axes;
    switch(kind) {
      case 'quadratic':case 'vertex':case 'roots':drawing+=curve(x=>.75*x*x-.8,-2.3,2.3);
        drawing+=kind==='vertex'?dot(0,-.8):dot(-Math.sqrt(.8/.75),0)+dot(Math.sqrt(.8/.75),0); break;
      case 'intersect': drawing+=curve(x=>.75*x*x-.9,-2.35,2.35)+curve(x=>.5*x+.35,-2.8,2.8,gold)+dot(-1, -.15)+dot(5/3,71/60);break;
      case 'interval':drawing=line([-3,0],[3,0],'class="study-axis"')+line([-1.7,0],[2,0])+dot(-1.7,0)+dot(2,0);break;
      case 'region':drawing+=path([[-2,0],[2,0],[0,2],[-2,0]],'class="study-fill"')+curve(x=>2-Math.abs(x),-2.6,2.6);break;
      case 'cubic':drawing+=curve(x=>.45*x*x*x-x,-2.35,2.35);break;
      case 'translate':drawing+=curve(x=>.9*x*x-.8,-2.1,2.1)+curve(x=>.9*(x-1)**2-.8,-1.1,2.9,gold);break;
      case 'perpendicular':drawing+=curve(x=>.6*x+.4)+curve(x=>-x/.6+.4,-1.8,1.25,gold);break;
      case 'triangle':drawing=triangle;break;
      case 'height':drawing=triangle+line([.7,-.8],[.7,2.65],gold);break;
      case 'circle':drawing=disk+'<circle cx="103" cy="58" r="3" class="study-dot"/><path d="M103 58h42" class="study-alt"/>';break;
      case 'tangentCircle':drawing=disk+'<path d="M145 5v106 M103 58h42" class="study-alt"/>';break;
      case 'circumcircle':drawing=disk+'<path d="M103 16 L66.63 79 L139.37 79 Z" class="study-alt"/>';break;
      case 'unitCircle':drawing=disk+'<path d="M44 58h118 M103 6v104" class="study-axis"/><path d="M103 58l29.7 -29.7v29.7z" class="study-alt"/>';break;
      case 'sine':case 'trigRoots':drawing+=curve(x=>1.9*Math.sin(1.5*x));if(kind==='trigRoots')drawing+=dot(0,0)+dot(Math.PI/1.5,0)+dot(-Math.PI/1.5,0);break;
      case 'vectors':case 'displacement':drawing+=arrow([-2,-1],[.2,1.6])+arrow([.2,1.6],[2.4,1])+line([-2,-1],[2.4,1],gold);break;
      case 'vectorLength':drawing+=arrow([0,0],[2.4,2.6])+path([[2.4,2.6],[2.4,0],[0,0]],gold);break;
      case 'tangent':drawing+=curve(x=>.7*x*x,-2.15,2.15)+curve(x=>1.4*x-.7,-.65,2.7,gold)+dot(1,.7);break;
      case 'area':case 'signedArea':{
        const f=kind==='area'?x=>.3*x*x+.5:x=>1.25*Math.sin(1.5*x);
        const a=kind==='area'?-1.5:-2,b=2;
        const polygon=[[a,0],...Array.from({length:61},(_,i)=>{const x=a+(b-a)*i/60;return[x,f(x)]}),[b,0]];
        drawing+=path(polygon,'class="study-fill"')+curve(f);break;}
      case 'exponential':drawing+=curve(x=>2**x,-2.9,1.65)+curve(x=>2**(-x),-1.65,2.9,gold);break;
      case 'logarithm':drawing+=curve(Math.log2,.32,2.95)+dot(1,0);break;
      case 'fit':drawing+=curve(x=>.64*x+.7);for(const [x,y] of [[-2,-.35],[-1.2,-.18],[-.25,.61],[.6,.96],[1.5,1.8],[2.5,2.16]])drawing+=dot(x,y);break;
      default:drawing+=curve(x=>.85*x+.45,-2.5,2.9);
    }
    return '<svg viewBox="0 0 220 115" class="study-figure" aria-hidden="true"><defs><marker id="arrow-'+kind+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10" fill="currentColor" stroke="none"/></marker></defs>'+drawing+'</svg>';
  }
  function topics(slide) {
    const plain=s=>(s.transcription?.tex || (s.text?.paragraphs || []).map(p=>p.parts.map(r=>r.text||'').join('')).join(' ')).trim();
    const unwrap=s=>s.trim().replace(/^\\text\{([\s\S]*)\}$/,'$1').trim();
    const heading=s=>unwrap(s).replace(/^\\textbf\{([\s\S]*)\}$/,'$1').replace(/^\d+[:.]\s*/,'').trim();
    const lines=slide.shapes.filter(s=>!slide.headerShapes.includes(s.id)).map(plain);
    if(slide.chapter>=7)return lines.flatMap((line,i)=>i%2?[]:[{h:heading(line),p:unwrap(lines[i+1])}]);
    return lines.map(line=>{const [h,...p]=line.split('\\par');return {h:heading(h),p:p.map(unwrap).join(' ')};});
  }
  function mount(container,slide,title) {
    if(slide.title.trim().toLowerCase()!=='chapter overview' || slide.sourceSlide>3 || !groups[slide.chapter])return null;
    const content=topics(slide), cards=groups[slide.chapter];
    if (slide.chapter===14) content[0].h="Exponential Functions";
    if(!cards.every(([indices])=>indices.every(i=>content[i])))return null;
    const render=tex=>FMQ_SLIDE_RENDERER.imageContent(tex,{math});
    container.innerHTML='<section class="luisa-overview"><h2>'+FMQ_SLIDE_RENDERER.escape(title)+'</h2><div class="study-columns">'+cards.map(([items,kind])=>
      '<article>'+illustration(kind)+items.map(i=>'<h3>'+FMQ_SLIDE_RENDERER.escape(content[i].h)+'</h3>'+(content[i].p?'<div class="study-copy">'+render(content[i].p)+'</div>':'')).join('')+'</article>').join('')+'</div></section>';
    return {complete:true,next(){},all(){}};
  }
  return {mount};
})();
