// Prepare source controls for both the teaching slide and its print rendering.
(function (root) {
  function cleanLabel(value) {
    const clean = value.trim().replace(/^\?\s*/, '').replace(/^((?:\d+[a-z]?|[a-z](?:\([ivx]+\))?|\([ivx]+\)))\s*\?$/i, '$1');
    return value.includes('?') && /^[A-Z]$/.test(clean) ? clean.toLowerCase() : clean;
  }

  function teachingNames(value) {
    return value.replace(/\bfro\s*[-–—]?\s*(tip|animation)\b/gi, (_, name) => name.toLowerCase() === 'tip' ? 'Tip' : 'Animation');
  }

  function prepareParagraph(paragraph) {
    delete paragraph.webStage;
    // Run boundaries can separate the prefix, hyphen and name in PowerPoint.
    const parts = paragraph.parts;
    for (const part of parts) delete part.fontFamily;
    const line = parts.map(r => r.text ?? '\u0000').join('');
    const starts = [];
    let offset = 0;
    for (const part of parts) {
      starts.push(offset);
      offset += (part.text ?? '\u0000').length;
    }
    for (const match of [...line.matchAll(/\bfro\s*[-–—]?\s*(tip|animation)\b/gi)].reverse()) {
      const start = match.index, end = start + match[0].length;
      for (let i = parts.length - 1; i >= 0; i--) {
        const part = parts[i], pos = starts[i];
        if (!part.text || pos >= end || pos + part.text.length <= start) continue;
        const left = Math.max(0, start-pos), right = Math.min(part.text.length, end-pos);
        part.text = part.text.slice(0,left) + (pos <= start ? teachingNames(match[0]) : '') + part.text.slice(right);
      }
    }
    if (paragraph.bullet || /^\s*(?:\d+[.)]|\([a-zivx]+\)|[a-z]\))\s/i.test(line)) {
      const indent = Math.max(paragraph.marginLeft || 0, (paragraph.fontSize || 22) * 1.4);
      paragraph.marginLeft = indent;
      paragraph.indent = -indent;
    }
  }

  function prepare(slide, deck) {
    const copy = JSON.parse(JSON.stringify(slide));
    copy.shapes = copy.shapes.filter(shape => !copy.headerShapes.includes(shape.id));
    function visit(shape) {
      delete shape.printFallback;
      delete shape.webStage;
      const paras = shape.text?.paragraphs || [];
      paras.forEach(prepareParagraph);
      if (shape.transcription?.tex) shape.transcription.tex = teachingNames(shape.transcription.tex);
      const runs = paras.flatMap(p => p.parts);
      const prompt = paras.map(p => p.parts.map(r => r.text ?? r.tex ?? '').join('')).join(' ').trim();
      const trigger = Object.hasOwn(copy.animation?.triggers || {}, shape.id);
      const caption = prompt || shape.transcription?.tex?.trim() || '';
      const rotation = trigger && /^Rotate through one (degree|radian)$/i.exec(caption);
      const control = rotation || trigger && /^(?:(?:click\s+to(?:\s+start)?|play)\s+)?(?:(?:fro\s*[-–]?\s*)?animation|sketch|plot)$/i.test(caption);
      if (control || shape.cover) {
        const original = deck.sourceCoverLabels ? shape.coverLabel ?? prompt : prompt || shape.coverLabel || '';
        const label = rotation ? 'Animation · '+(rotation[1].toLowerCase()==='degree'?'1°':'1 rad') : control ? (/sketch|plot/i.test(caption) ? 'Sketch' : 'Animation') : cleanLabel(original);
        const maths = !control && runs.some(r => r.type === 'math') && original.replace(/\?|\s/g,'') === prompt.replace(/\?|\s/g,'');
        const size = Math.min(26, Math.max(16, shape.box.h * .62));
        const parts = maths ? runs.filter(r => r.type === 'math' || r.text?.replace(/\?/g,'').trim()).map(r => ({...r, text:r.text?.replace(/\?/g,''),fontSize:size})) : [{type:'text',text:label,fontSize:size}];
        shape.fill = '#d7e9f8';
        shape.line = {color:'#829eb6',width:1};
        shape.text = {insets:[2,0,2,0],anchor:'ctr',wrap:true,paragraphs:[{align:'ctr',fontSize:size,color:'#173b60',parts}]};
        if (control) {
          shape.animationControl = true;
          // The print caption is taken separately from the source shape by the booklet author.
          delete shape.transcription;
        }
      }
      for (const child of shape.children || []) visit(child);
    }
    copy.shapes.forEach(visit);
    return copy;
  }

  function setTitle(element, title) {
    element.replaceChildren();
    for (const fragment of title.split(/(σ²|σ|Σ\s*x²|Σ\s*x|x̄)/g)) {
      const tex = {'σ²':'\\sigma^2','σ':'\\sigma','x̄':'\\bar{x}'}[fragment]
        || (fragment.startsWith('Σ') ? (fragment.endsWith('²') ? '\\sum x^2' : '\\sum x') : '');
      if (!tex) element.append(document.createTextNode(fragment));
      else {
        const math = document.createElement('span');
        root.katex.render(tex, math, {throwOnError:true, trust:false});
        element.append(math);
      }
    }
  }

  const api = {prepare,setTitle};
  if (typeof module !== 'undefined') module.exports = api;
  root.LUISA_CONTROLS = api;
})(typeof window === 'undefined' ? globalThis : window);
