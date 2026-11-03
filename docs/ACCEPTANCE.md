# Acceptance and gates
Tooling foundation: build/test/scan checks validate requirements/schema, catalogue destinations, portable output exclusions, checksums, dependency declarations and secret patterns. These are NOT lesson visual/mathematical acceptance.

For every changed chapter:
1. Compare all source teaching content, diagrams, notation and independent animation groups with output.
2. Inspect every initial, individual revealed, fully revealed and Reset state; actual click and Space ordering at board/laptop widths. No scrolling, clipping, gutter colours, overlap or tiny type.
3. Validate mathematics, full answer concealment, source labels and hanging indents.
4. Inspect every booklet page: two original slides/A4, titles/numbers, supplied theory intact, useful handwriting space, omitted answers only.
5. Test slides/booklet/textbook links in both libraries locally and live; check downloaded content is PDF/JSON, not a fallback HTML page.
6. Record artifact/source hashes, date, reviewer, viewports/pages, result and issues. Changed shared code invalidates dependent approvals.

Automatic checks do not count as final source/visual/interaction/print acceptance. User review remains distinct from agent acceptance. Do not bulk upgrade historic status rows.

## v0.25 bounded chapter acceptance

See [four-chapter evidence](evidence/v025-chapters.json): 188 teaching slides, 95 booklet pages and 88 extracted textbook pages. All four chapters received source/mathematics, visual, independent reveal/reset and print checks. Detailed private per-slide/page evidence includes resolved review findings. Library links were checked below a non-root prefix. This does not change historical chapter acceptance or certify PWA-001. Live release verification is separate.

Release verification: [Cloudflare and ADA evidence](evidence/v025-release.json), including identical complete manifests, actual resource hashes and a verified prior ADA recovery copy.

## v0.26 local acceptance
Eleven chapters:571 displayed slides,289 booklet pages,260 textbook pages. Source/mathematics/visual/reveal/print and both libraries checked per docs/evidence/v026-chapters.json. Integration original82 split with owner approval and matching board/booklet numbers. Download all62 available chapter packs passes at root and /AL; all11 requested chapters open offline. Interrupted worker/replacement preserves old offline resources and retries successfully. See docs/evidence/v026-offline-preview.json; physical-platform and owner acceptance boundaries remain explicit. Repository gate:158 requirements,152 destinations,16 tests,6644 packaged files. Deployment pending.
