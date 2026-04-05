# Usage

## Run an agent pack

```bash
python3 src/cli.py run --agent francis
python3 src/cli.py run --agent nox
python3 src/cli.py run --agent forge
```

## Run with JSON output

```bash
python3 src/cli.py run --agent francis --json
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

## Current v2 focus

- richer scoring modes
- promotion flow
- file-driven runner

Deep eval expansion for the rest of the agent roster comes after the core is stable.
