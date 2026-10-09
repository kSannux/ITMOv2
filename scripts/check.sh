#!/bin/sh
set -eu

# Simple test runner for practice_04

if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest is not installed. Please run: python3 -m pip install -r requirements.txt" >&2
  exit 2
fi

exec pytest -q
