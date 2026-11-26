'use strict';
window.mountLessonMedia = function (slide, find) {
  for (const shape of slide.shapes) {
    if (!shape.media) continue;
    const host = find(shape.id);
    const {type, id} = shape.media;
    const movie = type === 'youtube';
    if (!host || !(movie ? /^[\w-]{11}$/ : /^[a-z0-9]{8}$/).test(id)) continue;
    const link = document.createElement('a');
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'lesson-media-link';
    link.href = movie ? 'https://www.youtube.com/watch?v=' + id : 'https://www.geogebra.org/calculator/' + id;
    link.textContent = movie ? 'Open in YouTube ↗' : 'Open in GeoGebra ↗';
    const mount = () => {
      const frame = document.createElement('iframe');
      frame.className = 'lesson-media-frame';
      frame.title = movie ? 'Film clip from 21' : 'Newton–Raphson interactive diagram';
      frame.allowFullscreen = true;
      frame.allow = movie ? 'autoplay; encrypted-media; fullscreen' : 'fullscreen';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.src = movie ? 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1' :
                          'https://www.geogebra.org/calculator/' + id + '?embed';
      host.append(frame);
      return frame;
    };
    if (movie) {
      const play = document.createElement('button');
      play.className = 'lesson-media-play';
      play.type = 'button';
      play.textContent = '▶  Play clip';
      play.setAttribute('aria-label', 'Play film clip in full screen');
      play.addEventListener('click', () => {
        play.remove();
        const frame = mount();
        frame.requestFullscreen?.().catch(() => frame.focus());
      });
      host.append(play);
    } else {
      const toggle = document.createElement('button');
      toggle.type = 'button';
      host.classList.add('lesson-geogebra');
      toggle.className = 'lesson-media-toggle';
      toggle.textContent = 'Explore in GeoGebra';
      toggle.setAttribute('aria-pressed', 'false');
      let graph = null;
      toggle.addEventListener('click', () => {
        if (graph) {
          graph.remove();
          graph = null;
        } else {
          graph = mount();
        }
        toggle.textContent = graph ? 'Show graph' : 'Explore in GeoGebra';
        toggle.setAttribute('aria-pressed', String(Boolean(graph)));
      });
      host.append(toggle);
    }
    host.append(link);
  }
};
