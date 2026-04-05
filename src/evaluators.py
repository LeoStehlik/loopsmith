from __future__ import annotations

from typing import Dict, Tuple

from schema import EvalCase
from scoring import score_case


def _contains(text_l: str, term: str) -> bool:
    return term.lower() in text_l


def _forge_proof_before_done(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    proof_present = _contains(text_l, "proof")
    verify_present = _contains(text_l, "verify") or _contains(text_l, "verification")
    tests_present = _contains(text_l, "tests") or _contains(text_l, "test")
    premature_done = _contains(text_l, "done.") and not (proof_present or tests_present or verify_present)

    structural_pass = proof_present and verify_present and tests_present and not premature_done
    structural_score = 1.0 if structural_pass else 0.0
    final_score = round((base_score * 0.4) + (structural_score * 0.6), 3)

    reason_parts = []
    if proof_present:
        reason_parts.append("proof present")
    else:
        reason_parts.append("proof missing")
    if verify_present:
        reason_parts.append("verification present")
    else:
        reason_parts.append("verification missing")
    if tests_present:
        reason_parts.append("tests present")
    else:
        reason_parts.append("tests missing")
    if premature_done:
        reason_parts.append("premature done claim detected")

    details.update(
        {
            "evaluator": "forge_proof_before_done",
            "structural_checks": {
                "proof_present": proof_present,
                "verify_present": verify_present,
                "tests_present": tests_present,
                "premature_done": premature_done,
                "structural_pass": structural_pass,
                "structural_score": structural_score,
            },
            "component_scores": {
                **details.get("component_scores", {}),
                "case_specific_structural": structural_score,
                "final": final_score,
            },
        }
    )
    return final_score, details, "; ".join(reason_parts)


def _iris_ac_verdict(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    ac_present = _contains(text_l, "ac")
    pass_present = _contains(text_l, "pass")
    fail_present = _contains(text_l, "fail")
    unknown_present = _contains(text_l, "unknown")
    verdict_structure_ok = ac_present and pass_present and fail_present and unknown_present

    structural_score = 1.0 if verdict_structure_ok else 0.0
    final_score = round((base_score * 0.35) + (structural_score * 0.65), 3)
    reason = (
        f"ac_present={ac_present}; pass_present={pass_present}; "
        f"fail_present={fail_present}; unknown_present={unknown_present}"
    )

    details.update(
        {
            "evaluator": "iris_ac_verdict",
            "structural_checks": {
                "ac_present": ac_present,
                "pass_present": pass_present,
                "fail_present": fail_present,
                "unknown_present": unknown_present,
                "verdict_structure_ok": verdict_structure_ok,
                "structural_score": structural_score,
            },
            "component_scores": {
                **details.get("component_scores", {}),
                "case_specific_structural": structural_score,
                "final": final_score,
            },
        }
    )
    return final_score, details, reason


def _rex_layered_reporting(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    sprint_present = _contains(text_l, "sprint")
    pass_present = _contains(text_l, "pass")
    fail_present = _contains(text_l, "fail")
    overall_conclusion_guard = _contains(text_l, "overall conclusion") or _contains(text_l, "not complete")
    layered_reporting_ok = sprint_present and pass_present and fail_present

    structural_score = 1.0 if layered_reporting_ok else 0.0
    if overall_conclusion_guard:
        structural_score = min(1.0, structural_score + 0.2)
    final_score = round((base_score * 0.35) + (structural_score * 0.65), 3)
    final_score = min(1.0, final_score)
    reason = (
        f"sprint_present={sprint_present}; pass_present={pass_present}; "
        f"fail_present={fail_present}; overall_conclusion_guard={overall_conclusion_guard}"
    )

    details.update(
        {
            "evaluator": "rex_layered_reporting",
            "structural_checks": {
                "sprint_present": sprint_present,
                "pass_present": pass_present,
                "fail_present": fail_present,
                "overall_conclusion_guard": overall_conclusion_guard,
                "layered_reporting_ok": layered_reporting_ok,
                "structural_score": structural_score,
            },
            "component_scores": {
                **details.get("component_scores", {}),
                "case_specific_structural": structural_score,
                "final": round(final_score, 3),
            },
        }
    )
    return round(final_score, 3), details, reason


EVALUATORS = {
    "generic": None,
    "forge_proof_before_done": _forge_proof_before_done,
    "iris_ac_verdict": _iris_ac_verdict,
    "rex_layered_reporting": _rex_layered_reporting,
}


def evaluate_text(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    fn = EVALUATORS.get(case.evaluator)
    if fn is None:
        score, details = score_case(case, text)
        details["evaluator"] = "generic"
        reason = f"generic evaluator; final={details.get('component_scores', {}).get('final', score)}"
        return score, details, reason
    return fn(case, text)
