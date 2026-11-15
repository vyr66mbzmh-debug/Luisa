/* KaTeX constructs a few negated relations from two overprinted glyphs.
   Substitute the equivalent single Unicode character so that Chromium and
   Apple Quartz embed and display the same mathematical relation. */
window.prepareBookletMath = function(root) {
  const precomposed = {'=':'≠','∈':'∉','∋':'∌','≈':'≉','≡':'≢','<':'≮','>':'≯','≤':'≰','≥':'≱','∼':'≁','⊂':'⊄','⊃':'⊅','⊆':'⊈','⊇':'⊉'};
  for (const mark of root.querySelectorAll('.katex-html .mrel')) {
    if (mark.children.length || mark.textContent!=='\uE020') continue;
    for(let relation=mark.parentElement;relation && relation.closest('.katex-html');relation=relation.parentElement) {
      const rest=relation.textContent.replace('\uE020','');
      if(!precomposed[rest]) continue;
      relation.replaceChildren(document.createTextNode(precomposed[rest]));
      relation.style.fontFamily='"Times New Roman", Georgia, serif';
      break;
    }
  }
};
