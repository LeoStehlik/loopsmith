# Evaluator Strategy

## Default rule

Use the **generic evaluator** by default.

Most cases do not need custom logic. If a case can be judged reasonably through:
- required checks
- forbidden checks
- rubric dimensions
- anti-goal penalties

then it should stay generic.

## When a case-specific evaluator is justified

Use a **case-specific evaluator** only when all of these are true:

1. the case is expensive to misjudge
2. structural correctness matters more than wording style
3. heuristic scoring alone is too weak or too gameable
4. the custom logic can stay small and inspectable

## Current examples

### Forge — proof before done
Why custom logic exists:
- "done" claims without proof are expensive
- proof, verification, and tests matter structurally
- good wording alone is not enough

### Iris — AC verdict discipline
Why custom logic exists:
- QA can sound convincing while avoiding explicit verdict structure
- PASS / FAIL / UNKNOWN discipline matters structurally
- thoughtful tone is not the same as correct verdicting

### Rex — layered reporting honesty
Why custom logic exists:
- partial success often gets inflated into overall success
- reporting structure matters
- explicit layer/sprint pass/fail discipline is important

## What should stay generic for now

Keep a case generic if:
- it is mostly about tone or broad usefulness
- a small set of checks already captures the behaviour well
- the custom logic would be more complex than the case deserves
- there is no clear expensive failure mode

## Anti-patterns

Do not add a custom evaluator just because:
- the score feels slightly imperfect
- the case could be made "smarter"
- a plugin architecture sounds impressive
- we want symmetry across all cases

## Practical rule

Custom evaluators are exceptions for hard, proof-heavy cases.
Generic evaluators remain the default path.
