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

  // PowerPoint arrays also represent matrices and polynomial division. A table
  // with one labelled first column may safely acquire rules around every cell.
  function ruleDataTables(tex) {
    return tex.replace(/\\begin\{array\}\{([lcr|]+)\}([\s\S]*?)\\end\{array\}/g, (original, spec, body) => {
      if (!/^[lcr]\|[lcr]+$/.test(spec) || /\\(?:multicolumn|cline|begin)/.test(body)) return original;
      const rows = body.split('\\\\').map(row => row.replace(/\\hline\s*/g, '').trim()).filter(Boolean);
      if (rows.length < 2 || rows.some(row => !row.split('&')[0].trim())) return original;
      const columns = spec.replace('|','').split('').join('|');
      return '\\begin{array}{|' + columns + '|}\\hline ' + rows.join('\\\\\\hline ') + '\\\\\\hline\\end{array}';
    });
  }

  function alignRevealRows(shapes, limit) {
    const owns = (shape, id) => [].concat(shape.answerFor || []).includes(id) || shape.revealWith === id;
    const movable = shape => shape.cover && !shape.answerClips && !shape.box.rotation && !shape.box.flipV && !shape.box.flipH;
    const controls = shapes.filter(movable).sort((a,b) => a.box.y-b.box.y || a.box.x-b.box.x);
    const used = new Set();
    const right = r => r.x+r.w, bottom = r => r.y+r.h;
    const intersects = (a,b) => a.x < right(b)-1 && right(a) > b.x+1 && a.y < bottom(b)-1 && bottom(a) > b.y+1;
    for (const first of controls) {
      if (used.has(first)) continue;
      const row = [first];
      for (const other of controls) {
        if (used.has(other) || other === first) continue;
        const a=first.box,b=other.box;
        if (Math.abs(a.y-b.y) > Math.min(a.h,b.h)*.55 || Math.min(a.w,b.w)<Math.max(a.w,b.w)*.55) continue;
        if (row.every(s => right(s.box)<=b.x+1 || right(b)<=s.box.x+1)) row.push(other);
      }
      if (row.length<2) continue;
      const top=Math.max(...row.map(s=>s.box.y)), height=Math.max(...row.map(s=>s.box.h));
      if (top+height>limit+1) continue;
      const fits=row.every(control=>{
        const b=control.box, area={...b,y:top,h:height};
        return !shapes.some(s=>s!==control && !owns(s,control.id) && !row.includes(s) &&
          s.box && intersects(s.box,area) && !intersects(s.box,b));
      });
      if (!fits) continue;
      for (const control of row) {
        const dy=top-control.box.y;
        for (const shape of shapes) if (owns(shape,control.id) && dy) shape.box.y+=dy;
        control.box.y=top;
        control.box.h=height;
        used.add(control);
      }
    }
  }

  function formatSubparts(tex, render) {
    const parts = tex.split(/\\par\b/);
    const label = /^\s*(?:(\d+)\s+)?(?:\(([a-h])\)|([a-h])\)|\\textbf\{\(?([a-h])\)?[.)]?\})\s+/;
    if (!parts.some(part => label.test(part))) return null;
    let inside = false;
    const html = parts.map(part => {
      const m = part.match(label);
      if (!m) return '<span class="' + (inside ? 'luisa-part-continuation' : 'luisa-part-preamble') + '">' + render(part) + '</span>';
      const gap = inside ? ' luisa-next-part' : '';
      inside = true;
      const number = m[1] ? '<span class="luisa-question-number">' + m[1] + '</span>' : '';
      return number + '<span class="luisa-lettered-part' + gap + '"><span class="luisa-part-label">(' + (m[2] || m[3] || m[4]) + ')</span>' + render(part.slice(m[0].length)) + '</span>';
    }).join('');
    return '<span class="lesson-image-prose">' + html + '</span>';
  }

  function formatPanel(shape) {
    if (!shape.text || shape.cover || !/^(rect|roundRect|.*Callout.*)$/i.test(shape.geometry || '')) return;
    const fill = String(shape.fill || '').toLowerCase();
    if (!/^(?:#(?:000000|e97738|f79646|ffc000)|rgba?\((?:0,0,0|247,150,70|255,192,0),?[^)]*\))$/.test(fill)) return;
    delete shape.latexInk;
    shape.fill = '#ecf4fa';
    shape.line = {color:'#9eb6c9',width:1};
    for (const paragraph of shape.text.paragraphs || []) {
      paragraph.color = '#183957';
      for (const run of paragraph.parts) run.color = '#183957';
    }
  }

  function markPolicy(slide) {
    const shapes = (slide.shapes || []).flatMap(function flatten(shape) {
      return [shape, ...(shape.children || []).flatMap(flatten)];
    });
    const content = s => [s.transcription?.tex, ...(s.text?.paragraphs || []).map(p => p.parts.map(r => r.text ?? r.tex ?? '').join(''))].filter(Boolean).join(' ');
    const markedParts = new Set();
    let earned = false;
    let current = '';
    const partAtStart = /^\s*(?:\d+\.?\s*)?(?:\(([a-h])\)|([a-h])\)|\\textbf\{\(?([a-h])\)?[.)]?\})\s*/;
    for (const shape of shapes) {
      const solution = shape.answerFor || /^(?:work|answer|solution)/i.test(shape.id);
      if (!solution || shape.cover) continue;
      const owner = shapes.find(s => s.cover && s.id === shape.answerFor);
      const named = (owner?.coverLabel || '').match(/(?:^|\()([a-h])\)?$/);
      if (named) current = named[1];
      for (const line of content(shape).split(/\\par\b|\n/)) {
        const m = line.match(partAtStart);
        if (m) current = m[1] || m[2] || m[3];
        if (!/(?:\[[MAB]\d+\]|(?:^|\s)[MAB]\d+\s*(?=\s|$))/.test(line.replace(/Edexcel\s+[MAB]\d+/gi,''))) continue;
        earned = true;
        if (current) markedParts.add(current);
      }
    }
    return function format(value, question) {
      if (!value) return value;
      let part = '';
      let out = value.split(/(\\par\b)/).map(line => {
        const m = line.match(partAtStart);
        if (m) part = m[1] || m[2] || m[3];
        const supported = earned && (!part || markedParts.has(part));
        const allocation = (_, n) => supported ? '[' + n + (n === '1' ? ' mark]' : ' marks]') : '';
        let result = line.replace(/[[(](\d{1,2})\s+marks?[\])]/gi, allocation);
        if (question) result = result.replace(/(?:^|(?<=\s))\((\d{1,2})\)(?=\s*$)/g, allocation);
        return result;
      }).join('');
      return out.replace(/\\par\s*(?=\\par\b|$)/g, '').trimEnd();
    };
  }

  function prepare(slide, deck) {
    const copy = JSON.parse(JSON.stringify(slide));
    const marks = markPolicy(copy);
    copy.shapes = copy.shapes.filter(shape => !copy.headerShapes.includes(shape.id));
    if (!copy.flowLayout) alignRevealRows(copy.shapes, copy.contentHeight || deck.height);
    function visit(shape) {
      formatPanel(shape);
      delete shape.printFallback;
      delete shape.webStage;
      const paras = shape.text?.paragraphs || [];
      const isPrompt = !shape.cover && !shape.answerFor && !/^(?:work|answer|solution)/i.test(shape.id);
      for (const p of paras) {
        prepareParagraph(p);
        const last = p.parts.at(-1);
        if (last?.text) last.text = marks(last.text, isPrompt && !p.parts.some(r => r.type === 'math' && !r.text) && !(p.parts.length === 1 && /^\s*\(\d+\)\s*$/.test(last.text)));
      }
      if (shape.transcription) {
        for (const prop of ['tex','printTex']) if (shape.transcription[prop]) shape.transcription[prop] = marks(shape.transcription[prop], isPrompt);
      }
      for (const p of paras) for (const part of p.parts) if (part.tex) part.tex=ruleDataTables(part.tex);
      if (shape.transcription?.tex) shape.transcription.tex = ruleDataTables(teachingNames(shape.transcription.tex));
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
    title = title.replace(/^exam[ -]style questions?\s*[.!:]?$/i, 'Exam style question');
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

  function updateToolbar(slide, total, number = slide.sourceSlide) {
    const heading = document.getElementById('lesson-title');
    if (slide.titleTex) root.katex.render(slide.titleTex, heading, {throwOnError:true,trust:false});
    else {
      const sourceExam = /^(?:test your understanding|exam[ -]style questions?|tough question)$/i.test(slide.title)
        && slide.shapes.some(shape => /Edexcel.{0,50}(?:\d{4}|Q\d)/i.test([shape.transcription?.tex, ...(shape.text?.paragraphs || []).flatMap(p => p.parts.map(r => r.text || ''))].join(' ')));
      setTitle(heading, sourceExam ? 'Exam style question' : slide.title);
    }
    heading.title = slide.title;
    root.dispatchEvent(new CustomEvent('luisa-slide', {detail: Number(number)}));
    document.getElementById('slide-number').textContent = number;
    document.getElementById('compact-slide').textContent = `${number} / ${total}`;
    document.getElementById('slide-select').title = slide.title;
  }

  function bookletUrl(value) {
    const url = new URL(value, document.baseURI);
    const names = {"resources/pure-year-1/v11/booklets/chapter-01.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch01_Algebraic_Expressions.pdf", "resources/pure-year-1/v11/booklets/chapter-02.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch02_Quadratics.pdf", "resources/pure-year-1/v11/booklets/chapter-03.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch03_Equations_And_Inequalities.pdf", "resources/pure-year-1/v11/booklets/chapter-04.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch04_Graphs_And_Transformations.pdf", "resources/pure-year-1/v11/booklets/chapter-05.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch05_Straight_Line_Graphs.pdf", "resources/pure-year-1/v11/booklets/chapter-06.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch06_Circles.pdf", "resources/pure-year-1/v11/booklets/chapter-07.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch07_Algebraic_Methods.pdf", "resources/pure-year-1/v11/booklets/chapter-08.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch08_The_Binomial_Expansion.pdf", "resources/pure-year-1/v11/booklets/chapter-09.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch09_Trigonometric_Ratios.pdf", "resources/pure-year-1/v11/booklets/chapter-10.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch10_Trigonometric_Identities_And_Equations.pdf", "resources/pure-year-1/v11/booklets/chapter-11.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch11_Vectors.pdf", "resources/pure-year-1/v11/booklets/chapter-12.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch12_Differentiation.pdf", "resources/pure-year-1/v11/booklets/chapter-13.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch13_Integration.pdf", "resources/pure-year-1/v11/booklets/chapter-14.pdf": "resources/pure-year-1/v11/booklets/Pure1_Ch14_Exponentials_And_Logarithms.pdf", "resources/pure-year-2/v12/booklets/chapter-01.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch01_Algebraic_Methods.pdf", "resources/pure-year-2/v12/booklets/chapter-02.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch02_Functions_And_Graphs.pdf", "resources/pure-year-2/v12/booklets/chapter-03.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch03_Sequences_And_Series.pdf", "resources/pure-year-2/v12/booklets/chapter-04.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch04_Binomial_Expansion.pdf", "resources/pure-year-2/v12/booklets/chapter-05.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch05_Radians.pdf", "resources/pure-year-2/v12/booklets/chapter-06.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch06_Trigonometric_Functions.pdf", "resources/pure-year-2/v12/booklets/chapter-07.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch07_Trigonometry_And_Modelling.pdf", "resources/teaching/v003/pure-year-2/booklets/chapter-08.pdf": "resources/teaching/v003/pure-year-2/booklets/Pure2_Ch08_Parametric_Equations.pdf", "resources/pure-year-2/v12/booklets/chapter-09.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch09_Differentiation.pdf", "resources/pure-year-2/v12/booklets/chapter-10.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch10_Numerical_Methods.pdf", "resources/pure-year-2/v12/booklets/chapter-11.pdf": "resources/pure-year-2/v12/booklets/Pure2_Ch11_Integration.pdf", "resources/teaching/v003/pure-year-2/booklets/chapter-12.pdf": "resources/teaching/v003/pure-year-2/booklets/Pure2_Ch12_Vectors.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-01.pdf": "resources/teaching/v003/applied-year-1/booklets/Statistics1_Ch01_Data_Collection.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-02.pdf": "resources/teaching/v003/applied-year-1/booklets/Statistics1_Ch02_Measures_Of_Location_And_Spread.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-03.pdf": "resources/teaching/v003/applied-year-1/booklets/Statistics1_Ch03_Representations_Of_Data.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-04.pdf": "resources/teaching/v003/applied-year-1/booklets/Statistics1_Ch04_Correlation.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-05.pdf": "resources/teaching/v003/applied-year-1/booklets/Statistics1_Ch05_Probability.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-06.pdf": "resources/teaching/v003/applied-year-1/booklets/Statistics1_Ch06_Statistical_Distributions.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-07.pdf": "resources/teaching/v003/applied-year-1/booklets/Statistics1_Ch07_Hypothesis_Testing.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-08.pdf": "resources/teaching/v003/applied-year-1/booklets/Mechanics1_Ch08_Modelling_In_Mechanics.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-09.pdf": "resources/teaching/v003/applied-year-1/booklets/Mechanics1_Ch09_Constant_Acceleration.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-10.pdf": "resources/teaching/v003/applied-year-1/booklets/Mechanics1_Ch10_Forces_And_Motion.pdf", "resources/teaching/v003/applied-year-1/booklets/chapter-11.pdf": "resources/teaching/v003/applied-year-1/booklets/Mechanics1_Ch11_Variable_Acceleration.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-01.pdf": "resources/teaching/v003/applied-year-2/booklets/Statistics2_Ch01_Regression_Correlation_And_Hypothesis_Testing.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-02.pdf": "resources/teaching/v003/applied-year-2/booklets/Statistics2_Ch02_Conditional_Probability.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-03.pdf": "resources/teaching/v003/applied-year-2/booklets/Statistics2_Ch03_The_Normal_Distribution.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-04.pdf": "resources/teaching/v003/applied-year-2/booklets/Mechanics2_Ch04_Moments.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-05.pdf": "resources/teaching/v003/applied-year-2/booklets/Mechanics2_Ch05_Forces_And_Friction.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-06.pdf": "resources/teaching/v003/applied-year-2/booklets/Mechanics2_Ch06_Projectiles.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-07.pdf": "resources/teaching/v003/applied-year-2/booklets/Mechanics2_Ch07_Applications_Of_Forces.pdf", "resources/teaching/v003/applied-year-2/booklets/chapter-08.pdf": "resources/teaching/v003/applied-year-2/booklets/Mechanics2_Ch08_Further_Kinematics.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-01.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch01_Complex_Numbers.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-02.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch02_Argand_Diagrams.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-03.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch03_Series.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-04.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch04_Roots_Of_Polynomials.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-05.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch05_Volumes_Of_Revolution.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-06.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch06_Matrices.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-07.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch07_Linear_Transformations.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-08.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch08_Proof_By_Induction.pdf", "resources/teaching/v003/core-pure-1/booklets/chapter-09.pdf": "resources/teaching/v003/core-pure-1/booklets/CorePure1_Ch09_Vectors.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-01.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch01_Complex_Numbers.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-02.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch02_Series.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-03.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch03_Methods_In_Calculus.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-04.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch04_Volumes_Of_Revolution.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-05.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch05_Polar_Coordinates.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-06.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch06_Hyperbolic_Functions.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-07.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch07_Methods_In_Differential_Equations.pdf", "resources/teaching/v003/core-pure-2/booklets/chapter-08.pdf": "resources/teaching/v003/core-pure-2/booklets/CorePure2_Ch08_Modelling_With_Differential_Equations.pdf"};
    for (const [oldPath,newPath] of Object.entries(names)) {
      if (url.pathname.endsWith("/"+oldPath)) {
        url.pathname = url.pathname.slice(0,-oldPath.length)+newPath;
        break;
      }
    }
    return url.href;
  }

  function setChapterDocuments(value) {
    const booklet = bookletUrl(value);
    document.getElementById('booklet-chapter').href = booklet;
    const link = document.getElementById('chapter-solutions');
    const chapter = Object.values(root.LUISA_TEACHING).flatMap(book => book.chapters)
      .find(item => new URL(item.booklet, document.baseURI).href === booklet);
    link.hidden = !chapter?.solutions;
    if (chapter?.solutions) link.href = chapter.solutions;
    else link.removeAttribute('href');
  }

  const api = {formatSubparts,prepare,setTitle,updateToolbar,bookletUrl,setChapterDocuments};
  if (typeof module !== 'undefined') module.exports = api;
  root.LUISA_CONTROLS = api;
})(typeof window === 'undefined' ? globalThis : window);
