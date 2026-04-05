from __future__ import annotations

from typing import Dict, List, Tuple

from schema import CheckRule, EvalCase, RubricDimension


def _contains_terms(text_l: str, terms: List[str]) -> bool:
    return all(term.lower() in text_l for term in terms)


def score_required_checks(text: str, rules: List[CheckRule]) -> Tuple[float, List[Dict[str, object]]]:
    text_l = text.lower()
    if not rules:
        return 1.0, []
    details = []
    passed = 0
    for rule in rules:
        ok = _contains_terms(text_l, rule.terms)
        details.append({"label": rule.label, "passed": ok, "terms": rule.terms})
        if ok:
            passed += 1
    return round(passed / len(rules), 3), details


def score_forbidden_checks(text: str, rules: List[CheckRule]) -> Tuple[float, List[Dict[str, object]]]:
    text_l = text.lower()
    if not rules:
        return 1.0, []
    details = []
    clean = 0
    for rule in rules:
        triggered = any(term.lower() in text_l for term in rule.terms)
        details.append({"label": rule.label, "triggered": triggered, "terms": rule.terms})
        if not triggered:
            clean += 1
    return round(clean / len(rules), 3), details


def score_rubric(text: str, dims: List[RubricDimension]) -> Tuple[float, List[Dict[str, object]]]:
    text_l = text.lower()
    if not dims:
        return 0.0, []

    weighted_total = 0.0
    total_weight = 0.0
    details = []

    for dim in dims:
        positive_hits = sum(1 for term in dim.positive_terms if term.lower() in text_l)
        negative_hits = sum(1 for term in dim.negative_terms if term.lower() in text_l)
        positive_den = max(1, len(dim.positive_terms))
        negative_den = max(1, len(dim.negative_terms))
        score = min(1.0, positive_hits / positive_den)
        score -= 0.5 * (negative_hits / negative_den)
        score = max(0.0, min(1.0, round(score, 3)))

        weighted_total += score * dim.weight
        total_weight += dim.weight
        details.append(
            {
                "id": dim.id,
                "label": dim.label,
                "score": score,
                "weight": dim.weight,
                "positive_hits": positive_hits,
                "negative_hits": negative_hits,
            }
        )

    if total_weight == 0:
        return 0.0, details
    return round(weighted_total / total_weight, 3), details


def score_anti_goals(text: str, anti_goals: List[str]) -> Tuple[float, List[str]]:
    text_l = text.lower()
    hits = [goal for goal in anti_goals if goal.lower() in text_l]
    if not anti_goals:
        return 0.0, []
    penalty = min(1.0, round(0.2 * len(hits), 3))
    return penalty, hits


def score_case(case: EvalCase, text: str) -> Tuple[float, Dict[str, object]]:
    required_score, required_details = score_required_checks(text, case.required_checks)
    forbidden_score, forbidden_details = score_forbidden_checks(text, case.forbidden_checks)
    rubric_score, rubric_details = score_rubric(text, case.rubric_dimensions)
    anti_goal_penalty, anti_goal_hits = score_anti_goals(text, case.anti_goals)

    if case.scoring_mode == "pass_fail":
        score = 1.0 if required_score == 1.0 and forbidden_score == 1.0 else 0.0
    elif case.scoring_mode == "rubric":
        score = rubric_score - anti_goal_penalty
    else:
        hard_weight = case.weights.get("hard_checks", 0.5)
        rubric_weight = case.weights.get("rubric", 0.5)
        hard_score = (required_score + forbidden_score) / 2
        score = (hard_score * hard_weight) + (rubric_score * rubric_weight) - anti_goal_penalty

    score = max(0.0, min(1.0, round(score, 3)))
    details: Dict[str, object] = {
        "required_checks": required_details,
        "forbidden_checks": forbidden_details,
        "rubric_dimensions": rubric_details,
        "anti_goal_hits": anti_goal_hits,
        "anti_goal_penalty": anti_goal_penalty,
    }
    return score, details
