from __future__ import annotations

from collections import Counter
from typing import Any


THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Ease of use & navigation": ("simple", "easy", "clear", "confusing", "organized", "navigation"),
    "Speed & reliability": ("quick", "fast", "slow", "response", "reliable"),
    "Reporting & exports": ("export", "report", "reporting", "summary"),
    "Guidance & support": ("setup", "guidance", "instructions", "support"),
    "Visual design": ("layout", "design", "readable", "dashboard"),
}
POSITIVE_WORDS = ("easy", "saves", "quick", "fast", "clear", "useful", "like", "pleasant", "confidence", "recommend")
NEGATIVE_WORDS = ("confusing", "slow", "frustrating", "cannot", "need", "needs", "too long", "waste")


def extract_insights(responses: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize theme mentions, sentiment, highlights, and a validation score."""
    if not responses:
        raise ValueError("At least one response is required to extract insights.")

    theme_counts: Counter[str] = Counter()
    sentiment_counts: Counter[str] = Counter(
        {"positive": 0, "neutral": 0, "negative": 0}
    )
    scored_responses: list[dict[str, Any]] = []
    for response in responses:
        text = str(response["answer"]).casefold()
        for theme, keywords in THEME_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                theme_counts[theme] += 1

        positive = sum(text.count(word) for word in POSITIVE_WORDS)
        negative = sum(text.count(word) for word in NEGATIVE_WORDS)
        sentiment = "positive" if positive > negative else "negative" if negative > positive else "neutral"
        sentiment_counts[sentiment] += 1
        scored_responses.append({**response, "sentiment": sentiment})

    total = len(responses)
    themes = [
        {"theme": theme, "mentions": mentions, "share": round(mentions * 100 / total)}
        for theme, mentions in theme_counts.most_common()
    ]
    sentiment_percentages = {
        sentiment: round(sentiment_counts[sentiment] * 100 / total)
        for sentiment in ("positive", "neutral", "negative")
    }
    average_rating = sum(int(response["rating"]) for response in responses) / total
    validation_score = round(average_rating / 5 * 100)
    top_theme = themes[0]["theme"] if themes else "No recurring theme"
    positive_share = sentiment_percentages["positive"]
    summary = (
        f"Across {total} synthetic responses, {positive_share}% were classified as positive. "
        f"The most frequently mentioned topic was {top_theme}. "
        f"The average product rating was {average_rating:.1f} out of 5."
    )
    highlights = sorted(
        scored_responses,
        key=lambda response: (
            {"positive": 2, "neutral": 1, "negative": 0}[response["sentiment"]],
            int(response["rating"]),
        ),
        reverse=True,
    )
    return {
        "themes": themes,
        "sentiment_counts": dict(sentiment_counts),
        "sentiment_percentages": sentiment_percentages,
        "average_rating": round(average_rating, 2),
        "validation_score": validation_score,
        "summary": summary,
        "highlights": highlights[: min(5, total)],
        "responses": scored_responses,
    }
