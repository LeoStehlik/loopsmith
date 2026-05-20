#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def copy_repo(target: Path) -> None:
    def ignore(dirpath: str, names: list[str]) -> set[str]:
        return {".git", "__pycache__", ".pytest_cache"}.intersection(names)

    shutil.copytree(ROOT, target, ignore=ignore)


def assert_json_output(output: str, key: str) -> None:
    data = json.loads(output)
    if key not in data:
        raise SystemExit(f"missing `{key}` in JSON output")


def main() -> int:
    run([sys.executable, "-m", "compileall", "-q", "src"], ROOT)
    run([sys.executable, "src/cli.py", "--help"], ROOT)

    with tempfile.TemporaryDirectory(prefix="loopsmith-smoke-") as tmp:
        work = Path(tmp) / "repo"
        copy_repo(work)
        agent = run([sys.executable, "src/cli.py", "run", "--agent", "conductor", "--json"], work)
        assert_json_output(agent.stdout, "results")
        shared = run([sys.executable, "src/cli.py", "run-shared", "--pack", "golden:anti-bullshit", "--json"], work)
        assert_json_output(shared.stdout, "summary")

    print("loopsmith smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
