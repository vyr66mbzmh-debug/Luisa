/* Chapter 14 teaching activities. The booklet export uses these same prompts and final states. */
window.LuisaChapter14 = (() => {
  const pages = new Set([4,5,8,16,17,18,21,22,27,28,31,32,33,34,46,47,48,49]);
  const {plot,colours} = LuisaChapterGraphs;
  const math = tex => katex.renderToString(tex,{throwOnError:true,trust:false,output:'htmlAndMathml'});
  const eq = tex => '<div class="equation">'+math(tex)+'</div>';
  const escape = value => value.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  function prose(value) {
    return value.split(/(\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\))/).map(part=>{
      if(part.startsWith('\\['))return eq(part.slice(2,-2));
      if(part.startsWith('\\('))return math(part.slice(2,-2));
      return escape(part).replace(/\n/g,'<br>');
    }).join('');
  }
  function mount(container,slide,changed) {
    if(slide.singlePageExercise || slide.chapter!==14 || !pages.has(slide.sourceSlide))return null;
    const n=slide.sourceSlide, shapes=slide.shapes;
    const activityImage='resources/pure-year-1/native/'+(slide.activityImage||'');
    const root=document.createElement('section');root.className='ch14';container.replaceChildren(root);
    const copy=id=>{
      const shape=shapes.find(s=>s.id==='native-'+id);
      return prose(shape.transcription.tex.slice(6,-1));
    };
    const steps=[];
    let proofStarted=false;
    function action(id,run) {
      const s={id,done:false,run};steps.push(s);return s;
    }
    function perform(id) {
      const s=steps.find(a=>a.id===id);
      if(!s || s.done)return;
      s.done=true;s.run();changed();
    }
    const q=selector=>root.querySelector(selector);
    let serial=0;
    function cover(contents,label='',after=()=>{}) {
      const id='r'+(++serial);
      action(id,()=>{const slot=q('[data-slot="'+id+'"]');slot.classList.add('open');
        const control=slot.querySelector('button');
        control.tabIndex=-1;
        if(slot.closest('td'))control.setAttribute('aria-label',slot.querySelector('.working').textContent);
        after();});
      return `<div class="slot" data-slot="${id}"><div class="working">${contents}</div><button type="button" class="cover" data-action="${id}" aria-label="${label||'Reveal answer '+serial}">${label}</button></div>`;
    }
    function stage(id,html) {
      action(id,()=>{const e=q('#'+id);e.classList.remove('ghost');e.classList.add('stage');});
      return '<div class="ghost" id="'+id+'">'+html+'</div>';
    }
    const values = arr=>arr.map(v=>'<td>'+v+'</td>').join('');
    const fraction = v=>v===.25?math('\\tfrac14'):v===.5?math('\\tfrac12'):math(String(v));
    const note = s=>'<p>'+s+'</p>';
    const button=(id,label)=>'<button type="button" class="choice" data-action="'+id+'">'+label+'</button>';
    function pointTable(logarithmic) {
      const xs=logarithmic?[.25,.5,1,2,4,8]:[-2,-1,0,1,2,3,4];
      const ys=xs.map(x=>logarithmic?Math.log2(x):2**x),seen=new Set();
      const cfg=logarithmic?{x:[-.5,9],y:[-3,4],ticksX:[0,2,4,6,8],ticksY:[-2,-1,0,1,2,3]}:
        {x:[-3,4.6],y:[-1,19],ticksX:[-2,-1,0,1,2,3,4],ticksY:[0,4,8,12,16]};
      const graph=last=>{
        const curves=seen.size===xs.length?[{fn:logarithmic?Math.log2:x=>2**x,min:logarithmic?.03:cfg.x[0],draw:true}]:[];
        q('.graph').innerHTML=plot({...cfg,label:slide.title,curves,points:[...seen].map(i=>[xs[i],ys[i],colours[0],i===last])});
        if(curves.length)q('.curve').style.animationDelay='.24s';
      };
      root.innerHTML=eq(logarithmic?'y=\\log_2 x':'y=2^x')+'<table><tr><th>x</th>'+values(xs.map(fraction))+'</tr><tr><th>y</th>'+
        values(ys.map((y,i)=>cover(fraction(y),'',()=>{seen.add(i);graph(i);})))+'</tr></table><div class="graph"></div>'+note(copy(4));
      graph(-1);
    }
    function compare() {
      const specs=[[['1.5^x',x=>1.5**x],['2^x',x=>2**x],['3^x',x=>3**x]],[['2^x',x=>2**x],['2^{-x}',x=>2**(-x)]]];
      function draw(j) {
        const curves=specs[j].flatMap(([,fn],i)=>q('[data-action="curve'+j+i+'"]').getAttribute('aria-pressed')==='true'?[{fn,colour:colours[i],dash:[null,"9 4","2 4"][i]}]:[]);
        q('#graph'+j).innerHTML=plot({x:[-3,3],y:[-1,12],ticksX:[-3,-2,-1,0,1,2,3],ticksY:[0,3,6,9,12],label:'Exponential comparison '+(j+1),curves});
      }
      const panels=specs.map((group,j)=>{
        const controls=group.map(([label],i)=>{
          const id='curve'+j+i;action(id,()=>{q('[data-action="'+id+'"]').setAttribute('aria-pressed','true');draw(j);});
          return '<button type="button" class="choice" style="color:'+colours[i]+'" aria-pressed="false" data-action="'+id+'">'+math(label)+'</button>';
        }).join('');
        const legend=group.map(([label],i)=>'<span><b style="color:'+colours[i]+'">'+['━','┄','···'][i]+'</b> '+math('y='+label)+'</span>').join('　');
        return '<div class="stack"><h2>'+copy(j?4:1)+'</h2><div class="controls">'+controls+'</div><div id="graph'+j+'"></div><div class="print-only">'+legend+'</div>'+ (j?cover(copy(5),'Relationship'):note(copy(2)))+'</div>';
      });root.innerHTML='<div class="cols">'+panels.join('')+'</div>';draw(0);draw(1);
    }
    function specialBase() {
      const rows=[['1','0'],['1.5','0.41(1.5^x)'],['2','0.69(2^x)'],['2.5','0.92(2.5^x)'],['3','1.10(3^x)'],['3.5','1.25(3.5^x)']];
      const url='https://www.geogebra.org/material/iframe/id/bajx8km2/width/1780/height/1410/sdz/true/smb/false/stb/false/sfsb/true';
      const graphs=slide.gradientGraphs;
      const graphPath=graph=>'resources/pure-year-1/native/'+graph.asset;
      const graphLabel=graph=>'Exponential function and its derivative for base '+graph.base;
      const initial=graphs.findIndex(graph=>graph.base==='2');
      const diagram='<div class="gradient-activity"><img class="gradient-graph" src="'+graphPath(graphs[initial])+'" alt="'+graphLabel(graphs[initial])+'">'+
        '<div class="gradient-key"><span>'+math('f(x)=a^x')+'</span><span>'+math("f\\prime(x)=a^x\\ln a")+'</span></div>'+
        '<label class="base-selector">Base '+math('a')+' <input type="range" min="0" max="'+(graphs.length-1)+'" value="'+initial+'" step="1"><output>2</output></label></div>';
      root.classList.add('special-base');
      const diagramLink='<a class="frame-link" href="https://www.geogebra.org/classic/bajx8km2" target="_blank" rel="noopener noreferrer">See it in <img src="assets/luisa/geogebra-gold.png" width="29" height="29" alt=""> GeoGebra</a>';
      root.innerHTML=note(copy(1))+'<div class="cols compact"><div class="stack"><table><tr><th>'+math('y')+'</th><th>'+math('\\mathrm dy/\\mathrm dx')+' (approx.)</th></tr>'+
        rows.map(([a,r])=>'<tr>'+values([math(a+'^x'),math(r)])+'</tr>').join('')+'</table>'+note(copy(3))+cover(copy(4),'Special base')+'</div>'+
        '<div class="stack">'+diagram+'<details class="original-gradient"><summary>Interactive GeoGebra diagram</summary></details>'+diagramLink+'</div></div>';
      const select=q('.base-selector input'), image=q('.gradient-graph');
      function updateGraph() {
        const graph=graphs[Number(select.value)];
        image.src=graphPath(graph);image.alt=graphLabel(graph);
        q('.base-selector output').textContent=graph.base;
        select.setAttribute('aria-valuetext',graph.base);
      }
      updateGraph();select.addEventListener('input',updateGraph);
      const original=q('.original-gradient');
      original.addEventListener('toggle',()=>{
        if (!original.open) return;
        if (!original.querySelector('iframe')) {
          const frame=document.createElement('iframe');
          frame.title='GeoGebra: gradient of an exponential';frame.src=url;frame.allowFullscreen=true;
          original.append(frame);
        }
      });
    }
    function balance(){
      root.innerHTML='<h2>'+copy(1)+'</h2>'+note(copy(2))+copy(3)+'<table><tr><th>'+math('n')+'</th>'+values(['1','2','12','365','10000'])+
        '</tr><tr><th>Balance</th>'+values(['2','2.25','2.6130','2.7146','2.7181'].map(y=>cover(y)))+'</tr></table>'+cover(copy(5),'Formal definition of the Euler number');
    }
    function conversion(){
      root.classList.add('conversion');
      const colour=(name,tex)=>'\\textcolor{'+({base:'#235c87',power:'#96393a',result:'#22684f'})[name]+'}{'+tex+'}';
      const expForm=colour('base','2')+'^{'+colour('power','3')+'}='+colour('result','8');
      const logForm='\\log_{'+colour('base','2')+'}'+colour('result','8')+'='+colour('power','3');
      root.innerHTML='<h2>Which power of 2 gives 8?</h2>'+eq('2^{\\square}=8')+
        '<div class="conversion-sequence">'+stage('power-form','<h3>Exponential form</h3>'+eq(expForm))+
        stage('log-form','<h3>Logarithmic form</h3>'+eq(logForm))+'</div>'+
        stage('correspondence','<p>Both statements use base '+math('2')+'. The power '+math('3')+' in the exponential is the output of the logarithm. Its input is '+math('8')+'.</p>')+
        stage('general','<h3>For a real logarithm</h3>'+eq('a^x=n\\quad\\Longleftrightarrow\\quad\\log_a n=x')+
          note(math('a>0,\\quad a\\ne1,\\quad n>0,\\quad x\\in\\mathbb R')+'. Read '+math('\\log_a n')+' as “log base '+math('a')+' of '+math('n')+'”. Raising '+math('a')+' to a power and taking log base '+math('a')+' are inverse operations.'));
      const correspondence=steps.find(s=>s.id==='log-form'),show=correspondence.run;
      correspondence.run=()=>{
        show();
        // KaTeX sets colour through a style attribute and may serialise it as hex or RGB.
        const redTerm=panel=>[...panel.querySelectorAll('.katex-html span')].find(el=>el.textContent==='3' && getComputedStyle(el).color==='rgb(150, 57, 58)');
        const power=redTerm(q('#power-form')),output=redTerm(q('#log-form'));
        if(!power || !output || matchMedia('(prefers-reduced-motion: reduce)').matches)return;
        const a=power.getBoundingClientRect(),b=output.getBoundingClientRect(),scale=root.getBoundingClientRect().width/root.offsetWidth;
        const tracer=document.createElement('span');tracer.className='power-tracer';tracer.innerHTML=math('3');root.append(tracer);
        const frame=root.getBoundingClientRect();tracer.style.left=(a.x-frame.x)/scale+'px';tracer.style.top=(a.y-frame.y)/scale+'px';
        const motion=tracer.animate([{transform:'translate(0,0)',opacity:1},{transform:'translate('+(b.x-a.x)/scale+'px,'+(b.y-a.y)/scale+'px)',opacity:.3}],{duration:800,easing:'ease-in-out'});
        motion.onfinish=()=>tracer.remove();
      };
      root.dataset.printSequence='conversion';
    }
    function inverses(){
      const pairs=[['3x','x/3'],['x+3','x-3'],['x^2\\quad(x\\ge0)','\\sqrt{x}'],['x^5','\\sqrt[5]{x}'],['3^x','\\log_3 x']];
      root.innerHTML=note(copy(1))+copy(2)+note(copy(3))+'<table class="vertical-table"><tr><th>Operation</th><th>Inverse operation</th></tr>'+
        pairs.map(([a,b])=>'<tr>'+values([math(a),cover(math(b))])+'</tr>').join('')+'</table>';
    }
    function logs(){
      const laws=[['\\log_a(uv)','\\log_a u+\\log_a v'],['\\log_a(u/v)','\\log_a u-\\log_a v'],['\\log_a(u^k)','k\\log_a u'],['\\log_a u','\\dfrac{\\log_b u}{\\log_b a}']];
      const derivation=[
        math('2^3=8')+'　The missing power is 3.',
        math('\\log_{10}8=\\log_{10}(2^3)=3\\log_{10}2'),
        math('\\dfrac{\\log_{10}8}{\\log_{10}2}=3=\\log_2 8'),
        math('a^x=u\\;\\Longrightarrow\\;\\log_b u=x\\log_b a')+'<br>'+math('\\log_a u=x=\\dfrac{\\log_b u}{\\log_b a}')
      ];
      root.classList.add('log-laws');
      const proof=i=>{proofStarted=true;q('.proof').innerHTML=derivation.slice(0,i+1).map(line=>'<div>'+line+'</div>').join('');};
      root.innerHTML=note('For '+math('u,v>0')+' and bases '+math('a,b>0')+' with '+math('a\\ne1')+' and '+math('b\\ne1')+'.')+ '<div class="law-derivation"><div class="law-list">'+laws.map(([a,b],i)=>'<div class="law"><span>'+math(a+' =')+'</span>'+cover(math(b),'',()=>{if(i===3)proof(0);})+'</div>').join('')+
        note(copy(8))+'</div><div class="proof" aria-live="polite"></div></div>';
      for(let i=1;i<derivation.length;i++)action('proof'+i,()=>proof(i));
      root.dataset.proof=derivation.map(line=>'<div>'+line+'</div>').join('');
    }
    function paired(){
      const row=(...pairs)=>'<div class="answers">'+pairs.map(([id,label])=>cover(copy(id),label)).join('')+'</div>';
      if(n===17){root.innerHTML=note(copy(1))+row([2,'Initial size'],[3,'Initial rate'])+note(copy(4));return;}
      if(n===18){
        root.classList.add('pesticide');
        root.innerHTML=note(copy(1))+
          '<div class="pesticide-work"><div class="pesticide-parts">'+[[2,3,'a',4,5,'b'],[6,7,'c',8,9,'d']].map(([p,a,l,p2,a2,l2])=>
            '<div class="answers"><p>'+copy(p)+'</p><p>'+copy(p2)+'</p></div>'+row([a,l],[a2,l2])).join('')+'</div>'+
          '<div class="pesticide-graph"><p>e. Sketch the graph of '+math('P')+' against '+math('t')+'.</p>'+
          cover('<img src="resources/pure-year-1/native/assets/ch14-18.svg" data-blank-src="resources/pure-year-1/native/assets/ch14-18-blank.svg" alt="Pesticide density against time">','Graph')+'</div></div>';return;
      }
      if(n===32){
        const given=shapes.find(s=>s.id==='native-1').transcription.tex.slice(6,-1).split('\n');
        const prompts=given.map(line=>{
          const part=line.match(/^\(([ab])\)\s+(.*)$/);
          return part ? '<p class="luisa-lettered-part"><span class="luisa-part-label">('+part[1]+')</span>'+prose(part[2])+'</p>' : note(prose(line));
        }).join('');
        root.innerHTML=prompts+row([2,'Part (a)'],[3,'Part (b)']);return;
      }
      if(n===34){root.innerHTML='<div class="stack compact">'+note(copy(1))+cover(copy(2),'Answer')+'</div><div class="stack compact"><h2>Challenge</h2>'+note(copy(3))+cover(copy(4),'Proof')+'</div>';return;}
      root.innerHTML=note(copy(1))+row([2,n===33?'use law of logs to derive an equation in x..':'1'],[3,n===33?'.. then solve the equation':'2']);
    }
    function doubling(){
      let year=0,logged=false;
      const draw=()=>{
        const times=Array.from({length:year/2+1},(_,i)=>i*2);
        const graph=(log)=>plot({x:[0,12.5],y:log?[0,6.6]:[0,68],ticksX:[0,2,4,6,8,10,12],ticksY:log?[0,2,4,6]:[0,16,32,48,64],xlabel:'Years',ylabel:log?'log₂(count)':'Relative count',label:log?'Logged count':'Relative count',curves:[{fn:x=>log?x/2:2**(x/2),max:year,colour:colours[1]}],points:times.map(t=>[t,log?t/2:2**(t/2),t===year?colours[0]:colours[1]])});
        q('#raw').innerHTML=graph(false);q('#logged').innerHTML=logged?graph(true):'';
        q('#comparison').innerHTML='Year '+year+' · Relative count '+2**(year/2)+(logged?' · Logged count '+year/2:'')+(logged && year>=2?'　·　Count ×2, logged count +1':'');
        q('#year').disabled=year>=12;q('#transform').disabled=logged;
        q('#observation').innerHTML=logged?math('\\log_2(2y)=1+\\log_2 y')+'　Every doubling adds 1. Equal time steps give a straight line.':'What shape would you expect after taking logarithms?';
      };
      root.innerHTML=note(copy(2))+'<div class="cols"><div id="raw"></div><div id="logged"></div></div><p id="comparison"></p><div class="controls"><button id="year" class="choice">+2 years</button><button id="transform" class="choice">Show log₂(count)</button></div><p id="observation"></p>';
      for(let t=2;t<=12;t+=2)action('year'+t,()=>{year=t;draw();});
      action('transform',()=>{logged=true;draw();});
      q('#year').onclick=()=>perform('year'+(year+2));q('#transform').onclick=()=>perform('transform');draw();
    }
    function earthquake(){
      root.innerHTML='<h2>The Richter scale</h2><div class="cols"><div class="stack"><img class="ch-photo" alt="Relative wave amplitude A divided by its magnitude-four value. Each unit increase in magnitude multiplies amplitude by ten." src="'+activityImage+'"></div><div class="stack"><p>At the same recording distance, how much larger is the recorded wave amplitude for magnitude 5 than for magnitude 4?</p><p>Use the magnitude 4 amplitude as one unit.</p><div class="amplitude reference"></div>'+
        stage('magnitude','<p>Magnitude 5 · 10 units</p><div class="amplitude bigger"></div>')+'</div></div>'+
        stage('scale',eq('\\Delta M=\\log_{10}(10/1)=1')+'A tenfold increase in measured amplitude adds one magnitude unit. The vertical axis uses powers of ten. Descriptions such as minor, moderate, strong, major or great refer to the event. How strongly it is felt also depends on where the observer is.');
    }
    function power(){
      const raw={x:[0,4.2],y:[0,140],ticksX:[0,1,2,3,4],ticksY:[0,32,64,96,128],label:'Ordinary axes: cubic',curves:[{fn:x=>2*x**3,colour:colours[1]}],points:[[1,2],[2,16],[4,128]].map((p,i)=>[...p,colours[i]])};
      const log={x:[-.05,.66],y:[0,2.35],ticksX:[0,.3,.6],ticksY:[0,.6,1.2,1.8],xlabel:'log₁₀ x',ylabel:'log₁₀ y',label:'Log–log axes',points:raw.points.map(([x,y,c])=>[Math.log10(x),Math.log10(y),c,true])};
      root.innerHTML=note(copy(1))+'<p>Each time x doubles, what happens to y?</p><div class="cols"><div>'+plot(raw)+'</div>'+
        '<div id="logplot"></div></div><div id="relation" class="proof"></div>';
      action('algebra',()=>q('#relation').innerHTML=math('\\log y=\\log(2x^3)=\\log 2+3\\log x'));
      action('coordinates',()=>{q('#logplot').innerHTML=plot(log);const original=[...q('.cols').querySelectorAll(':scope > div:first-child .dot')];
        const mapped=[...q('#logplot').querySelectorAll('.dot')];
        if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
          mapped.forEach((dot,i)=>{
            const a=original[i].getBoundingClientRect(), b=dot.getBoundingClientRect(), scale=dot.getScreenCTM();
            dot.animate([{transform:`translate(${(a.x-b.x)/scale.a}px,${(a.y-b.y)/scale.d}px)`},{transform:'translate(0,0)'}],{duration:700,easing:'ease-out'});
          });
        }
        q('#relation').innerHTML=math('(x,y)\\longmapsto(\\log x,\\log y)')+'　Follow the same three points onto the logged axes.';});
      action('straight',()=>{q('#logplot').innerHTML=plot({...log,curves:[{fn:x=>3*x+Math.log10(2),colour:colours[1],draw:true}],segments:log.points.slice(1).flatMap(([x,y],i)=>[[log.points[i][0],log.points[i][1],x,log.points[i][1]],[x,log.points[i][1],x,y]])});
        q('#relation').innerHTML=math('m=\\dfrac{\\log 8}{\\log 2}=3,\\qquad Y=3X+\\log 2')+'　The intercept is '+math('\\log 2')+'.';});
    }
    function models(){
      root.classList.add('model-comparison');
      const panels=['power','exponential'].map((key,i)=>{
        const X=i?'x':'\\log x',m=i?'\\log b':'n';
        const axes={x:[-.5,3],y:[-1,4],ticksX:[0,1,2],ticksY:[],xlabel:i?'x':'log x',ylabel:'log y',label:'Schematic transformed axes'};
        const frame=plot({...axes,curves:[{fn:x=>x+.7,colour:colours[i],draw:true}],points:[[0,.7,colours[0]]]});
        const paperGrid='<template class="print-grid">'+plot(axes)+'</template>';
        return '<div class="stack"><h2>'+(i?'Exponential model':'Power model')+'</h2>'+eq(i?'y=ab^x':'y=ax^n')+
          stage(key+'eq',eq(i?'\\log y=\\log a+x\\log b':'\\log y=\\log a+n\\log x')+eq('\\log y=('+m+')('+X+')+\\log a'))+
          stage(key+'axes','<div class="label-transfer" data-blank-graph>'+frame+paperGrid+'</div><p>Gradient '+math(m)+' · Vertical intercept '+math('\\log a')+'</p>')+'</div>';
      });
      root.innerHTML='<h2>Which axes will give a straight line?</h2><div class="cols compact">'+panels.join('')+'</div><p>Compare with '+math('Y=mX+c')+'. Use the same log base throughout. Power model: '+math('a,x>0')+'. Exponential model: '+math('a,b>0')+'.</p>';
    }
    if(n===4 || n===27)pointTable(n===27);
    else if(n===5)compare();
    else if(n===8)specialBase();
    else if(n===16)balance();
    else if(n===21)inverses();
    else if(n===22)conversion();
    else if(n===28)logs();
    else if(n===46)doubling();
    else if(n===47)earthquake();
    else if(n===48)power();
    else if(n===49)models();
    else paired();
    root.addEventListener('click',event=>{const b=event.target.closest('[data-action]');if(b)perform(b.dataset.action);});
    return {next(){const proof=proofStarted && steps.find(s=>!s.done && s.id.startsWith('proof'));
      const next=proof || steps.find(s=>!s.done);if(next)perform(next.id);},get complete(){return steps.every(s=>s.done);},all(){for(const s of steps)perform(s.id);}};
  }
  return {mount};
})();
