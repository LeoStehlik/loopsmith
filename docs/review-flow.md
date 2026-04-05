# Review Flow

## 1. Run a pack

```bash
python3 src/cli.py run --agent iris
python3 src/cli.py run --agent rex
python3 src/cli.py run-shared --pack golden:anti-bullshit
```

## 2. Inspect the pack summary

Each run writes:
- per-case JSON and markdown files in `runs/`
- aggregate pack summaries in `runs/summaries/`
- refreshed operator views in:
  - `runs/review-queue.md`
  - `runs/promotion-index.md`

The aggregate summary shows:
- total cases
- eligible candidates
- review candidates
- discarded candidates
- golden regressions
- grouping by agent
- top deltas

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

## 5. Promote or reject explicitly

```bash
python3 src/cli.py promote --agent francis --candidate candidate-001 --approved-by leo --notes "Approved after review"
python3 src/cli.py reject --agent forge --candidate candidate-003 --approved-by leo --notes "Rejected after review"
```

These actions refresh the review queue and promotion index automatically.

## 6. Golden case rule

If a golden case regresses, treat that as a strong stop signal. Golden cases exist to prevent polished nonsense from quietly becoming baseline.
