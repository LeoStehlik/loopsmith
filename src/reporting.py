from __future__ import annotations

from typing import Any, Dict, Iterable, List


class ReportFormatter:
    """Render Loopsmith JSON results into compact chat-friendly summaries."""

    def __init__(self, style: str = "telegram"):
        self.style = style

    def format_run_report(self, agent: str, data: Dict[str, Any]) -> str:
        if "error" in data:
            return f"❌ Error running eval: {data['error']}"

        summary = data.get("summary", {}) or {}
        results = data.get("results", []) or []
        if not results:
            return f"🔲 No candidates found for {agent}. Add one to candidates/{agent}/ to start."

        lines: List[str] = [f"🚀 *Loopsmith Report: {agent.upper()}*", ""]
        for result in results:
            lines.extend(self._format_result(result))
            lines.append("")

        lines.append("---")
        lines.extend(self._format_summary(summary))
        return "\n".join(lines).strip()

    def _format_result(self, result: Dict[str, Any]) -> Iterable[str]:
        delta = float(result.get("delta", 0.0) or 0.0)
        delta_emoji = "📈" if delta > 0 else "📉" if delta < 0 else "↔️"
        candidate = ((result.get("details") or {}).get("candidate") or {})
        reason = candidate.get("reason") or result.get("notes", "")
        dimensions = candidate.get("dimension_scores") or {}
        dimension_stub = self._format_dimensions(dimensions)

        return [
            f"🔹 *Case:* `{result.get('eval_id', 'unknown')}`",
            f"👤 *Cand:* `{result.get('candidate_id', 'unknown')}`",
            f"📊 *Score:* {result.get('baseline_score', 0)} → {result.get('candidate_score', 0)} ({delta_emoji} {delta:.3f})",
            f"⚖️ *Verdict:* `{str(result.get('promotion_state', 'review')).upper()}`",
            f"📝 *Reason:* {reason}",
            f"🧠 *Dimensions:* {dimension_stub}",
        ]

    def _format_dimensions(self, dimensions: Dict[str, Any]) -> str:
        if not dimensions:
            return "n/a"
        parts = []
        for name, score in sorted(dimensions.items()):
            try:
                parts.append(f"`{name}`={float(score):.2f}")
            except (TypeError, ValueError):
                continue
        return ", ".join(parts) if parts else "n/a"

    def _format_summary(self, summary: Dict[str, Any]) -> Iterable[str]:
        return [
            f"Total Cases: {summary.get('total_cases', 0)}",
            f"Eligible: {summary.get('eligible', 0)}",
            f"Review: {summary.get('review', 0)}",
            f"Discard: {summary.get('discard', 0)}",
            f"Golden Regressions: {summary.get('golden_regressions', 0)}",
        ]
