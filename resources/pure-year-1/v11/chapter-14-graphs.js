// Graphs share a fixed coordinate frame so matching points can be compared across reveals.
window.LuisaChapterGraphs = (() => {
  const colours = ['#aa2734', '#22649a', '#188065'];
  function plot({x, y, ticksX, ticksY, xlabel = 'x', ylabel = 'y', label, curves = [], points = [], segments = []}) {
    const w = 560, h = 285, left = 61, right = 30, top = 32, bottom = 40;
    const px = v => left + (v-x[0]) / (x[1]-x[0]) * (w-left-right);
    const py = v => h-bottom - (v-y[0]) / (y[1]-y[0]) * (h-top-bottom);
    const line = (x1,y1,x2,y2,cls) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"/>`;
    const axisX = px(Math.max(x[0], Math.min(0, x[1])));
    const axisY = py(Math.max(y[0], Math.min(0, y[1])));
    const number = value => String(value).replace('-', '−');
    const grid = ticksX.map(v => line(px(v),top,px(v),h-bottom,'grid')+
      line(px(v),axisY-3,px(v),axisY+3,'tick')+
      `<text x="${px(v)-(v===0?4:0)}" y="${axisY+20}" text-anchor="${v===0?'end':'middle'}">${number(v)}</text>`).join('') +
      ticksY.map(v => line(left,py(v),w-right,py(v),'grid')+
        (v===0?'':line(axisX-3,py(v),axisX+3,py(v),'tick')+
          `<text x="${axisX-7}" y="${py(v)+5}" text-anchor="end">${number(v)}</text>`)).join('');
    // The axis names use upright log and italic variables, including on the animated plots.
    const axisName = str => {
      const names={'x':'<tspan font-style="italic">x</tspan>','y':'<tspan font-style="italic">y</tspan>',
        'log x':'log <tspan font-style="italic">x</tspan>','log y':'log <tspan font-style="italic">y</tspan>',
        'log₁₀ x':'log<tspan dy="3" font-size="11">10</tspan><tspan dy="-3" font-style="italic"> x</tspan>',
        'log₁₀ y':'log<tspan dy="3" font-size="11">10</tspan><tspan dy="-3" font-style="italic"> y</tspan>'};
      return names[str] || str;
    };
    const paths = curves.map(({fn, colour = colours[0], min = x[0], max = x[1], draw = false, dash = null}) => {
      let d = '', visible = false;
      for(let i=0;i<=360;i++){
        const a = min+(max-min)*i/360, b=fn(a);
        if(!Number.isFinite(b)||b<y[0]||b>y[1]) { visible=false; continue; }
        d += (visible?'L':'M')+px(a).toFixed(2)+' '+py(b).toFixed(2)+' ';visible=true;
      }
      return `<path class="curve ${draw?'draw':''}" ${draw?'pathLength="1"':''} ${dash?'stroke-dasharray="'+dash+'"':''} d="${d}" stroke="${colour}"/>`;
    }).join('');
    const dots=points.map(([a,b,colour,enter])=>`<circle class="dot ${enter?'land':''}" cx="${px(a)}" cy="${py(b)}" r="5.8" fill="${colour||colours[0]}"/>`).join('');
    const guides=segments.map(([a,b,c,d])=>line(px(a),py(b),px(c),py(d),'guide')).join('');
    return `<svg class="ch-plot" viewBox="0 0 ${w} ${h}" role="img" aria-label="${label}">
      ${grid}${line(left,axisY,w-right+8,axisY,'axis')}${line(axisX,top-8,axisX,h-bottom,'axis')}
      <path class="axis-arrow" d="M${w-right+1} ${axisY-3.5}l7 3.5 -7 3.5M${axisX-3.5} ${top-1}l3.5 -7 3.5 7"/>
      ${paths}${guides}${dots}
      <text class="axis-name" x="${w-right+11}" y="${axisY-8}" text-anchor="end">${axisName(xlabel)}</text>
      <text class="axis-name" x="${axisX+8}" y="${top-11}">${axisName(ylabel)}</text></svg>`;
  }
  return {plot, colours};
})();
