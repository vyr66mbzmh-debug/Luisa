// All teaching players expose the same three toolbar actions.
(() => {
  const region = document.getElementById('slide-region');
  if (!region) return;
  region.style.touchAction = 'pan-y pinch-zoom';
  region.tabIndex = -1;
  // Once a slide control fires, Space should continue the teaching sequence.
  // Capture before its listener stops propagation; move focus after that listener.
  const returnFocus = event => {
    if (event.target.closest('[role="button"],button') && !event.target.closest('a,input,select,textarea')) {
      queueMicrotask(() => region.focus({preventScroll:true}));
    }
  };
  region.addEventListener('click', returnFocus, true);
  region.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') returnFocus(event);
  }, true);
  for (const id of ['previous', 'next', 'next-step', 'reset']) {
    document.getElementById(id)?.addEventListener('click', () => region.focus({preventScroll:true}));
  }
  const controls = 'button, a, input, select, textarea, summary, [role="button"], [contenteditable="true"]';
  let start;
  let mouseStart;
  const onControl = event => Boolean(event.target.closest(controls));
  let suppressDragClick = false;

  function horizontalAction(dx, dy) {
    if (Math.abs(dx) < 45 || Math.abs(dx) <= 1.5 * Math.abs(dy)) return;
    return dx < 0 ? 'next' : 'previous';
  }

  region.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse' || event.button !== 0 || onControl(event)) return;
    suppressDragClick = false;
    mouseStart = { x: event.clientX, y: event.clientY };
  });
  window.addEventListener('pointercancel', () => { mouseStart = null; });
  window.addEventListener('blur', () => { mouseStart = null; });
  window.addEventListener('pointerup', event => {
    if (!mouseStart || event.pointerType !== 'mouse') return;
    const action = horizontalAction(event.clientX - mouseStart.x, event.clientY - mouseStart.y);
    mouseStart = null;
    if (!action || !window.getSelection()?.isCollapsed) return;
    suppressDragClick = true;
    document.getElementById(action).click();
    window.getSelection()?.removeAllRanges();
  });
  region.addEventListener('dragstart', event => {
    if (mouseStart) event.preventDefault();
  });
  region.addEventListener('click', event => {
    if (suppressDragClick && event.isTrusted) {
      suppressDragClick = false;
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }, true);

  region.addEventListener('click', event => {
    if (!event.defaultPrevented && !onControl(event) && window.getSelection()?.isCollapsed) document.getElementById('next-step').click();
  });

  // A horizontal wheel gesture can continue delivering momentum after navigation.
  let wheelDistance = 0, wheelUsed = false, lastWheel = -Infinity;
  region.addEventListener('wheel', event => {
    const now = performance.now();
    if (now - lastWheel > 250) {
      wheelDistance = 0;
      wheelUsed = false;
    }
    lastWheel = now;
    if (onControl(event) || event.ctrlKey || Math.abs(event.deltaX) <= 1.5 * Math.abs(event.deltaY)) return;
    if (!event.cancelable) return;
    event.preventDefault();
    if (wheelUsed) return;
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? region.clientWidth : 1;
    wheelDistance += event.deltaX * unit;
    if (Math.abs(wheelDistance) >= 45) {
      wheelUsed = true;
      document.getElementById(wheelDistance > 0 ? 'next' : 'previous').click();
    }
  }, { passive: false });

  region.addEventListener('touchstart', event => {
    start = !onControl(event) && event.touches.length === 1 ? event.changedTouches[0] : null;
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
