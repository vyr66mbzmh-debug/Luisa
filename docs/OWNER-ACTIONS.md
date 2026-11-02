# Setup controls and owner actions
Do not mark any provider setting complete until verified in that provider.

| Control | State | Action |
|---|---|---|
| GitHub repository rename | Verified | Existing repository is now Luisa; history retained. |
| Public Cloudflare hostname | Retained | Existing fmq-6d9.pages.dev remains authorised. |
| GitHub local remote | Updated | origin points to the renamed repository. |
| GitHub build/test/scan | Verified on foundation branch | build/test/scan passed on 68e5166 and 389ee96; foundation merged in PR #3; live manifest verified revision 358d1be, version 0.24, clean. |
| Main protections | Verified 2026-11-02 | main rule created: PR required, build/test/scan, up-to-date branch, linear history, bypass disabled; force pushes/deletion disabled. |
| Cloudflare renamed integration | Verified on preview | Cloudflare check successfully deployed commit 68e5166 from renamed repository. |
| Cloudflare gate build / dist output | Configured 2026-11-02 | Command python3 scripts/luisa.py gate; output dist; Python 3.12.8 configured. Live production manifest verified revision 358d1be, version 0.24, clean. |
| Secret Protection / push protection | Verified enabled 2026-11-02 | GitHub security settings show Secret Protection enabled and push protection on. Local pattern scan has a narrower scope. |
| GitHub Project and roadmap issue | Created 2026-11-02 | Luisa development project #1, roadmap issue #2 and foundation PR #3. Status, Priority, PR and Wave fields; built-in item workflows; no new token required. |
| GitHub CLI / integrations | CLI absent locally | Signed-in GitHub UI currently has owner access; connector is read-only. No credential widening is silently performed. |
| Private usage log | Implemented | Outside repository; exact task token usage remains unavailable unless provider reports it. |
| Source authoring dependencies | Follow-up | Private historical build toolchain must be inventoried/pinned before claiming full authoring portability. |
| Restart watchdog / hourly reports | Not enabled by design | New explicit authorisation needed. |

Secrets and private denylist phrases, if desired, must be entered by the owner through GitHub settings, never pasted into prompts or committed. This setup does not require an LLM key or any new deployment credential.
