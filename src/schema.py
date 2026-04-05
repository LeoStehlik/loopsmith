from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

ScoreMode = Literal["pass_fail", "rubric", "composite"]
Verdict = Literal["keep", "discard", "review"]
PromotionState = Literal["eligible", "discard", "review", "promoted", "rejected"]
RiskLevel = Literal["L1", "L2", "L3"]
MatchMode = Literal["all", "any"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CheckRule:
    label: str
    terms: List[str] = field(default_factory=list)
    match_mode: MatchMode = "all"
    min_terms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RubricDimension:
    id: str
    label: str
    weight: float = 1.0
    positive_terms: List[str] = field(default_factory=list)
    negative_terms: List[str] = field(default_factory=list)
    guidance: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvalCase:
    id: str
    agent: str
    title: str
    scenario: str
    scoring_mode: ScoreMode
    golden: bool = False
    risk_level: RiskLevel = "L1"
    tags: List[str] = field(default_factory=list)
    required_checks: List[CheckRule] = field(default_factory=list)
    forbidden_checks: List[CheckRule] = field(default_factory=list)
    rubric_dimensions: List[RubricDimension] = field(default_factory=list)
    anti_goals: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "required_checks": [rule.to_dict() for rule in self.required_checks],
            "forbidden_checks": [rule.to_dict() for rule in self.forbidden_checks],
            "rubric_dimensions": [dim.to_dict() for dim in self.rubric_dimensions],
        }


@dataclass
class CandidateChange:
    id: str
    agent: str
    eval_id: str
    surface: str
    description: str
    risk_level: RiskLevel
    path: Optional[str] = None
    response_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvalResult:
    eval_id: str
    agent: str
    candidate_id: str
    baseline_score: float
    candidate_score: float
    verdict: Verdict
    promotion_state: PromotionState
    notes: str
    scoring_mode: ScoreMode
    timestamp: str = field(default_factory=utc_now_iso)
    golden: bool = False
    duration_ms: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def delta(self) -> float:
        return round(self.candidate_score - self.baseline_score, 3)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["delta"] = self.delta()
        return data


@dataclass
class PromotionRecord:
    candidate_id: str
    agent: str
    eval_ids: List[str]
    status: PromotionState
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    final_disposition: Optional[str] = None
    notes: str = ""
    timestamp: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentProfile:
    id: str
    role: str
    goals: List[str]
    eval_pack: str
    allowed_surfaces: List[str]
    restricted_surfaces: List[str] = field(default_factory=list)
    forbidden_surfaces: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
