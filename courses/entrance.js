'use strict';

let entranceDesign = 'formation';
let stopLogo;
const completedLogos = new Set();

try {
  const saved = localStorage.getItem('luisa-entrance-choice');
  if (Object.hasOwn(logoDesigns, saved)) entranceDesign = saved;
} catch {}

function releaseLogo() {
  if (stopLogo) stopLogo();
  stopLogo = null;
}

function mountEntrance() {
  main.replaceChildren(document.getElementById('entrance-template').content.cloneNode(true));
  const select = document.getElementById('design-select');
  const banner = main.querySelector('.banner-frame');
  const motion = main.querySelector('#motion');

  for (const [id, design] of Object.entries(logoDesigns)) {
    select.append(new Option(design.label, id, false, id === entranceDesign));
  }
  function draw() {
    releaseLogo();
    const id = entranceDesign;
    stopLogo = mountLogo(banner, id, motion, completedLogos.has(id), () => completedLogos.add(id));
  }
  select.onchange = () => {
    entranceDesign = select.value;
    completedLogos.delete(entranceDesign);
    try { localStorage.setItem('luisa-entrance-choice', entranceDesign); } catch {}
    draw();
  };
  draw();
}
