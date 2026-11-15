// A small, local worksheet for the cubic used in the Newton–Raphson lesson.
(() => {
  const rowLimit = 7;
  const display = value => {
    if (!Number.isFinite(value)) return '—';
    return Number(value.toPrecision(10)).toString().replace('e+', 'e');
  };
  function makeRow(x, number) {
    const fx = x ** 3 + x ** 2 - 5 * x + 2;
    const derivative = 3 * x ** 2 + 2 * x - 5;
    const next = derivative === 0 ? NaN : x - fx / derivative;
    return {number, values:[x, fx, derivative, next]};
  }
  function formula(column, number, start) {
    switch (column) {
      case 'A': {
        if (number === 2) return String(start);
        const previous = number - 1;
        return '=A' + previous + '-B' + previous + '/C' + previous;
      }
      case 'B': return '=A' + number + '^3+A' + number + '^2-5*A' + number + '+2';
      case 'C': return '=3*A' + number + '^2+2*A' + number + '-5';
    }
  }

  function mount(host, onChange) {
    let rows = [], selection = {column:'B', number:2};
    const paper = document.createElement('div');
    paper.className = 'newton-paper';
    paper.append(...host.childNodes);
    const live = document.createElement('div');
    live.className = 'newton-sheet';
    host.append(paper,live);
    host = live;
    host.innerHTML = `
      <div class="newton-inputs">
        <label>Starting value (A2) <input type="number" step="any" value="0" aria-label="Starting value in A2"></label>
        <span class="newton-address"></span><output class="newton-formula" aria-label="Selected cell formula"></output>
      </div>
      <table aria-label="Newton–Raphson worksheet">
        <thead><tr><th scope="col"></th><th scope="col">A · <i>x</i><sub>n</sub></th><th scope="col">B · <i>f</i>(<i>x</i><sub>n</sub>)</th><th scope="col">C · <i>f</i>′(<i>x</i><sub>n</sub>)</th></tr></thead>
        <tbody></tbody>
      </table>
      <div class="newton-actions"><button type="button" class="newton-next">Next row</button><button type="button" class="newton-reset">Reset</button><span class="newton-message" role="status"></span></div>`;
    const input = host.querySelector('input');
    const body = host.querySelector('tbody');
    const nextButton = host.querySelector('.newton-next');
    const resetButton = host.querySelector('.newton-reset');
    const status = host.querySelector('.newton-message');
    const canAdvance = () => {
      if (!rows.length) return false;
      const [x, fx, derivative, next] = rows.at(-1).values;
      return derivative !== 0 && [fx,derivative,next].every(Number.isFinite) && next !== x;
    };
    function showFormula() {
      const {column, number} = selection;
      host.querySelector('.newton-address').textContent = column + number;
      host.querySelector('.newton-formula').textContent = rows.length ? formula(column,number,input.valueAsNumber) : '—';
      for (const cell of body.querySelectorAll('button')) {
        const selected = cell.dataset.column === column && Number(cell.dataset.row) === number;
        cell.setAttribute('aria-pressed',String(selected));
        const row = Number(cell.dataset.row);
        const referenced = column === 'A' ? row === number - 1 :
          row === number && cell.dataset.column === 'A';
        cell.classList.toggle('referenced-cell', referenced);
      }
    }
    function draw() {
      const fragment = document.createDocumentFragment();
      const visibleRows = rows.slice(-rowLimit);
      for (let i = 0; i < rowLimit; i++) {
        const data = visibleRows[i];
        const number = data?.number ?? (visibleRows[0]?.number ?? 2) + i;
        const tr = document.createElement('tr');
        const header = document.createElement('th');
        header.scope = 'row';
        header.textContent = String(number);
        tr.append(header);
        for (const [index,column] of ['A','B','C'].entries()) {
          const td = document.createElement('td');
          if (data) {
            const button = document.createElement('button');
            button.type = 'button';
            button.dataset.row = String(number);
            button.dataset.column = column;
            button.textContent = display(data.values[index]);
            button.setAttribute('aria-label',column + number + ', ' + button.textContent + ', inspect formula');
            td.append(button);
          }
          tr.append(td);
        }
        fragment.append(tr);
      }
      body.replaceChildren(fragment);
      const latest = rows.at(-1);
      let message = 'Select a cell to inspect its formula.';
      if (!latest) message = 'Enter a finite starting value in A2.';
      else if (latest.values[2] === 0) message = 'The tangent is horizontal. Choose another starting value.';
      else if (!latest.values.every(Number.isFinite)) message = 'This calculation exceeds the numerical range. Choose another starting value.';
      else if (!canAdvance()) message = 'The approximation has stabilised at the precision of this worksheet.';
      status.textContent = message;
      nextButton.disabled = !canAdvance();
      showFormula();
      onChange();
    }
    function restart() {
      rows = Number.isFinite(input.valueAsNumber) ? [makeRow(input.valueAsNumber,2)] : [];
      selection = {column:'B',number:2};
      draw();
    }
    function advance() {
      if (!canAdvance()) return;
      const latest = rows.at(-1);
      rows.push(makeRow(latest.values[3],latest.number + 1));
      if (rows.length > rowLimit) rows.shift();
      selection = {column:'A',number:latest.number + 1};
      draw();
    }
    function reveal() {
      // A worksheet page has seven visible rows. The teacher can continue beyond the page.
      for (let i=1; i<rowLimit && canAdvance(); i++) advance();
    }
    input.addEventListener('input',restart);
    input.addEventListener('keydown',event => event.stopPropagation());
    body.addEventListener('click',event => {
      const cell = event.target.closest('button');
      if (cell) {
        selection = {column:cell.dataset.column, number:Number(cell.dataset.row)};
        showFormula();
      }
    });
    nextButton.addEventListener('click',advance);
    resetButton.addEventListener('click',() => { input.value = '0'; restart(); });
    restart();
    return {advance,canAdvance,reveal};
  }
  function preparePrint(canvas, config) {
    if (!config) return;
    canvas.querySelector('.newton-sheet')?.remove();
    canvas.querySelector('.newton-paper')?.classList.remove('newton-paper');
    canvas.querySelector('[data-shape="' + config.printedFormulas + '"]')?.classList.remove('is-hidden');
  }
  window.LUISA_NEWTON_SHEET = {mount,preparePrint};
})();
