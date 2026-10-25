"""Itinerary assembly, destination ranking, and targeted slot swaps."""

from __future__ import annotations

from datetime import timedelta
from typing import Optional
from uuid import uuid4

from src.demo_data import (
    ACTIVITY_BANK,
    CITY_POIS,
    DESTINATIONS,
    base_costs,
    currency_meta,
    find_destination,
    season_for,
)
from src.models import (
    SLOT_LABELS,
    ActivitySlot,
    DataQuality,
    DestinationInfo,
    DestinationRecommendation,
    Itinerary,
    ItineraryDay,
    TripPreferences,
    ensure_slot_ids,
)


DEFAULT_SLOT_TIMES = {
    "Morning Sightseeing": ("09:00", "12:00"),
    "Lunch Recommendation": ("12:30", "14:00"),
    "Afternoon Leisure": ("14:30", "17:30"),
    "Evening Dining & Entertainment": ("19:00", "21:30"),
}


def infer_vibe(prefs: TripPreferences) -> str:
    if prefs.vibe:
        return prefs.vibe
    dest = find_destination(prefs.destination)
    if dest:
        for option in dest["vibes"]:
            if option in ACTIVITY_BANK:
                return option
        return "Urban"
    interests = set(prefs.interests)
    if "History" in interests:
        return "Cultural"
    if "Adventure" in interests:
        return "Mountains"
    if "Nightlife" in interests:
        return "Urban"
    return "Urban"


def recommend_destinations(prefs: TripPreferences, limit: int = 3) -> list[DestinationRecommendation]:
    vibe = infer_vibe(prefs)
    season = season_for(prefs.start_date)
    month = prefs.start_date.month
    ranked: list[tuple[int, dict]] = []
    for item in DESTINATIONS:
        score = 40
        if vibe in item["vibes"] or vibe.lower() in [t.lower() for t in item["tags"]]:
            score += 30
        if prefs.budget_level in item["budget_fit"]:
            score += 15
        else:
            score -= 8
        if month in item["best_months"]:
            score += 15
        else:
            score += 4
        for interest in prefs.interests:
            if interest.lower() in " ".join(item["tags"]).lower() or interest.lower() in item["highlights"].lower():
                score += 5
        if prefs.travel_party == "Family" and "Nightlife" in item["tags"]:
            score -= 4
        ranked.append((min(score, 98), item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    results: list[DestinationRecommendation] = []
    for score, item in ranked[:limit]:
        in_season = month in item["best_months"]
        season_note = (
            f"Estimate — {item['city']} is often more comfortable in months {item['best_months']}. "
            f"Your dates fall in {season}."
        )
        if in_season:
            season_note = (
                f"Estimate — {item['city']} is typically in a favorable window in month {month}. "
                "This is a seasonal heuristic, not live weather."
            )
        reasons = [
            f"Matches a {vibe.lower()} travel mood.",
            f"Budget band {prefs.budget_level} is a reasonable fit among {', '.join(item['budget_fit'])}.",
            item["highlights"],
        ]
        results.append(
            DestinationRecommendation(
                city=item["city"],
                country=item["country"],
                match_score=score,
                reasons=reasons,
                highlight_tags=item["tags"],
                season_note=season_note,
                budget_fit=", ".join(item["budget_fit"]),
                suggested_duration=f"{prefs.duration_days} days",
                is_estimate=True,
                currency=item["currency"],
                currency_symbol=item["currency_symbol"],
            )
        )
    return results


def _slot_template(vibe: str, label: str, day_index: int) -> dict[str, str]:
    bank = ACTIVITY_BANK.get(vibe, ACTIVITY_BANK["Urban"])
    options = bank.get(label, ACTIVITY_BANK["Urban"][label])
    return options[day_index % len(options)]


def _party_tweak(title: str, prefs: TripPreferences) -> str:
    if prefs.travel_party == "Family":
        return title + " (family-friendly window)"
    if prefs.travel_party == "Solo":
        return title + " (easy to do independently)"
    if prefs.travel_party == "Friends":
        return title + " (good for a small group)"
    return title + " (easy for two)"


def _pace_note(prefs: TripPreferences) -> str:
    if prefs.pace == "Relaxed":
        return "Buffer time is built in; skip extra add-ons."
    if prefs.pace == "Fast-Paced":
        return "Keep transfers short; this day is denser by design."
    return "A balanced mix of headline stops and downtime."


def build_demo_itinerary(prefs: TripPreferences, city_override: Optional[str] = None) -> Itinerary:
    city_name = (city_override or prefs.destination or "").strip()
    catalog = find_destination(city_name)
    vibe = infer_vibe(prefs)
    if not catalog:
        catalog = {
            "city": city_name or f"{vibe} getaway",
            "country": "Traveler's choice",
            "currency": "USD",
            "currency_symbol": "$",
            "areas": [f"{vibe} quarter", "Riverside", "Old town", "Night district"],
            "highlights": f"A {vibe.lower()} leaning plan built from demo templates.",
            "tags": [vibe] + list(prefs.interests),
        }
    meta = currency_meta(catalog.get("currency", "USD"))
    costs = base_costs(meta["currency"], prefs.budget_level)
    areas = catalog.get("areas") or [f"{catalog['city']} center"]
    city_pois = CITY_POIS.get(catalog["city"], [])
    days: list[ItineraryDay] = []
    for i in range(prefs.duration_days):
        day_date = prefs.start_date + timedelta(days=i)
        area = areas[i % len(areas)]
        poi = city_pois[i % len(city_pois)] if city_pois else None
        if poi:
            area = poi["area"]
        slots: list[ActivitySlot] = []
        for label in SLOT_LABELS:
            tmpl = _slot_template(vibe, label, i)
            start, end = DEFAULT_SLOT_TIMES[label]
            title = poi["title"] if poi and label == "Morning Sightseeing" else tmpl["title"]
            if prefs.interests and label == "Lunch Recommendation" and "Food" in prefs.interests:
                title = "Regional tasting lunch"
            if prefs.interests and label == "Evening Dining & Entertainment" and "Nightlife" in prefs.interests:
                title = "Neighborhood night-out dinner"
            if prefs.interests and label == "Afternoon Leisure" and "Adventure" in prefs.interests and vibe != "Cultural":
                title = "Light adventure window"
            cost = costs[label]
            if prefs.pace == "Relaxed" and label == "Afternoon Leisure":
                cost = round(cost * 0.8, 2)
            slots.append(
                ActivitySlot(
                    slot_id=f"d{i + 1}-{label.split()[0].lower()}",
                    time_label=label,
                    start_time=start,
                    end_time=end,
                    title=_party_tweak(title, prefs),
                    description=(
                        f"{tmpl['desc']} Neighborhood focus: {area}. {_pace_note(prefs)} "
                        "Cost is an estimate, not a live quote."
                    ),
                    neighborhood=area,
                    estimated_cost=cost,
                    cost_notes="Estimate — not a live price, opening hour, or booked rate.",
                    grouping_note=f"Kept in {area} to reduce backtracking.",
                )
            )
        days.append(
            ItineraryDay(
                day_number=i + 1,
                date=day_date.isoformat(),
                theme=f"{area} day",
                area=area,
                grouping_rationale=(
                    f"Day {i + 1} clusters stops in {area} so you are not crossing the city between meals and sightseeing."
                ),
                slots=slots,
            )
        )
    dest = DestinationInfo(
        city=catalog["city"],
        country=catalog.get("country", ""),
        currency=meta["currency"],
        currency_symbol=meta["currency_symbol"],
        fx_to_inr=meta["fx_to_inr"],
        fx_to_usd=meta["fx_to_usd"],
        fx_note=meta["fx_note"],
    )
    itinerary = Itinerary(
        itinerary_id=str(uuid4()),
        title=f"{prefs.duration_days}-day {dest.city} itinerary",
        destination=dest,
        summary=(
            f"A {prefs.pace.lower()} {prefs.duration_days}-day plan for a {prefs.travel_party.lower()} trip "
            f"with a {prefs.budget_level.lower()} budget. Nearby attractions are grouped by neighborhood each day."
        ),
        assumptions=[
            "Prices, weather, opening hours, and routes are estimates or demo values — not live verified data.",
            f"Budget level '{prefs.budget_level}' scales typical meal and activity costs, not real-time quotes.",
            "FX conversions use a static table for INR and USD context only.",
            "Transit between clustered stops is assumed to be walkable or a short local ride.",
            "Always reconfirm visas, closures, and reservations before travel.",
        ],
        days=days,
        total_estimated_cost=0,
        data_quality=DataQuality(
            mode="demo",
            prices_verified=False,
            weather_verified=False,
            opening_hours_verified=False,
            routes_verified=False,
            notes=[
                "Demo/fallback generator is active.",
                "Do not treat costs or seasonal notes as confirmed.",
            ],
        ),
        preferences=prefs.model_dump(mode="json"),
    )
    return ensure_slot_ids(itinerary)


def apply_demo_swap(itinerary: Itinerary, day_number: int, slot_id: str, request: str, prefs: TripPreferences) -> Itinerary:
    vibe = infer_vibe(prefs)
    request_l = (request or "").lower()
    for day in itinerary.days:
        if day.day_number != day_number:
            continue
        for slot in day.slots:
            if slot.slot_id != slot_id:
                continue
            title = slot.title
            desc = slot.description
            if "vegetarian" in request_l or "vegan" in request_l:
                title = "Vegetarian-friendly neighborhood lunch or dinner"
                desc = "Swapped to a plant-forward option in the same area so the rest of the day stays intact."
            elif "market" in request_l:
                title = "Outdoor market wander"
                desc = "Replaced the original stop with a market in the same neighborhood cluster."
            elif "museum" in request_l and "swap" in request_l:
                title = "Open-air heritage walk"
                desc = "Museum time swapped for an outdoor option without changing other slots."
            elif "nightlife" in request_l or "bar" in request_l:
                title = "Low-key live music or rooftop drinks"
                desc = "Evening slot updated; daytime plan is unchanged."
            elif "adventure" in request_l:
                title = "Guided light adventure session"
                desc = "Inserted a more active option still based in this day's area."
            else:
                tmpl = _slot_template(vibe, slot.time_label, day.day_number)
                title = f"Updated: {tmpl['title']}"
                desc = f"Adjusted from your request: {request}. {tmpl['desc']} Same neighborhood: {day.area}."
            slot.title = title
            slot.description = desc + " Estimate only — not a live booking."
            slot.grouping_note = f"Replacement kept in {day.area}."
            itinerary.data_quality.notes.append(f"Slot {slot_id} on day {day_number} was regenerated.")
            itinerary.recalculate_total()
            return itinerary
    raise ValueError("Could not find that day or time slot to update.")


def preferences_from_itinerary(itinerary: Itinerary) -> TripPreferences:
    raw = itinerary.preferences or {}
    if raw:
        return TripPreferences.model_validate(raw)
    n_days = max(len(itinerary.days), 1)
    start = itinerary.days[0].date
    return TripPreferences(
        destination=itinerary.destination.city,
        duration_days=n_days,
        start_date=start,
        end_date=itinerary.days[-1].date,
        budget_level="Moderate",
        travel_party="Couple",
        pace="Moderate",
        interests=["Food"],
    )
