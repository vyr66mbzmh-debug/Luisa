/* Measured A4 paper export. Source HTML and step ordering stay unchanged. */
(() => {
  'use strict';
  const macros = {'\\p':'\\mathrm P(#1)','\\cosec':'\\operatorname{cosec}','\\cosech':'\\operatorname{cosech}','\\sech':'\\operatorname{sech}','\\coth':'\\operatorname{coth}','\\arcosech':'\\operatorname{arcosech}','\\arcsech':'\\operatorname{arcsech}','\\arsech':'\\operatorname{arsech}','\\arcoth':'\\operatorname{arcoth}','\\arsinh':'\\operatorname{arsinh}','\\arcosh':'\\operatorname{arcosh}','\\artanh':'\\operatorname{artanh}','\\Real':'\\operatorname{Re}','\\Imag':'\\operatorname{Im}','\\ssum':'\\sum_{r=1}^{#1}#2','\\arraystretch':'1'};
  const source = row => `Source: Luisa ${row.skillCode} Q${row.number}`;
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
    if (!node.children.length || node.matches('[data-math],figure,table,.math-table,p')) return null;
    if (node.matches('ol,ul')) {
      return [...node.children].map((child, index) => {
        const list = node.cloneNode(false);
        if (node.tagName === 'OL') list.start = (Number(node.getAttribute('start')) || 1) + index;
        list.append(child.cloneNode(true));
        return list;
      });
    }
    return [...node.childNodes].filter(n => n.nodeType !== 3 || n.textContent.trim()).map(child => {
      const wrapper = node.cloneNode(false);
      wrapper.append(child.cloneNode(true));
      return wrapper;
    });
  }
  async function create(rows) {
    if (!Array.isArray(rows) || !rows.length) throw Error('Select at least one question first.');
    if (new Set(rows.map(row => row.id)).size !== rows.length) throw Error('A paper cannot contain duplicate questions.');
    if (rows.some(row => !row.id || !row.question || !Array.isArray(row.steps) || !row.steps.length)) throw Error('Every selected question needs its original prompt and worked solution.');
    const win = window.open('', '_blank');
    if (!win) throw Error('Allow pop-ups for Luisa to open the paper preview.');
    const doc = win.document;
    doc.open();
    doc.write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Maths Paper</title></head><body></body></html>');
    doc.close();
    const base = element(doc, 'base'); base.href = document.baseURI; doc.head.append(base);
    const toolbar = element(doc, 'aside', 'print-toolbar');
    const title = element(doc, 'strong', '', 'Luisa · Paper preview');
    const status = element(doc, 'p', 'print-status', 'Preparing complete questions, diagrams and worked solutions…');
    status.setAttribute('role', 'status');
    const print = element(doc, 'button', '', 'Print / Save PDF'); print.type = 'button'; print.disabled = true;
    const close = element(doc, 'button', 'secondary', 'Close preview'); close.type = 'button'; close.onclick = () => win.close();
    toolbar.append(title, status, print, close); doc.body.append(toolbar);
    const pages = element(doc, 'main', 'print-pages'); pages.setAttribute('aria-label', 'Question paper and worked solutions'); doc.body.append(pages);
    let ready = false;
    win.addEventListener('beforeprint', () => doc.body.classList.toggle('not-ready', !ready));
    try {
      await whileOpen(win, Promise.all([asset(doc, 'link', 'papers-print.css'), asset(doc, 'link', 'vendor/katex.min.css'), asset(doc, 'script', 'vendor/katex.min.js')]));
      const rendered = rows.map((row, index) => {
        const question = element(doc, 'article', 'print-question'); question.dataset.questionId = row.id;
        question.append(heading(doc, row, index + 1), content(doc, row.question));
        const working = element(doc, 'div', 'working-space'); working.setAttribute('aria-label', 'Space for working'); working.append(element(doc, 'span', '', 'Working')); question.append(working);
        const solution = content(doc, row.steps.map(html => `<div class="solution-step">${html}</div>`).join(''));
        return {row, question, solution};
      });
      const staging = element(doc, 'div', 'print-staging'); doc.body.append(staging);
      rendered.forEach(item => staging.append(item.question, item.solution));
      await whileOpen(win, prepare(win, staging, status), 120000);
      function page(kind) {
        const sheet = element(doc, 'section', `print-page ${kind}-page`);
        const banner = element(doc, 'header', 'page-banner');
        banner.append(element(doc, 'span', 'wordmark', 'Luisa'), element(doc, 'span', '', kind === 'questions' ? 'Question paper' : 'Worked solutions'));
        const body = element(doc, 'div', 'page-content');
        const footer = element(doc, 'footer', 'page-footer');
        footer.append(element(doc, 'span', '', kind === 'questions' ? 'Show your working clearly.' : 'Matched to the questions in this paper.'), element(doc, 'span', 'page-number'));
        sheet.append(banner, body, footer); pages.append(sheet);
        return body;
      }
      const warnings = [];
      for (let i = 0; i < rendered.length; i += 2) {
        if (i % 20 === 0) {
          if (win.closed) throw Error('Paper preview was closed.');
          status.textContent = `Laying out questions: ${i + 1} of ${rows.length}…`;
          await new Promise(resolve => window.setTimeout(resolve, 0));
        }
        const body = page('questions');
        for (const item of rendered.slice(i, i + 2)) {
          body.append(item.question);
          if (overflows(item.question) || wideContent(item.question.querySelector('.math-content'))) item.question.classList.add('compact');
          if (overflows(item.question)) {
            for (const list of item.question.querySelectorAll('.math-content > ol.parts, .math-content > ul.parts')) {
              list.classList.add('columns');
              if (list.scrollWidth > list.clientWidth + 1 || wideContent(list)) list.classList.remove('columns');
            }
          }
          if (overflows(item.question) || wideContent(item.question.querySelector('.math-content'))) warnings.push(`${source(item.row)} is too long or wide for a half-page with useful working space at readable type size.`);
        }
      }
      // Solutions always begin on a fresh page, after every question.
      let body;
      for (let index = 0; index < rendered.length; index++) {
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
          // A wrapper with one child may still contain a splittable list.
          if (pieces?.length === 1 && block.firstElementChild && block.firstElementChild !== block) {
            const inner = splitBlock(block.firstElementChild);
            if (inner?.length > 1) { queue.unshift(...inner); continue; }
          }
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
        return {window: win, pageCount: total, warnings: [...new Set(warnings)], ready: false};
      }
      ready = true;
      status.textContent = `${rows.length} questions · ${total} A4 pages · worked solutions at the back. Choose A4, 100% scale and turn off browser headers and footers in the print dialog. Select Save as PDF to download.`;
      print.disabled = false; print.onclick = () => win.print();
      return {window: win, pageCount: total, warnings: [], ready: true};
    } catch (error) {
      if (!win.closed) { doc.body.classList.add('not-ready'); status.textContent = `Paper preview unavailable: ${error.message}`; }
      throw error;
    }
  }
  window.LUISA_PAPERS_PRINT = Object.freeze({create});
})();
