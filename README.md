# Loopsmith

**Loopsmith** is an eval-driven framework for improving multi-agent systems through controlled candidate changes, evidence-based comparison, and explicit promotion boundaries.

**Tagline:** Improve agents the way you improve software: define the eval, test the candidate, keep only what survives evidence.

## What it is for

Use Loopsmith when an agent is producing output that is:
- good enough to be dangerous
- repetitive or sludgy
- hard to trust
- hard to review consistently
- drifting after prompt or policy changes

Loopsmith is for cases where taste alone is not enough and blind prompting is not good enough.

It helps answer questions like:
- Is this candidate actually better than the baseline?
- Did we improve the output or just rewrite it differently?
- Which failures should block promotion?
- What is live right now, and why?

## What it is not for

Loopsmith is not a chatbot wrapper, a benchmark vanity project, or a generic agent platform.

It is not trying to replace judgment. It is trying to make judgment more disciplined.

## The loop

Each loop compares:
- a **baseline**
- a **candidate**
- one or more **eval cases**
- a **verdict** and **promotion state**

A candidate must improve evidence, not just sound clever.

## One concrete example

A research agent can be factually competent but still painful to read. The brief may repeat the same thesis across sections, keep weak topics alive, and bury the useful signal under repetitive scaffolding.

Loopsmith can treat that as a bounded quality problem:
- baseline = current research brief policy
- candidate = shorter, sharper signal-density policy
- eval = anti-sludge, anti-repetition, weak-topic-drop checks
- promotion = only after the candidate clearly beats the baseline

See:
- `docs/research-brief-quality-pack.md`
- `candidates/scout/research-policy-v3.md`
- `candidates/scout/candidate-signal-density.json`

## The kinds of failures Loopsmith can catch

Loopsmith is useful for recurring failure modes such as:
- robotic direct-chat replies
- generic research sludge
- false completion claims
- vague QA verdicts
- proof without proof
- cumulative regression dishonesty
- repetitive scaffolding that hides weak signal

## Repo layout

- `agents/` — agent profiles
- `evals/` — agent and shared eval pack definitions
- `baseline/` — current baseline outputs or fixtures
- `candidates/` — candidate variants under test
- `promoted/` — promoted candidate manifests
- `rejected/` — rejected candidate manifests
- `ledger/` — promotion history
- `policies/` — mutation boundaries and promotion rules
- `runs/` — generated run logs, summaries, review queue, promotion index, and provenance views
- `src/` — schemas, scoring, loaders, runner, CLI, summaries, operator views
- `docs/` — design notes, usage, review flow, artifact policy, evaluator strategy, shared-pack guidance, sanitisation notes, and pack patterns

## CLI examples

```bash
python3 src/cli.py run --agent conductor
python3 src/cli.py run --agent scout --json
python3 src/cli.py run --agent iris
python3 src/cli.py run --agent rex
python3 src/cli.py run-shared --pack golden:anti-bullshit
python3 src/cli.py promote --agent conductor --candidate candidate-001 --approved-by reviewer
```

## Research brief quality packs

Loopsmith can improve research agents that are technically competent but operationally dull to read.

A research brief quality pack can encode recurring failure modes like:
- repeated thesis inflation
- template fatigue across sections
- weak-topic retention
- reader-specific scaffolding bloat
- fake completeness instead of signal density

See `docs/research-brief-quality-pack.md` for the public pattern.

## Operator views

Once a repo has multiple packs and promotion states, the human operator needs a clean control surface.
Loopsmith generates:
- pack summaries
- a review queue
- a promotion index
- a baseline provenance view

so a reviewer can quickly see what is eligible, what needs review, what regressed, what is currently live, and where that live state came from.

## Shared packs

Some failure modes are not agent-local. Shared packs let Loopsmith express cross-agent behavioural families as first-class objects with explicit metadata, participating agents, and clearer operator-facing summaries.

## Evaluator-specific logic

Some cases are too important to judge with loose heuristics alone. Loopsmith supports case-specific evaluators for proof-heavy checks such as:
- Forge proof-before-done
- Iris AC verdict discipline
- Iris review-vs-validation boundary
- Rex cumulative regression honesty
- Rex layered reporting honesty

## Current status

Loopsmith shipped a real v1 and is now moving through hardening passes. The public-share cleanup is documented in `docs/recovery-pass.md`.

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
10. documented evaluator strategy and selective expansion rules
11. artifact policy and baseline provenance views
12. shared packs as first-class objects with metadata
13. reusable research-brief quality pack pattern for anti-sludge and signal-density tuning

## Current deep areas

- Conductor
- Scout
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
