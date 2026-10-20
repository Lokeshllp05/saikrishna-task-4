from __future__ import annotations

from typing import Any


PERSONA_ARCHETYPES: tuple[dict[str, Any], ...] = (
    {
        "name": "Alex Morgan",
        "role": "Product Manager",
        "age": 34,
        "experience_years": 9,
        "goal": "Make confident product decisions using clear customer evidence.",
        "pain_point": "Research findings arrive too late to influence sprint planning.",
    },
    {
        "name": "Jordan Lee",
        "role": "Small Business Owner",
        "age": 41,
        "experience_years": 12,
        "goal": "Finish routine work quickly without needing technical training.",
        "pain_point": "Busy screens and confusing setup steps waste limited time.",
    },
    {
        "name": "Sam Patel",
        "role": "UX Researcher",
        "age": 29,
        "experience_years": 6,
        "goal": "Collect reliable feedback and share actionable themes with the team.",
        "pain_point": "Manual analysis and inconsistent exports make synthesis slow.",
    },
    {
        "name": "Taylor Brooks",
        "role": "Operations Analyst",
        "age": 37,
        "experience_years": 11,
        "goal": "Track processes with accurate data and dependable response times.",
        "pain_point": "Slow pages interrupt work and reduce confidence in the results.",
    },
    {
        "name": "Riley Chen",
        "role": "First-time Founder",
        "age": 26,
        "experience_years": 3,
        "goal": "Understand customers and prioritize improvements on a small budget.",
        "pain_point": "It is difficult to tell which feedback should be acted on first.",
    },
)


def generate_personas(count: int, product_name: str = "Product") -> list[dict[str, Any]]:
    """Create repeatable synthetic persona profiles for a local research demo."""
    if not 1 <= count <= 100:
        raise ValueError("Persona count must be between 1 and 100.")
    product_name = product_name.strip()
    if not product_name:
        raise ValueError("Product name cannot be empty.")

    personas: list[dict[str, Any]] = []
    for index in range(count):
        archetype = PERSONA_ARCHETYPES[index % len(PERSONA_ARCHETYPES)]
        cycle = index // len(PERSONA_ARCHETYPES)
        persona = dict(archetype)
        if cycle:
            persona["name"] = f"{archetype['name']} {cycle + 1}"
            persona["age"] += cycle
        persona.update({"id": f"persona-{index + 1:03d}", "product": product_name})
        personas.append(persona)
    return personas
