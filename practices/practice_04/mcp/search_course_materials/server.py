#!/usr/bin/env python3
"""
search_course_materials: CLI tool for searching course materials.

Purpose
- Find text matches across course directories and return file paths, line numbers, and snippets.

Interfaces
- CLI args or stdin JSON:
  Input:
    - query (str, required, length >= 2)
    - include (glob str | [glob], optional)
    - limit (int, default 10, max 100)
  Output:
    - { "results": [{"path","line","snippet"}], "meta": {"query","count","truncated"} }
  Errors:
    - { "error": {"code": "INVALID_INPUT"|"INVALID_INCLUDE"|"INTERNAL", "message": str } }

Notes
- Designed to be callable by an agent/skill and easily wrapped by an MCP stdio server.
- Does not require external packages.
"""

from __future__ import annotations

import argparse
import glob as _glob
import io
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple


DEFAULT_LIMIT = 10
MAX_LIMIT = 100


def _default_source_globs() -> List[str]:
    globs: List[str] = []
    if os.path.isdir("lections"):
        globs.append("lections/**")
    if os.path.isdir("practices"):
        globs.append("practices/**")
    if os.path.isdir("docs"):
        globs.append("docs/**")
    if os.path.isfile("README.md"):
        globs.append("README.md")
    return globs


def _normalize_include(include: Optional[object]) -> Optional[List[str]]:
    if include is None:
        return None
    if isinstance(include, str):
        return [include]
    if isinstance(include, (list, tuple)) and all(isinstance(x, str) for x in include):
        return list(include)
    raise ValueError("INVALID_INCLUDE: include must be a glob string or list of glob strings")


def _expand_files(globs: Optional[Sequence[str]]) -> List[str]:
    patterns = globs if globs else _default_source_globs()
    files: List[str] = []
    seen = set()
    for patt in patterns:
        for path in _glob.glob(patt, recursive=True):
            if os.path.isdir(path):
                continue
            # Skip hidden files in .git and compiled/binary likely files
            if "/.git/" in path or path.endswith(".pyc"):
                continue
            # Deduplicate
            if path not in seen:
                seen.add(path)
                files.append(path)
    return files


@dataclass
class SearchResult:
    path: str
    line: int
    snippet: str


def _iter_lines(path: str) -> Iterable[Tuple[int, str]]:
    try:
        with io.open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, start=1):
                yield i, line.rstrip("\n")
    except Exception:
        return


def _make_snippet(line: str, query: str, width: int = 160) -> str:
    # Simple snippet: trim line and show around the first match
    idx = line.lower().find(query.lower())
    if idx == -1:
        return (line[: width] + ("…" if len(line) > width else "")).strip()
    start = max(0, idx - width // 4)
    end = min(len(line), idx + len(query) + width // 4)
    snippet = line[start:end]
    # Replace tabs for readability
    snippet = snippet.replace("\t", " ")
    if start > 0:
        snippet = "…" + snippet
    if end < len(line):
        snippet = snippet + "…"
    return snippet


def search(query: str, include: Optional[Sequence[str]] = None, limit: int = DEFAULT_LIMIT) -> Tuple[List[SearchResult], bool]:
    if not isinstance(query, str) or len(query.strip()) < 2:
        raise ValueError("INVALID_INPUT: query must be a non-empty string of length >= 2")
    if not isinstance(limit, int) or limit <= 0:
        limit = DEFAULT_LIMIT
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    include_globs = _normalize_include(include)
    files = _expand_files(include_globs)

    results: List[SearchResult] = []
    truncated = False

    q = query.lower()
    for path in files:
        # Basic text filtering: only search likely-text files
        _, ext = os.path.splitext(path)
        if ext and ext.lower() not in {".md", ".txt", ".py", ".json", ".yml", ".yaml"}:
            # Permit files without extension too
            if ext:
                continue
        for line_no, line in _iter_lines(path):
            if q in line.lower():
                results.append(SearchResult(path=path, line=line_no, snippet=_make_snippet(line, query)))
                if len(results) >= limit:
                    truncated = True
                    return results, truncated
    return results, truncated


def _json_success(results: List[SearchResult], query: str, truncated: bool) -> str:
    payload = {
        "results": [
            {"path": r.path, "line": r.line, "snippet": r.snippet}
            for r in results
        ],
        "meta": {"query": query, "count": len(results), "truncated": truncated},
    }
    return json.dumps(payload, ensure_ascii=False)


def _json_error(code: str, message: str) -> str:
    return json.dumps({"error": {"code": code, "message": message}}, ensure_ascii=False)


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="search_course_materials CLI")
    parser.add_argument("--query", "-q", help="query string (length >= 2)")
    parser.add_argument("--include", "-i", action="append", help="glob include pattern (can be given multiple times)")
    parser.add_argument("--limit", "-n", type=int, default=DEFAULT_LIMIT, help=f"max results (default {DEFAULT_LIMIT}, max {MAX_LIMIT})")
    parser.add_argument("--stdin", action="store_true", help="read JSON input from stdin")
    args = parser.parse_args(argv)

    try:
        if args.stdin:
            try:
                data = json.load(sys.stdin)
            except json.JSONDecodeError as e:
                print(_json_error("INVALID_INPUT", f"invalid JSON on stdin: {e}"))
                return 2
            query = data.get("query")
            include = data.get("include")
            limit = data.get("limit", DEFAULT_LIMIT)
        else:
            query = args.query
            include = args.include  # already a list if passed multiple times
            limit = args.limit

        results, truncated = search(query=query, include=include, limit=limit)
        print(_json_success(results, query=query, truncated=truncated))
        return 0
    except ValueError as ve:
        msg = str(ve)
        if msg.startswith("INVALID_INCLUDE"):
            print(_json_error("INVALID_INCLUDE", msg.split(":", 1)[1].strip() if ":" in msg else msg))
            return 3
        if msg.startswith("INVALID_INPUT"):
            print(_json_error("INVALID_INPUT", msg.split(":", 1)[1].strip() if ":" in msg else msg))
            return 2
        print(_json_error("INVALID_INPUT", msg))
        return 2
    except Exception as e:
        print(_json_error("INTERNAL", str(e)))
        return 1


if __name__ == "__main__":
    sys.exit(run_cli())
