# Loopsmith

**Loopsmith** is an eval-driven framework for improving multi-agent systems through controlled candidate changes, evidence-based comparison, and explicit promotion boundaries.

**Tagline:** Improve agents the way you improve software: define the eval, test the candidate, keep only what survives evidence.

## Current status

Loopsmith shipped a real v1 and is now moving through the next hardening passes.

### V1 delivered
1. repo skeleton
2. initial eval schema
3. initial run logging schema
4. mutation boundaries
5. first loop runner
6. 3 strong demo agents
7. starter packs for the rest
8. public sanitisation

### V2 delivered so far
1. better scoring (`pass_fail`, `rubric`, `composite`)
2. promotion flow with human approval
3. file-driven runner + CLI
4. stronger Iris and Rex packs
5. anti-bullshit golden cases
6. pack-level review summaries
7. stronger shared-pack review flow
8. review queue and promotion index
9. case-specific evaluators for proof-heavy cases

## Core model

Each loop compares:
- a **baseline**
- a **candidate**
- one or more **eval cases**
- a **verdict** and **promotion state**

A candidate must improve evidence, not just sound clever.

## Agents in scope

- Francis
- Forge
- Chip
- Spark
- Nova
- Nox
- Iris
- Rex

## Current deep areas

- Francis
- Nox
- Forge
- Iris
- Rex

The other agents still ship with lighter starter packs while the core is being hardened.

## Design rules

- No giant-file soup
- Split by concern
- Explicit mutation boundaries
- Human promotion gate for meaningful changes
- Public-safe structure from the start

## Layout

- `agents/` — agent profiles
- `evals/` — agent and shared eval pack definitions
- `baseline/` — current baseline outputs or fixtures
- `candidates/` — candidate variants under test
- `promoted/` — promoted candidate manifests
- `rejected/` — rejected candidate manifests
- `ledger/` — promotion history
- `policies/` — mutation boundaries and promotion rules
- `runs/` — generated run logs, summaries, review queue, and promotion index
- `src/` — schemas, scoring, loaders, runner, CLI, summaries, operator views
- `docs/` — design notes, usage, review flow, and sanitisation notes

## CLI examples

```bash
python3 src/cli.py run --agent francis
python3 src/cli.py run --agent nox --json
python3 src/cli.py run --agent iris
python3 src/cli.py run --agent rex
python3 src/cli.py run-shared --pack golden:anti-bullshit
python3 src/cli.py promote --agent francis --candidate candidate-001 --approved-by leo
```

## Why the golden pack matters

Loopsmith is not just for checking success paths. It is also for catching trust-killing failure patterns such as:
- robotic direct-chat replies
- generic research sludge
- false completion claims
- vague QA verdicts
- other forms of operational bullshit

## Why the operator views matter

Once a repo has multiple packs and promotion states, the human operator needs a clean control surface.
Loopsmith now generates:
- pack summaries
- a review queue
- a promotion index

so a reviewer can quickly see what is eligible, what needs review, what regressed, and what is currently live.

## Why evaluator-specific logic matters

Some cases are too important to judge with loose heuristics alone. Loopsmith now supports case-specific evaluators for proof-heavy checks such as Forge proof-before-done, Iris AC verdict discipline, and Rex layered reporting honesty.
