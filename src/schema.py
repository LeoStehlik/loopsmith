from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Literal, Optional, List, Dict, Any

ScoreMode = Literal["pass_fail", "rubric", "composite"]
Verdict = Literal["keep", "discard", "review"]
RiskLevel = Literal["L1", "L2", "L3"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EvalCase:
    id: str
    agent: str
    title: str
    scenario: str
    scoring_mode: ScoreMode
    expected: str
    failure_modes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    risk_level: RiskLevel = "L1"
    golden: bool = False
    anti_goals: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CandidateChange:
    id: str
    agent: str
    surface: str
    description: str
    risk_level: RiskLevel
    path: Optional[str] = None
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
    notes: str
    scoring_mode: ScoreMode
    timestamp: str = field(default_factory=utc_now_iso)
    golden: bool = False
    duration_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def delta(self) -> float:
        return self.candidate_score - self.baseline_score

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["delta"] = self.delta()
        return data


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
