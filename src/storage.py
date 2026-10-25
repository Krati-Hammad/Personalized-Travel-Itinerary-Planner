"""Trip persistence: SQLite by default, optional Supabase."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from src.config import DATA_DIR, SQLITE_PATH, AppSettings
from src.models import Itinerary, SavedTrip


CREATE_SQL = """
CREATE TABLE IF NOT EXISTS trips (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(CREATE_SQL)
    conn.commit()
    return conn


def _row_to_trip(row: sqlite3.Row) -> SavedTrip:
    payload = json.loads(row["payload"])
    return SavedTrip(
        id=row["id"],
        title=row["title"],
        destination=row["destination"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        created_at=row["created_at"],
        payload=payload,
    )


class TripStore:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.backend = "sqlite"
        self._supabase = None
        if settings.supabase_configured:
            try:
                from supabase import create_client

                self._supabase = create_client(settings.supabase_url, settings.supabase_key)
                self.backend = "supabase"
            except Exception:
                self.backend = "sqlite"

    def save(self, itinerary: Itinerary) -> SavedTrip:
        trip_id = itinerary.itinerary_id or str(uuid4())
        itinerary.itinerary_id = trip_id
        created = datetime.now(timezone.utc).isoformat()
        start = itinerary.days[0].date if itinerary.days else ""
        end = itinerary.days[-1].date if itinerary.days else ""
        payload = itinerary.model_dump(mode="json")
        record = SavedTrip(
            id=trip_id,
            title=itinerary.title,
            destination=f"{itinerary.destination.city}, {itinerary.destination.country}",
            start_date=start,
            end_date=end,
            created_at=created,
            payload=payload,
        )
        if self.backend == "supabase" and self._supabase is not None:
            try:
                self._supabase.table("trips").upsert(
                    {
                        "id": record.id,
                        "title": record.title,
                        "destination": record.destination,
                        "start_date": record.start_date,
                        "end_date": record.end_date,
                        "created_at": record.created_at,
                        "payload": record.payload,
                    }
                ).execute()
                return record
            except Exception:
                self.backend = "sqlite"
        conn = _connect()
        conn.execute(
            """
            INSERT OR REPLACE INTO trips (id, title, destination, start_date, end_date, created_at, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.title,
                record.destination,
                record.start_date,
                record.end_date,
                record.created_at,
                json.dumps(record.payload),
            ),
        )
        conn.commit()
        conn.close()
        return record

    def list_trips(self) -> list[SavedTrip]:
        if self.backend == "supabase" and self._supabase is not None:
            try:
                res = self._supabase.table("trips").select("*").order("created_at", desc=True).execute()
                trips = []
                for item in res.data or []:
                    payload = item.get("payload") or {}
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    trips.append(
                        SavedTrip(
                            id=item["id"],
                            title=item["title"],
                            destination=item["destination"],
                            start_date=item["start_date"],
                            end_date=item["end_date"],
                            created_at=item["created_at"],
                            payload=payload,
                        )
                    )
                return trips
            except Exception:
                self.backend = "sqlite"
        conn = _connect()
        rows = conn.execute("SELECT * FROM trips ORDER BY created_at DESC").fetchall()
        conn.close()
        return [_row_to_trip(row) for row in rows]

    def get(self, trip_id: str) -> Optional[SavedTrip]:
        for trip in self.list_trips():
            if trip.id == trip_id:
                return trip
        return None

    def delete(self, trip_id: str) -> None:
        if self.backend == "supabase" and self._supabase is not None:
            try:
                self._supabase.table("trips").delete().eq("id", trip_id).execute()
                return
            except Exception:
                self.backend = "sqlite"
        conn = _connect()
        conn.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
        conn.commit()
        conn.close()
