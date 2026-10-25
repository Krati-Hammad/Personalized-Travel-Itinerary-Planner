"""Personalized Travel Itinerary Planner — Streamlit entry point."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from src.ai_service import generate_itinerary, generate_recommendations, swap_activity
from src.config import (
    APP_NAME,
    APP_TAGLINE,
    BUDGET_LEVELS,
    INTERESTS,
    PACES,
    TRAVEL_PARTIES,
    VALID_PROVIDERS,
    VIBES,
    load_settings,
)
from src.models import Itinerary, itinerary_from_dict
from src.pdf_export import build_pdf_bytes
from src.storage import TripStore
from src.ui_styles import CUSTOM_CSS
from src.validation import ValidationError, build_preferences


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_state() -> None:
    defaults = {
        "page": "Plan a Trip",
        "itinerary": None,
        "recommendations": [],
        "api_key_override": "",
        "provider_override": "",
        "last_error": "",
        "discover_error": "",
        "swap_request": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def settings_now():
    return load_settings(st.session_state)


def store_now() -> TripStore:
    return TripStore(settings_now())


def show_hero() -> None:
    settings = settings_now()
    badge = (
        '<span class="badge badge-demo">DEMO MODE</span>'
        if settings.demo_mode
        else '<span class="badge badge-ai">AI MODE</span>'
    )
    st.markdown(
        f"""
        <div class="hero">
          <div>{badge}</div>
          <h1 class="hero-title" style="color:white;margin:0.4rem 0 0.2rem 0;">{APP_NAME}</h1>
          <p>{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if settings.demo_mode:
        st.info(
            "No API key is active, so demo/fallback content is shown. "
            "Costs, weather notes, opening hours, and routes are estimates — not live verified data. "
            "Add a Gemini or Groq key in Settings to try model-generated plans."
        )
    else:
        st.caption(
            f"Using {settings.active_provider.title()} for generation. "
            "Prices, weather, hours, and routes are still estimates unless a live data source is connected (this app does not claim they are verified)."
        )


def sidebar_nav() -> str:
    with st.sidebar:
        st.markdown("### Voyage desk")
        page = st.radio(
            "Navigate",
            ["Plan a Trip", "Discover Destinations", "My Itineraries", "Settings"],
            label_visibility="collapsed",
        )
        settings = settings_now()
        st.markdown("---")
        st.markdown("**Status**")
        st.write("Mode:", "Demo fallback" if settings.demo_mode else f"AI · {settings.active_provider}")
        st.write("Storage:", "Supabase" if settings.supabase_configured else "Local SQLite")
        st.caption("SQLite is enough to run. Supabase is optional.")
        if st.session_state.get("itinerary"):
            city = st.session_state.itinerary.destination.city
            st.caption(f"Current plan: {city}")
    return page


def money(itinerary: Itinerary, amount: float) -> str:
    symbol = itinerary.destination.currency_symbol
    code = itinerary.destination.currency
    inr = itinerary.convert(amount, "inr")
    usd = itinerary.convert(amount, "usd")
    return f"{symbol}{amount:,.2f} {code}  ·  ₹{inr:,.2f}  ·  ${usd:,.2f}"


def preference_form(key_prefix: str, require_destination: bool = False):
    today = date.today()
    col1, col2, col3 = st.columns(3)
    with col1:
        destination = st.text_input(
            "Destination city (optional if you pick a vibe)",
            placeholder="Kyoto, Goa, Lisbon…",
            key=f"{key_prefix}_dest",
        )
        vibe = st.selectbox("Travel vibe", ["", *VIBES], key=f"{key_prefix}_vibe")
        duration = st.number_input("Duration (days)", min_value=1, max_value=21, value=4, key=f"{key_prefix}_dur")
    with col2:
        start = st.date_input("Start date", value=today + timedelta(days=14), min_value=today, key=f"{key_prefix}_start")
        budget = st.selectbox("Budget level", BUDGET_LEVELS, index=1, key=f"{key_prefix}_budget")
        party = st.selectbox("Travel party", TRAVEL_PARTIES, index=1, key=f"{key_prefix}_party")
    with col3:
        pace = st.selectbox("Pace", PACES, index=1, key=f"{key_prefix}_pace")
        interests = st.multiselect("Interests", INTERESTS, default=["Food", "History"], key=f"{key_prefix}_interests")
        st.caption("Leave destination blank to get top-3 city matches from your vibe and budget.")
    if require_destination and not (destination or "").strip() and not vibe:
        st.warning("Add a destination or a travel vibe to continue.")
    end = start + timedelta(days=int(duration) - 1)
    st.caption(f"Trip window: **{start.isoformat()}** → **{end.isoformat()}** ({duration} days)")
    return destination, vibe or None, int(duration), start, budget, party, pace, interests


def render_itinerary(itinerary: Itinerary) -> None:
    dest = itinerary.destination
    st.subheader(itinerary.title)
    st.write(f"**{dest.city}, {dest.country}** · {len(itinerary.days)} days")
    st.write(itinerary.summary)
    mode = itinerary.data_quality.mode.upper()
    st.markdown(
        f'<div class="card"><span class="badge badge-{"demo" if mode == "DEMO" else "ai"}">{mode}</span> '
        f'<span class="small-muted">Prices, weather, hours, and routes are not live-verified. {dest.fx_note}</span></div>',
        unsafe_allow_html=True,
    )

    running = 0.0
    metric1, metric2, metric3 = st.columns(3)
    total = itinerary.total_estimated_cost
    metric1.metric("Estimated total (local)", f"{dest.currency_symbol}{total:,.2f} {dest.currency}")
    metric2.metric("Approx. INR", f"₹{itinerary.convert(total, 'inr'):,.0f}")
    metric3.metric("Approx. USD", f"${itinerary.convert(total, 'usd'):,.0f}")

    with st.expander("Assumptions", expanded=False):
        for item in itinerary.assumptions:
            st.write(f"- {item}")

    settings = settings_now()
    for day in itinerary.days:
        with st.expander(f"Day {day.day_number} · {day.date} · {day.theme} · {day.area}", expanded=day.day_number == 1):
            st.caption(day.grouping_rationale)
            for slot in day.slots:
                running += float(slot.estimated_cost or 0)
                left, right = st.columns([3.2, 1.4])
                with left:
                    st.markdown(f"**{slot.time_label}** · {slot.start_time}–{slot.end_time}")
                    st.markdown(f"**{slot.title}**")
                    st.write(slot.description)
                    st.caption(f"{slot.neighborhood} · {slot.grouping_note} · {slot.cost_notes}")
                with right:
                    st.markdown(
                        f'<p class="slot-cost">{money(itinerary, slot.estimated_cost)}</p>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Running total: {money(itinerary, running)}")
                    req_key = f"swap_{day.day_number}_{slot.slot_id}"
                    request = st.text_input(
                        "Swap / tweak this slot",
                        placeholder="e.g. swap the museum for an outdoor market",
                        key=req_key,
                    )
                    b1, b2 = st.columns(2)
                    if b1.button("Update slot", key=f"go_{req_key}"):
                        try:
                            with st.spinner("Updating only this time slot…"):
                                updated = swap_activity(
                                    itinerary,
                                    itinerary_prefs(itinerary),
                                    settings,
                                    day.day_number,
                                    slot.slot_id,
                                    request,
                                )
                            st.session_state.itinerary = updated
                            st.session_state.last_error = ""
                            st.success("Only this slot was regenerated. The rest of the plan is unchanged.")
                            st.rerun()
                        except ValidationError as exc:
                            st.session_state.last_error = str(exc)
                            st.error(str(exc))
                    if b2.button("Demo swap", key=f"dswap_{req_key}"):
                        try:
                            st.session_state.itinerary = swap_activity(
                                itinerary,
                                itinerary_prefs(itinerary),
                                settings,
                                day.day_number,
                                slot.slot_id,
                                request or "refresh this activity",
                                force_demo=True,
                            )
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
            st.markdown("---")
            st.write("Day complete. Cumulative trip spend so far:", money(itinerary, running))

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Save this trip", use_container_width=True):
            saved = store_now().save(itinerary)
            st.success(f"Saved “{saved.title}” ({store_now().backend} storage).")
    with c2:
        try:
            pdf_bytes = build_pdf_bytes(itinerary)
            st.download_button(
                "Export current itinerary PDF",
                data=pdf_bytes,
                file_name=f"{dest.city.lower().replace(' ', '_')}_itinerary.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"PDF export failed: {exc}")
    with c3:
        st.caption("The PDF is built from the itinerary currently on screen, including any slot swaps.")


def itinerary_prefs(itinerary: Itinerary):
    from src.itinerary import preferences_from_itinerary

    return preferences_from_itinerary(itinerary)


def page_plan() -> None:
    st.header("Plan a Trip")
    st.write("Capture preferences, then generate a neighborhood-grouped day-by-day plan.")
    dest, vibe, duration, start, budget, party, pace, interests = preference_form("plan")
    use_demo = st.checkbox("Force demo generator (even if an API key is set)", value=False)
    go = st.button("Generate itinerary", type="primary")
    if go:
        try:
            prefs = build_preferences(dest, vibe, duration, start, budget, party, pace, interests)
            settings = settings_now()
            st.session_state.last_error = ""
            if prefs.needs_destination_pick:
                st.warning("No destination entered — pick a recommended city below.")
                with st.spinner("Finding up to 3 matching cities…"):
                    recs = generate_recommendations(prefs, settings, force_demo=use_demo or settings.demo_mode)
                st.session_state.recommendations = [r.model_dump(mode="json") for r in recs]
                st.session_state.pending_prefs = prefs.model_dump(mode="json")
            else:
                with st.spinner("Building your day-by-day itinerary…"):
                    itinerary = generate_itinerary(prefs, settings, force_demo=use_demo)
                st.session_state.itinerary = itinerary
                st.success("Itinerary ready.")
        except ValidationError as exc:
            st.session_state.last_error = str(exc)
        except Exception as exc:
            st.session_state.last_error = f"Something went wrong: {exc}"

    if st.session_state.get("last_error"):
        st.error(st.session_state.last_error)
        if st.button("Generate demo itinerary instead"):
            try:
                prefs = build_preferences(
                    dest or "Lisbon", vibe or "Cultural", duration, start, budget, party, pace, interests
                )
                st.session_state.itinerary = generate_itinerary(prefs, settings_now(), force_demo=True)
                st.session_state.last_error = ""
                st.rerun()
            except Exception as inner:
                st.error(str(inner))

    recs = st.session_state.get("recommendations") or []
    if recs and not (dest or "").strip():
        st.subheader("Pick a recommended city to generate a full plan")
        cols = st.columns(min(3, len(recs)))
        for idx, rec in enumerate(recs[:3]):
            with cols[idx]:
                st.markdown(f"### {rec['city']}")
                st.caption(f"{rec['country']} · match {rec['match_score']}")
                st.write(" · ".join(rec.get("highlight_tags") or []))
                for reason in rec.get("reasons") or []:
                    st.write(f"- {reason}")
                st.info(rec.get("season_note", "Season note is an estimate."))
                if rec.get("is_estimate", True):
                    st.caption("Demo/estimate recommendation — not live weather or pricing.")
                if st.button(f"Plan {rec['city']}", key=f"planrec_{idx}"):
                    try:
                        prefs = build_preferences(
                            rec["city"], vibe, duration, start, budget, party, pace, interests
                        )
                        with st.spinner(f"Planning {rec['city']}…"):
                            st.session_state.itinerary = generate_itinerary(
                                prefs, settings_now(), city_override=rec["city"], force_demo=use_demo
                            )
                        st.rerun()
                    except ValidationError as exc:
                        st.error(str(exc))

    if st.session_state.get("itinerary"):
        st.markdown("---")
        render_itinerary(st.session_state.itinerary)


def page_discover() -> None:
    st.header("Discover Destinations")
    st.write("When you have a mood rather than a city, get three estimate-labeled matches.")
    dest, vibe, duration, start, budget, party, pace, interests = preference_form("disc")
    use_demo = st.checkbox("Use demo recommendations", value=settings_now().demo_mode)
    if st.button("Recommend 3 cities", type="primary"):
        try:
            prefs = build_preferences(dest, vibe or "Beach", duration, start, budget, party, pace, interests)
            # Discover should recommend even if a destination was typed; ignore destination for ranking mood.
            prefs = prefs.model_copy(update={"destination": ""})
            with st.spinner("Ranking destinations…"):
                recs = generate_recommendations(prefs, settings_now(), force_demo=use_demo)
            st.session_state.discover_recs = [r.model_dump(mode="json") for r in recs]
            st.session_state.discover_error = ""
        except ValidationError as exc:
            st.session_state.discover_error = str(exc)

    if st.session_state.get("discover_error"):
        st.error(st.session_state.discover_error)
    if st.session_state.get("discover_error") and st.button("Show demo recommendations", key="demo_recs"):
        prefs = build_preferences("", vibe or "Cultural", duration, start, budget, party, pace, interests)
        recs = generate_recommendations(prefs, settings_now(), force_demo=True)
        st.session_state.discover_recs = [r.model_dump(mode="json") for r in recs]
        st.session_state.discover_error = ""
        st.rerun()

    recs = st.session_state.get("discover_recs") or []
    if not recs:
        st.markdown(
            '<div class="card">No recommendations yet. Choose a vibe, budget, and dates, then run the matcher.</div>',
            unsafe_allow_html=True,
        )
        return
    cols = st.columns(3)
    for idx, rec in enumerate(recs[:3]):
        with cols[idx]:
            st.markdown(f'<div class="card"><h3>{rec["city"]}, {rec["country"]}</h3>', unsafe_allow_html=True)
            st.metric("Match", f"{rec['match_score']}")
            st.write(" ".join(f"`{tag}`" for tag in rec.get("highlight_tags") or []))
            for reason in rec.get("reasons") or []:
                st.write(f"- {reason}")
            st.warning(rec.get("season_note", "Seasonal fit is an estimate, not live weather."))
            st.caption(f"Budget fit: {rec.get('budget_fit')} · {rec.get('suggested_duration')}")
            if st.button("Build itinerary", key=f"disc_plan_{idx}"):
                try:
                    prefs = build_preferences(rec["city"], vibe, duration, start, budget, party, pace, interests)
                    with st.spinner("Generating plan…"):
                        st.session_state.itinerary = generate_itinerary(
                            prefs, settings_now(), city_override=rec["city"], force_demo=use_demo
                        )
                    st.session_state.page = "Plan a Trip"
                    st.success(f"Itinerary created for {rec['city']}. Open Plan a Trip to review it.")
                except ValidationError as exc:
                    st.error(str(exc))
            st.markdown("</div>", unsafe_allow_html=True)


def page_itineraries() -> None:
    st.header("My Itineraries")
    store = store_now()
    st.caption(f"Storage backend: **{store.backend}**. Local SQLite is the default fallback.")
    trips = store.list_trips()
    if not trips:
        st.markdown(
            '<div class="card">No saved trips yet. Generate a plan and click <b>Save this trip</b>.</div>',
            unsafe_allow_html=True,
        )
        return
    for trip in trips:
        with st.container():
            st.markdown(f"### {trip.title}")
            st.write(f"{trip.destination} · {trip.start_date} → {trip.end_date}")
            st.caption(f"Saved {trip.created_at} · id `{trip.id}`")
            b1, b2, b3 = st.columns(3)
            if b1.button("Open", key=f"open_{trip.id}"):
                st.session_state.itinerary = itinerary_from_dict(trip.payload)
                st.success("Loaded into the planner. Scroll the Plan a Trip page or review below.")
            try:
                loaded = itinerary_from_dict(trip.payload)
                pdf_bytes = build_pdf_bytes(loaded)
                b2.download_button(
                    "Export PDF",
                    data=pdf_bytes,
                    file_name=f"{trip.title.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"dl_{trip.id}",
                )
            except Exception as exc:
                b2.error(f"PDF export failed: {exc}")
            if b3.button("Delete", key=f"del_{trip.id}"):
                store.delete(trip.id)
                st.rerun()
            st.markdown("---")
    if st.session_state.get("itinerary"):
        st.subheader("Currently open itinerary")
        render_itinerary(st.session_state.itinerary)


def page_settings() -> None:
    st.header("Settings / API configuration")
    st.write("Keys stay in Streamlit session, environment variables, or Streamlit secrets — never in source files.")
    settings = settings_now()
    provider = st.selectbox(
        "AI provider",
        VALID_PROVIDERS,
        index=VALID_PROVIDERS.index(settings.active_provider) if settings.active_provider in VALID_PROVIDERS else 0,
    )
    api_key = st.text_input(
        "API key for the selected provider",
        type="password",
        value=st.session_state.get("api_key_override") or "",
        help="Overrides GEMINI_API_KEY / GROQ_API_KEY for this browser session only.",
    )
    if st.button("Save session credentials"):
        st.session_state.provider_override = provider
        st.session_state.api_key_override = api_key.strip()
        st.success("Session credentials stored in memory only.")
        st.rerun()
    if st.button("Clear session key (return to demo if no env/secrets key)"):
        st.session_state.api_key_override = ""
        st.session_state.provider_override = ""
        st.rerun()

    st.markdown("### How secrets are read")
    st.code(
        "GEMINI_API_KEY or GROQ_API_KEY\nAI_PROVIDER=gemini|groq\nSUPABASE_URL (optional)\nSUPABASE_KEY (optional)",
        language="text",
    )
    st.write(
        f"Environment/secrets Gemini key present: **{'yes' if settings.gemini_api_key else 'no'}** · "
        f"Groq key present: **{'yes' if settings.groq_api_key else 'no'}** · "
        f"Supabase configured: **{'yes' if settings.supabase_configured else 'no'}**"
    )
    st.info(
        "Demo mode is automatic when no key is available. The app will still generate itineraries, "
        "recommendations, PDF guides, and local trip history."
    )
    st.markdown("### Optional Supabase")
    st.write(
        "To persist trips across Streamlit Cloud sessions, create a `trips` table and add `SUPABASE_URL` "
        "plus `SUPABASE_KEY` (anon) in secrets. Until then, SQLite/`data/trips.db` is used."
    )
    st.code(
        """create table if not exists trips (
  id text primary key,
  title text,
  destination text,
  start_date text,
  end_date text,
  created_at text,
  payload jsonb
);""",
        language="sql",
    )


def main() -> None:
    init_state()
    show_hero()
    page = sidebar_nav()
    try:
        if page == "Plan a Trip":
            page_plan()
        elif page == "Discover Destinations":
            page_discover()
        elif page == "My Itineraries":
            page_itineraries()
        else:
            page_settings()
    except Exception as exc:
        st.error(f"The app hit an unexpected error: {exc}")
        st.caption("Adjust inputs, retry, or stay in demo mode. Nothing should crash the whole session.")


main()
