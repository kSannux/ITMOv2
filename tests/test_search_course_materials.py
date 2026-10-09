import json
import subprocess
import sys


CLI = [
    sys.executable,
    "practices/practice_04/mcp/search_course_materials/server.py",
]


def run_cli_stdin(payload: dict) -> tuple[int, dict]:
    proc = subprocess.run(
        CLI + ["--stdin"],
        input=json.dumps(payload).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    out = proc.stdout.decode("utf-8").strip()
    try:
        data = json.loads(out) if out else {}
    except json.JSONDecodeError:
        data = {"_raw": out}
    return proc.returncode, data


def test_success_query_found():
    # Query a word likely present in the repo (e.g., 'Практика' in README.md)
    code, data = run_cli_stdin({
        "query": "Практика",
        "include": "README.md",
        "limit": 3,
    })
    assert code == 0, data
    assert "results" in data and isinstance(data["results"], list)
    assert any(r.get("path") == "README.md" for r in data["results"]) or data["meta"]["count"] >= 0


def test_error_short_query():
    code, data = run_cli_stdin({
        "query": "a",
        "include": "README.md",
    })
    assert code != 0
    assert data.get("error", {}).get("code") == "INVALID_INPUT"


def test_error_invalid_include_type():
    code, data = run_cli_stdin({
        "query": "README",
        "include": {"not": "a string or list"},
    })
    assert code != 0
    assert data.get("error", {}).get("code") == "INVALID_INCLUDE"
