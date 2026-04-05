from __future__ import annotations

import argparse
import json
from pathlib import Path

from loaders import ROOT, load_agent_profiles, load_candidates, load_shared_eval_pack, baseline_path, load_text
from runner import promote_candidate, reject_candidate, run_agent, evaluate_case, write_run_files


def cmd_run(args: argparse.Namespace) -> int:
    profiles = load_agent_profiles(args.agent)
    if not profiles:
        raise SystemExit(f"No agent profile found for {args.agent}")

    summaries = []
    for profile in profiles.values():
        results = run_agent(profile, candidate_id=args.candidate)
        summaries.extend([result.to_dict() for result in results])

    if args.json:
        print(json.dumps(summaries, indent=2))
    else:
        for result in summaries:
            print(
                f"{result['agent']} :: {result['eval_id']} :: {result['candidate_id']} :: "
                f"{result['promotion_state']} ({result['candidate_score']} vs {result['baseline_score']})"
            )
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
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    candidate = _find_candidate(args.agent, args.candidate)
    record = reject_candidate(args.agent, candidate, approved_by=args.approved_by, notes=args.notes)
    print(json.dumps(record.to_dict(), indent=2))
    return 0


def cmd_run_shared(args: argparse.Namespace) -> int:
    pack = load_shared_eval_pack(args.pack)
    candidates_by_agent = load_candidates()
    summaries = []

    for case in pack:
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
            summaries.append(result.to_dict())

    if args.json:
        print(json.dumps(summaries, indent=2))
    else:
        for result in summaries:
            print(
                f"{result['agent']} :: {result['eval_id']} :: {result['candidate_id']} :: "
                f"{result['promotion_state']} ({result['candidate_score']} vs {result['baseline_score']})"
            )
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
