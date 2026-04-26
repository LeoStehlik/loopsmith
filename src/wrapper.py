from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from reporting import ReportFormatter

LOOPSMITH_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = LOOPSMITH_ROOT / "src" / "cli.py"


class LoopsmithWrapper:
    """Bridge the Loopsmith CLI to chat-friendly consumers."""

    def __init__(self):
        self.python_bin = "python3"
        self.reporter = ReportFormatter(style="telegram")

    def run_agent_eval(self, agent: str, candidate: Optional[str] = None) -> Dict[str, Any]:
        cmd = [self.python_bin, str(CLI_PATH), "run", "--agent", agent, "--json"]
        if candidate:
            cmd.extend(["--candidate", candidate])
        return self._run_json_command(cmd)

    def promote_candidate(self, agent: str, candidate_id: str, approved_by: str, notes: str = "") -> Dict[str, Any]:
        cmd = [
            self.python_bin,
            str(CLI_PATH),
            "promote",
            "--agent",
            agent,
            "--candidate",
            candidate_id,
            "--approved-by",
            approved_by,
        ]
        if notes:
            cmd.extend(["--notes", notes])
        return self._run_json_command(cmd)

    def reject_candidate(self, agent: str, candidate_id: str, approved_by: str, notes: str = "") -> Dict[str, Any]:
        cmd = [
            self.python_bin,
            str(CLI_PATH),
            "reject",
            "--agent",
            agent,
            "--candidate",
            candidate_id,
            "--approved-by",
            approved_by,
        ]
        if notes:
            cmd.extend(["--notes", notes])
        return self._run_json_command(cmd)

    def format_telegram_report(self, agent: str, data: Dict[str, Any]) -> str:
        return self.reporter.format_run_report(agent=agent, data=data)

    def _run_json_command(self, cmd: list[str]) -> Dict[str, Any]:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": result.stderr.strip() or result.stdout.strip()}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = self._extract_first_json_object(result.stdout)
            if payload is None:
                return {"error": f"Could not parse CLI output as JSON: {result.stdout.strip()}"}
            return payload

    @staticmethod
    def _extract_first_json_object(text: str) -> Dict[str, Any] | None:
        start = text.find("{")
        if start == -1:
            return None
        depth = 0
        for index in range(start, len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(text[start : index + 1])
        return None


if __name__ == "__main__":
    wrapper = LoopsmithWrapper()
    print(wrapper.format_telegram_report("scout", wrapper.run_agent_eval("scout")))
