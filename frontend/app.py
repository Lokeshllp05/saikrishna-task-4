from __future__ import annotations

import os
import sys
from typing import Any

import pandas as pd
import streamlit as st

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

from backend.agents.insight_extractor import extract_insights
from backend.agents.persona_generator import generate_personas
from backend.reports.pdf_generator import build_pdf
from backend.simulation.simulators import simulate_interview, simulate_survey


def run_research(product_name: str, participant_count: int, mode: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    personas = generate_personas(participant_count, product_name)
    responses: list[dict[str, Any]] = []
    if mode in ("Survey", "Both"):
        responses.extend(simulate_survey(personas))
    if mode in ("Interview", "Both"):
        responses.extend(simulate_interview(personas))
    insights = extract_insights(responses)
    return personas, insights["responses"], insights


st.set_page_config(page_title="Synthetic User Research", page_icon="📊", layout="wide")
st.title("Synthetic User Research Dashboard")
st.caption("Explore repeatable synthetic research results, compare feedback themes, and export a structured report.")

if "research_data" not in st.session_state:
    st.session_state.research_data = run_research("Product", 12, "Both")

with st.sidebar:
    st.header("Run an experiment")
    with st.form("research_controls"):
        product_name = st.text_input("Product or study name", value="Product")
        participant_count = st.slider("Synthetic participants", min_value=5, max_value=50, value=12)
        simulation_mode = st.selectbox("Simulation mode", ("Both", "Survey", "Interview"))
        run_experiment = st.form_submit_button("Run research")

    st.caption(
        "This demo generates deterministic synthetic personas and responses locally. "
        "It does not contact real users or an external AI service."
    )

if run_experiment:
    try:
        st.session_state.research_data = run_research(
            product_name, participant_count, simulation_mode
        )
        st.success("Research run completed.")
    except ValueError as error:
        st.error(str(error))

personas, responses, insights = st.session_state.research_data
report_data = {
    "study_title": personas[0]["product"],
    "personas": personas,
    "responses": responses,
    "insights": insights,
    "validation_score": insights["validation_score"],
}

st.subheader(report_data["study_title"])
metric_columns = st.columns(4)
metric_columns[0].metric("Product validation", f"{insights['validation_score']} / 100")
metric_columns[1].metric("Responses analyzed", len(responses))
metric_columns[2].metric("Synthetic personas", len(personas))
metric_columns[3].metric("Average rating", f"{insights['average_rating']} / 5")
st.progress(insights["validation_score"], text="Overall product validation score")

overview, profiles, response_tab = st.tabs(
    ("Insights overview", "Persona profiles", "Response details")
)

with overview:
    st.markdown("### Research insight summary")
    st.write(insights["summary"])
    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.markdown("#### Theme clusters")
        if insights["themes"]:
            theme_data = pd.DataFrame(insights["themes"])
            st.bar_chart(theme_data, x="theme", y="mentions")
        else:
            st.info("No theme keywords were detected in these responses.")
    with chart_columns[1]:
        st.markdown("#### Sentiment breakdown")
        sentiment_data = pd.DataFrame(
            [
                {"Sentiment": sentiment.title(), "Responses": count, "Share (%)": percentage}
                for sentiment, count in insights["sentiment_counts"].items()
                for percentage in [insights["sentiment_percentages"][sentiment]]
            ]
        )
        st.bar_chart(sentiment_data, x="Sentiment", y="Responses")
        st.dataframe(
            sentiment_data[["Sentiment", "Share (%)"]],
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("### Key persona quotes")
    for highlight in insights["highlights"]:
        st.info(
            f'“{highlight["answer"]}” — {highlight["persona_name"]} '
            f'({highlight["mode"].title()}, {highlight["sentiment"].title()})'
        )

with profiles:
    st.markdown("### Generated persona profiles")
    persona_rows = [
        {
            "Persona": persona["name"],
            "Role": persona["role"],
            "Age": persona["age"],
            "Experience (years)": persona["experience_years"],
            "Goal": persona["goal"],
            "Pain point": persona["pain_point"],
        }
        for persona in personas
    ]
    st.dataframe(pd.DataFrame(persona_rows), hide_index=True, use_container_width=True)

with response_tab:
    st.markdown("### Survey and interview responses")
    response_rows = [
        {
            "Persona": response["persona_name"],
            "Mode": response["mode"].title(),
            "Rating": response["rating"],
            "Sentiment": response["sentiment"].title(),
            "Response": response["answer"],
        }
        for response in responses
    ]
    st.dataframe(pd.DataFrame(response_rows), hide_index=True, use_container_width=True)

report_bytes = build_pdf(report_data)
st.download_button(
    "Download structured research report (PDF)",
    data=report_bytes,
    file_name="synthetic_user_research_report.pdf",
    mime="application/pdf",
    type="primary",
)
