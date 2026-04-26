# Usage

## Run an agent pack

```bash
python3 src/cli.py run --agent conductor
python3 src/cli.py run --agent scout
python3 src/cli.py run --agent forge
python3 src/cli.py run --agent iris
python3 src/cli.py run --agent rex
```

## Run with JSON output

```bash
python3 src/cli.py run --agent conductor --json
```

## Run shared golden cases

```bash
python3 src/cli.py run-shared --pack golden:anti-bullshit
```

Shared packs are first-class Loopsmith objects with explicit metadata and participating agents.

## Review summaries

Each run writes aggregate summaries to `runs/summaries/`.

The console output also shows:
- total cases
- eligible count
- review count
- discard count
- golden regressions count
- summary file locations
- review queue path
- promotion index path
- baseline provenance path

## Operator views

Generated automatically after runs, promotions, and rejections:
- `runs/review-queue.md`
- `runs/review-queue.json`
- `runs/promotion-index.md`
- `runs/promotion-index.json`
- `runs/baseline-provenance.md`
- `runs/baseline-provenance.json`

## Promote a candidate

Promotion requires explicit human approval.

```bash
python3 src/cli.py promote --agent conductor --candidate candidate-001 --approved-by reviewer --notes "Approved after review"
```

## Reject a candidate

```bash
python3 src/cli.py reject --agent forge --candidate candidate-003 --approved-by reviewer --notes "Rejected after review"
```

## Current focus

- richer scoring modes
- promotion flow
- file-driven runner
- Iris and Rex proof packs
- anti-bullshit golden cases
- pack-level review summaries
- operator views for review, promotion state, and baseline provenance
- shared packs as first-class objects
- research-brief quality packs for anti-sludge and signal-density tuning

## Research brief quality example

Scout now also carries a public example of a research-brief signal-density candidate:

- policy: `candidates/scout/research-policy-v3.md`
- manifest: `candidates/scout/candidate-signal-density.json`
- sample response: `candidates/scout/responses/candidate-signal-density.txt`
- pattern note: `docs/research-brief-quality-pack.md`

This is the right Loopsmith shape when a research agent is factually competent but too repetitive, too complete, or too padded to be genuinely useful.
