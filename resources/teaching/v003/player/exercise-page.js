/* Each question occupies one teaching panel in the viewer and in both booklets. Visibility changes never reflow the question. */
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
      return `<img class="exercise-figure" src="${escape(base + item.asset)}" alt="${escape(item.alt || ('Diagram for question ' + spec.questionNumber))}">`;
    }
    const formatMarks = LUISA_CONTROLS.markPolicy(slide);
    const question = imageContent(formatMarks(objects.get(spec.question).transcription.tex, true), {});
    const introduction = spec.introduction
      ? '<div class="exercise-introduction">'+imageContent(objects.get(spec.introduction).transcription.tex, {})+'</div>'
      : '';
    function workingContent(ids) {
      const fragments = [];
      for (let index = 0; index < ids.length; index++) {
        const item = objects.get(ids[index]);
        if (!item.asset) {
          fragments.push(imageContent(formatMarks(item.transcription.tex, false), {}));
          continue;
        }
        if (spec.pairWorkingFigures && objects.get(ids[index + 1])?.asset) {
          fragments.push('<div class="exercise-figure-pair">'+figure(item.id)+figure(ids[++index])+'</div>');
        } else {
          fragments.push(figure(item.id));
        }
      }
      return fragments.join('');
    }
    const underQuestion = spec.underQuestion
      ? '<div class="exercise-under-question" data-answer-for="solution">'+workingContent([spec.underQuestion])+'</div>'
      : '';
    const band = spec.diagramBand;
    const topFigures = spec.headerFigures || [];
    const working = workingContent(spec.working.filter(id => id !== band && !topFigures.includes(id)));
    const diagrams = spec.figures.map(figure).join('');
    const questionFigures = (spec.figures.length >= 3 || spec.pairFigures)
      ? '<div class="exercise-figure-grid">' + diagrams + '</div>'
      : diagrams;
    const number = escape(objects.get('number').transcription.tex);
    const title = '<strong>'+number+'</strong><button class="exercise-reveal" data-shape="solution" aria-label="Solution" aria-expanded="false">Solution</button>';
    const head = topFigures.length
      ? '<div class="exercise-head exercise-figure-header"><div>'+title+'</div>'+diagrams+
        topFigures.map(id => '<div class="exercise-header-answer" data-answer-for="solution">'+figure(id)+'</div>').join('')+'</div>'
      : '<div class="exercise-head">'+title+'</div>';
    return `<div class="source-slide" data-source-slide="${slide.sourceSlide}" style="width:${slide.contentWidth}px;height:${slide.contentHeight}px"><div class="lesson-canvas exercise-sheet" style="width:100%;height:100%">${head}${introduction}<div class="exercise-columns${spec.compactWorking ? ' exercise-long-working' : ''}"><div class="exercise-question" data-shape="prompt">${question}${topFigures.length ? '' : questionFigures}${underQuestion}</div><div class="exercise-working" data-shape="work-0" data-answer-for="solution">${working}</div></div>${band ? '<div class="exercise-diagram-band" data-answer-for="solution">'+figure(band)+'</div>' : ''}</div></div>`;
  }
  function fit(sheet) {
    if (!sheet || sheet.classList.contains('source-exercise')) return;
    const container = sheet.querySelector('.exercise-columns');
    const solution = sheet.querySelector('.exercise-working');
    const question = sheet.querySelector('.exercise-question');
    const maths = [...solution.querySelectorAll('.katex-html')];
    const figures = [...solution.querySelectorAll('.exercise-figure')];
    // Long question stems and short numerical solutions need a different
    // division of the board from brief prompts with extended working.
    const widths = question.querySelector('.exercise-figure-grid') ? [50, 55, 45, 38, 30] : [30, 38, 45, 50, 55];
    if (container.classList.contains('exercise-long-working')) widths.push(28, 32, 34, 36, 40, 42, 47, 52);
    function fits(size) {
      container.style.fontSize = size + 'px';
      for (const width of widths) {
        container.style.gridTemplateColumns = width + '% minmax(0,1fr)';
        if (question.scrollHeight > question.clientHeight + 1 || question.scrollWidth > question.clientWidth + 1) continue;
        for (const count of [1, 2, 3, 4]) {
          solution.style.columnCount = count;
          if (solution.scrollWidth > solution.clientWidth + 1 || solution.scrollHeight > solution.clientHeight + 1) continue;
          const outer = solution.getBoundingClientRect();
          const scale = outer.width / solution.clientWidth;
          const gap = parseFloat(getComputedStyle(solution).columnGap);
          const columnWidth = (solution.clientWidth - (count - 1) * gap) / count;
          if (maths.some(e => e.getBoundingClientRect().width > columnWidth * scale + 1)) continue;
          if ([...maths, ...figures].some(e => e.getBoundingClientRect().right > outer.right + 1)) continue;
          return true;
        }
      }
      return false;
    }
    if (fits(29)) return;
    let low = 16, high = 58;
    while (high - low > 1) {
      const mid = Math.floor((high + low) / 2);
      if (fits(mid / 2)) low = mid;
      else high = mid;
    }
    fits(low / 2);
  }
  function fitWhenReady(sheet) {
    if (!sheet) return;
    function fitCurrentSheet() {
      if (sheet.isConnected) fit(sheet);
    }
    fitCurrentSheet();
    const images = [...sheet.querySelectorAll('img')].map(image => image.decode());
    Promise.allSettled([document.fonts.ready, ...images]).then(fitCurrentSheet);
  }
  window.LUISA_EXERCISE = {render, fit, fitWhenReady};
})();
