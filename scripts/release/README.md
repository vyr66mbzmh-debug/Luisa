# Release tooling

These tools take a reviewed change from a PR to a verified, archived and reported release on Cloudflare (owner edition) and ADA (staff and pupil editions). The step order is in `docs/agentic/RELEASE-RUNBOOK.md`. Every script reads private values only through `private.py` and never prints them. Results, printed PDFs and records go to `<state>/releases/v<version>/`.

| Script | Use |
|---|---|
| `private.py` | The only reader of `WORKSPACE.json` (`$LUISA_STATE_DIR` or `~/.local/share/luisa-agent-state`). Required key names, leak checks (`assert_no_private_values`), the private work folder, and SSH helpers (BatchMode, strict host keys) |
| `doctor.py` | `luisa.py doctor`: read-only cold-start check. Prints PASS, MISSING (with the human action) or OPTIONAL |
| `docs.py` | `apply docs/releases/v<v>.json --tokens "..."`: release.json, version history, CHANGELOG, ROADMAP, the HANDOFF release block (the old block goes to `docs/handoff/HISTORY.md`) and the report |
| `report.py` | `build`, `check` and `email`: the release report and development-progress page with exactly one handoff (OPS-069). `check` runs in the gate (`luisa.py report`) |
| `land_build.py` | `--pr N --review-record review.json`: exact-head CI, land, fast-forward main, prove the tree, build and check the three editions |
| `verify_owner.py` | Waits for Cloudflare to serve the merged revision, then runs `qa_live.py owner` and `qa_offline.py` |
| `qa_live.py` | `owner`, `ada` or `owner --url <local>` (dry run): live Papers, print, exam paper, manifests and the published report. Expectations come from the build and the metadata. The ADA run uses temporary accounts, which are removed afterwards |
| `qa_offline.py` | PWA offline packs, Papers and print with the network disconnected (`--local` for a dry run) |
| `ada.py` | `status`, `stage`, `activate`, `accounts-check`, `rollback` and `cleanup` for the ADA server (layout from WORKSPACE `ada.layout.*`) |
| `finish.py` | `archive`, `cleanup`, `check-published`, `report --intro` and `complete` (OPS-070) |
| `tokens.py` | Per-call token totals from JSON Lines transcripts (`baseline`, `since`, `total`) for the issue's token log |

Browser scripts use Playwright locators only; there are no string-evaluated waits, so ADA's Content Security Policy is respected. The browser is chosen by `--channel` or `LUISA_BROWSER_CHANNEL` (`chrome`, or `chromium` for Playwright's bundled browser).
