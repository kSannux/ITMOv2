import base64
import json
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from enum import Enum

import pytest

from export_json import export_visible_to_json, make_export_filename


class Color(Enum):
    RED = "red"


class NumericColor(Enum):
    RED = 1


def parse_payload(payload: str):
    document = json.loads(payload, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    assert set(document) == {"export_date", "total_items", "filters_applied", "data"}
    assert document["export_date"].endswith("Z")
    datetime.fromisoformat(document["export_date"].replace("Z", "+00:00"))
    assert document["total_items"] == len(document["data"])
    return document


def test_exports_rows_in_order_with_metadata_and_unicode():
    rows = [{"id": 2, "name": "Боб", "note": None}, {"id": 1, "name": "Алиса"}]
    filters = {"q": "а", "active": True}

    document = parse_payload(export_visible_to_json(rows, filters))

    assert document["filters_applied"] == filters
    assert document["data"] == rows
    assert [row["id"] for row in document["data"]] == [2, 1]


def test_preserves_duplicate_rows_and_shared_nested_values():
    shared = {"value": [1, 2]}
    rows = [{"nested": shared}, {"nested": shared}, {"nested": {"value": [1, 2]}}]
    document = parse_payload(export_visible_to_json(rows, {}))
    assert document["data"] == [{"nested": shared}] * 3


def test_empty_list_has_exact_error():
    with pytest.raises(ValueError, match=r"^Empty dataset$"):
        export_visible_to_json([])


def test_none_filters_become_empty_dict_and_filters_are_not_mutated():
    assert parse_payload(export_visible_to_json([{}], None))["filters_applied"] == {}

    filters = {"nested": {"values": [1, 2]}}
    original = deepcopy(filters)
    document = parse_payload(export_visible_to_json([{"id": 1}], filters))
    filters["nested"]["values"].append(3)

    assert filters != document["filters_applied"]
    assert filters != original
    assert document["filters_applied"] == original


def test_normalizes_supported_values_and_special_floats_recursively():
    rows = [{
        "datetime": datetime(2026, 1, 2, 3, 4, 5, 123456),
        "date": date(2026, 1, 2),
        "time": time(3, 4, 5, 123456),
        "decimal": Decimal("10.50"),
        "enum": Color.RED,
        "numeric_enum": NumericColor.RED,
        "bytes": b"hi",
        "values": [float("nan"), float("inf"), float("-inf")],
    }]

    item = parse_payload(export_visible_to_json(rows, {}))["data"][0]

    assert item["datetime"] == "2026-01-02T03:04:05.123456Z"
    assert item["date"] == "2026-01-02"
    assert item["time"] == "03:04:05.123456Z"
    assert item["decimal"] == "10.50"
    assert item["enum"] == "red"
    assert item["numeric_enum"] == 1
    assert item["bytes"] == base64.b64encode(b"hi").decode()
    assert item["values"] == ["NaN", "Infinity", "-Infinity"]


def test_timezone_aware_datetime_is_converted_to_utc():
    value = datetime(2026, 1, 2, 5, 4, 5, tzinfo=timezone(timedelta(hours=2)))
    item = parse_payload(export_visible_to_json([{"value": value}], {}))["data"][0]
    assert item["value"] == "2026-01-02T03:04:05Z"


def test_rejects_non_list_rows_and_non_string_keys():
    with pytest.raises(TypeError):
        export_visible_to_json(({"id": 1},))
    with pytest.raises(TypeError):
        export_visible_to_json([{"id": 1, 2: "bad"}])


def test_rejects_unsupported_values_and_invalid_filters_without_mutation():
    class Unsupported:
        pass

    rows = [{"value": Unsupported()}]
    original_value = rows[0]["value"]
    with pytest.raises(TypeError):
        export_visible_to_json(rows)
    assert rows[0]["value"] is original_value

    filters = {"value": float("nan")}
    with pytest.raises(ValueError):
        export_visible_to_json([{"id": 1}], filters)
    assert math_is_nan(filters["value"])


def math_is_nan(value):
    return value != value


def test_rejects_cycles_without_partial_result():
    rows = [{}]
    rows[0]["self"] = rows[0]
    with pytest.raises(ValueError, match="cyclic"):
        export_visible_to_json(rows)


def test_filename_is_utc_and_does_not_touch_filesystem():
    moment = datetime(2026, 10, 29, 14, 34, 56, tzinfo=timezone(timedelta(hours=2)))
    assert make_export_filename(moment) == "export-20261029-123456.json"
    assert make_export_filename(datetime(2026, 10, 29, 12, 34, 56)) == "export-20261029-123456.json"
    with pytest.raises(TypeError):
        make_export_filename("2026")
