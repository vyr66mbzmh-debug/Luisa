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

  const api = {prepare,setTitle,bookletUrl};
  if (typeof module !== 'undefined') module.exports = api;
  root.LUISA_CONTROLS = api;
})(typeof window === 'undefined' ? globalThis : window);
