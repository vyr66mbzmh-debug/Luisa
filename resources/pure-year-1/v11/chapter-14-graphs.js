// Graphs share a fixed coordinate frame so matching points can be compared across reveals.
window.LuisaChapterGraphs = (() => {
  const colours = ['#aa2734', '#22649a', '#188065'];
  function plot({x, y, ticksX, ticksY, xlabel = 'x', ylabel = 'y', label, curves = [], points = [], segments = []}) {
    const w = 560, h = 285, left = 55, right = 23, top = 23, bottom = 49;
    const px = v => left + (v-x[0]) / (x[1]-x[0]) * (w-left-right);
    const py = v => h-bottom - (v-y[0]) / (y[1]-y[0]) * (h-top-bottom);
    const line = (x1,y1,x2,y2,cls) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"/>`;
    const axisX = px(Math.max(x[0], Math.min(0, x[1])));
    const axisY = py(Math.max(y[0], Math.min(0, y[1])));
    const grid = ticksX.map(v => line(px(v),top,px(v),h-bottom,'grid')+`<text x="${px(v)}" y="${h-bottom+20}" text-anchor="middle">${v}</text>`).join('') +
      ticksY.map(v => line(left,py(v),w-right,py(v),'grid')+`<text x="${left-7}" y="${py(v)+5}" text-anchor="end">${v}</text>`).join('');
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
      ${grid}${line(left,axisY,w-right,axisY,'axis')}${line(axisX,top,axisX,h-bottom,'axis')}${paths}${guides}${dots}
      <text x="${w-right}" y="${h-4}" text-anchor="end">${xlabel}</text><text x="${left}" y="16">${ylabel}</text></svg>`;
  }
  return {plot, colours};
})();
