# Shared Packs

## What a shared pack is

A shared pack is a Loopsmith pack that spans multiple agents instead of belonging to just one.

Use a shared pack when the thing you want to detect is a cross-agent pattern, for example:
- robotic replies
- vague verdicts
- false completion claims
- generic sludge
- other trust-failure families

## How shared packs differ from agent packs

### Agent pack
- centred on one agent
- loaded from that agent profile
- run with `python3 src/cli.py run --agent <agent>`

### Shared pack
- has explicit pack metadata
- declares participating agents
- groups multiple cross-agent cases together
- run with `python3 src/cli.py run-shared --pack <pack-id>`

## Current example

Loopsmith ships with:
- `golden:anti-bullshit`

This is a shared golden pack that checks trust-killing failure patterns across multiple agents.

## File shape

A shared pack has:
- `pack.json` — pack metadata
- `cases.json` — the shared cases

Example layout:

```text
evals/shared/anti-bullshit/
  pack.json
  cases.json
```

## Why this matters

Shared packs are one of the clearest ways to express that some failure modes are not role-local. They are system-level behavioural problems that show up in different agents with different wording.
