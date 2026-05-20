# Proof Loop Relationship

Loopsmith and Proof Loop are deliberately separate.

## Boundary

Proof Loop is the task-level finish protocol:

- freeze acceptance criteria
- separate builder and verifier roles
- store task-local artifacts
- block self-certified done claims

Loopsmith is the improvement harness:

- compare baseline vs candidate behaviour
- run eval packs
- score recurring failure modes
- promote or reject changes with a ledger
- show what is live now and why

Short version:

> Proof Loop governs a task. Loopsmith improves the agent system over time.

## When To Use Proof Loop

Use Proof Loop for non-trivial coding work where the risk is a false done claim, weak verification, or acceptance criteria drift.

A successful Proof Loop ends with a task-local PASS verdict.

## When To Use Loopsmith

Use Loopsmith when the same failure pattern repeats across tasks or agents.

Examples:

- builders repeatedly claim done without evidence
- verifiers avoid AC-by-AC verdicts
- reviewers approve narrative summaries without live checks
- research agents produce repetitive sludge
- fixers ignore regression risk

A successful Loopsmith loop ends with a promoted candidate, rejected candidate, and durable ledger entry.

## How A Proof Loop Failure Becomes A Loopsmith Eval

1. Take the smallest representative Proof Loop artifact set.
2. Use the task brief, `spec.md`, `evidence.md`, `verdict.json`, or `problems.md` as eval input.
3. Define the expected behaviour and anti-goals.
4. Add the current behaviour as the baseline.
5. Test a candidate prompt, policy, evaluator, or workflow change.
6. Promote only if the candidate improves evidence without regressing golden cases.

## Practical Rule

Do not wrap every Proof Loop task in Loopsmith.

Use Proof Loop for task completion discipline. Use Loopsmith when completion failures reveal a reusable behaviour problem.
