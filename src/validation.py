"""Form and AI-output validation helpers."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from typing import Any, Optional

from src.models import Itinerary, TripPreferences, ensure_slot_ids, itinerary_from_dict


class ValidationError(ValueError):
    pass


def parse_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValidationError("Use a valid start date.")


def build_preferences(
    destination: str,
    vibe: Optional[str],
    duration_days: int,
    start_date: Any,
    budget_level: str,
    travel_party: str,
    pace: str,
    interests: list[str],
) -> TripPreferences:
    if duration_days < 1 or duration_days > 21:
        raise ValidationError("Trip duration must be between 1 and 21 days.")
    start = parse_date(start_date)
    if start < date.today():
        raise ValidationError("Start date cannot be in the past.")
    dest = (destination or "").strip()
    vibe_value = vibe if vibe in ("Beach", "Mountains", "Cultural", "Urban") else None
    if not dest and not vibe_value:
        raise ValidationError("Enter a destination city or choose a travel vibe.")
    if not budget_level:
        raise ValidationError("Select a budget level.")
    if not travel_party:
        raise ValidationError("Select who is traveling.")
    if not pace:
        raise ValidationError("Select a travel pace.")
    try:
        return TripPreferences(
            destination=dest,
            vibe=vibe_value,
            duration_days=int(duration_days),
            start_date=start,
            end_date=start + timedelta(days=int(duration_days) - 1),
            budget_level=budget_level,  # type: ignore[arg-type]
            travel_party=travel_party,  # type: ignore[arg-type]
            pace=pace,  # type: ignore[arg-type]
            interests=list(interests or []),  # type: ignore[arg-type]
        )
    except Exception as exc:
        raise ValidationError(str(exc)) from exc


def extract_json_payload(text: str) -> Any:
    if not text or not text.strip():
        raise ValidationError("The AI returned an empty response.")
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned, re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError as exc:
                raise ValidationError("Could not parse AI JSON. Try again or use demo mode.") from exc
        start_list = cleaned.find("[")
        end_list = cleaned.rfind("]")
        if start_list >= 0 and end_list > start_list:
            try:
                return json.loads(cleaned[start_list : end_list + 1])
            except json.JSONDecodeError as exc:
                raise ValidationError("Could not parse AI JSON. Try again or use demo mode.") from exc
        raise ValidationError("Could not parse AI JSON. Try again or use demo mode.")


def validate_itinerary_payload(payload: dict[str, Any]) -> Itinerary:
    try:
        itinerary = itinerary_from_dict(payload)
        return ensure_slot_ids(itinerary)
    except Exception as exc:
        raise ValidationError(
            "The itinerary did not match the required schema. Retry generation or switch to demo mode."
        ) from exc
