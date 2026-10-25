"""Application configuration, secrets, and demo-mode detection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Personalized Travel Itinerary Planner"
APP_TAGLINE = "Day-by-day plans grouped by neighborhood — with a clear demo fallback."

VALID_PROVIDERS = ("gemini", "groq")
DEFAULT_PROVIDER = "gemini"

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

DATA_DIR = os.getenv("TRAVEL_DATA_DIR", os.path.join(os.getcwd(), "data"))
SQLITE_PATH = os.path.join(DATA_DIR, "trips.db")

# Static FX table used only as unlabeled-as-live estimates.
ESTIMATED_FX = {
    "INR": {"to_inr": 1.0, "to_usd": 0.012},
    "USD": {"to_inr": 83.5, "to_usd": 1.0},
    "EUR": {"to_inr": 90.0, "to_usd": 1.08},
    "GBP": {"to_inr": 106.0, "to_usd": 1.27},
    "JPY": {"to_inr": 0.56, "to_usd": 0.0067},
    "AUD": {"to_inr": 55.0, "to_usd": 0.66},
    "SGD": {"to_inr": 62.0, "to_usd": 0.74},
    "AED": {"to_inr": 22.7, "to_usd": 0.27},
    "THB": {"to_inr": 2.4, "to_usd": 0.029},
    "IDR": {"to_inr": 0.0053, "to_usd": 0.000063},
    "ZAR": {"to_inr": 4.6, "to_usd": 0.055},
    "MAD": {"to_inr": 8.4, "to_usd": 0.10},
    "NZD": {"to_inr": 50.0, "to_usd": 0.60},
}

BUDGET_LEVELS = ("Budget", "Moderate", "Luxury")
TRAVEL_PARTIES = ("Solo", "Couple", "Family", "Friends")
PACES = ("Relaxed", "Moderate", "Fast-Paced")
INTERESTS = ("Food", "Adventure", "History", "Nightlife")
VIBES = ("Beach", "Mountains", "Cultural", "Urban")


def _secret_get(name: str, default: str = "") -> str:
    value = os.getenv(name, default) or default
    try:
        import streamlit as st

        if hasattr(st, "secrets"):
            try:
                secret_val = st.secrets.get(name)
                if secret_val:
                    return str(secret_val).strip()
            except Exception:
                pass
    except Exception:
        pass
    return str(value).strip()


@dataclass
class AppSettings:
    provider: str = DEFAULT_PROVIDER
    gemini_api_key: str = ""
    groq_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    session_override_key: str = ""
    session_override_provider: str = ""

    @property
    def active_provider(self) -> str:
        provider = (self.session_override_provider or self.provider or DEFAULT_PROVIDER).lower()
        return provider if provider in VALID_PROVIDERS else DEFAULT_PROVIDER

    @property
    def active_api_key(self) -> str:
        if self.session_override_key:
            return self.session_override_key.strip()
        if self.active_provider == "groq":
            return self.groq_api_key
        return self.gemini_api_key

    @property
    def demo_mode(self) -> bool:
        return not bool(self.active_api_key)

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)


def load_settings(session: Optional[dict[str, Any]] = None) -> AppSettings:
    session = session or {}
    return AppSettings(
        provider=_secret_get("AI_PROVIDER", DEFAULT_PROVIDER).lower() or DEFAULT_PROVIDER,
        gemini_api_key=_secret_get("GEMINI_API_KEY"),
        groq_api_key=_secret_get("GROQ_API_KEY"),
        supabase_url=_secret_get("SUPABASE_URL"),
        supabase_key=_secret_get("SUPABASE_KEY") or _secret_get("SUPABASE_ANON_KEY"),
        session_override_key=str(session.get("api_key_override") or "").strip(),
        session_override_provider=str(session.get("provider_override") or "").strip(),
    )
