from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_PATH))

from backend.agents.insight_extractor import extract_insights
from backend.agents.persona_generator import generate_personas
from backend.reports.pdf_generator import build_pdf, generate_pdf
from backend.simulation.simulators import simulate_interview, simulate_survey


def test_persona_generation_returns_complete_distinct_profiles() -> None:
    personas = generate_personas(7, "Research Portal")

    assert len(personas) == 7
    assert len({persona["id"] for persona in personas}) == 7
    assert all(
        persona["name"]
        and persona["role"]
        and persona["goal"]
        and persona["pain_point"]
        and persona["product"] == "Research Portal"
        for persona in personas
    )


@pytest.mark.parametrize(
    ("simulator", "mode"),
    ((simulate_survey, "survey"), (simulate_interview, "interview")),
)
def test_simulation_modes_produce_rated_persona_responses(
    simulator: Any, mode: str
) -> None:
    personas = generate_personas(6)
    responses = simulator(personas)

    assert len(responses) == len(personas)
    assert all(response["mode"] == mode for response in responses)
    assert {response["persona_id"] for response in responses} == {
        persona["id"] for persona in personas
    }
    assert all(response["question"] and response["answer"] for response in responses)
    assert all(1 <= response["rating"] <= 5 for response in responses)


def test_insight_extraction_derives_themes_sentiment_and_score() -> None:
    personas = generate_personas(5)
    responses = simulate_survey(personas)

    insights = extract_insights(responses)

    assert sum(insights["sentiment_counts"].values()) == len(responses)
    assert set(insights["sentiment_counts"]) == {"positive", "neutral", "negative"}
    assert sum(insights["sentiment_percentages"].values()) in range(99, 102)
    assert insights["themes"]
    assert insights["validation_score"] == round(
        sum(response["rating"] for response in responses) / len(responses) / 5 * 100
    )
    assert len(insights["highlights"]) <= 5
    assert all("sentiment" in response for response in insights["responses"])


def test_report_generation_contains_full_study_and_writes_pdf(tmp_path: Path) -> None:
    personas = generate_personas(8, "Research Portal")
    responses = simulate_survey(personas) + simulate_interview(personas)
    insights = extract_insights(responses)
    assert {response["mode"] for response in insights["responses"]} == {
        "survey",
        "interview",
    }
    report_data = {
        "study_title": "Research Portal",
        "personas": personas,
        "responses": insights["responses"],
        "insights": insights,
        "validation_score": insights["validation_score"],
    }

    pdf_bytes = build_pdf(report_data)
    output_path = tmp_path / "research_report.pdf"
    returned_path = generate_pdf(output_path, report_data)

    assert pdf_bytes.startswith(b"%PDF")
    assert output_path.read_bytes().startswith(b"%PDF")
    assert Path(returned_path) == output_path
    assert output_path.stat().st_size > 1000


@pytest.mark.parametrize(
    "factory",
    (
        lambda: generate_personas(0),
        lambda: generate_personas(1, " "),
        lambda: simulate_survey([]),
        lambda: simulate_interview([]),
        lambda: extract_insights([]),
        lambda: build_pdf({}),
    ),
)
def test_invalid_research_inputs_fail_explicitly(factory: Any) -> None:
    with pytest.raises(ValueError):
        factory()
