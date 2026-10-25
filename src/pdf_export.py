"""One-click PDF travel guide generation with ReportLab."""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.models import Itinerary

TEAL = colors.HexColor("#0F6C73")
SAND = colors.HexColor("#F4EFE6")
INK = colors.HexColor("#1F2A2E")
MUTED = colors.HexColor("#5C6B70")


TRAVEL_CHECKLIST = [
    "Passport / ID validity and any required visas",
    "Travel insurance details and policy number",
    "Flights, trains, and lodging confirmations (offline copies)",
    "Local SIM / eSIM or roaming plan",
    "Medications, prescriptions, and a small first-aid kit",
    "Power adapter and portable charger",
    "Copies of tickets and this itinerary stored offline",
    "Weather-appropriate clothing and walking shoes",
    "Payment cards notified for travel plus some local cash",
    "Reconfirm opening hours and reservations before each day",
]

EMERGENCY_CHECKLIST = [
    "Local emergency number for the destination country",
    "Nearest embassy or consulate contact",
    "Hotel / lodging 24-hour desk number",
    "Travel companion phone numbers",
    "Bank / card lost-and-stolen numbers",
    "Travel insurance 24/7 assistance line",
    "Doctor or clinic recommended by lodging",
    "Backup copies of passport stored separately",
]


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleX",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=22,
            textColor=TEAL,
            spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "h": ParagraphStyle(
            "H",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=14,
            textColor=TEAL,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyX",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10,
            textColor=INK,
            leading=14,
        ),
        "muted": ParagraphStyle(
            "Muted",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=9,
            textColor=MUTED,
            leading=12,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=9,
            textColor=INK,
            leading=12,
        ),
    }


def _bullets(items: Iterable[str], style) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=8) for item in items],
        bulletType="bullet",
        leftIndent=12,
    )


def build_pdf_bytes(itinerary: Itinerary) -> bytes:
    """Build a PDF from the in-memory itinerary currently on screen."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=itinerary.title,
        author="Personalized Travel Itinerary Planner",
    )
    styles = _styles()
    story = []
    dest = itinerary.destination
    symbol = dest.currency_symbol
    story.append(Paragraph("Personalized Travel Itinerary Planner", styles["muted"]))
    story.append(Paragraph(itinerary.title, styles["title"]))
    story.append(
        Paragraph(
            f"{dest.city}, {dest.country} · {itinerary.days[0].date if itinerary.days else ''} – "
            f"{itinerary.days[-1].date if itinerary.days else ''}",
            styles["body"],
        )
    )
    story.append(Paragraph(itinerary.summary, styles["body"]))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Data quality: prices, weather, opening hours, and routes in this guide are estimates. "
            f"Mode: {itinerary.data_quality.mode}. {dest.fx_note}",
            styles["muted"],
        )
    )

    total = itinerary.total_estimated_cost
    story.append(Paragraph("Budget snapshot", styles["h"]))
    budget_rows = [
        ["Local total (estimate)", f"{symbol}{total:,.2f} {dest.currency}"],
        ["Approx. INR", f"₹{itinerary.convert(total, 'inr'):,.2f}"],
        ["Approx. USD", f"${itinerary.convert(total, 'usd'):,.2f}"],
    ]
    table = Table(budget_rows, colWidths=[90 * mm, 80 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SAND),
                ("TEXTCOLOR", (0, 0), (-1, -1), INK),
                ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)

    story.append(Paragraph("Assumptions", styles["h"]))
    story.append(_bullets(itinerary.assumptions, styles["small"]))

    running = 0.0
    for day in itinerary.days:
        story.append(Paragraph(f"Day {day.day_number} · {day.date} · {day.theme}", styles["h"]))
        story.append(Paragraph(f"Area focus: {day.area}. {day.grouping_rationale}", styles["muted"]))
        rows = [["Time", "Plan", "Est. cost", "Cumulative"]]
        for slot in day.slots:
            running += float(slot.estimated_cost or 0)
            plan = (
                f"<b>{slot.time_label}: {slot.title}</b><br/>"
                f"{slot.start_time}–{slot.end_time} · {slot.neighborhood}<br/>"
                f"{slot.description}<br/><i>{slot.cost_notes}</i>"
            )
            rows.append(
                [
                    Paragraph(f"{slot.start_time}<br/>{slot.end_time}", styles["small"]),
                    Paragraph(plan, styles["small"]),
                    Paragraph(f"{symbol}{slot.estimated_cost:,.2f}", styles["small"]),
                    Paragraph(f"{symbol}{running:,.2f}", styles["small"]),
                ]
            )
        day_table = Table(rows, colWidths=[22 * mm, 100 * mm, 24 * mm, 24 * mm])
        day_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D5D0C6")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ]
            )
        )
        story.append(day_table)

    story.append(Paragraph("Practical travel checklist", styles["h"]))
    story.append(_bullets(TRAVEL_CHECKLIST, styles["small"]))
    story.append(Paragraph("Emergency-contact checklist", styles["h"]))
    story.append(
        Paragraph(
            "Fill in real numbers before you travel. This list is a reminder, not a live directory.",
            styles["muted"],
        )
    )
    story.append(_bullets(EMERGENCY_CHECKLIST, styles["small"]))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "Generated by Personalized Travel Itinerary Planner. Verify details independently before you go.",
            styles["muted"],
        )
    )
    doc.build(story)
    return buffer.getvalue()
