/* One board sheet is also one worked PDF page. Visibility changes never reflow the question. */
(() => {
  const {escape, imageContent} = FMQ_SLIDE_RENDERER;
  function renderSourcePlates(slide, base) {
    const {sourcePlates: plates, questionNumber} = slide.singlePageExercise;
    const plate = (item) => `<img src="${escape(base + item.asset)}" alt="${escape(item.alt)}" width="${item.width}" height="${item.height}">`;
    return `<div class="source-slide" data-source-slide="${slide.sourceSlide}" style="width:1440px;height:840px"><div class="lesson-canvas exercise-sheet source-exercise" style="width:100%;height:100%;--prompt-width:${plates.left}px"><div class="exercise-head"><strong>Question ${escape(String(questionNumber))}</strong><button class="exercise-reveal" data-shape="solution" aria-label="Solution" aria-expanded="false">Solution</button></div><div class="source-exercise-body"><div data-shape="prompt">${plate(plates.questionPlate)}</div><div data-shape="work-0" data-answer-for="solution">${plate(plates.workingPlate)}</div></div></div></div>`;
  }
  function render(slide, base) {
    const spec = slide.singlePageExercise;
    if (spec.sourcePlates) return renderSourcePlates(slide, base);
    const objects = new Map(slide.shapes.map(shape => [shape.id, shape]));
    function figure(id) {
      const item = objects.get(id);
      return `<img class="exercise-figure" src="${escape(base + item.asset)}" alt="${escape(item.alt || 'Mechanics diagram')}">`;
    }
    const formatMarks = LUISA_CONTROLS.markPolicy(slide);
    const question = imageContent(formatMarks(objects.get(spec.question).transcription.tex, true), {});
    const band = spec.diagramBand;
    function renderWork(id) {
      const item = objects.get(id);
      return item.asset ? figure(id) : imageContent(formatMarks(item.transcription.tex, false), {});
    }
    const parts = spec.parts;
    if (parts) {
      const cards = parts.every(part => part.figure);
      const rows = parts.map(part => {
        const prompt = part.figure ? figure(part.figure) : imageContent(formatMarks(part.prompt, true), {});
        const button = `<button class="exercise-reveal" data-shape="${escape(part.control)}" aria-label="${escape(part.label)}" aria-expanded="false">${escape(part.label)}</button>`;
        const work = `<div data-shape="${escape(part.work)}" data-answer-for="${escape(part.control)}">${renderWork(part.work)}</div>`;
        return `<section class="matched-row"><div class="matched-question">${prompt}</div><div class="matched-answer">${button}${work}</div></section>`;
      }).join('');
      const number = escape(objects.get('number').transcription.tex);
      const intro = `<div class="matched-intro"><div data-shape="prompt"><strong>${number}</strong>${question}</div>${spec.figures.map(figure).join('')}</div>`;
      return `<div class="source-slide" data-source-slide="${slide.sourceSlide}" style="width:${slide.contentWidth}px;height:${slide.contentHeight}px"><div class="lesson-canvas exercise-sheet matched-sheet${cards ? ' matched-cards' : ''}" style="width:100%;height:100%">${intro}<div class="matched-rows">${rows}</div></div></div>`;
    }
    const working = spec.working.filter(id => id !== band).map(renderWork).join('');
    const reveal = '<button class="exercise-reveal" data-shape="solution" aria-label="Solution" aria-expanded="false">Solution</button>';
    const workAttrs = 'class="exercise-working" data-shape="work-0" data-answer-for="solution"';
    const width = spec.questionWidth;
    const layout = Number.isFinite(width) && width >= 30 && width <= 65
      ? ' data-balanced-exercise style="width:100%;height:100%;--exercise-question-width:' + width + '%"'
      : ' style="width:100%;height:100%"';
    const number = escape(objects.get('number').transcription.tex);
    return `<div class="source-slide" data-source-slide="${slide.sourceSlide}" style="width:${slide.contentWidth}px;height:${slide.contentHeight}px"><div class="lesson-canvas exercise-sheet"${layout}><div class="exercise-head"><strong>${number}</strong>${reveal}</div><div class="exercise-columns"><div class="exercise-question" data-shape="prompt">${question}${spec.figures.map(figure).join('')}</div><div ${workAttrs}>${working}</div></div>${band ? '<div class="exercise-diagram-band" data-answer-for="solution">'+figure(band)+'</div>' : ''}</div></div>`;
  }
  function fit(sheet) {
    if (!sheet || sheet.classList.contains('source-exercise')) return;
    if (sheet.classList.contains('matched-sheet')) {
      const cells = [...sheet.querySelectorAll('.matched-question,.matched-answer,.matched-rows')];
      for (let size = 30; size >= 14; size -= 0.5) {
        sheet.style.fontSize = size + 'px';
        if (sheet.scrollHeight <= sheet.clientHeight + 1 && cells.every(cell =>
          cell.scrollWidth <= cell.clientWidth + 1 && cell.scrollHeight <= cell.clientHeight + 1)) break;
      }
      return;
    }
    const container = sheet.querySelector('.exercise-columns');
    const solution = sheet.querySelector('.exercise-working');
    // Size against hidden working as well, so revealing it leaves everything in place.
    for (let size = 29; size >= 8; size -= 0.5) {
      for (const count of [1, 2, 3, 4]) {
        container.style.fontSize = size + 'px';
        solution.style.columnCount = count;
        if (solution.scrollWidth > solution.clientWidth + 1 || solution.scrollHeight > solution.clientHeight + 1) continue;
        const question = sheet.querySelector('.exercise-question');
        if (question.scrollHeight > question.clientHeight + 1 || question.scrollWidth > question.clientWidth + 1) continue;
        const outer = solution.getBoundingClientRect();
        const scale = outer.width / solution.clientWidth;
        const colWidth = (solution.clientWidth - (count-1)*parseFloat(getComputedStyle(solution).columnGap))/count;
        if ([...solution.querySelectorAll('.katex-html')].some(e => e.getBoundingClientRect().width > colWidth*scale+1)) continue;
        if ([...solution.querySelectorAll('.katex-html,.exercise-figure')].some(e=>e.getBoundingClientRect().right > outer.right + 1)) continue;
        return;
      }
    }
  }
  window.LUISA_EXERCISE = {render, fit};
})();
