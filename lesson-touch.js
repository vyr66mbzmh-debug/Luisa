// All teaching players expose the same three toolbar actions.
(() => {
  const region = document.getElementById('slide-region');
  if (!region) return;
  region.style.touchAction = 'pan-y pinch-zoom';
  const controls = 'button, a, input, select, textarea, summary, [role="button"], [contenteditable="true"]';
  let start;
  let mouseStart;
  let suppressDragClick = false;

  function horizontalAction(dx, dy) {
    if (Math.abs(dx) < 45 || Math.abs(dx) <= 1.5 * Math.abs(dy)) return;
    return dx < 0 ? 'next' : 'previous';
  }

  region.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    suppressDragClick = false;
    mouseStart = { x: event.clientX, y: event.clientY };
  });
  window.addEventListener('blur', () => { mouseStart = null; });
  window.addEventListener('pointerup', event => {
    if (!mouseStart || event.pointerType !== 'mouse') return;
    const action = horizontalAction(event.clientX - mouseStart.x, event.clientY - mouseStart.y);
    mouseStart = null;
    if (!action) return;
    suppressDragClick = true;
    document.getElementById(action).click();
    window.getSelection()?.removeAllRanges();
  });
  region.addEventListener('dragstart', event => {
    if (mouseStart) event.preventDefault();
  });
  region.addEventListener('click', event => {
    if (!suppressDragClick || !event.isTrusted) return;
    suppressDragClick = false;
    event.preventDefault();
    event.stopImmediatePropagation();
  }, true);

  region.addEventListener('touchstart', event => {
    start = event.touches.length === 1 ? event.changedTouches[0] : null;
  }, { passive: true });
  document.addEventListener('touchstart', event => {
    if (event.touches.length > 1) start = null;
  }, { passive: true });
  region.addEventListener('touchcancel', () => { start = null; });
  region.addEventListener('touchend', event => {
    const first = start;
    start = null;
    const last = event.changedTouches[0];
    if (!first || event.touches.length || first.identifier !== last.identifier) return;
    const dx = last.clientX - first.clientX;
    const dy = last.clientY - first.clientY;
    let action = horizontalAction(dx, dy);
    if (!action && (Math.hypot(dx, dy) <= 10 && !event.target.closest(controls))) {
      action = 'next-step';
    }
    if (!action) {
      return;
    }
    if (event.cancelable) event.preventDefault(); // Suppress the extra click generated after a handled touch.
    document.getElementById(action).click();
  }, { passive: false });
})();
