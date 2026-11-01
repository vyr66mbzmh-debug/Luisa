# Luisa
Mathematics teaching slides, student booklets, textbook chapters and practice libraries.

**New agent or new chat:** start with [START-HERE](docs/handoff/START-HERE.md), then [HANDOFF](HANDOFF.md) and [AGENTS](AGENTS.md). The [requirements table](docs/requirements/REQUIREMENTS.md) is generated from the [canonical register](docs/requirements/register.json).

Repository: https://github.com/vyr66mbzmh-debug/Luisa
Production: https://fmq-6d9.pages.dev/ — the existing public address is deliberately retained.

## Developer commands
Python 3.12.8 is the pinned CI reference; stdlib tooling also supports Python 3.12–3.15. No package installation is needed for the static site tooling.

```sh
python3 scripts/luisa.py gate
python3 scripts/luisa.py build
python3 scripts/luisa.py serve --directory dist
```
Open http://127.0.0.1:8778/ . The build creates a deployable `dist/` and checksum manifest without private authoring files. It does not rebuild historical teaching content. Serving requires HTTP, not opening index.html directly.

See [architecture](docs/ARCHITECTURE.md), [twelve-factor mapping](docs/TWELVE-FACTOR.md), [DevOps](docs/DEVOPS.md), [roadmap](docs/ROADMAP.md), [acceptance](docs/ACCEPTANCE.md), [owner setup](docs/OWNER-ACTIONS.md) and [usage](docs/usage/README.md). Historical README files are not current instructions. Source textbooks/PPTX and full lesson-authoring tools remain in the owner's separate materials workspace; cloning this repo reproduces the deployed site, not all original source authoring.
