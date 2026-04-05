from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from schema import AgentProfile, CandidateChange, CheckRule, EvalCase, RubricDimension

ROOT = Path(__file__).resolve().parent.parent


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


SHARED_EVAL_PACKS = {
    "golden:anti-bullshit": "evals/golden/anti-bullshit.json",
}


def load_agent_profiles(agent_id: str | None = None) -> Dict[str, AgentProfile]:
    agents_dir = ROOT / "agents"
    profiles: Dict[str, AgentProfile] = {}
    for path in sorted(agents_dir.glob("*.json")):
        data = _read_json(path)
        profile = AgentProfile(**data)
        if agent_id and profile.id != agent_id:
            continue
        profiles[profile.id] = profile
    return profiles


def load_eval_pack(pack_path: str) -> List[EvalCase]:
    path = ROOT / pack_path
    payload = _read_json(path)
    cases: List[EvalCase] = []
    for data in payload:
        required = [CheckRule(**item) for item in data.get("required_checks", [])]
        forbidden = [CheckRule(**item) for item in data.get("forbidden_checks", [])]
        rubric = [RubricDimension(**item) for item in data.get("rubric_dimensions", [])]
        case = EvalCase(
            id=data["id"],
            agent=data["agent"],
            title=data["title"],
            scenario=data["scenario"],
            scoring_mode=data["scoring_mode"],
            golden=data.get("golden", False),
            risk_level=data.get("risk_level", "L1"),
            tags=data.get("tags", []),
            required_checks=required,
            forbidden_checks=forbidden,
            rubric_dimensions=rubric,
            anti_goals=data.get("anti_goals", []),
            weights=data.get("weights", {}),
            metadata=data.get("metadata", {}),
        )
        cases.append(case)
    return cases


def load_candidates(agent_id: str | None = None) -> Dict[str, List[CandidateChange]]:
    candidates_dir = ROOT / "candidates"
    out: Dict[str, List[CandidateChange]] = {}
    dirs = [candidates_dir / agent_id] if agent_id else [p for p in candidates_dir.iterdir() if p.is_dir()]
    for agent_dir in sorted(dirs):
        if not agent_dir.exists():
            continue
        agent_candidates: List[CandidateChange] = []
        for path in sorted(agent_dir.glob("*.json")):
            data = _read_json(path)
            candidate = CandidateChange(**data)
            agent_candidates.append(candidate)
        if agent_candidates:
            out[agent_dir.name] = agent_candidates
    return out


def load_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def load_shared_eval_pack(name: str) -> List[EvalCase]:
    path = SHARED_EVAL_PACKS.get(name)
    if not path:
        raise ValueError(f"Unknown shared eval pack: {name}")
    return load_eval_pack(path)


def baseline_path(agent: str, eval_id: str) -> Path:
    return ROOT / "baseline" / agent / f"{eval_id}.txt"
