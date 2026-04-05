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

## V2 focus

### Phase 1 — Scoring
- support `pass_fail`, `rubric`, and `composite`
- add hard checks, rubric dimensions, and anti-goals as schema-level concepts
- keep golden cases as regression guards

### Phase 2 — Promotion flow
- explicit `baseline/`, `candidates/`, `promoted/`, and `rejected/` states
- human review gate for promotion
- durable promotion ledger

### Phase 3 — File-driven runner
- load profiles from `agents/`
- load evals from `evals/`
- load candidates from `candidates/`
- provide a real CLI
- emit machine-readable and human-readable outputs

## V2 deep demos

- Francis
- Nox
- Forge

## Deferred until after core hardening

- deep expansion of Iris and Rex
- broader pack depth for Chip, Spark, and Nova
- hidden case sophistication beyond core support
- judge-model scoring
- UI or hosted service work
