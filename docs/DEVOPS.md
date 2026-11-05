# Development and release workflow
Owner approved automatic future publishing on 2026-11-01, after checks. Public URL stays https://fmq-6d9.pages.dev/ ; repository is renamed Luisa, retaining its ID/history. No new paid services or schedules.

## One bounded job
1. Read the short handoff/rules and relevant requirement IDs. Inspect git status, worktrees and open PRs. Never replace unfinished owner work.
2. Create an issue with a user goal, requirement IDs, acceptance checklist, tests/manual evidence, risk and dependencies. One branch and PR per job. Group tiny related documentation chores.
3. Implement on `task/<issue>-<slug>`; the lead owns shared CI/config/catalogues. Use targeted tests, one heavy job at a time. Delegation only when authorised; fresh brief and worktree, no forks.
4. Run `python3 scripts/luisa.py gate`. This checks register consistency, available catalogue resources, file sizes, tooling tests, basic secret patterns and static packaging. Source/maths/visual/interaction/print checks remain explicit for teaching changes.
5. Review the diff before opening PR. Use an independent reviewer for security, routing, shared rendering/print geometry or complex mathematics; self-review focused documentation chores. Record findings; fix instead of suppressing checks.
6. Push branch, open PR with acceptance table. Wait for `build`, `test`, `scan` on the exact head; missing or failed required checks prevent landing. Squash merge through `scripts/land.py` when authenticated GitHub CLI is available, or the equivalent reviewed GitHub UI flow. No force pushes or direct production edits.
7. Cloudflare builds the merged commit using `python3 scripts/luisa.py gate` with output directory `dist` once dashboard configuration is confirmed. GitHub main protections must require build/test/scan. Until both are verified, report the enforcement gap; never claim gates are enforced just because files exist.
8. Verify build-manifest revision/version and actual changed slides/JSON/PDF destinations online; reject HTML fallback bodies. A pipeline start is not successful publication. Record release evidence, update handoff and send the mandatory final owner email under standing authorisation FR-024, unless the owner explicitly defers that particular report. Follow docs/handoff/RELEASE-EMAIL.md; preserve and report any pending notification.

## Build, run and rollback
`python3 scripts/luisa.py build` creates `dist/` and a SHA256 file manifest. The public artifact excludes docs, .git, materials, usage and credentials. Unmarked directories cannot be erased by the build. Serve with `python3 scripts/luisa.py serve --directory dist --port 8778`; loopback only.
Use the same checked artifact for Cloudflare, ADA and local preview. Keep commit SHA and artifact digest with each release. Roll back via Cloudflare's known successful deployment or rebuild the prior checked Git revision in a separate worktree; never reset/overwrite working main. Verify the rollback online.

The local master remains _LUISA/website; materials/ and backups/ stay alongside. Private WORKSPACE.json in LUISA_STATE_DIR maps machine paths, mail sender and authoring roots. New machine: clone repo, install Python reference, gate/build/serve; supply private source materials only for chapter-authoring tasks. Full historical slide-generation environment is not yet portable.

## Provider and host boundaries
GitHub rename must retain repository ID; update local origin and references. Cloudflare project name/public hostname do not need to change. Confirm Git integration follows the renamed repo and deploys the new SHA. If GitHub App access is tied to a former selected name, the owner may need to reconnect; never grant broader access silently.
Public runtime needs no credentials. Mail and ADA are separate private adapters; credential creation/expansion remains an owner step. Do not put SSH endpoints, mailbox passwords or local owner paths into public docs.

CI uses Python 3.12.8, pinned action commit SHAs, read-only contents permission, timeouts and concurrency cancellation. Current pattern scan is not a replacement for GitHub full-history secret scanning; the latter is a separate setup item. Requirements evidence must not be inferred from CI coverage.

## Required ADA copy after every website release
After each checked production release, copy the same dist artifact to ADA's established public directory through the existing private SSH adapter. Credentials, host, target and browser URL live in private WORKSPACE.json. Files there are served automatically: do not run a Python HTTP server, expose port 8000 or request SSH forwarding.

Use document-relative asset/navigation URLs and explicit .html page destinations. Never assume deployment at /. Catalogue JSON/PDF links must also stay within the deployment prefix. Test with a plain static server under a non-root prefix before release. The SW cache revision must change when cached runtime files change.

Stage the complete artifact outside public, verify every manifest hash on ADA, then replace the public tree using the established deployment scope. Do not copy source books, development docs, Git metadata or usage/credentials into public. Verify the live manifest matches the released Git revision and check logo/CSS, skill and textbook views, teaching chapter navigation, a lesson JSON and booklet/textbook PDFs. Report an ADA failure as an incomplete release even if Cloudflare succeeds.

## ADA retention (owner instruction 2026-11-03)
Keep only the latest verified Luisa release on ADA. Do not retain historical Luisa releases, source/deployment ZIPs or completed staging folders there. Recovery artifacts remain outside ADA (Cloudflare and the local OneDrive backup). Check disk capacity before staging; reuse identical files from the current deployment where possible. Verify the staged artifact and activate by directory switch rather than duplicating the complete release. After live verification, remove superseded Luisa directories and temporary staging artifacts, preserving unrelated server files.

PDF reader modules use .js filenames because ADA serves .mjs as application/octet-stream. Verify the live module Content-Type as well as its hash; local browser testing alone cannot establish host MIME compatibility.
