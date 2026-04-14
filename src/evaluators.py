from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, Tuple
from urllib import error, request

from schema import EvalCase
from scoring import score_case


@dataclass
class JudgeVerdict:
    score: float
    reason: str
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    provider: str = "unknown"
    model: str = ""
    raw_response: str = ""
    anti_goal_hits: list[str] = field(default_factory=list)
    required_passed: list[str] = field(default_factory=list)
    forbidden_triggered: list[str] = field(default_factory=list)
    fallback: bool = False
    error: str | None = None

    def normalized(self) -> "JudgeVerdict":
        self.score = max(0.0, min(1.0, round(float(self.score), 3)))
        cleaned: Dict[str, float] = {}
        for key, value in self.dimension_scores.items():
            try:
                cleaned[str(key)] = max(0.0, min(1.0, round(float(value), 3)))
            except (TypeError, ValueError):
                continue
        self.dimension_scores = cleaned
        return self

    def to_details(self) -> Dict[str, Any]:
        return asdict(self)


class BaseJudge(ABC):
    def __init__(self, provider: str, model: str, timeout: int = 30):
        self.provider = provider
        self.model = model
        self.timeout = timeout

    @abstractmethod
    def complete(self, prompt: str) -> str:
        raise NotImplementedError

    def build_prompt(self, case: EvalCase, text: str) -> str:
        rubric_lines = [
            f"- {dim.id} ({dim.label}, weight={dim.weight}): {dim.guidance}" for dim in case.rubric_dimensions
        ] or ["- none"]
        required_lines = [f"- {rule.label}: {', '.join(rule.terms)}" for rule in case.required_checks] or ["- none"]
        forbidden_lines = [f"- {rule.label}: {', '.join(rule.terms)}" for rule in case.forbidden_checks] or ["- none"]
        anti_goal_lines = [f"- {goal}" for goal in case.anti_goals] or ["- none"]

        return f"""You are a high-precision response judge for Loopsmith.
Return only valid JSON with this schema:
{{
  "score": <float 0.0-1.0>,
  "reason": "<short explanation>",
  "dimension_scores": {{"<dimension_id>": <float 0.0-1.0>}},
  "anti_goal_hits": ["<anti-goal>"] ,
  "required_passed": ["<required check label>"],
  "forbidden_triggered": ["<forbidden check label>"]
}}

Score semantically. Do not rely on exact keyword overlap. Use the rubric guidance, anti-goals, required checks, and forbidden checks.

EVAL CASE
- id: {case.id}
- title: {case.title}
- scenario: {case.scenario}
- scoring_mode: {case.scoring_mode}
- golden: {case.golden}
- risk_level: {case.risk_level}

RUBRIC DIMENSIONS
{os.linesep.join(rubric_lines)}

REQUIRED CHECKS
{os.linesep.join(required_lines)}

FORBIDDEN CHECKS
{os.linesep.join(forbidden_lines)}

ANTI-GOALS
{os.linesep.join(anti_goal_lines)}

RESPONSE TO EVALUATE
<<<BEGIN_RESPONSE>>>
{text}
<<<END_RESPONSE>>>
"""

    def parse_verdict(self, raw_text: str) -> JudgeVerdict:
        sanitized = self._sanitize_response(raw_text)
        payload = self._extract_json_object(sanitized)
        verdict = JudgeVerdict(
            score=payload.get("score", 0.5),
            reason=str(payload.get("reason", "LLM judge returned no reason.")),
            dimension_scores=payload.get("dimension_scores", {}) or {},
            provider=self.provider,
            model=self.model,
            raw_response=sanitized,
            anti_goal_hits=payload.get("anti_goal_hits", []) or [],
            required_passed=payload.get("required_passed", []) or [],
            forbidden_triggered=payload.get("forbidden_triggered", []) or [],
        )
        return verdict.normalized()

    def evaluate(self, case: EvalCase, text: str) -> JudgeVerdict:
        prompt = self.build_prompt(case, text)
        raw_text = self.complete(prompt)
        return self.parse_verdict(raw_text)

    @staticmethod
    def _sanitize_response(raw_text: str) -> str:
        text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw_text)
        text = text.replace("\b", "")
        text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)
        return text.strip()

    @staticmethod
    def _extract_json_object(raw_text: str) -> Dict[str, Any]:
        decoder = json.JSONDecoder()
        for match in re.finditer(r"\{", raw_text):
            try:
                payload, _ = decoder.raw_decode(raw_text[match.start() :])
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and "score" in payload:
                return payload
        raise ValueError("No judge verdict JSON object found in response")


class OllamaJudge(BaseJudge):
    def complete(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "score": {"type": "number"},
                    "reason": {"type": "string"},
                    "dimension_scores": {"type": "object"},
                    "anti_goal_hits": {"type": "array", "items": {"type": "string"}},
                    "required_passed": {"type": "array", "items": {"type": "string"}},
                    "forbidden_triggered": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["score", "reason", "dimension_scores"]
            },
            "options": {"temperature": 0},
        }
        req = request.Request(
            os.environ.get("LOOPSMITH_OLLAMA_URL", "http://127.0.0.1:11434/api/generate"),
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        return str(data.get("response", "")).strip()


class OpenAIJudge(BaseJudge):
    def __init__(self, provider: str, model: str, timeout: int = 30, api_key: str | None = None):
        super().__init__(provider=provider, model=model, timeout=timeout)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI judge provider")

    def complete(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "input": prompt,
        }
        req = request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc

        parts = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()


def _neutral_judge_verdict(case: EvalCase, err: Exception, provider: str, model: str) -> Tuple[float, Dict[str, object], str]:
    verdict = JudgeVerdict(
        score=0.5,
        reason="Judge failure, falling back to neutral score.",
        dimension_scores={dim.id: 0.5 for dim in case.rubric_dimensions},
        provider=provider,
        model=model,
        fallback=True,
        error=str(err),
    ).normalized()
    details = verdict.to_details()
    details["evaluator"] = "llm_judge"
    return verdict.score, details, verdict.reason


def _build_judge(case: EvalCase) -> BaseJudge:
    metadata = case.metadata or {}
    provider = str(metadata.get("judge_provider") or os.environ.get("LOOPSMITH_JUDGE_PROVIDER") or "ollama").lower()
    timeout = int(metadata.get("judge_timeout") or os.environ.get("LOOPSMITH_JUDGE_TIMEOUT") or 30)

    if provider == "openai":
        model = str(metadata.get("judge_model") or os.environ.get("LOOPSMITH_OPENAI_MODEL") or "gpt-4.1-mini")
        return OpenAIJudge(provider=provider, model=model, timeout=timeout)

    model = str(metadata.get("judge_model") or os.environ.get("LOOPSMITH_OLLAMA_MODEL") or "gemma4:31b-cloud")
    return OllamaJudge(provider=provider, model=model, timeout=timeout)


def _llm_judge_bridge(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    judge = _build_judge(case)
    try:
        verdict = judge.evaluate(case, text)
    except Exception as err:
        return _neutral_judge_verdict(case, err, judge.provider, judge.model)

    details = verdict.to_details()
    details["evaluator"] = "llm_judge"
    return verdict.score, details, verdict.reason


def _forge_proof_before_done(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    proof_present = "proof" in text_l
    verify_present = "verify" in text_l or "verification" in text_l
    tests_present = "tests" in text_l or "test" in text_l
    premature_done = "done." in text_l and not (proof_present or tests_present or verify_present)
    structural_pass = proof_present and verify_present and tests_present and not premature_done
    structural_score = 1.0 if structural_pass else 0.0
    final_score = round((base_score * 0.4) + (structural_score * 0.6), 3)
    details.update({
        "evaluator": "forge_proof_before_done",
        "structural_score": structural_score,
        "structural_checks": {
            "proof_present": proof_present,
            "verify_present": verify_present,
            "tests_present": tests_present,
            "premature_done": premature_done,
        },
    })
    return final_score, details, "structural check complete"


def _iris_ac_verdict(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    structural_score = 1.0 if all(x in text_l for x in ["ac", "pass", "fail", "unknown"]) else 0.0
    final_score = round((base_score * 0.35) + (structural_score * 0.65), 3)
    details.update({"evaluator": "iris_ac_verdict", "structural_score": structural_score})
    return final_score, details, "structural check complete"


def _iris_review_vs_validation(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    structural_score = 1.0 if "validation" in text_l and ("evidence" in text_l or "incomplete" in text_l) else 0.0
    final_score = round((base_score * 0.4) + (structural_score * 0.6), 3)
    details.update({"evaluator": "iris_review_vs_validation", "structural_score": structural_score})
    return final_score, details, "structural check complete"


def _rex_cumulative_regression(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    structural_score = 1.0 if all(x in text_l for x in ["full", "regression", "not complete"]) else 0.0
    final_score = round((base_score * 0.4) + (structural_score * 0.6), 3)
    details.update({"evaluator": "rex_cumulative_regression", "structural_score": structural_score})
    return final_score, details, "structural check complete"


def _rex_layered_reporting(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    text_l = text.lower()
    base_score, details = score_case(case, text)
    structural_score = 1.0 if all(x in text_l for x in ["sprint", "pass", "fail"]) else 0.0
    final_score = round((base_score * 0.35) + (structural_score * 0.65), 3)
    details.update({"evaluator": "rex_layered_reporting", "structural_score": structural_score})
    return final_score, details, "structural check complete"


EvaluatorFn = Callable[[EvalCase, str], Tuple[float, Dict[str, object], str]]

EVALUATORS: Dict[str, EvaluatorFn | None] = {
    "generic": None,
    "llm_judge": _llm_judge_bridge,
    "forge_proof_before_done": _forge_proof_before_done,
    "iris_ac_verdict": _iris_ac_verdict,
    "iris_review_vs_validation": _iris_review_vs_validation,
    "rex_cumulative_regression": _rex_cumulative_regression,
    "rex_layered_reporting": _rex_layered_reporting,
}


def evaluate_text(case: EvalCase, text: str) -> Tuple[float, Dict[str, object], str]:
    fn = EVALUATORS.get(case.evaluator)
    if fn is None:
        score, details = score_case(case, text)
        details["evaluator"] = "generic"
        return score, details, f"generic evaluator; final={score}"
    return fn(case, text)
