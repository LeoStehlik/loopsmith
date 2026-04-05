from __future__ import annotations

import json
from pathlib import Path
from typing import List

from loaders import ROOT, baseline_path, load_candidates, load_eval_pack, load_text
from operator_views import refresh_operator_views
from schema import AgentProfile, CandidateChange, EvalCase, EvalResult, PromotionRecord, utc_now_iso
from scoring import score_case
from summaries import build_summary, write_summary

RUNS_DIR = ROOT / "runs"
SUMMARIES_DIR = RUNS_DIR / "summaries"
LEDGER_PATH = ROOT / "ledger" / "promotion-log.jsonl"


def ensure_dirs() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)


def evaluate_case(
    profile: AgentProfile,
    case: EvalCase,
    candidate: CandidateChange,
    baseline_response: str,
    candidate_response: str,
) -> EvalResult:
    baseline_score, baseline_details = score_case(case, baseline_response)
    candidate_score, candidate_details = score_case(case, candidate_response)

    if case.golden and candidate_score < baseline_score:
        verdict = "discard"
        promotion_state = "discard"
        notes = "Golden case regressed."
    elif candidate_score > baseline_score:
        verdict = "keep"
        promotion_state = "eligible"
        notes = "Candidate improved score over baseline and is eligible for human-reviewed promotion."
    elif candidate_score == baseline_score:
        verdict = "review"
        promotion_state = "review"
        notes = "No measurable change. Human review needed."
    else:
        verdict = "discard"
        promotion_state = "discard"
        notes = "Candidate scored worse than baseline."

    return EvalResult(
        eval_id=case.id,
        agent=profile.id,
        candidate_id=candidate.id,
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        verdict=verdict,
        promotion_state=promotion_state,
        notes=notes,
        scoring_mode=case.scoring_mode,
        golden=case.golden,
        details={
            "surface": candidate.surface,
            "title": case.title,
            "risk_level": case.risk_level,
            "baseline": baseline_details,
            "candidate": candidate_details,
        },
    )


def write_run_files(result: EvalResult) -> tuple[Path, Path]:
    ensure_dirs()
    stem = f"{result.agent}__{result.eval_id}__{result.candidate_id}"
    json_path = RUNS_DIR / f"{stem}.json"
    md_path = RUNS_DIR / f"{stem}.md"

    json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    md_path.write_text(
        "\n".join(
            [
                f"# Run Summary — {result.agent}",
                "",
                f"- Eval: `{result.eval_id}`",
                f"- Candidate: `{result.candidate_id}`",
                f"- Baseline score: `{result.baseline_score}`",
                f"- Candidate score: `{result.candidate_score}`",
                f"- Delta: `{result.delta()}`",
                f"- Verdict: `{result.verdict}`",
                f"- Promotion state: `{result.promotion_state}`",
                f"- Golden: `{result.golden}`",
                f"- Notes: {result.notes}",
            ]
        ),
        encoding="utf-8",
    )
    return json_path, md_path


def write_pack_summary(results: List[EvalResult], run_kind: str, subject: str) -> tuple[Path, Path]:
    ensure_dirs()
    summary = build_summary(results, run_kind=run_kind, subject=subject)
    paths = write_summary(summary, SUMMARIES_DIR)
    refresh_operator_views()
    return paths


def append_ledger(record: PromotionRecord) -> None:
    ensure_dirs()
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict()) + "\n")


def promote_candidate(agent: str, candidate: CandidateChange, approved_by: str, notes: str = "") -> PromotionRecord:
    source_response = ROOT / (candidate.response_path or "")
    target_baseline = baseline_path(agent, candidate.eval_id)
    target_baseline.parent.mkdir(parents=True, exist_ok=True)
    target_baseline.write_text(source_response.read_text(encoding="utf-8"), encoding="utf-8")

    promoted_dir = ROOT / "promoted" / agent
    promoted_dir.mkdir(parents=True, exist_ok=True)
    promoted_manifest = promoted_dir / f"{candidate.id}.json"
    promoted_manifest.write_text(json.dumps(candidate.to_dict(), indent=2), encoding="utf-8")

    record = PromotionRecord(
        candidate_id=candidate.id,
        agent=agent,
        eval_ids=[candidate.eval_id],
        status="promoted",
        approved_by=approved_by,
        approved_at=utc_now_iso(),
        final_disposition="promoted",
        notes=notes or "Candidate promoted into baseline.",
    )
    append_ledger(record)
    refresh_operator_views()
    return record


def reject_candidate(agent: str, candidate: CandidateChange, approved_by: str, notes: str = "") -> PromotionRecord:
    rejected_dir = ROOT / "rejected" / agent
    rejected_dir.mkdir(parents=True, exist_ok=True)
    rejected_manifest = rejected_dir / f"{candidate.id}.json"
    rejected_manifest.write_text(json.dumps(candidate.to_dict(), indent=2), encoding="utf-8")

    record = PromotionRecord(
        candidate_id=candidate.id,
        agent=agent,
        eval_ids=[candidate.eval_id],
        status="rejected",
        approved_by=approved_by,
        approved_at=utc_now_iso(),
        final_disposition="rejected",
        notes=notes or "Candidate explicitly rejected.",
    )
    append_ledger(record)
    refresh_operator_views()
    return record


def run_agent(profile: AgentProfile, candidate_id: str | None = None) -> List[EvalResult]:
    cases = {case.id: case for case in load_eval_pack(profile.eval_pack)}
    candidates_by_agent = load_candidates(profile.id)
    candidates = candidates_by_agent.get(profile.id, [])
    results: List[EvalResult] = []

    for candidate in candidates:
        if candidate_id and candidate.id != candidate_id:
            continue
        case = cases.get(candidate.eval_id)
        if not case:
            continue
        baseline_response = baseline_path(profile.id, case.id).read_text(encoding="utf-8")
        candidate_response = load_text(candidate.response_path or "")
        result = evaluate_case(profile, case, candidate, baseline_response, candidate_response)
        write_run_files(result)
        results.append(result)

    return results
