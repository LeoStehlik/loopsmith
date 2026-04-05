from __future__ import annotations

import argparse
import json

from loaders import load_agent_profiles, load_candidates, load_shared_pack, baseline_path, load_text
from operator_views import BASELINE_PROVENANCE_MD, PROMOTION_INDEX_MD, REVIEW_QUEUE_MD
from runner import (
    evaluate_case,
    promote_candidate,
    reject_candidate,
    run_agent,
    write_pack_summary,
    write_run_files,
)


def _print_result_lines(results: list[dict]) -> None:
    for result in results:
        print(
            f"{result['agent']} :: {result['eval_id']} :: {result['candidate_id']} :: "
            f"{result['promotion_state']} ({result['candidate_score']} vs {result['baseline_score']})"
        )


def _print_summary_stub(summary_json, summary_md, summary_data: dict) -> None:
    print(
        f"Summary: total={summary_data['total_cases']} eligible={summary_data['eligible']} "
        f"review={summary_data['review']} discard={summary_data['discard']} "
        f"golden_regressions={summary_data['golden_regressions']}"
    )
    print(f"Summary files: {summary_json} | {summary_md}")
    print(f"Review queue: {REVIEW_QUEUE_MD}")
    print(f"Promotion index: {PROMOTION_INDEX_MD}")
    print(f"Baseline provenance: {BASELINE_PROVENANCE_MD}")


def cmd_run(args: argparse.Namespace) -> int:
    profiles = load_agent_profiles(args.agent)
    if not profiles:
        raise SystemExit(f"No agent profile found for {args.agent}")

    results = []
    for profile in profiles.values():
        results.extend(run_agent(profile, candidate_id=args.candidate))

    summary_json, summary_md = write_pack_summary(results, run_kind="agent-pack", subject=args.agent)
    summary_data = json.loads(summary_json.read_text(encoding="utf-8"))

    if args.json:
        print(json.dumps({"results": [result.to_dict() for result in results], "summary": summary_data}, indent=2))
    else:
        _print_result_lines([result.to_dict() for result in results])
        _print_summary_stub(summary_json, summary_md, summary_data)
    return 0


def _find_candidate(agent: str, candidate_id: str):
    candidates = load_candidates(agent).get(agent, [])
    for candidate in candidates:
        if candidate.id == candidate_id:
            return candidate
    raise SystemExit(f"Candidate {candidate_id} not found for agent {agent}")


def cmd_promote(args: argparse.Namespace) -> int:
    candidate = _find_candidate(args.agent, args.candidate)
    record = promote_candidate(args.agent, candidate, approved_by=args.approved_by, notes=args.notes)
    print(json.dumps(record.to_dict(), indent=2))
    print(f"Review queue: {REVIEW_QUEUE_MD}")
    print(f"Promotion index: {PROMOTION_INDEX_MD}")
    print(f"Baseline provenance: {BASELINE_PROVENANCE_MD}")
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    candidate = _find_candidate(args.agent, args.candidate)
    record = reject_candidate(args.agent, candidate, approved_by=args.approved_by, notes=args.notes)
    print(json.dumps(record.to_dict(), indent=2))
    print(f"Review queue: {REVIEW_QUEUE_MD}")
    print(f"Promotion index: {PROMOTION_INDEX_MD}")
    print(f"Baseline provenance: {BASELINE_PROVENANCE_MD}")
    return 0


def cmd_run_shared(args: argparse.Namespace) -> int:
    pack_meta, pack_cases = load_shared_pack(args.pack)
    candidates_by_agent = load_candidates()
    results = []

    for case in pack_cases:
        profiles = load_agent_profiles(case.agent)
        profile = profiles.get(case.agent)
        if not profile:
            continue
        for candidate in candidates_by_agent.get(case.agent, []):
            if candidate.eval_id != case.id:
                continue
            baseline_response = baseline_path(case.agent, case.id).read_text(encoding="utf-8")
            candidate_response = load_text(candidate.response_path or "")
            result = evaluate_case(profile, case, candidate, baseline_response, candidate_response)
            write_run_files(result)
            results.append(result)

    subject = pack_meta.id.replace(":", "-")
    summary_json, summary_md = write_pack_summary(results, run_kind="shared-pack", subject=subject)
    summary_data = json.loads(summary_json.read_text(encoding="utf-8"))
    summary_data["pack"] = {
        "id": pack_meta.id,
        "title": pack_meta.title,
        "description": pack_meta.description,
        "kind": pack_meta.kind,
        "participating_agents": pack_meta.participating_agents,
    }

    if args.json:
        print(json.dumps({"results": [result.to_dict() for result in results], "summary": summary_data}, indent=2))
    else:
        print(f"Shared pack: {pack_meta.title} ({pack_meta.id})")
        print(f"Description: {pack_meta.description}")
        print(f"Participating agents: {', '.join(pack_meta.participating_agents)}")
        _print_result_lines([result.to_dict() for result in results])
        _print_summary_stub(summary_json, summary_md, summary_data)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Loopsmith CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run evals for an agent")
    run.add_argument("--agent", required=True)
    run.add_argument("--candidate", required=False)
    run.add_argument("--json", action="store_true")
    run.set_defaults(func=cmd_run)

    run_shared = sub.add_parser("run-shared", help="Run a shared eval pack")
    run_shared.add_argument("--pack", required=True)
    run_shared.add_argument("--json", action="store_true")
    run_shared.set_defaults(func=cmd_run_shared)

    promote = sub.add_parser("promote", help="Promote an eligible candidate into baseline")
    promote.add_argument("--agent", required=True)
    promote.add_argument("--candidate", required=True)
    promote.add_argument("--approved-by", required=True)
    promote.add_argument("--notes", default="")
    promote.set_defaults(func=cmd_promote)

    reject = sub.add_parser("reject", help="Reject a candidate")
    reject.add_argument("--agent", required=True)
    reject.add_argument("--candidate", required=True)
    reject.add_argument("--approved-by", required=True)
    reject.add_argument("--notes", default="")
    reject.set_defaults(func=cmd_reject)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))
