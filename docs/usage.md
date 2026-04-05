# Usage

## Run an agent pack

```bash
python3 src/cli.py run --agent francis
python3 src/cli.py run --agent nox
python3 src/cli.py run --agent forge
python3 src/cli.py run --agent iris
python3 src/cli.py run --agent rex
```

## Run with JSON output

```bash
python3 src/cli.py run --agent francis --json
```

## Run shared golden cases

```bash
python3 src/cli.py run-shared --pack golden:anti-bullshit
```

## Promote a candidate

Promotion requires explicit human approval.

```bash
python3 src/cli.py promote --agent francis --candidate candidate-001 --approved-by leo --notes "Approved after review"
```

## Reject a candidate

```bash
python3 src/cli.py reject --agent forge --candidate candidate-003 --approved-by leo --notes "Rejected after review"
```

## Current focus

- richer scoring modes
- promotion flow
- file-driven runner
- Iris and Rex proof packs
- anti-bullshit golden cases
