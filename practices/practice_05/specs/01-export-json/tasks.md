# Tasks: export-filtered-json

**Input**: Design documents from `specs/01-export-json/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/python-export.md`, `quickstart.md`

**Tests**: Included because the user explicitly requested pytest tests. Write tests before implementation and verify they fail first.

**Repository paths**: All implementation, test, and documentation paths below are relative to `practices/practice_05/`.

## Phase 1: Setup

**Purpose**: Confirm the existing Python test environment and preserve the project runner.

- [X] T001 [P] Verify Python and pytest are available for practice-local tests; no shared runner or requirements file is present in `practices/practice_05/`
- [X] T002 Record that the repository-wide runner collects unrelated practices and fails on duplicate module imports; feature tests run directly from `practices/practice_05/tests/`

## Phase 2: Foundational

**Purpose**: Align the feature-local contract and establish the public Python interface before story implementation.

- [X] T003 Synchronize `specs/01-export-json/spec.md` with agreed contract, including current-page-only export, native disabled plus wrapper tooltip, filters as an unchanged dict copy, and NaN/Infinity string conversion in data
- [X] T004 [P] Specify public functions `export_visible_to_json` and `make_export_filename` plus exact input/error behavior in `specs/01-export-json/contracts/python-export.md`

## Phase 3: User Story 1 - Export current-page rows as JSON (Priority: P1, proposed)

**Goal**: Serialize a caller-provided snapshot of current-page rows into a valid UTF-8 JSON payload with UTC metadata, copied filters, preserved row order, visible fields, and defined normalization/error behavior.

**Independent Test**: `python -m pytest -q tests/test_export_json.py` passes; parsed output has exactly four top-level fields, `total_items == len(data)`, valid UTC-Z timestamp, copied filters, and data in input order. Empty input raises exact `ValueError("Empty dataset")`.

### Tests for User Story 1

- [X] T005 [P] [US1] Replace the truncated `tests/test_export_json.py` with contract tests for payload shape, current-page order, duplicate rows, nullable values, Unicode, and exact empty-dataset ValueError
- [X] T006 [P] [US1] Add tests in `tests/test_export_json.py` for deep-copy/no-mutation of `filters_applied`, UTC datetime/date/time handling, Decimal/Enum/bytes, and nested NaN/Infinity/-Infinity conversion
- [X] T007 [US1] Add invalid-input tests in `tests/test_export_json.py` for wrong top-level types, non-string dict keys, unsupported values, filter non-finite numbers, cycles, and failure without partial output or input mutation
- [X] T008 [P] [US1] Add deterministic UTC filename tests for `make_export_filename` in `tests/test_export_json.py`, including offset-aware and naive datetime inputs

### Implementation for User Story 1

- [X] T009 [US1] Implement strict recursive JSON normalization and payload creation in `export_json.py`: exact fields `export_date`, `total_items`, `filters_applied`, `data`; empty list raises `ValueError("Empty dataset")`; preserve null/bool/int/string/finite float and row order; normalize NaN/Infinity/-Infinity in data to strings; do not mutate inputs or coerce non-string keys
- [X] T010 [US1] Implement `make_export_filename(moment=None)` in `export_json.py` using UTC format `export-YYYYMMDD-HHMMSS.json`, treating naive datetimes as UTC and rejecting invalid moment types
- [X] T011 [US1] Run `python -m pytest -q tests/test_export_json.py` and resolve all failures in `export_json.py` and `tests/test_export_json.py`

**Checkpoint**: User Story 1 is complete when targeted pytest passes and the function returns either a complete parseable payload or a documented exception.

## Phase 4: User Story 2 - Surface empty and serialization failures consistently (Priority: P1, proposed)

**Goal**: Give the caller reliable exceptions that map to the agreed UI behavior without disguising serialization failures as empty data.

**Independent Test**: Contract tests distinguish exact `ValueError("Empty dataset")` from other invalid-input errors; no invalid input produces a partial payload or mutates caller-owned data.

### Tests for User Story 2

- [X] T012 [P] [US2] Add tests in `tests/test_export_json.py` distinguishing empty-list ValueError from other ValueError/TypeError cases and verifying rejected filters are not normalized or mutated

### Implementation for User Story 2

- [X] T013 [US2] Refine error paths in `export_json.py` so only an empty row list raises `ValueError("Empty dataset")`; unsupported data raises TypeError, filter non-finite values raise ValueError, and cycles raise ValueError without returning a payload
- [X] T014 [US2] Run targeted pytest and confirm exceptions needed by the UI caller remain distinguishable in `tests/test_export_json.py`

**Checkpoint**: Caller can map only the exact empty-dataset case specially; all other serializer failures remain generic export errors.

## Phase 5: User Story 3 - Produce deterministic UTC download filenames (Priority: P2, proposed)

**Goal**: Provide a default filename matching the agreed UTC timestamp convention.

**Independent Test**: Fixed timestamps produce exactly `export-YYYYMMDD-HHMMSS.json`; offset-aware timestamps are converted to UTC before formatting.

### Implementation for User Story 3

- [X] T015 [US3] Verify and document `make_export_filename` behavior for UTC conversion and same-second filename collisions in `specs/01-export-json/contracts/python-export.md`
- [X] T016 [US3] Confirm filename cases in `tests/test_export_json.py` and ensure the helper performs no filesystem writes

**Checkpoint**: Filename generation is deterministic for a supplied instant and leaves collision handling to the UI save mechanism.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate reproducibility, performance, and documented integration boundaries.

- [X] T017 [P] Create `scripts/benchmark_export_json.py` with one warm-up and 20 measurements over the documented 10,000-row fixed payload; report environment and timings; fail unless at least 19 runs complete within 2 seconds
- [X] T018 Run the benchmark from `scripts/benchmark_export_json.py` and record the result in the implementation report without weakening the SC-4 threshold
- [X] T019 Run the feature validation commands in `specs/01-export-json/quickstart.md` and distinguish targeted feature-test results from unrelated repository collection errors
- [X] T020 Review `export_json.py` and `tests/test_export_json.py` against `specs/01-export-json/contracts/python-export.md`; confirm the UI wrapper/tooltip/download behavior is documented as integration work rather than claimed as implemented here

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately; T002 is diagnostic only and does not block targeted feature work if unrelated repository errors occur.
- **Foundational (Phase 2)**: T003 and T004 precede final contract tests and implementation. T003 is a documentation reconciliation task.
- **User Story 1 (Phase 3)**: Depends on setup and foundational decisions; T005–T008 precede T009–T011.
- **User Story 2 (Phase 4)**: Depends on the serializer and test baseline from US1; strengthens error semantics.
- **User Story 3 (Phase 5)**: Filename helper is part of the same library but is independently testable after setup; T015/T016 finalize its contract and verification.
- **Polish (Phase 6)**: Depends on the completed serializer and tests.

### User Story Dependencies

- **US1 (P1, proposed)**: Main JSON export; starts after foundational contract alignment.
- **US2 (P1, proposed)**: Depends on US1 public error paths; independently validates caller-facing failure distinctions.
- **US3 (P2, proposed)**: Filename generation is a separate helper and can be implemented alongside US1 if working in separate files; current test file is shared, so its tests must be sequenced to avoid conflicts.

### Within Each User Story

- Tests precede implementation (requested pytest coverage).
- The implementation and test file are shared; do not edit either concurrently across tasks.
- Benchmark work can proceed independently after the serializer contract is stable.

### Parallel Opportunities

- T001 and T004 can proceed in parallel (environment inspection vs contract documentation).
- T005 and T006 can be drafted in parallel only if coordinated as a single eventual edit to `tests/test_export_json.py`; do not write the same file concurrently.
- T017 is parallelizable with documentation review after T011, as it touches a separate file.
- US2 error tests and US3 filename tests are conceptually independent but both touch `tests/test_export_json.py`; execute sequentially unless work is isolated and merged carefully.

---

## Parallel Example: User Story 1

```text
Task T001: verify pytest availability and runner behavior
Task T004: document the public serializer and filename contract
```

The two tasks touch separate concerns and can run concurrently. All edits to `tests/test_export_json.py` and `export_json.py` should be sequential because they are shared files.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete T001 and foundational contract alignment T003–T004.
2. Write and run US1 contract tests (T005–T008) to identify expected failures.
3. Implement serializer and UTC filename helper (T009–T010).
4. Validate US1 independently with T011.

### Incremental Delivery

1. Deliver current-page JSON payload and core validation (US1).
2. Confirm exact empty-vs-other-error behavior for UI integration (US2).
3. Confirm UTC filename generation (US3).
4. Run performance and repository checks (Phase 6).

### Parallel Team Strategy

A second contributor may prepare the benchmark task after the serializer contract is stable. Work on the shared serializer/test files should remain sequential to avoid conflicting edits.

---

## Notes

- Every task uses the required checkbox, sequential task ID, optional `[P]`, user-story label where applicable, and explicit file path.
- Priority labels are proposed because the spec gives scenarios but no P1/P2 priorities.
- UI implementation is not present in this Python-library scope; native disabled plus tooltip, loading state, and download handling remain caller integration acceptance criteria.
