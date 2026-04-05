# Loopsmith

Loopsmith is an eval-driven framework for improving multi-agent systems through controlled candidate changes, evidence-based comparison, and explicit promotion boundaries.

## V1 scope

Loopsmith v1 focuses on the shortest path to something real:

1. repo skeleton
2. eval schema
3. run logging schema
4. mutation boundaries
5. loop runner
6. 3 strong demo agents
7. starter packs for the rest
8. public sanitisation

## Core model

Each loop compares:
- a **baseline**
- a **candidate**
- one or more **eval cases**
- a **verdict**: keep, discard, or review

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

## V1 deep demos

- Francis
- Nox
- Forge

The other agents ship with starter profiles and starter eval packs in v1.

## Design rules

- No giant-file soup
- Split by concern
- Explicit mutation boundaries
- Human promotion gate for meaningful changes
- Public-safe structure from the start

## Layout

- `agents/` — agent profiles
- `evals/` — eval pack definitions
- `policies/` — mutation boundaries and promotion rules
- `candidates/` — candidate variants under test
- `runs/` — generated run logs and results
- `src/` — loop runner and schemas
- `docs/` — design notes and sanitisation notes

## Status

This repo is being built privately first inside the OpenClaw workspace. It will only be sanitised and pushed public after the loop is real.
