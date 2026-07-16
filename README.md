# Forecasting Financial Inclusion in Ethiopia

A forecasting system tracking Ethiopia's digital financial transformation, built for
**Selam Analytics** on behalf of a consortium including development finance institutions,
mobile money operators, and the National Bank of Ethiopia.

The system forecasts the two core Global Findex dimensions of financial inclusion for 2025–2027:

1. **Access** — Account Ownership Rate (`ACC_OWNERSHIP`)
2. **Usage** — Digital Payment Adoption Rate (`USG_DIGITAL_PAYMENT`)

## Project Structure

```
ethiopia-fi-forecast/
├── .github/workflows/
│   └── unittests.yml          # CI: run pytest on push/PR
├── data/
│   ├── raw/                   # Starter dataset (unchanged)
│   │   ├── ethiopia_fi_unified_data.csv
│   │   └── reference_codes.csv
│   └── processed/             # Enriched, analysis-ready data
├── notebooks/
│   ├── README.md              # Notebook index
│   ├── 01_data_exploration.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_event_impact_modeling.ipynb
│   └── 04_forecasting.ipynb
├── src/                       # Reusable package (imported by notebooks & dashboard)
│   ├── __init__.py
│   ├── data_loader.py         # Load/validate unified-schema data
│   ├── schema.py              # Unified schema constants & validation
│   ├── event_impact.py        # Event effect functions & association matrix
│   └── forecasting.py         # Trend + event-augmented forecast models
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── tests/                     # Unit tests for src/
├── models/                    # Saved model artifacts
├── reports/
│   ├── figures/               # Exported charts
│   └── data_enrichment_log.md # Task 1 documentation
├── requirements.txt
└── README.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the starter dataset files in `data/raw/`:
- `ethiopia_fi_unified_data.csv`
- `reference_codes.csv`

## Running the Dashboard

```bash
streamlit run dashboard/app.py
```

## Running Tests

```bash
pytest tests/
```

## Data

The starter dataset uses a **unified schema** where `record_type` determines how a row is
interpreted:

| record_type | Description |
|---|---|
| `observation` | Measured values (Findex surveys, operator reports, infrastructure data) |
| `event` | Policies, product launches, market entries, milestones |
| `impact_link` | Modeled relationships between events and indicators (via `parent_id`) |
| `target` | Official policy goals (e.g., NFIS-II targets) |

Events carry a `category` but no `pillar`; their effects on indicators are expressed only
through `impact_link` records to keep the data unbiased.

## Methodology Overview

1. **Task 1 — Data Enrichment:** validate the starter data, add sourced observations,
   events, and impact links; log every addition in `reports/data_enrichment_log.md`.
2. **Task 2 — EDA:** temporal coverage, Access/Usage trajectories, the 2021–2024
   slowdown, event timeline overlays, correlation analysis.
3. **Task 3 — Event Impact Modeling:** translate impact links into time-varying effect
   functions (gradual adoption ramps with lags), build the event–indicator association
   matrix, validate against observed history (e.g., Telebirr's effect on mobile money
   accounts 2021→2024).
4. **Task 4 — Forecasting:** baseline trend regression plus an event-augmented model;
   optimistic/base/pessimistic scenarios with confidence intervals for 2025–2027.
5. **Task 5 — Dashboard:** interactive Streamlit app with Overview, Trends, Forecasts,
   and Inclusion Projections pages.

## Git Workflow

Each task is developed on its own branch (`task-1` … `task-5`) and merged into `main`
via pull request.
