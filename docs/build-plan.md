# Loopsmith Build Plan

## V1 delivered

- repo skeleton
- initial eval schema
- initial run logging schema
- mutation boundaries
- first loop runner
- 3 demo agents
- starter packs for the rest
- public sanitisation

## V2 delivered so far

### Phase 1 — Scoring
- support `pass_fail`, `rubric`, and `composite`
- hard checks, rubric dimensions, and anti-goals as schema-level concepts
- golden cases remain regression guards

### Phase 2 — Promotion flow
- explicit `baseline/`, `candidates/`, `promoted/`, and `rejected/` states
- human review gate for promotion
- durable promotion ledger

### Phase 3 — File-driven runner
- load profiles from `agents/`
- load evals from `evals/`
- load candidates from `candidates/`
- real CLI
- machine-readable and human-readable outputs

### Phase 4 — Proof and anti-bullshit packs
- stronger Iris pack
- stronger Rex pack
- shared anti-bullshit golden pack

## Deferred until after this

- deeper Chip/Spark/Nova work
- hidden-case sophistication beyond current golden support
- judge-model scoring
- UI or hosted service work
