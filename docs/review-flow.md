# Review Flow

## 1. Run a pack

```bash
python3 src/cli.py run --agent iris
python3 src/cli.py run --agent rex
python3 src/cli.py run-shared --pack golden:anti-bullshit
```

## 2. Inspect the pack summary

Each run now writes:
- per-case JSON and markdown files in `runs/`
- aggregate pack summaries in `runs/summaries/`

The aggregate summary shows:
- total cases
- eligible candidates
- review candidates
- discarded candidates
- golden regressions
- grouping by agent

## 3. Review candidate disposition

Use the summary as the top-level review surface:
- **eligible** = candidate looks good enough for human promotion review
- **review** = candidate needs judgement, unclear or flat result
- **discard** = candidate should not be promoted

## 4. Promote or reject explicitly

```bash
python3 src/cli.py promote --agent francis --candidate candidate-001 --approved-by leo --notes "Approved after review"
python3 src/cli.py reject --agent forge --candidate candidate-003 --approved-by leo --notes "Rejected after review"
```

## 5. Golden case rule

If a golden case regresses, treat that as a strong stop signal. Golden cases exist to prevent polished nonsense from quietly becoming baseline.
