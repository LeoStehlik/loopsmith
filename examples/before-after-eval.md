# Before / After Eval Example

This is the smallest useful Loopsmith story: a recurring agent behaviour is turned into a scored comparison instead of another vague complaint.

## Failure Pattern

A research agent keeps producing briefs that are technically competent but painful to read. The output repeats the same thesis in several sections, keeps weak topics alive, and buries the useful signal under generic scaffolding.

## Baseline

```text
The agent writes a long research brief with repeated sections, several marginal topics, and a polished but low-signal summary. It sounds complete, but the operator still has to dig for the actual point.
```

## Candidate

```text
The candidate policy forces the agent to drop weak topics, avoid repeating the same thesis, and preserve only the highest-signal items with a concrete operator angle.
```

## Eval Pack

The public pattern lives in [`docs/research-brief-quality-pack.md`](../docs/research-brief-quality-pack.md). It checks for:

- repeated thesis inflation
- template fatigue
- weak-topic retention
- fake completeness
- signal density

## Proof Artifact

Run:

```bash
python3 src/cli.py run --agent scout --json
```

Example generated run files:

- [`runs/scout__scout-brief-freshness-001__candidate-002.md`](../runs/scout__scout-brief-freshness-001__candidate-002.md)
- [`runs/review-queue.md`](../runs/review-queue.md)
- [`runs/promotion-index.md`](../runs/promotion-index.md)

The point is not that the candidate sounds nicer. The point is that the repo records why it should be reviewed, promoted, or rejected.
