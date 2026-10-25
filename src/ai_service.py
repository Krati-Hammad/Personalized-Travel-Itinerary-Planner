"""Gemini/Groq integration with a usable demo fallback."""

from __future__ import annotations

import json
from typing import Optional

from src.config import GEMINI_MODEL, GROQ_MODEL, AppSettings
from src.itinerary import apply_demo_swap, build_demo_itinerary, recommend_destinations
from src.models import DestinationRecommendation, Itinerary, TripPreferences, ensure_slot_ids
from src.validation import ValidationError, extract_json_payload, validate_itinerary_payload


SYSTEM_RULES = """You are a travel planner that returns ONLY valid JSON.
Never claim prices, weather, opening hours, or routes are live or verified.
Use estimates and include that wording in cost_notes and assumptions.
Group nearby attractions on the same day (one neighborhood/area per day).
Each day MUST contain these time_label values in order:
- Morning Sightseeing
- Lunch Recommendation
- Afternoon Leisure
- Evening Dining & Entertainment
Costs must be numbers in the local currency.
"""


def _prefs_blob(prefs: TripPreferences) -> str:
    return json.dumps(prefs.model_dump(mode="json"), indent=2)


def itinerary_schema_hint() -> str:
    return """{
  "title": "string",
  "destination": {
    "city": "string",
    "country": "string",
    "currency": "USD",
    "currency_symbol": "$",
    "fx_to_inr": 83.5,
    "fx_to_usd": 1.0,
    "fx_note": "Estimate — exchange rates are not live market quotes."
  },
  "summary": "string",
  "assumptions": ["string"],
  "days": [
    {
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "theme": "string",
      "area": "string",
      "grouping_rationale": "string",
      "slots": [
        {
          "slot_id": "d1-morning",
          "time_label": "Morning Sightseeing",
          "start_time": "09:00",
          "end_time": "12:00",
          "title": "string",
          "description": "string",
          "neighborhood": "string",
          "estimated_cost": 0,
          "cost_notes": "Estimate — not a live price quote.",
          "grouping_note": "string"
        }
      ]
    }
  ],
  "total_estimated_cost": 0,
  "data_quality": {
    "mode": "ai",
    "prices_verified": false,
    "weather_verified": false,
    "opening_hours_verified": false,
    "routes_verified": false,
    "notes": ["Estimates only"]
  },
  "preferences": {}
}"""


def _complete_itinerary(payload: dict, prefs: TripPreferences, mode: str) -> Itinerary:
    payload.setdefault("preferences", prefs.model_dump(mode="json"))
    payload.setdefault("title", f"{prefs.duration_days}-day trip")
    dq = payload.setdefault("data_quality", {})
    dq["mode"] = mode
    dq["prices_verified"] = False
    dq["weather_verified"] = False
    dq["opening_hours_verified"] = False
    dq["routes_verified"] = False
    itinerary = validate_itinerary_payload(payload)
    itinerary.recalculate_total()
    return ensure_slot_ids(itinerary)


def _call_gemini(api_key: str, prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    text = getattr(response, "text", None)
    if not text:
        raise ValidationError("Gemini returned no text.")
    return text


def _call_groq(api_key: str, prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.4,
        messages=[
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.choices[0].message.content
    if not text:
        raise ValidationError("Groq returned no text.")
    return text


def _call_model(settings: AppSettings, prompt: str) -> str:
    key = settings.active_api_key
    if not key:
        raise ValidationError("No API key configured.")
    if settings.active_provider == "groq":
        return _call_groq(key, prompt)
    return _call_gemini(key, prompt)


def generate_itinerary(
    prefs: TripPreferences,
    settings: AppSettings,
    city_override: Optional[str] = None,
    force_demo: bool = False,
) -> Itinerary:
    if city_override:
        prefs = prefs.model_copy(update={"destination": city_override})
    if force_demo or settings.demo_mode:
        return build_demo_itinerary(prefs, city_override=city_override)
    prompt = (
        f"{SYSTEM_RULES}\nCreate a complete itinerary JSON matching this schema:\n{itinerary_schema_hint()}\n"
        f"Trip preferences:\n{_prefs_blob(prefs)}\n"
        "Return one itinerary object, not a list. Fill every day of the duration."
    )
    try:
        raw = _call_model(settings, prompt)
        payload = extract_json_payload(raw)
        if isinstance(payload, list):
            payload = payload[0]
        return _complete_itinerary(payload, prefs, "ai")
    except Exception as exc:
        raise ValidationError(
            f"AI itinerary generation failed ({exc}). You can retry or generate a demo itinerary."
        ) from exc


def generate_recommendations(
    prefs: TripPreferences,
    settings: AppSettings,
    force_demo: bool = False,
) -> list[DestinationRecommendation]:
    demo = recommend_destinations(prefs)
    if force_demo or settings.demo_mode:
        return demo
    prompt = (
        f"{SYSTEM_RULES}\nRecommend the top 3 cities as a JSON list. Each item: "
        "city, country, match_score (0-100), reasons (list), highlight_tags (list), "
        "season_note, budget_fit, suggested_duration, is_estimate (true), currency, currency_symbol.\n"
        "Label season_note as an estimate. Do not invent live weather.\n"
        f"Preferences:\n{_prefs_blob(prefs)}"
    )
    try:
        raw = _call_model(settings, prompt)
        payload = extract_json_payload(raw)
        if isinstance(payload, dict):
            payload = payload.get("recommendations") or payload.get("cities") or [payload]
        results = [DestinationRecommendation.model_validate(item) for item in payload][:3]
        if not results:
            raise ValidationError("No recommendations returned.")
        return results
    except Exception as exc:
        raise ValidationError(
            f"AI destination recommendations failed ({exc}). You can retry or use demo recommendations."
        ) from exc


def swap_activity(
    itinerary: Itinerary,
    prefs: TripPreferences,
    settings: AppSettings,
    day_number: int,
    slot_id: str,
    request: str,
    force_demo: bool = False,
) -> Itinerary:
    if not request.strip():
        raise ValidationError("Describe the change you want for this time slot.")
    if force_demo or settings.demo_mode:
        return apply_demo_swap(itinerary, day_number, slot_id, request, prefs)

    target_slot = None
    target_day = None
    for day in itinerary.days:
        if day.day_number == day_number:
            target_day = day
            for slot in day.slots:
                if slot.slot_id == slot_id:
                    target_slot = slot
    if not target_slot or not target_day:
        raise ValidationError("That time slot could not be found.")

    prompt = (
        f"{SYSTEM_RULES}\nReplace ONLY this one activity slot. Return JSON for a single slot object "
        "with the same keys as ActivitySlot. Keep the same time_label, slot_id, start_time, end_time, "
        f"and neighborhood ({target_day.area}) unless the user explicitly needs a nearby alternative.\n"
        f"User request: {request}\nExisting slot:\n{target_slot.model_dump_json()}\n"
        f"Trip preferences:\n{_prefs_blob(prefs)}"
    )
    try:
        raw = _call_model(settings, prompt)
        payload = extract_json_payload(raw)
        if isinstance(payload, list):
            payload = payload[0]
        payload["slot_id"] = slot_id
        payload["time_label"] = target_slot.time_label
        payload.setdefault("start_time", target_slot.start_time)
        payload.setdefault("end_time", target_slot.end_time)
        payload.setdefault("neighborhood", target_day.area)
        from src.models import ActivitySlot

        new_slot = ActivitySlot.model_validate(payload)
        for day in itinerary.days:
            if day.day_number != day_number:
                continue
            day.slots = [new_slot if s.slot_id == slot_id else s for s in day.slots]
        itinerary.data_quality.notes.append(f"AI regenerated slot {slot_id} on day {day_number} only.")
        itinerary.recalculate_total()
        return itinerary
    except Exception as exc:
        raise ValidationError(
            f"AI slot update failed ({exc}). You can retry or apply a demo swap."
        ) from exc
