# Architecture
The app is an existing portable static HTML/CSS/JavaScript site with vendored KaTeX, chapter JSON, question assets and PDF booklets/extracts. Cloudflare Pages serves it. ADA and a local HTTP server can serve the same published artifact. There is no runtime database, SSR server, queue or secret in the browser.

| Concern | Authority / entry point |
|---|---|
| Question view | index.html, app.js, data.js, content/ and existing content bundles |
| Teaching chapter resources | teaching-catalogue.js, teaching-chapters.html |
| Textbook view and mappings | textbook-catalogue.json, textbook-view.js |
| Slide players | lesson-viewer.html, pure1-native-viewer.html, pure2-lesson-viewer.html, teaching-lesson-viewer.html and their renderer modules |
| Print | current PDF outputs under resources/; authoring outside public repo |
| Offline/cache | sw.js; invalidate cache on relevant product changes |
| Current product release | release.json; legacy displayed labels/catalogue metadata still require reconciliation before any later version change |
| Requirements | docs/requirements/register.json |
| Work/state | GitHub issues/PRs; short HANDOFF.md; private state for credentials, raw usage and detailed evidence |

Two catalogues currently duplicate resource routing. Keep them consistent in each change and check both; consolidate only in a separately scoped issue. Mappings identify book, chapter/subtopic and a stable underlying question ID, not copied question content. Future resources carry provider, access, edition, type, URL and topic mappings. Do not invent mapping confidence.

Source/build boundary: static artifact packaging is reproducible from Git; generating fresh slides/booklets currently depends on the private material tree and historical Python/Node/TeX/rendering tools. Portability of that authoring toolchain is a tracked follow-up, not falsely declared complete. New build scripts use stdlib only. Third-party KaTeX remains vendored with its license. Source content rights are separate from tooling licenses; do not apply a blanket license to textbooks or teaching decks.
