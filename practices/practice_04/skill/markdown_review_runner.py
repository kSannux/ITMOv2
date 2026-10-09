#!/usr/bin/env python3
"""
markdown-review runner (skeleton implementation)

Reads JSON from stdin or arguments and validates Markdown files for:
- broken local links (relative paths to missing files)
- unclosed code blocks (``` pairs)
- missing required sections (headings)

Input JSON fields:
- target_paths: string glob or list of globs (required)
- required_sections: list of strings (optional)
- options: { check_anchors: bool } (optional)

Output JSON:
- { issues: [...], summary: { broken_link, unclosed_code_block, missing_section } }

Errors:
- { error: { code: "INVALID_INPUT", message: str } }
"""

from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def _normalize_paths(target_paths: Optional[object]) -> List[str]:
    if isinstance(target_paths, str):
        return [target_paths]
    if isinstance(target_paths, list) and all(isinstance(x, str) for x in target_paths):
        return target_paths
    raise ValueError("INVALID_INPUT: target_paths must be a glob string or list of strings")


def _expand_markdown_files(patterns: Sequence[str]) -> List[str]:
    files: List[str] = []
    seen = set()
    for patt in patterns:
        for path in glob.glob(patt, recursive=True):
            if os.path.isdir(path):
                continue
            if not path.lower().endswith(".md"):
                continue
            if path not in seen:
                seen.add(path)
                files.append(path)
    return files


def _read_lines(path: str) -> List[str]:
    with io.open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().splitlines()


def _is_external_url(url: str) -> bool:
    return "://" in url or url.lower().startswith("mailto:")


def _check_links(file_path: str, lines: List[str], check_anchors: bool) -> List[Dict]:
    issues: List[Dict] = []
    base_dir = os.path.dirname(file_path)
    for i, line in enumerate(lines, start=1):
        for m in LINK_RE.finditer(line):
            url = m.group(2).strip()
            if _is_external_url(url):
                continue
            # Anchor-only link
            if url.startswith('#'):
                if check_anchors:
                    # optional: verify that an anchor exists (not implemented in skeleton)
                    pass
                continue
            # Split base and anchor
            base, *_anchor = url.split('#', 1)
            if not base:
                # local anchor-only, already handled
                continue
            abs_path = os.path.normpath(os.path.join(base_dir, base))
            if not os.path.exists(abs_path):
                issues.append({
                    "type": "broken_link",
                    "file": file_path,
                    "line": i,
                    "message": f"Broken local link to '{url}'",
                })
    return issues


def _check_code_blocks(file_path: str, lines: List[str]) -> List[Dict]:
    issues: List[Dict] = []
    code_open = False
    last_marker_line: Optional[int] = None
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            code_open = not code_open
            last_marker_line = i
    if code_open:
        issues.append({
            "type": "unclosed_code_block",
            "file": file_path,
            "line": last_marker_line,
            "message": "Unclosed code block detected (odd number of ``` markers)",
        })
    return issues


def _extract_headings(lines: List[str]) -> List[str]:
    heads: List[str] = []
    for line in lines:
        m = HEADER_RE.match(line)
        if m:
            heads.append(m.group(2).strip())
    return heads


def _check_required_sections(file_path: str, lines: List[str], required: Sequence[str]) -> List[Dict]:
    if not required:
        return []
    heads = set(_extract_headings(lines))
    issues: List[Dict] = []
    for section in required:
        if section not in heads:
            issues.append({
                "type": "missing_section",
                "file": file_path,
                "message": f"Missing required section: {section}",
            })
    return issues


def run_validation(payload: Dict) -> Dict:
    if not isinstance(payload, dict):
        return {"error": {"code": "INVALID_INPUT", "message": "payload must be an object"}}
    if "target_paths" not in payload:
        return {"error": {"code": "INVALID_INPUT", "message": "target_paths is required"}}

    try:
        patterns = _normalize_paths(payload.get("target_paths"))
    except ValueError as e:
        return {"error": {"code": "INVALID_INPUT", "message": str(e)}}

    required_sections = payload.get("required_sections") or []
    if required_sections and not (
        isinstance(required_sections, list) and all(isinstance(x, str) for x in required_sections)
    ):
        return {"error": {"code": "INVALID_INPUT", "message": "required_sections must be a list of strings"}}

    options = payload.get("options") or {}
    check_anchors = bool(options.get("check_anchors", False))

    files = _expand_markdown_files(patterns)
    issues: List[Dict] = []

    for path in files:
        try:
            lines = _read_lines(path)
        except Exception as e:
            issues.append({
                "type": "io_error",
                "file": path,
                "message": f"Failed to read file: {e}",
            })
            continue

        issues.extend(_check_links(path, lines, check_anchors))
        issues.extend(_check_code_blocks(path, lines))
        issues.extend(_check_required_sections(path, lines, required_sections))

    # Build summary
    summary = {"broken_link": 0, "unclosed_code_block": 0, "missing_section": 0}
    for it in issues:
        t = it.get("type")
        if t in summary:
            summary[t] += 1

    return {"issues": issues, "summary": summary}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="markdown-review runner")
    parser.add_argument("--stdin", action="store_true", help="read JSON input from stdin")
    parser.add_argument("--input", "-i", help="JSON string payload")
    args = parser.parse_args(argv)

    if args.stdin:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": {"code": "INVALID_INPUT", "message": f"invalid JSON on stdin: {e}"}}, ensure_ascii=False))
            return 2
    elif args.input:
        try:
            payload = json.loads(args.input)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": {"code": "INVALID_INPUT", "message": f"invalid JSON: {e}"}}, ensure_ascii=False))
            return 2
    else:
        print(json.dumps({"error": {"code": "INVALID_INPUT", "message": "no input provided"}}, ensure_ascii=False))
        return 2

    result = run_validation(payload)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if "error" not in result else 2


if __name__ == "__main__":
    sys.exit(main())
