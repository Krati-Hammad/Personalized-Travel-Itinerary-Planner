"""Curated demo destinations, seasonal notes, and itinerary templates."""

from __future__ import annotations

from datetime import date
from typing import Any

from src.config import ESTIMATED_FX

MONTH_SEASON = {
    1: "winter",
    2: "winter",
    3: "spring",
    4: "spring",
    5: "spring",
    6: "summer",
    7: "summer",
    8: "summer",
    9: "autumn",
    10: "autumn",
    11: "autumn",
    12: "winter",
}

DESTINATIONS: list[dict[str, Any]] = [
    {
        "city": "Goa",
        "country": "India",
        "vibes": ["Beach"],
        "budget_fit": ["Budget", "Moderate", "Luxury"],
        "currency": "INR",
        "currency_symbol": "₹",
        "best_months": [11, 12, 1, 2, 3],
        "tags": ["Beaches", "Seafood", "Nightlife"],
        "areas": ["North Goa", "Panaji", "South Goa", "Old Goa"],
        "highlights": "Sun, spice, and Portuguese-era neighborhoods.",
    },
    {
        "city": "Bali",
        "country": "Indonesia",
        "vibes": ["Beach", "Cultural"],
        "budget_fit": ["Budget", "Moderate", "Luxury"],
        "currency": "IDR",
        "currency_symbol": "Rp",
        "best_months": [4, 5, 6, 7, 8, 9],
        "tags": ["Temples", "Rice terraces", "Wellness"],
        "areas": ["Ubud", "Canggu", "Seminyak", "Uluwatu"],
        "highlights": "Island temples, coastline cliffs, and slow mornings.",
    },
    {
        "city": "Kyoto",
        "country": "Japan",
        "vibes": ["Cultural"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "JPY",
        "currency_symbol": "¥",
        "best_months": [3, 4, 5, 10, 11],
        "tags": ["Temples", "Gardens", "Food"],
        "areas": ["Higashiyama", "Arashiyama", "Gion", "Fushimi"],
        "highlights": "Walkable historic districts and seasonal gardens.",
    },
    {
        "city": "Paris",
        "country": "France",
        "vibes": ["Cultural", "Urban"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "EUR",
        "currency_symbol": "€",
        "best_months": [4, 5, 6, 9, 10],
        "tags": ["Museums", "Cafés", "Walks"],
        "areas": ["Marais", "Latin Quarter", "Montmartre", "Saint-Germain"],
        "highlights": "Museum clusters and café-lined neighborhoods.",
    },
    {
        "city": "Jaipur",
        "country": "India",
        "vibes": ["Cultural"],
        "budget_fit": ["Budget", "Moderate", "Luxury"],
        "currency": "INR",
        "currency_symbol": "₹",
        "best_months": [10, 11, 12, 1, 2, 3],
        "tags": ["Forts", "Markets", "Crafts"],
        "areas": ["Pink City", "Amer", "Bani Park", "C-Scheme"],
        "highlights": "Forts, bazaars, and courtyard dining.",
    },
    {
        "city": "Manali",
        "country": "India",
        "vibes": ["Mountains", "Adventure"],
        "budget_fit": ["Budget", "Moderate"],
        "currency": "INR",
        "currency_symbol": "₹",
        "best_months": [3, 4, 5, 6, 9, 10],
        "tags": ["Hiking", "Valleys", "Cafés"],
        "areas": ["Old Manali", "Mall Road", "Solang", "Naggar"],
        "highlights": "Valley walks and pine-scented café mornings.",
    },
    {
        "city": "Barcelona",
        "country": "Spain",
        "vibes": ["Urban", "Beach", "Cultural"],
        "budget_fit": ["Budget", "Moderate", "Luxury"],
        "currency": "EUR",
        "currency_symbol": "€",
        "best_months": [4, 5, 6, 9, 10],
        "tags": ["Architecture", "Tapas", "Coast"],
        "areas": ["Gothic Quarter", "Eixample", "Barceloneta", "Gràcia"],
        "highlights": "Compact districts, tapas bars, and a city beach.",
    },
    {
        "city": "New York",
        "country": "USA",
        "vibes": ["Urban"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "USD",
        "currency_symbol": "$",
        "best_months": [4, 5, 6, 9, 10],
        "tags": ["Museums", "Food", "Neighborhoods"],
        "areas": ["Lower Manhattan", "Brooklyn", "Midtown", "Upper West Side"],
        "highlights": "Walkable boroughs with dense food and museum clusters.",
    },
    {
        "city": "Rome",
        "country": "Italy",
        "vibes": ["Cultural"],
        "budget_fit": ["Budget", "Moderate", "Luxury"],
        "currency": "EUR",
        "currency_symbol": "€",
        "best_months": [4, 5, 9, 10],
        "tags": ["History", "Food", "Piazzas"],
        "areas": ["Centro Storico", "Trastevere", "Vatican", "Monti"],
        "highlights": "Ancient sites grouped by walkable historic cores.",
    },
    {
        "city": "Cape Town",
        "country": "South Africa",
        "vibes": ["Mountains", "Beach", "Urban"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "ZAR",
        "currency_symbol": "R",
        "best_months": [1, 2, 3, 11, 12],
        "tags": ["Coast", "Hikes", "Wine"],
        "areas": ["City Bowl", "Camps Bay", "Stellenbosch", "Hout Bay"],
        "highlights": "Mountain, Atlantic coast, and nearby wine country.",
    },
    {
        "city": "Lisbon",
        "country": "Portugal",
        "vibes": ["Urban", "Cultural", "Beach"],
        "budget_fit": ["Budget", "Moderate"],
        "currency": "EUR",
        "currency_symbol": "€",
        "best_months": [4, 5, 6, 9, 10],
        "tags": ["Viewpoints", "Tiles", "Seafood"],
        "areas": ["Alfama", "Baixa", "Belém", "Bairro Alto"],
        "highlights": "Hilltop viewpoints and compact historic quarters.",
    },
    {
        "city": "Dubai",
        "country": "UAE",
        "vibes": ["Urban", "Beach"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "AED",
        "currency_symbol": "د.إ",
        "best_months": [11, 12, 1, 2, 3],
        "tags": ["Skyline", "Desert", "Dining"],
        "areas": ["Downtown", "Marina", "Old Dubai", "Palm"],
        "highlights": "Modern skyline clusters plus heritage souks.",
    },
    {
        "city": "Bangkok",
        "country": "Thailand",
        "vibes": ["Urban", "Cultural", "Food"],
        "budget_fit": ["Budget", "Moderate"],
        "currency": "THB",
        "currency_symbol": "฿",
        "best_months": [11, 12, 1, 2],
        "tags": ["Temples", "Street food", "Markets"],
        "areas": ["Rattanakosin", "Sukhumvit", "Chinatown", "Riverside"],
        "highlights": "Temple islands, markets, and late-night food streets.",
    },
    {
        "city": "Udaipur",
        "country": "India",
        "vibes": ["Cultural"],
        "budget_fit": ["Budget", "Moderate", "Luxury"],
        "currency": "INR",
        "currency_symbol": "₹",
        "best_months": [10, 11, 12, 1, 2, 3],
        "tags": ["Lakes", "Palaces", "Crafts"],
        "areas": ["City Palace", "Lake Pichola", "Fateh Sagar", "Old City"],
        "highlights": "Lake palaces and compact old-city lanes.",
    },
    {
        "city": "Queenstown",
        "country": "New Zealand",
        "vibes": ["Mountains", "Adventure"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "NZD",
        "currency_symbol": "$",
        "best_months": [12, 1, 2, 3, 6, 7],
        "tags": ["Lakes", "Adventure", "Trails"],
        "areas": ["Town Centre", "Remarkables", "Glenorchy", "Arrowtown"],
        "highlights": "Lake Wakatipu days grouped by valley access.",
    },
    {
        "city": "Santorini",
        "country": "Greece",
        "vibes": ["Beach", "Cultural"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "EUR",
        "currency_symbol": "€",
        "best_months": [5, 6, 9, 10],
        "tags": ["Caldera", "Villages", "Sunset"],
        "areas": ["Fira", "Oia", "Pyrgos", "Perissa"],
        "highlights": "Cliff villages and a quieter inland/beach day.",
    },
    {
        "city": "Marrakech",
        "country": "Morocco",
        "vibes": ["Cultural", "Urban"],
        "budget_fit": ["Budget", "Moderate", "Luxury"],
        "currency": "MAD",
        "currency_symbol": "د.م.",
        "best_months": [3, 4, 5, 10, 11],
        "tags": ["Souks", "Riads", "Gardens"],
        "areas": ["Medina", "Jardin Majorelle", "Palmeraie", "Gueliz"],
        "highlights": "Medina walking days with a garden/new-town contrast.",
    },
    {
        "city": "Singapore",
        "country": "Singapore",
        "vibes": ["Urban", "Food"],
        "budget_fit": ["Moderate", "Luxury"],
        "currency": "SGD",
        "currency_symbol": "S$",
        "best_months": [1, 2, 3, 6, 7],
        "tags": ["Hawker food", "Gardens", "Neighborhoods"],
        "areas": ["Marina Bay", "Chinatown", "Kampong Glam", "Sentosa"],
        "highlights": "Neighborhood food clusters and compact transit hops.",
    },
]


ACTIVITY_BANK: dict[str, dict[str, list[dict[str, str]]]] = {
    "Beach": {
        "Morning Sightseeing": [
            {"title": "Coastal walk and viewpoint", "desc": "Start along the shoreline before crowds build."},
            {"title": "Harbor and old town stroll", "desc": "Explore the waterfront heritage streets on foot."},
        ],
        "Lunch Recommendation": [
            {"title": "Seafood shack lunch", "desc": "Casual catch-of-the-day plates near the beach."},
            {"title": "Waterfront café", "desc": "Light lunch with a sea breeze and shade."},
        ],
        "Afternoon Leisure": [
            {"title": "Beach club or swim window", "desc": "Stay in the same coastal pocket to avoid midday transit."},
            {"title": "Coastal market browse", "desc": "Slow shopping and shade breaks near the water."},
        ],
        "Evening Dining & Entertainment": [
            {"title": "Sunset dinner by the water", "desc": "Book an early table and stay for evening music."},
            {"title": "Night market and dessert walk", "desc": "Keep the evening in the same neighborhood cluster."},
        ],
    },
    "Mountains": {
        "Morning Sightseeing": [
            {"title": "Valley viewpoint hike", "desc": "Short trail with big views while temperatures are cooler."},
            {"title": "Old village and temple walk", "desc": "Explore a compact hillside settlement on foot."},
        ],
        "Lunch Recommendation": [
            {"title": "Mountain café lunch", "desc": "Hearty plates near the trailhead so you skip extra driving."},
            {"title": "Local thali or lodge kitchen", "desc": "Simple regional food close to your afternoon area."},
        ],
        "Afternoon Leisure": [
            {"title": "River or pine forest walk", "desc": "Stay in the same valley pocket after lunch."},
            {"title": "Scenic drive to a nearby hamlet", "desc": "One outbound hop, then linger rather than zigzag."},
        ],
        "Evening Dining & Entertainment": [
            {"title": "Fireplace lodge dinner", "desc": "Early dinner and stargazing near your stay."},
            {"title": "Mall road café crawl", "desc": "Keep nightlife walkable if the group wants a later night."},
        ],
    },
    "Cultural": {
        "Morning Sightseeing": [
            {"title": "Heritage core walking circuit", "desc": "Group the main monuments that sit in one historic district."},
            {"title": "Palace or museum cluster", "desc": "Start at opening time in a single ticketed zone."},
        ],
        "Lunch Recommendation": [
            {"title": "Courtyard restaurant", "desc": "Regional set lunch a short walk from the morning sites."},
            {"title": "Bazaar food hall", "desc": "Try local specialties without leaving the old city."},
        ],
        "Afternoon Leisure": [
            {"title": "Craft workshops and side streets", "desc": "Stay in the same district for shopping and shade."},
            {"title": "Garden or stepwell pause", "desc": "A quieter heritage stop instead of a long transfer."},
        ],
        "Evening Dining & Entertainment": [
            {"title": "Folk performance dinner", "desc": "Dinner plus cultural show in the same old-city pocket."},
            {"title": "Rooftop old-town dining", "desc": "Sunset views without crossing the city at rush hour."},
        ],
    },
    "Urban": {
        "Morning Sightseeing": [
            {"title": "Signature neighborhood walk", "desc": "Cover one borough or district before lunch."},
            {"title": "Museum morning", "desc": "Pick one major museum instead of splitting across town."},
        ],
        "Lunch Recommendation": [
            {"title": "Neighborhood bistro", "desc": "Sit-down lunch in the same district as the morning plan."},
            {"title": "Market hall tasting lunch", "desc": "Grazing lunch that matches a Food-forward interest."},
        ],
        "Afternoon Leisure": [
            {"title": "Park, waterfront, or design district", "desc": "Stay nearby; skip a crosstown hop in peak traffic."},
            {"title": "Independent shops and galleries", "desc": "Keep browsing walkable from lunch."},
        ],
        "Evening Dining & Entertainment": [
            {"title": "Reservation dinner and a show", "desc": "Cluster evening plans in one nightlife pocket."},
            {"title": "Late bites and a skyline walk", "desc": "Dessert and a viewpoint within a short ride."},
        ],
    },
}

CITY_POIS: dict[str, list[dict[str, str]]] = {
    "Goa": [
        {"area": "North Goa", "title": "Fort Aguada and Candolim beach loop"},
        {"area": "Old Goa", "title": "Basilica of Bom Jesus and Se Cathedral"},
        {"area": "Panaji", "title": "Fontainhas Latin Quarter walk"},
        {"area": "South Goa", "title": "Colva to Benaulim slow beach afternoon"},
    ],
    "Kyoto": [
        {"area": "Higashiyama", "title": "Kiyomizu-dera and Sannenzaka lanes"},
        {"area": "Arashiyama", "title": "Bamboo grove and riverside path"},
        {"area": "Fushimi", "title": "Fushimi Inari early shrine walk"},
        {"area": "Gion", "title": "Gion Shirakawa evening stroll"},
    ],
    "Paris": [
        {"area": "Louvre / Marais", "title": "Louvre morning then Marais lanes"},
        {"area": "Latin Quarter", "title": "Île de la Cité and Left Bank bookshops"},
        {"area": "Montmartre", "title": "Sacré-Cœur and village streets"},
        {"area": "Saint-Germain", "title": "Café terrace and gallery afternoon"},
    ],
    "Rome": [
        {"area": "Colosseum basin", "title": "Colosseum and Roman Forum pairing"},
        {"area": "Vatican", "title": "Vatican Museums and St. Peter's"},
        {"area": "Centro Storico", "title": "Pantheon to Trevi walking loop"},
        {"area": "Trastevere", "title": "Trastevere lanes and trattoria night"},
    ],
    "Jaipur": [
        {"area": "Amer", "title": "Amber Fort morning"},
        {"area": "Pink City", "title": "City Palace and Jantar Mantar"},
        {"area": "Pink City", "title": "Johari and Bapu Bazaar crafts"},
        {"area": "C-Scheme", "title": "Nahargarh sunset viewpoint"},
    ],
}


def currency_meta(code: str) -> dict[str, Any]:
    code = (code or "USD").upper()
    fx = ESTIMATED_FX.get(code, ESTIMATED_FX["USD"])
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "AUD": "A$",
        "SGD": "S$",
        "AED": "د.إ",
        "THB": "฿",
        "IDR": "Rp",
        "ZAR": "R",
        "MAD": "د.م.",
        "NZD": "NZ$",
    }
    return {
        "currency": code,
        "currency_symbol": symbols.get(code, "$"),
        "fx_to_inr": fx["to_inr"],
        "fx_to_usd": fx["to_usd"],
        "fx_note": "Estimate — exchange rates are not live market quotes.",
    }


def season_for(start: date) -> str:
    return MONTH_SEASON.get(start.month, "shoulder")


def find_destination(name: str) -> dict[str, Any] | None:
    needle = (name or "").strip().lower()
    if not needle:
        return None
    for item in DESTINATIONS:
        if item["city"].lower() == needle or needle in f"{item['city']} {item['country']}".lower():
            return item
    return None


def budget_multiplier(level: str) -> float:
    return {"Budget": 0.7, "Moderate": 1.0, "Luxury": 1.8}.get(level, 1.0)


def base_costs(currency: str, level: str) -> dict[str, float]:
    table = {
        "INR": {"Morning Sightseeing": 800, "Lunch Recommendation": 700, "Afternoon Leisure": 600, "Evening Dining & Entertainment": 1200},
        "USD": {"Morning Sightseeing": 35, "Lunch Recommendation": 22, "Afternoon Leisure": 20, "Evening Dining & Entertainment": 45},
        "EUR": {"Morning Sightseeing": 22, "Lunch Recommendation": 18, "Afternoon Leisure": 16, "Evening Dining & Entertainment": 40},
        "JPY": {"Morning Sightseeing": 1800, "Lunch Recommendation": 1500, "Afternoon Leisure": 1200, "Evening Dining & Entertainment": 3500},
        "IDR": {"Morning Sightseeing": 150000, "Lunch Recommendation": 120000, "Afternoon Leisure": 100000, "Evening Dining & Entertainment": 250000},
        "THB": {"Morning Sightseeing": 400, "Lunch Recommendation": 250, "Afternoon Leisure": 200, "Evening Dining & Entertainment": 700},
        "AED": {"Morning Sightseeing": 80, "Lunch Recommendation": 70, "Afternoon Leisure": 60, "Evening Dining & Entertainment": 150},
        "ZAR": {"Morning Sightseeing": 250, "Lunch Recommendation": 180, "Afternoon Leisure": 150, "Evening Dining & Entertainment": 350},
        "MAD": {"Morning Sightseeing": 80, "Lunch Recommendation": 90, "Afternoon Leisure": 70, "Evening Dining & Entertainment": 160},
        "SGD": {"Morning Sightseeing": 25, "Lunch Recommendation": 18, "Afternoon Leisure": 16, "Evening Dining & Entertainment": 45},
        "NZD": {"Morning Sightseeing": 40, "Lunch Recommendation": 28, "Afternoon Leisure": 25, "Evening Dining & Entertainment": 55},
    }
    defaults = table.get("USD")
    costs = table.get(currency, defaults)
    factor = budget_multiplier(level)
    return {k: round(v * factor, 2) for k, v in costs.items()}
