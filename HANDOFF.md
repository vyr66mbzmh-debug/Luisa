# Luisa handoff
Updated: 2026-11-01. Read AGENTS.md and docs/agentic/LEAD-RULES.md first.

## Current task
Owner authorised GitHub-only rename, twelve-factor static delivery tooling, Davide playbook adaptation, consolidated requirements and cross-provider handoff. Future publishing automatic after checks. Public URL remains https://fmq-6d9.pages.dev/ . Product version stays 0.24 during this infrastructure-only setup.

## State
- Existing GitHub repository renamed to https://github.com/vyr66mbzmh-debug/Luisa ; local origin updated, history retained.
- Foundation branch: chore/agentic-devops-foundation; commit 68e5166 is pushed; GitHub build/test/scan passed (run 41359635498). Not merged to main.
- Canonical register: docs/requirements/register.json (156 requirements). Generated table beside it. Imported assertions retain historical scope and need revalidation.
- Do not use older LESSON_REQUIREMENTS or V10–V13 maintenance policy as current authority.
- Cloudflare preview for 68e5166 succeeded: https://182cb78a.fmq-6d9.pages.dev . Rename integration works; production/gated-dist settings remain pending.
- No product chapter development or new schedules are part of this setup.

## Next exact actions (refresh after landing)
1. Inspect `git status --short` and `git worktree list`; preserve owner work.
2. Local gate passed (156 requirements, 110 destinations, 9 tooling tests, 6155 public files); CI also passed. Re-run after changes.
3. After owner unlocks Mac: open foundation PR against main, review latest docs, require build/test/scan, then squash merge. Complete Cloudflare sign-in and configure gate command + dist; verify deployment manifest.
4. Update this handoff and docs/OWNER-ACTIONS.md with real results. GitHub connector is read-only, shell has no GitHub credential; signed-in Chrome/Desktop were used. Do not bypass access.

## Relevant files
- docs/handoff/START-HERE.md: prompt/links for a fresh agent.
- docs/ARCHITECTURE.md, docs/TWELVE-FACTOR.md, docs/DEVOPS.md.
- docs/requirements/register.json: select relevant IDs, not whole history.
- docs/ROADMAP.md: remaining chapter availability and deferred features.
- docs/ACCEPTANCE.md: source/maths/visual/interaction/print proof.
- scripts/usage.py: private provider/model/task observations; no invented exact Codex cost.
- Private LUISA_STATE_DIR/WORKSPACE.json: machine paths and authoring/mail location.

## Baseline and boundaries
Last known live product is Luisa 0.24. Legacy Maths question completion: 3423/3423 (100%); sections 132/132, separate from expanded indexes and teaching progress. Full fresh acceptance is not inferred from those totals.
The public Git clone serves existing outputs; original decks/books and historical authoring toolchain are private external inputs. New content requires targeted source access.
At task completion stop and wait for owner scope. Future work uses one bounded issue/branch/PR; publish only after required gates and risk review. New features enter deferred scope unless explicitly activated.
