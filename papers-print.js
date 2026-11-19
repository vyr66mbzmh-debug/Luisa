/* Measured A4 paper export. Source HTML and step ordering stay unchanged. */
(() => {
  'use strict';
  const macros = {'\\p':'\\mathrm P(#1)','\\cosec':'\\operatorname{cosec}','\\cosech':'\\operatorname{cosech}','\\sech':'\\operatorname{sech}','\\coth':'\\operatorname{coth}','\\arcosech':'\\operatorname{arcosech}','\\arcsech':'\\operatorname{arcsech}','\\arsech':'\\operatorname{arsech}','\\arcoth':'\\operatorname{arcoth}','\\arsinh':'\\operatorname{arsinh}','\\arcosh':'\\operatorname{arcosh}','\\artanh':'\\operatorname{artanh}','\\Real':'\\operatorname{Re}','\\Imag':'\\operatorname{Im}','\\ssum':'\\sum_{r=1}^{#1}#2','\\arraystretch':'1'};
  const validMarks = row => Number.isInteger(row.marks) && row.marks >= 0;
  const source = row => row.sourceKind === 'past-exam' ? `Source: ${row.sourceLabel || 'Past exam'}` : row.sourceKind === 'practice-booklet'
    ? `Source: Practice Booklet · Chapter ${row.chapterNumber} · ${row.subchapterLabel || row.subchapterTitle} · ${/^\d/.test(row.questionLabel) ? 'Q' : ''}${row.questionLabel}`
    : `Source: Luisa ${row.skillCode} Q${row.number}`;
  const context = row => [row.courseTitle, row.bookTitle, row.topicTitle].filter(Boolean).join(' · ');
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
  function heading(doc, row, number, continuation = false) {
    const head = element(doc, 'header', 'question-heading');
    head.append(element(doc, 'h2', '', `Question ${number}${continuation ? ' · continued' : ''}`), element(doc, 'p', 'source', source(row)), element(doc, 'p', 'context', context(row)));
    if (validMarks(row)) head.append(element(doc, 'p', 'question-marks', `${row.marks} marks${continuation ? ' for the whole question' : ''}`));
    if (row.difficulty) head.append(element(doc, 'p', 'question-difficulty', `Difficulty: ${row.difficulty}`));
    return head;
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
  function overflows(node) { return node.scrollHeight > node.clientHeight + 1 || node.scrollWidth > node.clientWidth + 1; }
  function wideContent(node) {
    const edge = node.getBoundingClientRect().right;
    return [...node.querySelectorAll('.katex-html, img, table')].some(child => {
      const cell = child.closest('.parts.columns > li');
      return child.getBoundingClientRect().right > Math.min(edge, cell ? cell.getBoundingClientRect().right : edge) + 1;
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
    if (children.length > 1) return children.map((child, index) => {
      const wrapper = node.cloneNode(false);
      if (node.tagName === 'LI' && index) wrapper.style.listStyle = 'none';
      wrapper.append(child.cloneNode(true));
      return wrapper;
    });
    // Preserve every ancestor when reaching a nested table/list. This allows
    // table rows to continue on another sheet without flattening cells or labels.
    const pieces = node.firstElementChild && splitBlock(node.firstElementChild);
    return pieces?.map(piece => { const wrapper = node.cloneNode(false); wrapper.append(piece); return wrapper; }) || null;
  }
  async function create(rows, options = {}) {
    const layout = options.layout ?? 'two';
    const includeAnswers = options.includeAnswers ?? true;
    if (!['one', 'two', 'condensed'].includes(layout) || typeof includeAnswers !== 'boolean') throw Error('Choose a valid paper layout and answer option.');
    if (!Array.isArray(rows) || !rows.length) throw Error('Select at least one question first.');
    if (new Set(rows.map(row => row.id)).size !== rows.length) throw Error('A paper cannot contain duplicate questions.');
    if (rows.some(row => !row.id || !row.question || !Array.isArray(row.steps) || !row.steps.length)) throw Error('Every selected question needs its original prompt and worked solution.');
    const completeMarks = rows.every(row => row.sourceKind === 'past-exam' && validMarks(row));
    const totalMarks = completeMarks ? rows.reduce((sum, row) => sum + row.marks, 0) : null;
    const estimatedMinutes = completeMarks ? Math.ceil(totalMarks * 5 / 6) : null;
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
    const pages = element(doc, 'main', 'print-pages'); pages.classList.add(`layout-${layout}`); pages.setAttribute('aria-label', includeAnswers ? 'Question paper and worked solutions' : 'Question paper'); doc.body.append(pages);
    let ready = false;
    win.addEventListener('beforeprint', () => doc.body.classList.toggle('not-ready', !ready));
    try {
      await whileOpen(win, Promise.all([asset(doc, 'link', 'papers-print.css'), asset(doc, 'link', 'vendor/katex.min.css'), asset(doc, 'script', 'vendor/katex.min.js')]));
      const rendered = rows.map((row, index) => {
        const question = element(doc, 'article', 'print-question'); question.dataset.questionId = row.id;
        question.append(heading(doc, row, index + 1), content(doc, (row.contextHtml || '') + row.question));
        const working = element(doc, 'div', 'working-space'); working.setAttribute('aria-label', 'Space for working'); working.append(element(doc, 'span', '', 'Working')); if (layout !== 'condensed') question.append(working);
        const solution = includeAnswers ? content(doc, row.steps.map(html => `<div class="solution-step">${html}</div>`).join('')) : null;
        if (includeAnswers && row.hints?.length) {
          const hints = element(doc, 'section', 'solution-hints');
          hints.append(element(doc, 'h3', '', 'Hints from the booklet'), content(doc, row.hints.map(html => `<div class="solution-step">${html}</div>`).join('')));
          solution.append(hints);
        }
        return {row, question, solution};
      });
      const staging = element(doc, 'div', 'print-staging'); doc.body.append(staging);
      rendered.forEach(item => { staging.append(item.question); if (item.solution) staging.append(item.solution); });
      await whileOpen(win, prepare(win, staging, status), 120000);
      function page(kind) {
        const sheet = element(doc, 'section', `print-page ${kind}-page`);
        const banner = element(doc, 'header', 'page-banner');
        banner.append(element(doc, 'span', 'wordmark', 'Luisa'), element(doc, 'span', '', kind === 'questions' ? 'Question paper' : 'Worked solutions'));
        if (kind === 'questions' && completeMarks) banner.append(element(doc, 'span', 'paper-marks', `Total: ${totalMarks} marks · Estimated time: ${estimatedMinutes} min`));
        const body = element(doc, 'div', 'page-content');
        const footer = element(doc, 'footer', 'page-footer');
        footer.append(element(doc, 'span', '', kind === 'questions' ? 'Show your working clearly.' : 'Matched to the questions in this paper.'), element(doc, 'span', 'page-number'));
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
        if (!questionBody || (layout !== 'condensed' && questionBody.children.length === (layout === 'one' ? 1 : 2))) questionBody = page('questions');
        questionBody.append(item.question);
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
          section.append(heading(doc, item.row, i + 1, !first));
          prompt = element(doc, 'div', 'math-content'); section.append(prompt);
          if (layout !== 'condensed') section.append(item.question.querySelector('.working-space').cloneNode(true));
          body.append(section);
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
      // Assign each question's marks exactly once, on its final continuation page.
      if (completeMarks) {
        for (const item of rendered) {
          const sections = [...pages.querySelectorAll('.print-question')].filter(node => node.dataset.questionId === item.row.id);
          sections.at(-1).dataset.allocatedMarks = item.row.marks;
        }
        for (const sheet of pages.querySelectorAll('.questions-page')) {
          const marks = [...sheet.querySelectorAll('[data-allocated-marks]')].reduce((sum, node) => sum + Number(node.dataset.allocatedMarks), 0);
          sheet.querySelector('.page-footer > span').textContent = `Page total: ${marks} marks`;
          if (extendedQuestions.length) sheet.querySelector('.page-banner').append(element(doc, 'span', 'marks-policy', 'Continued questions: all marks counted on their final page.'));
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
          section.append(heading(doc, item.row, index + 1, continuation)); body.append(section);
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
  window.LUISA_PAPERS_PRINT = Object.freeze({create});
})();
