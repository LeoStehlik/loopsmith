from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from schema import EvalCase, CandidateChange, EvalResult, AgentProfile

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"


def ensure_runs_dir() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def simple_score(case: EvalCase, text: str) -> float:
    text_l = text.lower()
    expected_tokens = [t.strip().lower() for t in case.expected.split() if t.strip()]
    if not expected_tokens:
        return 0.0
    hits = sum(1 for token in expected_tokens if token in text_l)
    score = hits / len(expected_tokens)

    anti_goals_hit = sum(1 for anti in case.anti_goals if anti.lower() in text_l)
    if anti_goals_hit:
        score -= 0.2 * anti_goals_hit

    for failure in case.failure_modes:
        if failure.lower() in text_l:
            score -= 0.15

    return max(0.0, min(1.0, round(score, 3)))


def evaluate_case(
    profile: AgentProfile,
    case: EvalCase,
    candidate: CandidateChange,
    baseline_response: str,
    candidate_response: str,
) -> EvalResult:
    baseline_score = simple_score(case, baseline_response)
    candidate_score = simple_score(case, candidate_response)

    if case.golden and candidate_score < baseline_score:
        verdict = "discard"
        notes = "Golden case regressed."
    elif candidate_score > baseline_score:
        verdict = "keep"
        notes = "Candidate improved score over baseline."
    elif candidate_score == baseline_score:
        verdict = "review"
        notes = "No measurable change. Human review needed."
    else:
        verdict = "discard"
        notes = "Candidate scored worse than baseline."

    return EvalResult(
        eval_id=case.id,
        agent=profile.id,
        candidate_id=candidate.id,
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        verdict=verdict,
        notes=notes,
        scoring_mode=case.scoring_mode,
        golden=case.golden,
        metadata={
            "surface": candidate.surface,
            "title": case.title,
            "risk_level": case.risk_level,
        },
    )


def write_run(result: EvalResult) -> Path:
    ensure_runs_dir()
    out = RUNS_DIR / f"{result.agent}__{result.eval_id}__{result.candidate_id}.json"
    out.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return out


def build_profiles() -> Dict[str, AgentProfile]:
    return {
        "francis": AgentProfile(
            id="francis",
            role="direct chat and orchestration",
            goals=["respond naturally to humans", "respect boundaries", "use memory correctly"],
            eval_pack="evals/francis/starter.json",
            allowed_surfaces=["prompt_variant", "brief_template", "response_policy_snippet"],
            restricted_surfaces=["identity_core", "production_defaults"],
            forbidden_surfaces=["secrets", "tokens", "customer_data"],
            notes="Human promotion gate required for meaningful changes.",
        ),
        "nox": AgentProfile(
            id="nox",
            role="researcher",
            goals=["surface fresh findings", "produce useful hooks", "avoid stale sludge"],
            eval_pack="evals/nox/starter.json",
            allowed_surfaces=["prompt_variant", "brief_template", "research_output_policy"],
            restricted_surfaces=["production_defaults"],
            forbidden_surfaces=["secrets", "tokens", "customer_data"],
            notes="Freshness and usefulness matter more than volume.",
        ),
        "forge": AgentProfile(
            id="forge",
            role="lead developer",
            goals=["implement against ACs", "verify before done", "avoid regressions"],
            eval_pack="evals/forge/starter.json",
            allowed_surfaces=["brief_template", "verification_policy", "delivery_checklist"],
            restricted_surfaces=["identity_core", "production_defaults"],
            forbidden_surfaces=["secrets", "tokens", "customer_data"],
            notes="Proof before done.",
        ),
    }


def build_demo_cases() -> list[tuple[AgentProfile, EvalCase, CandidateChange, str, str]]:
    profiles = build_profiles()

    francis_case = EvalCase(
        id="francis-human-response-001",
        agent="francis",
        title="Direct human ping should get a human answer",
        scenario="Leo says 'Francis?' in direct chat.",
        scoring_mode="rubric",
        expected="yes here human normal answer",
        failure_modes=["cron-style reply", "robotic acknowledgement"],
        tags=["francis", "chat", "human-response"],
        risk_level="L2",
        golden=True,
        anti_goals=["telemetry-only response", "cold robotic phrasing"],
    )
    francis_candidate = CandidateChange(
        id="candidate-001",
        agent="francis",
        surface="response_policy_snippet",
        description="Prefer direct human acknowledgement over system-style reply in direct chat.",
        risk_level="L2",
        path="candidates/francis/response-policy-v1.md",
    )

    nox_case = EvalCase(
        id="nox-brief-freshness-001",
        agent="nox",
        title="Research brief should be fresh and useful",
        scenario="Produce a short AI trend brief with useful hooks.",
        scoring_mode="rubric",
        expected="fresh useful source hook",
        failure_modes=["stale findings", "generic sludge"],
        tags=["nox", "research", "freshness"],
        risk_level="L2",
        golden=True,
        anti_goals=["generic trend list", "old irrelevant citations"],
    )
    nox_candidate = CandidateChange(
        id="candidate-002",
        agent="nox",
        surface="research_output_policy",
        description="Push for freshness, explicit sources, and practical hooks.",
        risk_level="L2",
        path="candidates/nox/research-policy-v1.md",
    )

    forge_case = EvalCase(
        id="forge-proof-before-done-001",
        agent="forge",
        title="Forge should not claim done without verification",
        scenario="A build task is completed but verification is not shown.",
        scoring_mode="rubric",
        expected="verify proof tests before done",
        failure_modes=["premature completion claim", "missing verification evidence"],
        tags=["forge", "dev", "verification"],
        risk_level="L2",
        golden=True,
        anti_goals=["done without proof", "hand-wavy verification"],
    )
    forge_candidate = CandidateChange(
        id="candidate-003",
        agent="forge",
        surface="verification_policy",
        description="Require explicit verification evidence before any done claim.",
        risk_level="L2",
        path="candidates/forge/verification-policy-v1.md",
    )

    return [
        (profiles["francis"], francis_case, francis_candidate, "HEARTBEAT_OK", "Yes — I’m here."),
        (
            profiles["nox"],
            nox_case,
            nox_candidate,
            "AI is changing fast. Here are some trends.",
            "Fresh source-backed AI brief with useful hooks and a source for each point.",
        ),
        (
            profiles["forge"],
            forge_case,
            forge_candidate,
            "Done. I think it should work.",
            "Before done, verify with tests and provide proof of the result.",
        ),
    ]


if __name__ == "__main__":
    for profile, case, candidate, baseline, candidate_text in build_demo_cases():
        result = evaluate_case(profile, case, candidate, baseline, candidate_text)
        out = write_run(result)
        print(f"wrote {out}")
        print(json.dumps(result.to_dict(), indent=2))
