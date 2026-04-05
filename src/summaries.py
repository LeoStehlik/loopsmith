from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from schema import EvalResult, utc_now_iso


def build_summary(results: List[EvalResult], run_kind: str, subject: str) -> Dict[str, object]:
    by_agent: Dict[str, Dict[str, object]] = defaultdict(lambda: {
        "count": 0,
        "eligible": 0,
        "discard": 0,
        "review": 0,
        "golden_regressions": 0,
        "cases": [],
    })

    eligible_candidates: List[str] = []
    review_candidates: List[str] = []
    discarded_candidates: List[str] = []
    golden_regressions: List[str] = []

    for result in results:
        bucket = by_agent[result.agent]
        bucket["count"] += 1
        bucket[result.promotion_state] = bucket.get(result.promotion_state, 0) + 1
        if result.golden and result.promotion_state == "discard":
            bucket["golden_regressions"] += 1
            golden_regressions.append(f"{result.agent}:{result.eval_id}:{result.candidate_id}")
        bucket["cases"].append(
            {
                "eval_id": result.eval_id,
                "candidate_id": result.candidate_id,
                "promotion_state": result.promotion_state,
                "delta": result.delta(),
                "golden": result.golden,
            }
        )
        key = f"{result.agent}:{result.candidate_id}"
        if result.promotion_state == "eligible":
            eligible_candidates.append(key)
        elif result.promotion_state == "review":
            review_candidates.append(key)
        elif result.promotion_state == "discard":
            discarded_candidates.append(key)

    summary = {
        "timestamp": utc_now_iso(),
        "run_kind": run_kind,
        "subject": subject,
        "total_cases": len(results),
        "eligible": len(eligible_candidates),
        "discard": len(discarded_candidates),
        "review": len(review_candidates),
        "golden_regressions": len(golden_regressions),
        "eligible_candidates": eligible_candidates,
        "review_candidates": review_candidates,
        "discarded_candidates": discarded_candidates,
        "golden_regression_cases": golden_regressions,
        "by_agent": dict(by_agent),
    }
    return summary


def write_summary(summary: Dict[str, object], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = summary["timestamp"].replace(":", "-")
    stem = f"{summary['run_kind']}__{summary['subject']}__{stamp}"
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        f"# Summary — {summary['run_kind']} / {summary['subject']}",
        "",
        f"- Total cases: `{summary['total_cases']}`",
        f"- Eligible: `{summary['eligible']}`",
        f"- Review: `{summary['review']}`",
        f"- Discard: `{summary['discard']}`",
        f"- Golden regressions: `{summary['golden_regressions']}`",
        "",
    ]

    if summary["golden_regressions"]:
        lines += ["## Golden regressions", ""]
        for item in summary["golden_regression_cases"]:
            lines.append(f"- `{item}`")
        lines.append("")

    lines += ["## Recommended promotions", ""]
    if summary["eligible_candidates"]:
        for item in summary["eligible_candidates"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.append("")

    lines += ["## Needs review", ""]
    if summary["review_candidates"]:
        for item in summary["review_candidates"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.append("")

    lines += ["## Discarded", ""]
    if summary["discarded_candidates"]:
        for item in summary["discarded_candidates"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.append("")

    lines += ["## By agent", ""]
    for agent, info in summary["by_agent"].items():
        lines.append(f"### {agent}")
        lines.append("")
        lines.append(f"- Cases: `{info['count']}`")
        lines.append(f"- Eligible: `{info.get('eligible', 0)}`")
        lines.append(f"- Review: `{info.get('review', 0)}`")
        lines.append(f"- Discard: `{info.get('discard', 0)}`")
        lines.append(f"- Golden regressions: `{info.get('golden_regressions', 0)}`")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path
