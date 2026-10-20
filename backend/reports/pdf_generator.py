from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def build_pdf(report_data: dict[str, Any]) -> bytes:
    """Build a complete research report and return its PDF bytes."""
    required = {"personas", "responses", "insights", "validation_score"}
    missing = required.difference(report_data)
    if missing:
        raise ValueError(f"Report data is missing required fields: {', '.join(sorted(missing))}")
    if not report_data["personas"]:
        raise ValueError("At least one persona is required to generate a report.")
    if not report_data["responses"]:
        raise ValueError("At least one response is required to generate a report.")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Synthetic User Research Report",
        author="Synthetic User Research Dashboard",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17324d"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallBody",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=12,
        )
    )
    story: list[Any] = [
        Paragraph("Synthetic User Research Report", styles["ReportTitle"]),
        Paragraph(escape(str(report_data.get("study_title", "Product Research Study"))), styles["Heading2"]),
        Spacer(1, 8),
        Paragraph(
            f"<b>Product validation score:</b> {int(report_data['validation_score'])} / 100",
            styles["Heading3"],
        ),
        Paragraph(
            f"<b>Responses analyzed:</b> {len(report_data['responses'])} "
            f"&nbsp;&nbsp; <b>Personas:</b> {len(report_data['personas'])}",
            styles["BodyText"],
        ),
        Spacer(1, 12),
        Paragraph("Insight Summary", styles["Heading2"]),
        Paragraph(
            escape(str(report_data["insights"].get("summary", "No summary available."))),
            styles["BodyText"],
        ),
        Spacer(1, 12),
        Paragraph("Theme Clusters", styles["Heading2"]),
    ]

    theme_rows = [["Theme", "Mentions", "Share"]]
    for theme in report_data["insights"].get("themes", []):
        theme_rows.append(
            [
                Paragraph(escape(str(theme["theme"])), styles["SmallBody"]),
                str(theme["mentions"]),
                f"{theme['share']}%",
            ]
        )
    if len(theme_rows) == 1:
        theme_rows.append(["No themes detected", "0", "0%"])
    theme_table = Table(theme_rows, colWidths=[4.8 * inch, 0.8 * inch, 0.8 * inch], repeatRows=1)
    theme_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7e0e8")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f7fa")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([theme_table, Spacer(1, 12), Paragraph("Sentiment Breakdown", styles["Heading2"])])
    for sentiment, percentage in report_data["insights"].get("sentiment_percentages", {}).items():
        story.append(Paragraph(f"{escape(str(sentiment).title())}: {percentage}%", styles["BodyText"]))

    story.extend([Spacer(1, 12), Paragraph("Persona Profiles", styles["Heading2"])])
    for persona in report_data["personas"]:
        story.append(Paragraph(escape(str(persona["name"])), styles["Heading3"]))
        story.append(
            Paragraph(
                f"<b>Role:</b> {escape(str(persona['role']))} &nbsp;&nbsp; "
                f"<b>Age:</b> {persona['age']} &nbsp;&nbsp; "
                f"<b>Experience:</b> {persona['experience_years']} years",
                styles["SmallBody"],
            )
        )
        story.append(Paragraph(f"<b>Goal:</b> {escape(str(persona['goal']))}", styles["SmallBody"]))
        story.append(Paragraph(f"<b>Pain point:</b> {escape(str(persona['pain_point']))}", styles["SmallBody"]))
        story.append(Spacer(1, 7))

    story.extend([PageBreak(), Paragraph("Response Highlights", styles["Heading2"])])
    for response in report_data["responses"]:
        quote = escape(str(response["answer"]))
        story.append(
            Paragraph(
                f"<b>{escape(str(response['persona_name']))}</b> "
                f"({escape(str(response['mode']).title())}, "
                f"{escape(str(response['sentiment']).title())}, "
                f"rating {response['rating']}/5):",
                styles["SmallBody"],
            )
        )
        story.append(Paragraph(f"<i>“{quote}”</i>", styles["BodyText"]))
        story.append(Spacer(1, 9))

    doc.build(story)
    return buffer.getvalue()


def generate_pdf(
    filename: str | Path = "research_report.pdf",
    report_data: dict[str, Any] | None = None,
) -> str:
    """Write a report PDF to disk and return its path."""
    if report_data is None:
        raise ValueError("report_data must be provided; reports are generated from actual study results.")
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(build_pdf(report_data))
    return str(output_path)
