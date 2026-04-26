# Recovery Pass

Date: 2026-04-26

## Goal

Make the repository safe to share publicly now, with a clear public/private boundary and no reliance on private names or workstation-specific paths.

## What changed

### Public naming cleanup

- Replaced private-facing persona names in public docs, eval packs, candidate manifests, baseline fixtures, promoted artifacts, and checked-in run artifacts.
- The former direct-chat example persona now ships as `conductor`.
- The former research example persona now ships as `scout`.
- Replaced operator-specific references with generic labels such as `the operator`, `reviewer`, or equivalent public wording.

### Repo portability cleanup

- Removed workstation-specific absolute paths from `src/wrapper.py`.
- Reworked `src/migration.py` to derive paths from the repo layout and optional environment variables instead of embedding a personal machine path.
- Replaced the private local API host with a loopback default (`127.0.0.1`) and environment override support.

### Public artifact boundary

- Kept the cleanup measured: no large structural rewrite, but renamed the public example directories and checked-in artifacts that exposed private persona names.
- Left general agent architecture intact so the repo story still matches the working system.

## Remaining boundary assumptions

- This pass treats checked-in repo contents as public-facing material and sanitises them accordingly.
- Future private experiments should stay out of the public tree or be isolated before commit.
- If old git history contains secrets or sensitive infra details, history still needs separate review before publishing.

## Suggested single commit summary

`Sanitise public artifacts and generalise persona examples`
