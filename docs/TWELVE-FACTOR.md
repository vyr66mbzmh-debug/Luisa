# Twelve-factor application of Luisa
Based on https://12factor.net/ . Adapt the methodology to a static site, without adding a server merely to satisfy a checklist.

| Factor | Implementation / boundary |
|---|---|
| I Codebase | One GitHub repository, one main line, separate local/preview/production deployments; materials are external source inputs. |
| II Dependencies | Static packaging/checks use Python stdlib; CI Python and actions pinned; KaTeX vendored and inventoried. Full historical authoring environment portability remains open. |
| III Config | Build/server use environment/CLI inputs; no secrets in browser artifacts. Private environment config is outside Git. |
| IV Backing services | Cloudflare, ADA and mail are replaceable delivery/reporting adapters; no runtime DB. Credentials never bundled. |
| V Build/release/run | Check -> build immutable dist + SHA manifest -> release exact commit/artifact -> serve; do not edit production files. |
| VI Processes | Static requests have no server session state; build/admin commands are one-off processes. |
| VII Port binding | Local server binds 127.0.0.1 and configurable PORT (8778 default); Cloudflare/ADA provide HTTP externally. |
| VIII Concurrency | CDN handles requests; serial heavy authoring/check jobs; no unnecessary application workers. |
| IX Disposability | Static server starts promptly, handles SIGTERM shutdown; immutable artifacts permit rollback. |
| X Dev/prod parity | Serve dist locally and deploy identical relative resource paths; verify Cloudflare clean URLs and ADA subpath separately. |
| XI Logs | Tooling emits JSON events to stdout/stderr; CI retains check results; private usage/evidence logs stay private. |
| XII Admin processes | Build, check, requirements generation, usage logging and release verification are explicit one-off commands from the same revision. |

Do not describe this as a fully migrated dynamic twelve-factor backend. The runtime needs none. Separate authoring reproducibility and deployment-enforcement gaps are listed in OWNER-ACTIONS.md and ROADMAP.md.
