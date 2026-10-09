#!/usr/bin/env python3
"""
MCP stdio server for search_course_materials.

Registers a tool "search_course_materials.search" that searches across
course materials and returns matches with file paths, line numbers, and snippets.

Requirements:
- pip install mcp  # official Model Context Protocol Python library

Usage (stdio):
- This process is intended to be launched by an MCP-compatible client.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Optional, Sequence

try:
    # Use FastMCP from the mcp package (v2 API)
    from mcp.server.fastmcp import FastMCP as FastMCPServer
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "The 'mcp' package with FastMCP is required. Install/upgrade with 'pip install -U mcp'.\n"
        f"Import error: {e}"
    )

# Standalone search implementation (embedded to avoid import issues when launched as a script)
import glob as _glob
import io
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


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
            if "/.git/" in path or path.endswith(".pyc"):
                continue
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
    idx = line.lower().find(query.lower())
    if idx == -1:
        return (line[: width] + ("…" if len(line) > width else "")).strip()
    start = max(0, idx - width // 4)
    end = min(len(line), idx + len(query) + width // 4)
    snippet = line[start:end].replace("\t", " ")
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
        _, ext = os.path.splitext(path)
        if ext and ext.lower() not in {".md", ".txt", ".py", ".json", ".yml", ".yaml"}:
            if ext:
                continue
        for line_no, line in _iter_lines(path):
            if q in line.lower():
                results.append(SearchResult(path=path, line=line_no, snippet=_make_snippet(line, query)))
                if len(results) >= limit:
                    truncated = True
                    return results, truncated
    return results, truncated


INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "minLength": 2},
        "include": {
            "oneOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}},
                {"type": "null"},
            ]
        },
        "limit": {"type": "integer", "minimum": 1, "maximum": 100},
    },
    "required": ["query"],
    "additionalProperties": False,
}


try:
    server = FastMCPServer("search_course_materials")
except TypeError:
    server = FastMCPServer(name="search_course_materials")


async def tool_search(params: Dict[str, Any]) -> Dict[str, Any]:
    query = params.get("query")
    include = params.get("include")
    limit = params.get("limit")
    # Run the search (synchronous function; safe to run directly)
    try:
        results, truncated = search(query=query, include=include, limit=limit or 10)
        return {
            "results": [
                {"path": r.path, "line": r.line, "snippet": r.snippet}
                for r in results
            ],
            "meta": {"query": query, "count": len(results), "truncated": truncated},
        }
    except ValueError as ve:
        msg = str(ve)
        if msg.startswith("INVALID_INCLUDE"):
            raise ValueError("INVALID_INCLUDE: include must be a glob string or list of glob strings")
        if msg.startswith("INVALID_INPUT"):
            raise ValueError("INVALID_INPUT: query must be length >= 2")
        raise


# Register tool with FastMCP API (supports both function and decorator styles)
_tool_attr = getattr(server, "tool", None)
if callable(_tool_attr):
    try:
        # Function-style registration: (name, func)
        _tool_attr("search_course_materials.search", tool_search)
    except TypeError:
        # Decorator-style registration: tool(name)(func)
        dec = _tool_attr("search_course_materials.search")
        dec(tool_search)
else:
    raise SystemExit("FastMCP 'tool' registration API not found on server instance")


def main() -> None:
    # FastMCPServer handles stdio internally; register tool and serve.
    # This method is synchronous and manages its own event loop.
    server.run()


if __name__ == "__main__":
    main()
