# Evidence provenance

- `before/`: exact contexts and model outputs from the original vulnerable process, plus `security-tests-vulnerable.txt`, the complete run of `test_security.py` against `service.py` from `HEAD`.
- `after-final/`: final-code model contexts, exact JSONL responses, server execution results, and forced tool authorization checks.

Only local `127.0.0.1` services and synthetic lab data were used. No tokens,
passwords, server PIDs, logs, Python caches, or temporary fixture files are
included. No successful LLM prompt injection was demonstrated. Forced JSON
attacks are independent server-authorization tests.
