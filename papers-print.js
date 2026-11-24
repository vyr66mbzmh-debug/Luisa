/* Measured A4 paper export. Source HTML and step ordering stay unchanged. */
(() => {
  'use strict';
  const macros = {'\\p':'\\mathrm P(#1)','\\cosec':'\\operatorname{cosec}','\\cosech':'\\operatorname{cosech}','\\sech':'\\operatorname{sech}','\\coth':'\\operatorname{coth}','\\arcosech':'\\operatorname{arcosech}','\\arcsech':'\\operatorname{arcsech}','\\arsech':'\\operatorname{arsech}','\\arcoth':'\\operatorname{arcoth}','\\arsinh':'\\operatorname{arsinh}','\\arcosh':'\\operatorname{arcosh}','\\artanh':'\\operatorname{artanh}','\\Real':'\\operatorname{Re}','\\Imag':'\\operatorname{Im}','\\ssum':'\\sum_{r=1}^{#1}#2','\\arraystretch':'1'};
  const validMarks = row => Number.isInteger(row.marks) && row.marks >= 0;
  const source = row => ['past-exam', 'pmt', 'madas'].includes(row.sourceKind) ? `Source: ${(row.sourceLabel || 'Past exam').replace(/^Source:\s*/i, '')}` : row.sourceKind === 'practice-booklet'
    ? `Source: Practice Booklet · Chapter ${row.chapterNumber} · ${row.subchapterLabel || row.subchapterTitle} · ${/^\d/.test(row.questionLabel) ? 'Q' : ''}${row.questionLabel}`
    : `Source: Luisa ${row.skillCode} Q${row.number}`;
  const context = row => [row.courseTitle, row.bookTitle, row.topicTitle].filter(Boolean).join(' · ');
  // Owner rule B (v0.65): six minutes per five marks, rounded down to the whole minute.
  const paperMinutes = marks => Number.isInteger(marks) && marks > 0 ? Math.floor(marks * 6 / 5) : null;
  // Owner rule A (v0.65): every sub-question indicator is a bold bracketed number,
  // right-aligned in a reserved margin on the last line of the part it scores.
  function normaliseMarks(root) {
    for (const mark of root.querySelectorAll('.marks')) {
      const amount = /^\((\d+)(?:\s*marks?)?\)$/i.exec(mark.textContent.trim());
      if (amount) mark.textContent = `(${amount[1]})`;
      const parent = mark.parentElement;
      // A paragraph holding only the indicator would add an empty line of its own.
      if (parent?.matches('p') && [...parent.childNodes].every(node => node === mark || (node.nodeType === 3 && !node.textContent.trim()))) parent.replaceWith(mark);
    }
    return root;
  }
  const atomic = '.katex, img, svg, table, figure, br, hr';
  function precedingRects(node, mark, out) {
    for (const child of node.childNodes) {
      if (child === mark) return true;
      if (child.nodeType === 3) {
        if (!child.textContent.trim()) continue;
        const range = child.ownerDocument.createRange(); range.selectNodeContents(child);
        out.push(...[...range.getClientRects()].filter(rect => rect.width || rect.height));
        continue;
      }
      if (child.nodeType !== 1 || child.matches('.marks')) continue;
      if (child.contains(mark)) return precedingRects(child, mark, out);
      if (child.matches(atomic)) {
        const rect = child.getBoundingClientRect();
        if (rect.width || rect.height) out.push(rect);
        continue;
      }
      if (precedingRects(child, mark, out)) return true;
    }
    return false;
  }
  function placeMarks(root) {
    const placed = new Map();
    for (const mark of root.querySelectorAll('.marks')) {
      mark.style.top = '';
      const host = mark.offsetParent;
      const part = mark.parentElement?.closest('li, td, .math-content');
      if (!host || !part) continue;
      const rects = [];
      precedingRects(part, mark, rects);
      if (!rects.length) continue;
      const line = rects.at(-1), box = host.getBoundingClientRect(), height = mark.getBoundingClientRect().height;
      let top = line.bottom - box.top - host.clientTop - height;
      // Never let a later indicator overprint an earlier one in the same margin.
      if (placed.has(host)) top = Math.max(top, placed.get(host));
      mark.style.top = top + 'px';
      placed.set(host, top + height);
    }
  }
  function element(doc, tag, className, text) {
    const node = doc.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function whileOpen(win, promise, timeoutMs = 45000) {
    return new Promise((resolve, reject) => {
      const poll = window.setInterval(() => { if (win.closed) finish(Error('Paper preview was closed.')); }, 250);
      const timeout = window.setTimeout(() => finish(Error('Paper assets took too long to load. Please reconnect and try again.')), timeoutMs);
      function finish(error, value) { window.clearInterval(poll); window.clearTimeout(timeout); error ? reject(error) : resolve(value); }
      promise.then(value => finish(null, value), finish);
    });
  }
  function asset(doc, tag, url) {
    return new Promise((resolve, reject) => {
      const node = doc.createElement(tag);
      if (tag === 'link') { node.rel = 'stylesheet'; node.href = url; } else node.src = url;
      node.onload = resolve;
      node.onerror = () => reject(Error('Unable to load paper formatting. Please reconnect and try again.'));
      doc.head.append(node);
    });
  }
  const shortBooks = {
    'Pure Year 1': 'Y1 Pure', 'Pure Year 2': 'Y2 Pure',
    'Mechanics Year 1': 'Y1 Mech', 'Mechanics Year 2': 'Y2 Mech',
    'Statistics Year 1': 'Y1 Stats', 'Statistics Year 2': 'Y2 Stats',
    'Pure Core 1': 'Core Pure 1', 'Pure Core 2': 'Core Pure 2'
  };
  function compactSource(row) {
    if (row.sourceKind === 'practice-booklet') {
      const section = row.subchapterLabel || row.subchapterTitle;
      const set = /^Problem (?:solving: Set|set) (.+)$/i.exec(section);
      const exercise = /^\d+(?:\.\d+)*/.exec(section);
      const label = set?.[1] || exercise?.[0] || (/^(?:Exam[- ]style|Selected exam question bank questions)/i.test(section) ? 'Exam style' : section);
      return ['Practice', label, /^\d/.test(row.questionLabel) ? 'Q' + row.questionLabel : row.questionLabel].join(' ');
    }
    if (row.sourceKind === 'past-exam') return source(row).replace(/^Source: Edexcel (?:A Level )?/i, 'Edexcel ').replace(/^Source: /, '');
    if (['pmt', 'madas'].includes(row.sourceKind)) return source(row).replace(/^Source: /, '');
    return source(row);
  }
  function questionHeading(doc, row, number, continuation) {
    const head = element(doc, 'header', 'question-heading compact-heading');
    const chapter = row.printChapter;
    const course = (chapter?.courseTitle || row.courseTitle || '').replace(/^Maths A Level$/, 'A Level').replace('Further Maths A Level', 'Further Maths');
    const book = chapter?.bookTitle || row.bookTitle;
    const title = chapter?.title || row.chapterTitle || row.topicTitle;
    const chapterNumber = chapter?.id || row.chapterNumber;
    const topic = title === 'Applications of forces' ? 'Forces' : title;
    const place = row.sourceKind === 'madas' ? '' : [course, shortBooks[book] || book, chapterNumber && 'Ch' + chapterNumber, topic].filter(Boolean).join(' ');
    const difficulty = row.difficulty && (row.difficulty === 'very-hard' ? 'Very Hard' : row.difficulty[0].toUpperCase() + row.difficulty.slice(1));
    const detail = element(doc, 'span', 'compact-provenance', '(' + [place, compactSource(row), difficulty].filter(Boolean).join(' - ') + ')');
    detail.title = [source(row), row.sourceKind === 'madas' ? '' : context(row)].filter(Boolean).join(' · ');
    head.append(element(doc, 'h2', '', 'Q' + number + (continuation ? ' · continued' : '')), detail);
    if (validMarks(row) && !continuation) head.append(element(doc, 'strong', 'question-marks', '[' + row.marks + ' Marks]'));
    return head;
  }
  function creationStamp(created) {
    const date = created.toLocaleDateString('en-GB', {day: '2-digit', month: '2-digit', year: '2-digit'});
    const hours = created.getHours();
    const minutes = String(created.getMinutes()).padStart(2, '0');
    return date + ' ' + (hours % 12 || 12) + ':' + minutes + (hours < 12 ? 'am' : 'pm');
  }
  function content(doc, html) {
    const node = element(doc, 'div', 'math-content');
    // All callers supply the trusted, checked local question database.
    node.innerHTML = html;
    return node;
  }
  async function prepare(win, root, status) {
    let count = 0;
    const maths = root.querySelectorAll('[data-math]');
    for (const node of root.querySelectorAll('[data-math]')) {
      win.katex.render(node.dataset.math, node, {displayMode: node.dataset.display === 'true', throwOnError: true, strict: 'error', macros: {...macros}});
      if (++count % 100 === 0) {
        if (win.closed) throw Error('Paper preview was closed.');
        status.textContent = `Preparing mathematical content: ${count} of ${maths.length} expressions…`;
        await new Promise(resolve => window.setTimeout(resolve, 0));
      }
    }
    await Promise.all([...root.querySelectorAll('img')].map(img => new Promise((resolve, reject) => {
      img.loading = 'eager';
      const done = () => img.naturalWidth ? resolve() : reject(Error('A source diagram could not load. Please reconnect and try again.'));
      if (img.complete) done(); else { img.onload = done; img.onerror = done; }
    })));
    // Match the issued booklet fix: precomposed relations avoid overprinted
    // negation glyphs disappearing in Chromium/Apple Quartz PDFs.
    const relations = {'=':'≠','∈':'∉','∋':'∌','≈':'≉','≡':'≢','<':'≮','>':'≯','≤':'≰','≥':'≱','∼':'≁','⊂':'⊄','⊃':'⊅','⊆':'⊈','⊇':'⊉'};
    for (const mark of root.querySelectorAll('.katex-html .mrel')) {
      if (mark.children.length || mark.textContent !== '\uE020') continue;
      for (let relation = mark.parentElement; relation?.closest('.katex-html'); relation = relation.parentElement) {
        const replacement = relations[relation.textContent.replace('\uE020', '')];
        if (!replacement) continue;
        relation.textContent = replacement;
        relation.style.fontFamily = '"Times New Roman", Georgia, serif';
        break;
      }
    }
    await win.document.fonts.ready;
  }
  function fitQuestionHeading(question) {
    const detail = question.querySelector('.compact-provenance');
    for (const size of [9, 8.5, 8, 7.5]) {
      detail.style.fontSize = size + 'pt';
      if (detail.scrollWidth <= detail.clientWidth + 1) break;
    }
  }
  function overflows(node) { return node.scrollHeight > node.clientHeight + 1 || node.scrollWidth > node.clientWidth + 1; }
  // The marks margin is reserved: question content may not run into it.
  const contentRight = node => node.getBoundingClientRect().right - parseFloat(node.ownerDocument.defaultView.getComputedStyle(node).paddingRight || 0);
  function wideContent(node) {
    const edge = contentRight(node);
    return [...node.querySelectorAll('.katex-html, img, table')].some(child => {
      const cell = child.closest('.parts.columns > li');
      return child.getBoundingClientRect().right > Math.min(edge, cell ? contentRight(cell) : edge) + 1;
    });
  }
  // Split only at semantic boundaries. A single mathematical expression or diagram
  // is never cut, rasterised, or clipped to manufacture a fit.
  function splitBlock(node) {
    if (!node.children.length || node.matches('[data-math],figure,p')) return null;
    if (node.matches('ol,ul')) {
      if (node.children.length > 1) return [...node.children].map((child, index) => {
        const list = node.cloneNode(false);
        if (node.tagName === 'OL') list.start = Number(child.getAttribute('value')) || (Number(node.getAttribute('start')) || 1) + index;
        list.append(child.cloneNode(true));
        return list;
      });
    }
    const children = [...node.childNodes].filter(n => n.nodeType !== 3 || n.textContent.trim());
    // A marks indicator stays with the content it ends, so it never starts a sheet alone.
    const groups = [];
    for (const child of children) {
      if (groups.length && child.nodeType === 1 && child.matches('.marks')) groups.at(-1).push(child); else groups.push([child]);
    }
    if (groups.length > 1) return groups.map((group, index) => {
      const wrapper = node.cloneNode(false);
      if (node.tagName === 'LI' && index) wrapper.style.listStyle = 'none';
      wrapper.append(...group.map(child => child.cloneNode(true)));
      return wrapper;
    });
    // Preserve every ancestor when reaching a nested table/list. This allows
    // table rows to continue on another sheet without flattening cells or labels.
    // Any marks indicator grouped after that child travels with its last piece.
    const trailing = groups[0]?.slice(1) || [];
    const pieces = node.firstElementChild && splitBlock(node.firstElementChild);
    return pieces?.map((piece, index) => {
      const wrapper = node.cloneNode(false); wrapper.append(piece);
      if (index === pieces.length - 1) wrapper.append(...trailing.map(child => child.cloneNode(true)));
      return wrapper;
    }) || null;
  }
  async function create(rows, options = {}) {
    const layout = options.layout ?? 'one';
    const includeAnswers = options.includeAnswers ?? true;
    if (!['one', 'condensed'].includes(layout) || typeof includeAnswers !== 'boolean') throw Error('Choose a valid paper layout and answer option.');
    if (!Array.isArray(rows) || !rows.length) throw Error('Select at least one question first.');
    if (new Set(rows.map(row => row.id)).size !== rows.length) throw Error('A paper cannot contain duplicate questions.');
    if (rows.some(row => !row.id || !row.question || !Array.isArray(row.steps) || !row.steps.length)) throw Error('Every selected question needs its original prompt and worked solution.');
    const created = new Date();
    const stamp = creationStamp(created);
    // A real same-origin document is controlled by the offline service worker;
    // an about:blank popup cannot retrieve its cached formatting and diagrams.
    const previewURL = new URL('paper-preview.html', document.baseURI);
    const win = window.open(previewURL.href, '_blank');
    if (!win) throw Error('Allow pop-ups for Luisa to open the paper preview.');
    await whileOpen(win, new Promise((resolve, reject) => {
      const loaded = () => {
        try {
          if (!win.document.querySelector('meta[name="luisa-paper-preview"]')) {
            reject(Error('The paper preview could not open. Sign in or reconnect, then try again.'));
          } else resolve();
        } catch (_) { reject(Error('The paper preview could not open. Please try again.')); }
      };
      win.addEventListener('load', loaded, {once: true});
      if (win.location.href === previewURL.href && win.document.readyState === 'complete') loaded();
    }));
    const doc = win.document;
    doc.open();
    doc.write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Maths Paper</title></head><body></body></html>');
    doc.close();
    const base = element(doc, 'base'); base.href = document.baseURI; doc.head.append(base);
    const toolbar = element(doc, 'aside', 'print-toolbar');
    const title = element(doc, 'strong', '', 'Luisa · Paper preview');
    const status = element(doc, 'p', 'print-status', includeAnswers ? 'Preparing complete questions, diagrams and worked solutions…' : 'Preparing complete questions and diagrams…');
    status.setAttribute('role', 'status');
    const print = element(doc, 'button', '', 'Print / Save PDF'); print.type = 'button'; print.disabled = true;
    const close = element(doc, 'button', 'secondary', 'Close preview'); close.type = 'button'; close.onclick = () => win.close();
    toolbar.append(title, status, print, close); doc.body.append(toolbar);
    const pages = element(doc, 'main', 'print-pages marks-pending'); pages.classList.add(`layout-${layout}`); pages.setAttribute('aria-label', includeAnswers ? 'Question paper and worked solutions' : 'Question paper'); doc.body.append(pages);
    let ready = false;
    win.addEventListener('beforeprint', () => doc.body.classList.toggle('not-ready', !ready));
    try {
      await whileOpen(win, Promise.all([asset(doc, 'link', 'papers-print.css'), asset(doc, 'link', 'vendor/katex.min.css'), asset(doc, 'script', 'vendor/katex.min.js')]));
      const rendered = rows.map((row, index) => {
        const question = element(doc, 'article', 'print-question'); question.dataset.questionId = row.id;
        const contextHtml = row.sourceKind === 'past-exam' ? '' : row.contextHtml || '';
        question.append(questionHeading(doc, row, index + 1, false), normaliseMarks(content(doc, contextHtml + row.question)));
        const working = element(doc, 'div', 'working-space'); working.setAttribute('aria-label', 'Space for working'); working.append(element(doc, 'span', '', 'Working')); if (layout !== 'condensed') question.append(working);
        const solution = includeAnswers ? content(doc, row.steps.map(html => `<div class="solution-step">${html}</div>`).join('')) : null;
        if (solution && row.sourceKind === 'madas') solution.querySelector('.madas-total').textContent = `Total mark for question ${index + 1} is ${row.marks} marks.`;
        if (includeAnswers && row.hints?.length) {
          const hints = element(doc, 'section', 'solution-hints');
          hints.append(element(doc, 'h3', '', 'Hints from the booklet'), content(doc, row.hints.map(html => `<div class="solution-step">${html}</div>`).join('')));
          solution.append(hints);
        }
        return {row, question, solution};
      });
      const staging = element(doc, 'div', 'print-staging marks-pending'); doc.body.append(staging);
      rendered.forEach(item => { staging.append(item.question); if (item.solution) staging.append(item.solution); });
      await whileOpen(win, prepare(win, staging, status), 120000);
      function page(kind) {
        const sheet = element(doc, 'section', `print-page ${kind}-page`);
        const banner = element(doc, 'header', 'page-banner');
        banner.textContent = kind === 'questions' ? 'Question paper' : 'Worked solutions';
        const body = element(doc, 'div', 'page-content');
        const footer = element(doc, 'footer', 'page-footer');
        const time = element(doc, 'time', 'creation-time', stamp);
        time.dateTime = created.toISOString();
        footer.append(time, element(doc, 'span', 'page-number'));
        sheet.append(banner, body, footer); pages.append(sheet);
        return body;
      }
      const warnings = [];
      const extendedQuestions = [];
      let questionBody;
      for (let i = 0; i < rendered.length; i++) {
        if (i % 20 === 0) {
          if (win.closed) throw Error('Paper preview was closed.');
          status.textContent = `Laying out questions: ${i + 1} of ${rows.length}…`;
          await new Promise(resolve => window.setTimeout(resolve, 0));
        }
        const item = rendered[i];
        if (!questionBody || layout === 'one') questionBody = page('questions');
        questionBody.append(item.question);
        fitQuestionHeading(item.question);
        if (layout === 'condensed' && overflows(questionBody) && questionBody.children.length > 1) {
          item.question.remove(); questionBody = page('questions'); questionBody.append(item.question);
        }
        const questionOverflows = () => overflows(item.question) || (layout === 'condensed' && overflows(questionBody));
        if (questionOverflows() || wideContent(item.question.querySelector('.math-content'))) item.question.classList.add('compact');
        if (questionOverflows()) {
          for (const list of item.question.querySelectorAll('.math-content > ol.parts, .math-content > ul.parts')) {
            list.classList.add('columns');
            if (list.scrollWidth > list.clientWidth + 1 || wideContent(list)) list.classList.remove('columns');
          }
        }
        if (!questionOverflows() && !wideContent(item.question.querySelector('.math-content'))) continue;
        // Owner-approved exception: give the original question additional pages
        // at normal type size, preserving its position in the selected paper.
        extendedQuestions.push(source(item.row));
        item.question.remove();
        if (!questionBody.children.length) questionBody.parentElement.remove();
        questionBody = null;
        item.question.classList.remove('compact');
        item.question.querySelectorAll('.columns').forEach(list => list.classList.remove('columns'));
        const queue = [...item.question.querySelector('.math-content').childNodes].filter(n => n.nodeType !== 3 || n.textContent.trim()).map(node => node.cloneNode(true));
        let section, prompt;
        let first = true, hasContent = false;
        function extendedPage() {
          const body = page('questions'); body.parentElement.classList.add('extended-page');
          section = element(doc, 'article', 'print-question extended-question'); section.dataset.questionId = item.row.id;
          section.append(questionHeading(doc, item.row, i + 1, !first));
          prompt = element(doc, 'div', 'math-content'); section.append(prompt);
          if (layout !== 'condensed') section.append(item.question.querySelector('.working-space').cloneNode(true));
          body.append(section);
          fitQuestionHeading(section);
          if (layout === 'condensed') questionBody = body;
          first = false; hasContent = false;
        }
        extendedPage();
        while (queue.length) {
          const block = queue.shift(); prompt.append(block);
          if (wideContent(prompt)) block.nodeType === 1 && block.classList.add('compact');
          if (!overflows(section) && !(layout === 'condensed' && overflows(questionBody)) && !wideContent(prompt)) { hasContent = true; continue; }
          block.remove();
          if (hasContent) { extendedPage(); queue.unshift(block); continue; }
          const pieces = block.nodeType === 1 && splitBlock(block);
          if (pieces?.length > 1) { queue.unshift(...pieces); continue; }
          if (block.nodeType === 1) block.classList.add('compact');
          prompt.append(block);
          if (overflows(section) || (layout === 'condensed' && overflows(questionBody)) || wideContent(prompt)) warnings.push(`${source(item.row)} has an indivisible question expression or figure that does not fit a full page at readable size.`);
          hasContent = true;
        }
      }
      // Solutions always begin on a fresh page, after every question.
      let body;
      for (let index = 0; includeAnswers && index < rendered.length; index++) {
        const item = rendered[index];
        if (index % 10 === 0) {
          if (win.closed) throw Error('Paper preview was closed.');
          status.textContent = `Laying out worked solutions: ${index + 1} of ${rows.length}…`;
          await new Promise(resolve => window.setTimeout(resolve, 0));
        }
        if (!body) body = page('solutions');
        let section;
        function newSection(continuation) {
          section = element(doc, 'article', 'print-solution'); section.dataset.questionId = item.row.id;
          section.append(questionHeading(doc, item.row, index + 1, continuation));
          if (!continuation && item.row.sourceKind === 'madas') section.append(element(doc, 'p', 'scheme-credit', 'Adapted MADAS mark scheme · editorial mark allocations'));
          body.append(section);
          fitQuestionHeading(section);
        }
        newSection(false);
        const queue = [...item.solution.children].map(node => node.cloneNode(true));
        let hasContent = false;
        while (queue.length) {
          const block = queue.shift(); section.append(block);
          if (wideContent(block)) {
            block.classList.add('compact');
            if (wideContent(block)) warnings.push(`${source(item.row)} has a worked expression wider than the printable page.`);
          }
          if (!overflows(body)) { hasContent = true; continue; }
          block.remove();
          if (hasContent || body.children.length > 1) {
            if (!hasContent) section.remove();
            body = page('solutions'); newSection(hasContent); hasContent = false; queue.unshift(block); continue;
          }
          const pieces = splitBlock(block);
          if (pieces && pieces.length > 1) { queue.unshift(...pieces); continue; }
          block.classList.add('compact'); section.append(block);
          if (overflows(body)) warnings.push(`${source(item.row)} has a worked block too tall for one page; no content has been removed.`);
          hasContent = true;
        }
      }
      staging.remove();
      // Indicators stay out of measurement until pagination is final; they never change it.
      pages.classList.remove('marks-pending');
      placeMarks(pages);
      const total = pages.children.length;
      [...pages.children].forEach((sheet, index) => {
        sheet.querySelector('.page-number').textContent = `Page ${index + 1} of ${total}`;
        sheet.setAttribute('aria-label', `${sheet.classList.contains('questions-page') ? 'Questions' : 'Worked solutions'}, page ${index + 1} of ${total}`);
      });
      if (warnings.length) {
        doc.body.classList.add('not-ready');
        const message = 'This selection cannot be printed completely in the required layout. Remove or replace the listed questions, then create a new preview.';
        status.textContent = message;
        const list = element(doc, 'ul', 'print-errors'); [...new Set(warnings)].forEach(warning => list.append(element(doc, 'li', '', warning))); toolbar.append(list);
        return {window: win, pageCount: total, warnings: [...new Set(warnings)], extendedQuestions, ready: false};
      }
      ready = true;
      status.textContent = `${rows.length} questions · ${total} A4 pages · ${includeAnswers ? 'worked solutions at the back' : 'questions only'}.${extendedQuestions.length ? ` ${extendedQuestions.length} longer questions use extra space or continuation pages.` : ''} Choose A4, 100% scale and turn off browser headers and footers in the print dialog. Select Save as PDF to download.`;
      print.disabled = false; print.onclick = () => win.print();
      return {window: win, pageCount: total, warnings: [], extendedQuestions, ready: true};
    } catch (error) {
      if (!win.closed) { doc.body.classList.add('not-ready'); status.textContent = `Paper preview unavailable: ${error.message}`; }
      throw error;
    }
  }
  window.LUISA_PAPERS_PRINT = Object.freeze({create, paperMinutes, normaliseMarks, placeMarks, sourceLabel: source,
    // Shared, unchanged print internals for the teacher-only exam paper (papers-exam.js).
    internals: Object.freeze({macros, element, whileOpen, asset, content, prepare, overflows, wideContent, splitBlock})});
})();
