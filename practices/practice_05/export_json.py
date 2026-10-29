from __future__ import annotations

import base64
import json
import math
from datetime import date, datetime, time, timezone, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any


def _utc_datetime(value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("moment must be a datetime")
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _datetime_to_json(value: datetime) -> str:
    return _utc_datetime(value).isoformat().replace("+00:00", "Z")


def _time_to_json(value: time) -> str:
    if value.tzinfo is None:
        return value.isoformat() + "Z"
    anchor = datetime(2000, 1, 1, tzinfo=value.tzinfo)
    offset = value.utcoffset()
    if offset is None:
        raise TypeError("time timezone requires a fixed UTC offset")
    utc_value = (datetime.combine(anchor.date(), value) - offset).time()
    return utc_value.replace(tzinfo=None).isoformat() + "Z"


def _normalize_data(value: Any, active: set[int] | None = None) -> Any:
    """Normalize data values while rejecting unsupported or cyclic structures."""
    active = set() if active is None else active

    if value is None:
        return value
    if isinstance(value, Enum):
        return _normalize_data(value.value, active)
    if isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return value
    if isinstance(value, Decimal):
        if value.is_nan():
            return "NaN"
        if value.is_infinite():
            return "Infinity" if value > 0 else "-Infinity"
        return str(value)
    if isinstance(value, datetime):
        return _datetime_to_json(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return _time_to_json(value)
    if isinstance(value, (bytes, bytearray)):
        return base64.b64encode(bytes(value)).decode("ascii")

    identity = id(value)
    if isinstance(value, dict):
        if identity in active:
            raise ValueError("cyclic data structure")
        active.add(identity)
        try:
            result = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TypeError("JSON object keys must be strings")
                result[key] = _normalize_data(item, active)
            return result
        finally:
            active.remove(identity)

    if isinstance(value, list):
        if identity in active:
            raise ValueError("cyclic data structure")
        active.add(identity)
        try:
            return [_normalize_data(item, active) for item in value]
        finally:
            active.remove(identity)

    raise TypeError(f"unsupported value type: {type(value).__name__}")


def _copy_filters(filters_applied: dict[str, Any] | None) -> dict[str, Any]:
    if filters_applied is None:
        return {}
    if not isinstance(filters_applied, dict):
        raise TypeError("filters_applied must be a dict or None")
    result = {}
    active: set[int] = set()
    for key, value in filters_applied.items():
        if not isinstance(key, str):
            raise TypeError("JSON object keys must be strings")
        result[key] = _validate_filter_value(value, active)
    return result


def _validate_filter_value(value: Any, active: set[int]) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("filters_applied contains a non-finite number")
        return value
    if isinstance(value, dict):
        identity = id(value)
        if identity in active:
            raise ValueError("cyclic filters_applied")
        active.add(identity)
        try:
            result = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TypeError("JSON object keys must be strings")
                result[key] = _validate_filter_value(item, active)
            return result
        finally:
            active.remove(identity)
    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise ValueError("cyclic filters_applied")
        active.add(identity)
        try:
            return [_validate_filter_value(item, active) for item in value]
        finally:
            active.remove(identity)
    raise TypeError("filters_applied must contain JSON-compatible values")


def export_visible_to_json(
    filtered_items: list[dict[str, Any]],
    filters_applied: dict[str, Any] | None = None,
) -> str:
    """Return a strict JSON payload for the prepared rows on the current page."""
    if not isinstance(filtered_items, list):
        raise TypeError("filtered_items must be a list")
    if not filtered_items:
        raise ValueError("Empty dataset")

    filters_copy = _copy_filters(filters_applied)
    normalized_rows = []
    for row in filtered_items:
        if not isinstance(row, dict):
            raise TypeError("each row must be a dict")
        normalized_rows.append(_normalize_data(row))

    payload = {
        "export_date": _datetime_to_json(datetime.now(timezone.utc)),
        "total_items": len(normalized_rows),
        "filters_applied": filters_copy,
        "data": normalized_rows,
    }
    return json.dumps(payload, ensure_ascii=False, allow_nan=False)


def make_export_filename(moment: datetime | None = None) -> str:
    """Return the agreed UTC filename without touching the filesystem."""
    if moment is None:
        moment = datetime.now(timezone.utc)
    return _utc_datetime(moment).strftime("export-%Y%m%d-%H%M%S.json")


__all__ = ["export_visible_to_json", "make_export_filename"]
