/* Native lesson rendering shared by the board viewer and student booklets. */
(function(root){
'use strict';
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function geometry(s){const b=s.box,w=b.w,h=b.h,l=s.line||{},fill=s.fill||'transparent',stroke=l.color||'transparent';let body='',attrs=`fill="${fill}" stroke="${stroke}" stroke-width="${l.width||1}"${l.dash&&l.dash!=='solid'?' stroke-dasharray="'+(l.dash.toLowerCase().includes('dot')?'1 3':'5 3')+'"':''}`;
 const arrow=`<defs><marker id="arrow-${s.id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="${stroke}"/></marker></defs>`;
 if(s.geometry==='line'||s.geometry==='straightConnector1')body=arrow+`<line x1="0" y1="0" x2="${w}" y2="${h}" ${attrs}${l.head&&l.head!=='none'?` marker-start="url(#arrow-${s.id})"`:''}${l.tail&&l.tail!=='none'?` marker-end="url(#arrow-${s.id})"`:''}/>`;
 else if(s.geometry==='ellipse')body=`<ellipse cx="${w/2}" cy="${h/2}" rx="${w/2}" ry="${h/2}" ${attrs}/>`;
 else if(s.geometry==='rtTriangle')body=`<path d="M0 0 L0 ${h} L${w} ${h}Z" ${attrs}/>`;
 else if(s.geometry==='rightArrow')body=`<path d="M0 ${h*.25} H${w*.65} V0 L${w} ${h*.5} L${w*.65} ${h} V${h*.75} H0Z" ${attrs}/>`;
 else if(s.geometry==='downArrow')body=`<path d="M${w*.25} 0 H${w*.75} V${h*.65} H${w} L${w/2} ${h} L0 ${h*.65} H${w*.25}Z" ${attrs}/>`;
 else if(s.geometry==='rightBrace'||s.geometry==='leftBrace'){const x=s.geometry==='rightBrace'?0:w,k=s.geometry==='rightBrace'?1:-1;body=`<path d="M${x} 0 Q${x+k*w*.5} 0 ${x+k*w*.5} ${h*.15} V${h*.35} Q${x+k*w*.5} ${h*.5} ${x+k*w} ${h*.5} Q${x+k*w*.5} ${h*.5} ${x+k*w*.5} ${h*.65} V${h*.85} Q${x+k*w*.5} ${h} ${x} ${h}" fill="none" stroke="${stroke}" stroke-width="${l.width||1}"/>`;}
 else if(s.customSvg)body=s.customSvg;
 else body=`<rect x="0" y="0" width="${w}" height="${h}" ${attrs}/>`;
 return `<svg class="lesson-drawing" xmlns="http://www.w3.org/2000/svg" width="${Math.max(w,1)}" height="${Math.max(h,1)}" viewBox="0 0 ${Math.max(w,1)} ${Math.max(h,1)}" aria-hidden="true">${body}</svg>`;
}
function imageContent(tex,o){
 tex=String(tex).replace(/\\hfill\s*/g,' ');

 if(tex.includes('\\multicolumn')||tex.includes('\\cline')){
  const match=tex.match(/^\\begin\{array\}\{([^{}]*)\}([\s\S]*)\\end\{array\}$/);
  if(match){const specification=match[1],body=match[2],columns=specification.replace(/[^lcr]/g,'').length;let rows=[];
   for(let row of body.split('\\\\')){let rules=[];row=row.replace(/\\cline\{(\d+)-(\d+)\}/g,(_,a,b)=>{rules.push([Number(a),Number(b)]);return '';});let col=1,cells=[];
    for(const cell of row.split('&')){const m=cell.match(/^\\multicolumn(?:\{(\d+)\}|(\d+))(?:\{([lcr])\}|([lcr]))\{([\s\S]*)\}$/),span=m?Number(m[1]||m[2]):1,value=m?m[5]:cell;const top=rules.some(([a,b])=>col>=a&&col<=b);cells.push(`<td colspan="${span}" style="padding:1px 5px;text-align:right;${specification.includes('|')&&col===1?'border-right:1px solid currentColor;':''}${top?'border-top:1px solid currentColor;':''}"><span data-math="${esc(value)}">${o.math?o.math(value):''}</span></td>`);col+=span;}
    rows.push('<tr>'+cells.join('')+'</tr>');}
   return '<table class="lesson-tex-table" style="border-collapse:collapse;border-spacing:0">'+rows.join('')+'</table>';
  }
 }


 function words(value){return (value.match(/[A-Za-z]{3,}/g)||[]).length;}
 function plain(value){return esc(value).replace(/\\qquad\b\s*/g,'&emsp;&emsp;').replace(/\\quad\b\s*/g,'&emsp;').replace(/\\par\s*/g,'<br>').replace(/\\([%&#_$])/g,'$1').replace(/~+/g,' ').replace(/\n/g,'<br>');}
 function math(value,display=false){const aligned=value.match(/^\\begin\{aligned\}([\s\S]*)\\end\{aligned\}$/);if(aligned&&!/\\(?:phantom|frac|dfrac|sqrt|left|begin)\{[^}]*\\text/.test(aligned[1])&&!value.includes('\\phantom')&&/\\text\{[^}]{25}/.test(value))return '<div class="lesson-flow-equations">'+aligned[1].split('\\\\').map(row=>'<div style="margin-bottom:.2em">'+render(row.replace(/&/g,' '))+'</div>').join('')+'</div>';if(value.includes('\\multicolumn')||value.includes('\\cline'))return imageContent(value,o);return `<${display?'div':'span'} class="${display?'lesson-image-block':'lesson-image-inline'}" data-math="${esc(value)}">${o.math?o.math(value):''}</${display?'div':'span'}>`;}
 function render(value,prose=false){let out='',last=0,i=0,found=false;
 const flush=end=>{const v=value.slice(last,end);if(!v.trim()){out+=v.includes('\n')?v.replace(/[^\n]/g,'').replace(/\n/g,'<br>'):(v?' ':'');return;}out+=(prose||/\\par|[“”]/.test(v)||(!/\\(?!quad\b|qquad\b|par\b)[A-Za-z]|[=^_]/.test(v))||(words(v)>8&&!/\\(?!quad|qquad|par)[A-Za-z]/.test(v)))?plain(v):math(v);};
 while(i<value.length){if(value[i]==='\\'&&value[i-1]!=='\\'){
  const t=value.slice(i).match(/^\\(textbf|textit|emph|text)\{/);
  if(t){let j=i+t[0].length,d=1;for(;j<value.length&&d;j++){if(value[j]==='{'&&value[j-1]!=='\\')d++;if(value[j]==='}'&&value[j-1]!=='\\')d--;}if(d===0){const part=value.slice(i+t[0].length,j-1),newPart=t[1]==='textbf'&&/^[a-z][).]?$/.test(part)&&i>0&&/\\quad\s*$/.test(value.slice(last,i));flush(i);if(newPart)out+='<br>';const tag=t[1]==='textbf'?'strong':['textit','emph'].includes(t[1])?'em':'span';out+=`<${tag}>`+render(value.slice(i+t[0].length,j-1),true)+`</${tag}>`;last=j;i=j;found=true;continue;}}
  const env=value.slice(i).match(/^\\begin\{([^{}]+)\}/);
  if(env){const end='\\end{'+env[1]+'}',j=value.indexOf(end,i+env[0].length);if(j>=0){flush(i);out+=math(value.slice(i,j+end.length),true);last=j+end.length;i=last;found=true;continue;}}
  if(value[i+1]==='('||value[i+1]==='['){const close=value[i+1]==='('?String.raw`\)`:String.raw`\]`,j=value.indexOf(close,i+2);if(j>=0){flush(i);const display=value[i+1]==='[',punct=!display?(value.slice(j+2).match(/^[.,;:!?]+/)||[''])[0]:'';const rendered=math(value.slice(i+2,j),display);out+=punct?'<span class="lesson-math-punctuation" style="white-space:nowrap">'+rendered+esc(punct)+'</span>':rendered;last=j+2+punct.length;i=last;found=true;continue;}}
 }
 if(value[i]==='$'&&value[i-1]!=='\\'){const delim=value[i+1]==='$'?'$$':'$',j=value.indexOf(delim,i+delim.length);if(j>=0){flush(i);const display=delim==='$$',punct=!display?(value.slice(j+delim.length).match(/^[.,;:!?]+/)||[''])[0]:'';const rendered=math(value.slice(i+delim.length,j),display);out+=punct?'<span class="lesson-math-punctuation" style="white-space:nowrap">'+rendered+esc(punct)+'</span>':rendered;last=j+delim.length+punct.length;i=last;found=true;continue;}}
 i++;}
 if(!found&&!prose){if(!/\\[A-Za-z]|[=^_]/.test(value)||(words(value)>8&&!/\\(?!quad|qquad|par)[A-Za-z]/.test(value)))return plain(value);return math(value);}
 flush(value.length);return out;
 }
 return '<span class="lesson-image-prose">'+tex.split(/\\par\b/).map(part=>{
 const m=part.match(/^\s*(?:\\textbf\{(\d+[a-z]?|[a-z](?:\([ivx]+\))?|[ivx]+)[.)]?\}|(\d+[a-z]?|[a-z](?:\([ivx]+\))?|[ivx]+)[.)])\s+/);
 if(m)return '<span class="lesson-subpart" style="display:block;position:relative;margin-left:0;padding-left:2em"><span style="position:absolute;left:0">'+esc(m[1]||m[2])+'.</span>'+render(part.slice(m[0].length))+'</span>';
 return '<span style="display:block;'+(/^\s*\\(?:qquad|quad)/.test(part)?'margin-left:2em;':'')+'">'+render(part.replace(/^\s*\\(?:qquad|quad)\s*/,''))+'</span>';
 }).join('').replace(/<\/span>([.,;:])/g,'</span>&#8288;$1')+'</span>';
}

function shape(s,o){if(o.print&&s.screenOnly)return '';const b=s.box;let transform=`translate(${b.x}px,${b.y}px)`;if(b.rotation)transform+=` rotate(${b.rotation}deg)`;if(b.flipH||b.flipV)transform+=` scale(${b.flipH?-1:1},${b.flipV?-1:1})`;let inner='';
 if(s.kind==='grpSp'){const sx=b.w/(b.childW||b.w||1),sy=b.h/(b.childH||b.h||1);inner=`<div style="position:absolute;transform-origin:0 0;transform:scale(${sx},${sy}) translate(${-b.childX}px,${-b.childY}px)">${s.children.map(x=>shape(x,o)).join('')}</div>`;}
 else {
  inner=geometry(s);
  if(s.asset){const c=s.crop||{},cw=1-(c.l||0)-(c.r||0),ch=1-(c.t||0)-(c.b||0);inner+=`<div class="lesson-picture-crop" style="overflow:hidden;position:absolute;inset:0"><img draggable="false" alt="Original mathematical diagram or question" src="${o.assetBase||''}${esc(s.asset)}${o.assetRevision?(s.asset.includes('?')?'&':'?')+'build='+encodeURIComponent(o.assetRevision):''}" style="position:absolute;width:${100/cw}%;height:${100/ch}%;max-width:none;left:${-100*(c.l||0)/cw}%;top:${-100*(c.t||0)/ch}%;"/></div>`;}
  if(s.transcription){inner=geometry(s)+`<div class="lesson-image-tex" style="position:absolute;inset:0;font-size:${s.transcription.fontSize||20}px;line-height:1.35;color:${s.transcription.color||'#151515'};${s.transcription.center?'display:flex;align-items:center;justify-content:center;text-align:center;':''}">${imageContent(o.print&&s.transcription.printTex?s.transcription.printTex:s.transcription.tex,o)}</div>`;}
  if(s.textRegions&&s.assetSize){const [iw,ih]=s.assetSize,c=s.crop||{},cw=1-(c.l||0)-(c.r||0),ch=1-(c.t||0)-(c.b||0);for(const r of s.textRegions){const [x,y,w,h]=r.box;inner+=`<div class="lesson-image-tex" style="position:absolute;background:white;left:${(x/iw-(c.l||0))/cw*b.w}px;top:${(y/ih-(c.t||0))/ch*b.h}px;width:${w/iw/cw*b.w}px;height:${h/ih/ch*b.h}px;font-size:20px;line-height:1.15;overflow:hidden">${imageContent(r.tex,o)}</div>`;}}
  if(s.text){const t=s.text,[left,top,right,bottom]=t.insets;inner+=`<div class="lesson-text" style="position:absolute;left:${left}px;top:${top}px;right:${right}px;bottom:${bottom}px;display:flex;flex-direction:column;justify-content:${t.anchor==='ctr'?'center':t.anchor==='b'?'flex-end':'flex-start'};white-space:${t.wrap?'normal':'nowrap'};">`+t.paragraphs.map((p,index)=>`<div class="lesson-paragraph" data-paragraph="${index}" ${p.webStage?`data-stage="${p.webStage}"`:""} style="flex-shrink:0;white-space:${(p.parts.some(r=>/\t| {5}/.test(r.text||''))||p.parts.every(r=>r.type==='math'||!r.text?.trim()))?'nowrap':'normal'};margin:0;min-height:${p.fontSize*1.3}px;font-size:${p.fontSize}px;line-height:1.3;text-align:${{l:'left',ctr:'center',r:'right',just:'justify'}[p.align]||'left'};color:${s.cover?'white':p.color||'#000'};padding-left:${p.marginLeft||0}px;text-indent:${p.indent||0}px">${p.bullet?esc(p.bullet)+' ':''}${p.parts.map(r=>r.type==='math'?`<span style="font-size:${r.fontSize||p.fontSize}px" data-math="${esc(r.tex)}">${o.math?o.math(r.tex,p.color||'#000000'):''}</span>`:r.glyph?`<svg xmlns="http://www.w3.org/2000/svg" style="vertical-align:-.15em" width="${r.fontSize*r.glyph.width/r.glyph.em}px" height="${r.fontSize*r.glyph.height/r.glyph.em}px" viewBox="0 0 ${r.glyph.width} ${r.glyph.height}" fill="${r.color||p.color||'#000000'}">${r.glyph.paths}</svg>`:`<span style="white-space:inherit;font-size:${r.fontSize||p.fontSize}px;${r.fontFamily&&!r.fontFamily.startsWith('+')?'font-family:'+esc(r.fontFamily)+',Arial;':''}${r.bold?'font-weight:700;':''}${r.italic?'font-style:italic;':''}${r.color?'color:'+r.color+';':''}${r.baseline?'vertical-align:'+(r.baseline/1000)+'%;':''}">${esc((r.text||'').replace('‹#›',String(o.sourceSlide||''))).replace(/ {2,}/g,m=>'<span style="display:inline-block;width:'+m.length*.26+'em"></span>').replace(/\t/g,'<span style="display:inline-block;width:3em"></span>').replace(/\n/g,'<br>')}</span>`).join('')}</div>`).join('')+'</div>';}
 }
 if(s.link&&!s.cover&&!o.print){try{const u=new URL(s.link,'https://fmq.invalid/');if(['https:','http:'].includes(u.protocol))inner=`<a data-resource-link href="${esc(s.link)}" target="_blank" rel="noopener" aria-label="${esc(s.linkLabel||'Open resource')}" style="position:absolute;inset:0;display:block;color:#1760a6;text-decoration:underline">${inner}</a>`;}catch{}}
 if(o.textFits?.[s.id])inner=inner.replace('class="lesson-text" style="','class="lesson-text" style="transform-origin:left top;transform:'+o.textFits[s.id]+';');
 let fitIndex=0;if(o.fitFonts?.[s.id])inner=inner.replace(/(class="lesson-image-tex" style="[^"]*?font-size:)[0-9.]+px/g,(all,prefix)=>prefix+(o.fitFonts[s.id][fitIndex++]||20)+'px');
 return `<div class="lesson-shape${s.cover?' lesson-answer-cover':''}${s.answerFor?' lesson-owned-answer':''}" data-shape="${esc(s.id)}" ${s.equationQuestion?'data-equation-question="true"':''} ${s.answerFor?`data-answer-for="${esc(Array.isArray(s.answerFor)?s.answerFor.join(' '):s.answerFor)}"`:""} ${s.theoryReveal?'data-supplied-theory="true"':''} ${s.webStage?`data-stage="${s.webStage}"`:""} ${s.cover?'role="button" tabindex="0" aria-label="Reveal this answer" aria-expanded="false"':''} style="position:absolute;left:0;top:0;width:${b.w}px;height:${b.h}px;transform-origin:center;transform:${transform};${s.answerClips?`clip-path:path('${s.answerClips.map(r=>`M${r.x} ${r.y}h${r.w}v${r.h}h${-r.w}Z`).join(" ")}');`:s.answerFor?(s.kind==='cxnSp'||s.geometry==='line'||s.geometry==='straightConnector1'?"overflow:visible;":"overflow:hidden;"):""}">${inner}</div>`;
}
function render(slide,deck,options={}){return `<div class="lesson-canvas${options.paper?' lesson-paper':''}" style="width:${deck.width}px;height:${slide.contentHeight||deck.height}px;position:relative;background:white;overflow:hidden" data-slide="${slide.id}">${slide.shapes.map(s=>shape(s,{...options,sourceSlide:slide.sourceSlide})).join('')}</div>`;}
const api={render,shape,geometry,imageContent,escape:esc};if(typeof module!=='undefined')module.exports=api;root.FMQ_SLIDE_RENDERER=api;
})(typeof window==='undefined'?globalThis:window);
