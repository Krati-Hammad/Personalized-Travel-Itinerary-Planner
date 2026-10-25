"""Structured itinerary and preference schemas."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


BudgetLevel = Literal["Budget", "Moderate", "Luxury"]
TravelParty = Literal["Solo", "Couple", "Family", "Friends"]
Pace = Literal["Relaxed", "Moderate", "Fast-Paced"]
Interest = Literal["Food", "Adventure", "History", "Nightlife"]
Vibe = Literal["Beach", "Mountains", "Cultural", "Urban"]

SLOT_LABELS = (
    "Morning Sightseeing",
    "Lunch Recommendation",
    "Afternoon Leisure",
    "Evening Dining & Entertainment",
)


class TripPreferences(BaseModel):
    destination: str = ""
    vibe: Optional[Vibe] = None
    duration_days: int = Field(..., ge=1, le=21)
    start_date: date
    end_date: date
    budget_level: BudgetLevel
    travel_party: TravelParty
    pace: Pace
    interests: list[Interest] = Field(default_factory=list)

    @field_validator("destination")
    @classmethod
    def strip_destination(cls, value: str) -> str:
        return (value or "").strip()

    @field_validator("interests")
    @classmethod
    def unique_interests(cls, value: list[Interest]) -> list[Interest]:
        seen: list[Interest] = []
        for item in value:
            if item not in seen:
                seen.append(item)
        return seen

    @model_validator(mode="after")
    def dates_match_duration(self) -> "TripPreferences":
        expected_end = self.start_date + timedelta(days=self.duration_days - 1)
        if self.end_date != expected_end:
            self.end_date = expected_end
        if not self.destination and not self.vibe:
            raise ValueError("Enter a destination or choose a travel vibe.")
        return self

    @property
    def needs_destination_pick(self) -> bool:
        return not bool(self.destination)


class ActivitySlot(BaseModel):
    slot_id: str
    time_label: str
    start_time: str
    end_time: str
    title: str
    description: str
    neighborhood: str
    estimated_cost: float = Field(ge=0)
    cost_notes: str = "Estimate — not a live price quote."
    grouping_note: str = ""


class ItineraryDay(BaseModel):
    day_number: int = Field(ge=1)
    date: str
    theme: str
    area: str
    grouping_rationale: str
    slots: list[ActivitySlot]

    @field_validator("slots")
    @classmethod
    def require_slots(cls, value: list[ActivitySlot]) -> list[ActivitySlot]:
        if len(value) < 4:
            raise ValueError("Each day must include at least four time slots.")
        labels = [slot.time_label for slot in value[:4]]
        if labels != list(SLOT_LABELS):
            raise ValueError(
                "Each day must include Morning Sightseeing, Lunch Recommendation, "
                "Afternoon Leisure, and Evening Dining & Entertainment in that order."
            )
        return value


class DestinationInfo(BaseModel):
    city: str
    country: str
    currency: str = "USD"
    currency_symbol: str = "$"
    fx_to_inr: float = 83.5
    fx_to_usd: float = 1.0
    fx_note: str = "Estimate — exchange rates are not live market quotes."


class DataQuality(BaseModel):
    mode: Literal["demo", "ai"] = "demo"
    prices_verified: bool = False
    weather_verified: bool = False
    opening_hours_verified: bool = False
    routes_verified: bool = False
    notes: list[str] = Field(default_factory=list)


class Itinerary(BaseModel):
    itinerary_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    destination: DestinationInfo
    summary: str
    assumptions: list[str]
    days: list[ItineraryDay]
    total_estimated_cost: float = Field(ge=0)
    data_quality: DataQuality
    preferences: dict[str, Any] = Field(default_factory=dict)

    def convert(self, amount: float, to: str) -> float:
        if to.lower() == "inr":
            return round(amount * self.destination.fx_to_inr, 2)
        if to.lower() == "usd":
            return round(amount * self.destination.fx_to_usd, 2)
        return round(amount, 2)

    def recalculate_total(self) -> None:
        total = 0.0
        for day in self.days:
            for slot in day.slots:
                total += float(slot.estimated_cost or 0)
        self.total_estimated_cost = round(total, 2)


class DestinationRecommendation(BaseModel):
    city: str
    country: str
    match_score: int = Field(ge=0, le=100)
    reasons: list[str]
    highlight_tags: list[str]
    season_note: str
    budget_fit: str
    suggested_duration: str
    is_estimate: bool = True
    currency: str = "USD"
    currency_symbol: str = "$"


class SavedTrip(BaseModel):
    id: str
    title: str
    destination: str
    start_date: str
    end_date: str
    created_at: str
    payload: dict[str, Any]


def itinerary_from_dict(payload: dict[str, Any]) -> Itinerary:
    return Itinerary.model_validate(payload)


def ensure_slot_ids(itinerary: Itinerary) -> Itinerary:
    for day in itinerary.days:
        for index, slot in enumerate(day.slots):
            if not slot.slot_id:
                slot.slot_id = f"d{day.day_number}-s{index + 1}"
    itinerary.recalculate_total()
    return itinerary
