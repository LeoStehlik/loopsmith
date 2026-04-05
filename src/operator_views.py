from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from loaders import ROOT

RUNS_DIR = ROOT / "runs"
SUMMARIES_DIR = RUNS_DIR / "summaries"
LEDGER_PATH = ROOT / "ledger" / "promotion-log.jsonl"
REVIEW_QUEUE_MD = RUNS_DIR / "review-queue.md"
REVIEW_QUEUE_JSON = RUNS_DIR / "review-queue.json"
PROMOTION_INDEX_MD = RUNS_DIR / "promotion-index.md"
PROMOTION_INDEX_JSON = RUNS_DIR / "promotion-index.json"
BASELINE_PROVENANCE_MD = RUNS_DIR / "baseline-provenance.md"
BASELINE_PROVENANCE_JSON = RUNS_DIR / "baseline-provenance.json"


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_summary_files() -> List[Dict[str, object]]:
    if not SUMMARIES_DIR.exists():
        return []
    items = []
    for path in sorted(SUMMARIES_DIR.glob("*.json")):
        try:
            items.append(_read_json(path))
        except Exception:
            continue
    return items


def load_ledger() -> List[Dict[str, object]]:
    if not LEDGER_PATH.exists():
        return []
    records = []
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            continue
    return records


def build_review_queue() -> Dict[str, object]:
    summaries = load_summary_files()
    queue = {
        "eligible": [],
        "review": [],
        "discarded": [],
        "golden_regressions": [],
    }

    for summary in summaries:
        for item in summary.get("eligible_candidates", []):
            queue["eligible"].append({"key": item, "source": summary.get("subject")})
        for item in summary.get("review_candidates", []):
            queue["review"].append({"key": item, "source": summary.get("subject")})
        for item in summary.get("discarded_candidates", []):
            queue["discarded"].append({"key": item, "source": summary.get("subject")})
        for item in summary.get("golden_regression_cases", []):
            queue["golden_regressions"].append({"key": item, "source": summary.get("subject")})

    return queue


def write_review_queue(queue: Dict[str, object]) -> Tuple[Path, Path]:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_QUEUE_JSON.write_text(json.dumps(queue, indent=2), encoding="utf-8")

    lines = ["# Review Queue", "", "_Canonical current-state view: what needs attention next._", ""]
    for key in ["eligible", "review", "discarded", "golden_regressions"]:
        lines.append(f"## {key.replace('_', ' ').title()}")
        lines.append("")
        items = queue.get(key, [])
        if items:
            for item in items:
                lines.append(f"- `{item['key']}` (source: `{item['source']}`)")
        else:
            lines.append("- None")
        lines.append("")

    REVIEW_QUEUE_MD.write_text("\n".join(lines), encoding="utf-8")
    return REVIEW_QUEUE_JSON, REVIEW_QUEUE_MD


def build_promotion_index() -> Dict[str, object]:
    ledger = load_ledger()
    baseline_dir = ROOT / "baseline"
    promoted_dir = ROOT / "promoted"
    rejected_dir = ROOT / "rejected"

    baselines = []
    if baseline_dir.exists():
        for agent_dir in sorted(p for p in baseline_dir.iterdir() if p.is_dir()):
            for path in sorted(agent_dir.glob("*.txt")):
                baselines.append({"agent": agent_dir.name, "eval_id": path.stem, "path": str(path.relative_to(ROOT))})

    promoted = []
    if promoted_dir.exists():
        for agent_dir in sorted(p for p in promoted_dir.iterdir() if p.is_dir()):
            for path in sorted(agent_dir.glob("*.json")):
                promoted.append({"agent": agent_dir.name, "candidate": path.stem, "path": str(path.relative_to(ROOT))})

    rejected = []
    if rejected_dir.exists():
        for agent_dir in sorted(p for p in rejected_dir.iterdir() if p.is_dir()):
            for path in sorted(agent_dir.glob("*.json")):
                rejected.append({"agent": agent_dir.name, "candidate": path.stem, "path": str(path.relative_to(ROOT))})

    return {
        "baselines": baselines,
        "promoted": promoted,
        "rejected": rejected,
        "ledger_records": ledger[-20:],
    }


def write_promotion_index(index: Dict[str, object]) -> Tuple[Path, Path]:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    PROMOTION_INDEX_JSON.write_text(json.dumps(index, indent=2), encoding="utf-8")

    lines = ["# Promotion Index", "", "_Canonical current-state view: what is live, promoted, or rejected._", "", "## Current baselines", ""]
    baselines = index.get("baselines", [])
    if baselines:
        for item in baselines:
            lines.append(f"- `{item['agent']}` / `{item['eval_id']}` → `{item['path']}`")
    else:
        lines.append("- None")
    lines.append("")

    lines += ["## Promoted", ""]
    promoted = index.get("promoted", [])
    if promoted:
        for item in promoted:
            lines.append(f"- `{item['agent']}` / `{item['candidate']}` → `{item['path']}`")
    else:
        lines.append("- None")
    lines.append("")

    lines += ["## Rejected", ""]
    rejected = index.get("rejected", [])
    if rejected:
        for item in rejected:
            lines.append(f"- `{item['agent']}` / `{item['candidate']}` → `{item['path']}`")
    else:
        lines.append("- None")
    lines.append("")

    lines += ["## Recent ledger records", ""]
    records = index.get("ledger_records", [])
    if records:
        for item in records:
            lines.append(
                f"- `{item.get('agent')}` / `{item.get('candidate_id')}` / `{item.get('status')}`"
            )
    else:
        lines.append("- None")
    lines.append("")

    PROMOTION_INDEX_MD.write_text("\n".join(lines), encoding="utf-8")
    return PROMOTION_INDEX_JSON, PROMOTION_INDEX_MD


def build_baseline_provenance() -> Dict[str, object]:
    ledger = load_ledger()
    baseline_dir = ROOT / "baseline"
    provenance_items = []

    promoted_lookup: Dict[tuple[str, str], Dict[str, object]] = {}
    rejected_lookup: Dict[tuple[str, str], Dict[str, object]] = {}

    for record in ledger:
        agent = record.get("agent")
        eval_ids = record.get("eval_ids", [])
        if not agent or not eval_ids:
            continue
        for eval_id in eval_ids:
            key = (agent, eval_id)
            if record.get("status") == "promoted":
                promoted_lookup[key] = record
            elif record.get("status") == "rejected":
                rejected_lookup[key] = record

    if baseline_dir.exists():
        for agent_dir in sorted(p for p in baseline_dir.iterdir() if p.is_dir()):
            for path in sorted(agent_dir.glob("*.txt")):
                key = (agent_dir.name, path.stem)
                promoted_record = promoted_lookup.get(key)
                rejected_record = rejected_lookup.get(key)
                provenance_items.append(
                    {
                        "agent": agent_dir.name,
                        "eval_id": path.stem,
                        "baseline_path": str(path.relative_to(ROOT)),
                        "current_source_candidate": promoted_record.get("candidate_id") if promoted_record else None,
                        "approved_by": promoted_record.get("approved_by") if promoted_record else None,
                        "approved_at": promoted_record.get("approved_at") if promoted_record else None,
                        "last_rejected_candidate": rejected_record.get("candidate_id") if rejected_record else None,
                    }
                )

    return {"items": provenance_items}


def write_baseline_provenance(provenance: Dict[str, object]) -> Tuple[Path, Path]:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    BASELINE_PROVENANCE_JSON.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    lines = [
        "# Baseline Provenance",
        "",
        "_Canonical current-state view: where each current baseline came from._",
        "",
    ]
    items = provenance.get("items", [])
    if items:
        for item in items:
            lines += [
                f"## {item['agent']} / {item['eval_id']}",
                "",
                f"- Baseline: `{item['baseline_path']}`",
                f"- Current source candidate: `{item['current_source_candidate'] or 'unknown'}`",
                f"- Approved by: `{item['approved_by'] or 'unknown'}`",
                f"- Approved at: `{item['approved_at'] or 'unknown'}`",
                f"- Last rejected candidate: `{item['last_rejected_candidate'] or 'none'}`",
                "",
            ]
    else:
        lines.append("- None")
        lines.append("")

    BASELINE_PROVENANCE_MD.write_text("\n".join(lines), encoding="utf-8")
    return BASELINE_PROVENANCE_JSON, BASELINE_PROVENANCE_MD


def refresh_operator_views() -> Dict[str, Tuple[Path, Path]]:
    queue = build_review_queue()
    index = build_promotion_index()
    provenance = build_baseline_provenance()
    queue_paths = write_review_queue(queue)
    index_paths = write_promotion_index(index)
    provenance_paths = write_baseline_provenance(provenance)
    return {
        "review_queue": queue_paths,
        "promotion_index": index_paths,
        "baseline_provenance": provenance_paths,
    }
