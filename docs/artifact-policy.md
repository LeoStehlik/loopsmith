# Artifact Policy

Loopsmith generates a mix of files that do not all play the same role.

## 1. Canonical current-state views

These are generated views meant to answer "what is true now?"

Examples:
- `runs/review-queue.md`
- `runs/review-queue.json`
- `runs/promotion-index.md`
- `runs/promotion-index.json`
- `runs/baseline-provenance.md`
- `runs/baseline-provenance.json`

Treat these as operator surfaces.

## 2. Illustrative run artifacts

These show that Loopsmith actually ran and what it produced at a point in time.

Examples:
- per-case files in `runs/`
- pack summaries in `runs/summaries/`

These are useful as evidence and examples, but they are not the same thing as the current live state.

## 3. Current baseline state

The current baseline state lives primarily in:
- `baseline/`
- plus the provenance and promotion views that explain how it got there

A baseline file tells you what is currently live for a case fixture. The provenance/index views help explain where that baseline came from.

## 4. Promotion history

Promotion and rejection history lives in:
- `ledger/`
- `promoted/`
- `rejected/`

Those history-oriented files should be read together with the current-state views, not in isolation.

## 5. Future transient candidates

As the repo grows, some repeated run artifacts may eventually move toward a more transient or ignored model. For now, committed artifacts are acceptable because they show the system working, but that choice is intentional rather than accidental.

## Practical rule

When reading the repo:
- use `baseline-provenance` and `promotion-index` to understand what is current
- use `review-queue` to see what needs attention next
- use `runs/` and `runs/summaries/` as evidence and snapshots, not as the single source of truth
