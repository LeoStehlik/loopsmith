# TODO

## Next steps

### 1. Improve scoring
- Replace token-hit scoring with stronger rubric evaluation.
- Support pass/fail, rubric, and composite scoring with clearer rules.
- Add anti-goal weighting that is less naive than substring checks.

### 2. Add promotion flow
- Introduce explicit `baseline/`, `candidate/`, and `promoted/` structures.
- Add human approval workflow for promotion.
- Record promotion decisions durably.

### 3. Deepen eval packs
- Expand Francis pack beyond one direct-chat golden case.
- Expand Nox pack for source freshness, usefulness, and anti-slop checks.
- Expand Forge pack for proof-before-done and non-regression behaviour.
- Add stronger starter packs for Chip, Spark, Nova, Iris, and Rex.

### 4. Add hidden/golden cases
- Protect against benchmark gaming.
- Add anti-slop and anti-bullshit cases.
- Separate visible starter packs from protected regression cases.

### 5. Improve run reporting
- Add markdown summary reports alongside JSON logs.
- Track duration, model/provider, and optional cost metadata.
- Add comparison summaries across runs.

### 6. Add tests and packaging
- Add basic tests for schemas and runner behaviour.
- Make the runner easier to invoke from CLI.
- Add simple installation and usage guidance.

### 7. Public repo polish
- Add examples to README.
- Add architecture diagram or plain-English flow section.
- Add contribution guidance.
