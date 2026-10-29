"""Repeatable performance check for the 10,000-row JSON export contract."""

from __future__ import annotations

import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from export_json import export_visible_to_json


def main() -> int:
    rows = [
        {
            "id": index,
            "name": f"Пользователь {index}",
            "active": index % 2 == 0,
            "values": [index, index + 1, index + 2],
        }
        for index in range(10_000)
    ]
    filters = {"page": 1, "active": True}
    export_visible_to_json(rows, filters)

    durations = []
    for _ in range(20):
        start = time.perf_counter()
        export_visible_to_json(rows, filters)
        durations.append(time.perf_counter() - start)

    ordered = sorted(durations)
    p95 = ordered[18]
    passed = sum(duration <= 2.0 for duration in durations)
    print(f"Python: {sys.version.split()[0]} ({platform.platform()})")
    print(f"Rows: {len(rows)}; measurements: {len(durations)}")
    print("Durations (s): " + ", ".join(f"{value:.4f}" for value in durations))
    print(f"p95 nearest-rank: {p95:.4f}s; runs <= 2s: {passed}/20")
    return 0 if passed >= 19 else 1


if __name__ == "__main__":
    raise SystemExit(main())
