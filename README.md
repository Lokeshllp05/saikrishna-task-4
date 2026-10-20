# Synthetic User Research Dashboard

A local demo for generating synthetic user personas, running survey and interview simulations, exploring research insights, and downloading a structured PDF report.

> All participants and responses are synthetic examples generated locally. They do not represent real users or validated customer research.

## Features

- **Insights dashboard:** theme mention counts, sentiment breakdown, representative persona quotes, average rating, and a product validation score.
- **Research report:** downloadable PDF with persona profiles, response highlights, insight summary, theme clusters, sentiment, and validation score.
- **Research simulations:** generate profiles and run a survey, an interview, or both for a chosen study and participant count.
- **End-to-end tests:** verifies persona generation, both simulation modes, insight calculations, PDF output, and invalid-input handling.

## Requirements

- Python 3.10 or later
- pip

## Run on Windows

From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m streamlit run frontend/app.py
```

Alternatively, run `python ..\setup_and_run.py` from this directory's parent project folder. It installs the declared dependencies, runs the tests, and opens the dashboard in a browser.

## How the score works

The validation score is the mean response rating (1–5) converted to a 0–100 scale. Sentiment and theme clusters are transparent keyword-based summaries of the synthetic response text; they are intended for demonstrating the workflow, not for making real product decisions.
