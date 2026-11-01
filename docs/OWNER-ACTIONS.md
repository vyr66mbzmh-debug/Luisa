# Setup controls and owner actions
Do not mark any provider setting complete until verified in that provider.

| Control | State | Action |
|---|---|---|
| GitHub repository rename | Verified | Existing repository is now Luisa; history retained. |
| Public Cloudflare hostname | Retained | Existing fmq-6d9.pages.dev remains authorised. |
| GitHub local remote | Updated | origin points to the renamed repository. |
| GitHub build/test/scan | Verified on foundation branch | GitHub run 41359635498 passed; main protections still pending. |
| Main protections | Pending verification | Require PRs, build/test/scan and linear history; no bypass to hide a failed gate. |
| Cloudflare renamed integration | Verified on preview | Cloudflare check successfully deployed commit 68e5166 from renamed repository. |
| Cloudflare gate build / dist output | Blocked by owner sign-in | Complete existing Apple/Cloudflare authentication; configure gate command and dist output, then verify production. |
| Full-history secret scanning/push protection | Pending verification | Enable supported GitHub controls. Local pattern scan has a narrower scope. |
| GitHub Project and roadmap issue | Pending setup | Repo roadmap exists; reflect real issue state, not manually invented completion. |
| GitHub CLI / integrations | CLI absent locally | Signed-in GitHub UI currently has owner access; connector is read-only. No credential widening is silently performed. |
| Private usage log | Implemented | Outside repository; exact task token usage remains unavailable unless provider reports it. |
| Source authoring dependencies | Follow-up | Private historical build toolchain must be inventoried/pinned before claiming full authoring portability. |
| Restart watchdog / hourly reports | Not enabled by design | New explicit authorisation needed. |

Secrets and private denylist phrases, if desired, must be entered by the owner through GitHub settings, never pasted into prompts or committed. This setup does not require an LLM key or any new deployment credential.
