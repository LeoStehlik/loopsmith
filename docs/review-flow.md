# Review Flow

## 1. Run a pack

```bash
python3 src/cli.py run --agent iris
python3 src/cli.py run --agent rex
python3 src/cli.py run-shared --pack golden:anti-bullshit
```

For shared packs, Loopsmith now loads explicit pack metadata and participating-agent information before running cases.

## 2. Inspect the pack summary

Each run writes:
- per-case JSON and markdown files in `runs/`
- aggregate pack summaries in `runs/summaries/`
- refreshed operator views in:
  - `runs/review-queue.md`
  - `runs/promotion-index.md`
  - `runs/baseline-provenance.md`

The aggregate summary shows:
- total cases
- eligible candidates
- review candidates
- discarded candidates
- golden regressions
- grouping by agent
- top deltas

For shared packs, the summary also surfaces pack identity and participating agents.

## 3. Inspect the review queue

The review queue answers:
- what is promotion-eligible now?
- what still needs review?
- what was discarded recently?
- did any golden case regress?

## 4. Inspect the promotion index

The promotion index answers:
- what baseline is current?
- what has been promoted?
- what has been rejected?
- what recent approval actions happened?

## 5. Inspect baseline provenance

The provenance view answers:
- where did the current baseline come from?
- which candidate last set it?
- who approved it?
- what was the last rejected candidate if known?

## 6. Promote or reject explicitly

```bash
python3 src/cli.py promote --agent francis --candidate candidate-001 --approved-by leo --notes "Approved after review"
python3 src/cli.py reject --agent forge --candidate candidate-003 --approved-by leo --notes "Rejected after review"
```

These actions refresh the review queue, promotion index, and baseline provenance automatically.

## 7. Evaluator-specific reasons

For some proof-heavy cases, Loopsmith now records evaluator-specific reasons and structural checks. Use these when reviewing Forge, Iris, and Rex runs to understand *why* a candidate was judged eligible or discarded.

## 8. Golden case rule

If a golden case regresses, treat that as a strong stop signal. Golden cases exist to prevent polished nonsense from quietly becoming baseline.
