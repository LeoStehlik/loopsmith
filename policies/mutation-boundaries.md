# Mutation Boundaries

Loopsmith must not turn into uncontrolled self-editing prompt soup.

## Levels

### L1 — Low risk
Safe to evaluate and iterate frequently.

Examples:
- eval metadata
- scoring thresholds
- rubric wording
- tags
- example cases
- non-production docs

### L2 — Medium risk
Can be tested as candidates, but promotion requires explicit human review.

Examples:
- prompt variants
- brief templates
- routing heuristics
- role-policy snippets
- response policy fragments
- candidate harness settings

### L3 — High risk
Do not auto-promote. Human review required before any live use.

Examples:
- core identity rules
- safety boundaries
- production defaults
- model/provider defaults
- memory retrieval strategy in production

## Forbidden surfaces
Never mutate through Loopsmith candidates:

- secrets
- API keys
- tokens
- passwords
- private infra addresses
- customer names
- customer-specific prompts
- production auth material

## Promotion rule
A candidate may be promoted only if:
1. it improves or protects a measured outcome
2. it does not regress golden cases
3. it does not violate mutation boundaries
4. a human explicitly approves the promotion

## Design rule
Loopsmith compares candidates against baselines. It does not get to quietly rewrite the soul of the system.
