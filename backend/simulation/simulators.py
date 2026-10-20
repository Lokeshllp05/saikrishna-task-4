from __future__ import annotations

from typing import Any


SURVEY_ANSWERS: tuple[tuple[str, int], ...] = (
    ("The simple layout is easy to use and saves me time. I would recommend it.", 5),
    ("The export is useful, but setup is confusing and needs clearer guidance.", 3),
    ("Pages load quickly and the organized dashboard helps me finish work.", 5),
    ("The slow response makes this frustrating, and I cannot find the report.", 2),
    ("I like the clean design, though adding more export options would help.", 4),
)

INTERVIEW_ANSWERS: tuple[tuple[str, int], ...] = (
    ("I can get started quickly. The clear navigation makes the experience pleasant.", 5),
    ("I spend too long searching for exports. A simpler workflow would be helpful.", 3),
    ("Fast responses build my confidence, and the readable summary is useful.", 5),
    ("The confusing setup is frustrating. I need better instructions and support.", 2),
    ("The design feels organized, but I would like more flexible reporting.", 4),
)


def _simulate(personas: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    answers = SURVEY_ANSWERS if mode == "survey" else INTERVIEW_ANSWERS
    responses: list[dict[str, Any]] = []
    for index, persona in enumerate(personas):
        answer, rating = answers[index % len(answers)]
        responses.append(
            {
                "id": f"{mode}-response-{index + 1:03d}",
                "persona_id": persona["id"],
                "persona_name": persona["name"],
                "mode": mode,
                "question": (
                    "How would you rate the product and what would you improve?"
                    if mode == "survey"
                    else "Tell us about your experience and the biggest change you would make."
                ),
                "answer": answer,
                "rating": rating,
            }
        )
    return responses


def simulate_survey(personas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not personas:
        raise ValueError("At least one persona is required to run a survey.")
    return _simulate(personas, "survey")


def simulate_interview(personas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not personas:
        raise ValueError("At least one persona is required to run interviews.")
    return _simulate(personas, "interview")
