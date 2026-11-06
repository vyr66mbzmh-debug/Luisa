// All teaching players expose the same three toolbar actions.
(() => {
  const region = document.getElementById('slide-region');
  if (!region) return;
  region.style.touchAction = 'pan-y pinch-zoom';
  const controls = 'button, a, input, select, textarea, summary, [role="button"], [contenteditable="true"]';
  let start;

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
    let action;
    if (Math.abs(dx) >= 45 && Math.abs(dx) > 1.5 * Math.abs(dy)) {
      action = dx < 0 ? 'next' : 'previous';
    } else if (Math.hypot(dx, dy) <= 10 && !event.target.closest(controls)) {
      action = 'next-step';
    } else {
      return;
    }
    if (event.cancelable) event.preventDefault(); // Suppress the extra click generated after a handled touch.
    document.getElementById(action).click();
  }, { passive: false });
})();
