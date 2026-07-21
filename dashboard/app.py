"""Streamlit dashboard — Ethiopia Financial Inclusion Forecasting System.

Run with: streamlit run dashboard/app.py

Pages: Overview, Trends, Forecasts, Inclusion Projections. All data prep is
delegated to src/dashboard_data.py, src/event_impact.py, and
src/forecasting.py so the numbers shown here always match the notebooks.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dashboard_data import (
    INDICATOR_LABELS,
    filter_by_date_range,
    growth_rate_table,
    indicator_series,
    latest_value,
    overview_metrics,
    progress_toward_target,
)
from src.data_loader import join_impact_links_with_events
from src.event_impact import build_association_matrix
from src.forecasting import FORECAST_CONFIG, fit_trend, forecast_trend, standard_scenario_forecast

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

# Validated categorical palette (dataviz reference instance) — fixed order, never cycled
C1, C2, C3, C4 = "#2a78d6", "#008300", "#e87ba4", "#eda100"
FORECAST_YEARS = [2025, 2026, 2027]
FORECAST_DATES = ["2025-12-31", "2026-12-31", "2027-12-31"]

NFIS_II_TARGET = 70.0
DASHBOARD_FRONTIER = 60.0


@st.cache_data
def load_data():
    main = pd.read_csv(DATA_DIR / "ethiopia_fi_unified_data_enriched.csv",
                       parse_dates=["observation_date"])
    impact = pd.read_csv(DATA_DIR / "impact_links_enriched.csv",
                         parse_dates=["observation_date"])
    obs = main[main.record_type == "observation"].copy()
    events = main[main.record_type == "event"].copy()
    targets = main[main.record_type == "target"].copy()
    links = join_impact_links_with_events(main, impact)
    return {"main": main, "obs": obs, "events": events, "targets": targets, "links": links}


@st.cache_data
def load_scenarios():
    data = load_data()
    return {
        code: standard_scenario_forecast(code, data["links"], FORECAST_DATES)
        for code in FORECAST_CONFIG
    }


st.set_page_config(
    page_title="Ethiopia Financial Inclusion Forecast",
    page_icon="📊",
    layout="wide",
)

data = load_data()
obs, events, targets, links = data["obs"], data["events"], data["targets"], data["links"]

st.title("Ethiopia Financial Inclusion Forecasting System")
st.caption("Selam Analytics — tracking Ethiopia's digital financial transformation "
           "for the National Bank of Ethiopia, mobile money operators, and DFI partners")

PAGES = ["Overview", "Trends", "Forecasts", "Inclusion Projections"]
page = st.sidebar.radio("Navigate", PAGES)

st.sidebar.divider()
st.sidebar.download_button(
    "Download enriched dataset (CSV)",
    data=data["main"].to_csv(index=False),
    file_name="ethiopia_fi_unified_data_enriched.csv",
    mime="text/csv",
)

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
if page == "Overview":
    st.header("Overview")
    st.write(
        "Key indicators as of the latest available observation, with the change since "
        "the prior data point."
    )

    cards = overview_metrics(obs)
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        delta = f"{card['delta']:+.2f} {card['unit']}" if card["delta"] is not None else None
        col.metric(
            card["label"],
            f"{card['value']:.2f} {card['unit']}",
            delta=delta,
            help=f"As of {card['date'].date()}",
        )

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("P2P / ATM Crossover")
        p2p = indicator_series(obs, "USG_P2P_COUNT").iloc[-1]
        atm = indicator_series(obs, "USG_ATM_COUNT").iloc[-1]
        fig = go.Figure(go.Bar(
            x=["P2P transfers", "ATM withdrawals"],
            y=[p2p.value_numeric / 1e6, atm.value_numeric / 1e6],
            marker_color=[C1, C2],
            text=[f"{p2p.value_numeric/1e6:.0f}M", f"{atm.value_numeric/1e6:.0f}M"],
            textposition="outside",
        ))
        fig.update_layout(
            title="P2P transfers overtook ATM withdrawals in FY2024/25",
            yaxis_title="transactions, millions", showlegend=False, height=380,
        )
        st.plotly_chart(fig, width='stretch')

    with col_b:
        st.subheader("Growth Rate Highlights")
        indicator_choice = st.selectbox(
            "Indicator", ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT", "ACC_MM_ACCOUNT"],
            format_func=lambda c: INDICATOR_LABELS.get(c, c), key="overview_growth_indicator",
        )
        growth = growth_rate_table(obs, indicator_choice)
        fig = go.Figure(go.Bar(
            x=growth["period"], y=growth["pp_per_year"], marker_color=C1,
            text=[f"{v:+.2f}" for v in growth["pp_per_year"]], textposition="outside",
        ))
        fig.update_layout(
            title=f"{INDICATOR_LABELS.get(indicator_choice, indicator_choice)}: pp change per year",
            yaxis_title="pp / year", height=380,
        )
        st.plotly_chart(fig, width='stretch')

# ---------------------------------------------------------------------------
# Trends
# ---------------------------------------------------------------------------
elif page == "Trends":
    st.header("Trends")
    st.write("Explore indicator trajectories over time, with cataloged events overlaid.")

    all_codes = sorted(obs.indicator_code.unique())
    default_codes = ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT", "ACC_MM_ACCOUNT"]
    selected = st.multiselect(
        "Indicators to compare (channel comparison view)", all_codes,
        default=[c for c in default_codes if c in all_codes],
        format_func=lambda c: INDICATOR_LABELS.get(c, c),
    )

    min_date = obs.observation_date.min().date()
    max_date = obs.observation_date.max().date()
    date_range = st.slider(
        "Date range", min_value=min_date, max_value=max_date,
        value=(min_date, max_date),
    )
    show_events = st.checkbox("Overlay cataloged events", value=True)

    if selected:
        fig = go.Figure()
        palette = [C1, C2, C3, C4, "#1baf7a", "#eb6834", "#4a3aa7", "#e34948"]
        for i, code in enumerate(selected):
            series = filter_by_date_range(
                indicator_series(obs, code), date_range[0], date_range[1]
            )
            fig.add_trace(go.Scatter(
                x=series.observation_date, y=series.value_numeric,
                mode="lines+markers", name=INDICATOR_LABELS.get(code, code),
                line=dict(color=palette[i % len(palette)], width=2),
                marker=dict(size=8),
            ))
        if show_events:
            ev = events[
                (events.observation_date.dt.date >= date_range[0])
                & (events.observation_date.dt.date <= date_range[1])
            ]
            for _, r in ev.iterrows():
                fig.add_vline(x=r.observation_date, line_dash="dot",
                             line_color="#52514e", opacity=0.6)
        fig.update_layout(
            title="Indicator trends" + (" with event overlays" if show_events else ""),
            yaxis_title="%", hovermode="x unified", height=520,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, width='stretch')

        if show_events and len(ev):
            with st.expander(f"{len(ev)} cataloged events in this range"):
                st.dataframe(
                    ev[["observation_date", "indicator", "category"]]
                    .rename(columns={"observation_date": "date", "indicator": "event"})
                    .sort_values("date"),
                    hide_index=True, width='stretch',
                )
    else:
        st.info("Select at least one indicator to plot.")

    st.divider()
    st.subheader("Data table")
    table = obs[obs.indicator_code.isin(selected)][
        ["indicator_code", "observation_date", "value_numeric", "unit", "source_name", "confidence"]
    ].sort_values(["indicator_code", "observation_date"])
    st.dataframe(table, hide_index=True, width='stretch')
    st.download_button(
        "Download this data (CSV)", data=table.to_csv(index=False),
        file_name="trends_data.csv", mime="text/csv",
    )

# ---------------------------------------------------------------------------
# Forecasts
# ---------------------------------------------------------------------------
elif page == "Forecasts":
    st.header("Forecasts")
    st.write(
        "2025–2027 projections from the event-augmented model (Task 3's calibrated event "
        "effects, continued forward). A trend-regression baseline is available for comparison "
        "— see why it's not used as the primary forecast in `reports/forecast_results.md`."
    )

    scenarios = load_scenarios()
    target_choice = st.selectbox(
        "Indicator", list(FORECAST_CONFIG),
        format_func=lambda c: INDICATOR_LABELS.get(c, c),
    )
    show_trend = st.checkbox("Show trend-regression baseline (model selection)", value=False)

    s = scenarios[target_choice].copy()
    s["year"] = pd.to_datetime(s["date"]).dt.year
    hist = indicator_series(obs, target_choice)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(s.year) + list(s.year)[::-1],
        y=list(s.optimistic) + list(s.pessimistic)[::-1],
        fill="toself", fillcolor="rgba(42,120,214,0.15)", line=dict(width=0),
        name="scenario range", showlegend=True,
    ))
    fig.add_trace(go.Scatter(x=s.year, y=s.base, mode="lines+markers", name="base",
                             line=dict(color=C1, width=3), marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=s.year, y=s.pessimistic, mode="lines", name="pessimistic",
                             line=dict(color=C1, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=s.year, y=s.optimistic, mode="lines", name="optimistic",
                             line=dict(color=C1, width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(
        x=hist.observation_date.dt.year, y=hist.value_numeric, mode="markers",
        name="observed", marker=dict(color="#0b0b0b", size=10),
    ))

    if show_trend:
        years = hist.observation_date.dt.year.tolist()
        model = fit_trend(years, hist.value_numeric.tolist())
        trend = forecast_trend(model, FORECAST_YEARS)
        fig.add_trace(go.Scatter(
            x=trend.year, y=trend.forecast, mode="lines+markers", name="trend baseline",
            line=dict(color=C4, width=2, dash="dot"),
        ))

    if target_choice == "ACC_OWNERSHIP":
        fig.add_hline(y=NFIS_II_TARGET, line_dash="dot", line_color="#52514e",
                     annotation_text="NFIS-II target (70%)")
        fig.add_hline(y=DASHBOARD_FRONTIER, line_dash="dot", line_color="#52514e",
                     annotation_text="Dashboard frontier (60%)")

    fig.update_layout(
        title=f"{INDICATOR_LABELS.get(target_choice, target_choice)}: 2025–2027 forecast",
        yaxis_title="%", hovermode="x unified", height=520,
    )
    st.plotly_chart(fig, width='stretch')

    st.subheader("Forecast table")
    display_table = s[["year", "pessimistic", "base", "optimistic"]].round(1)
    st.dataframe(display_table, hide_index=True, width='stretch')
    st.download_button(
        "Download forecast table (CSV)", data=display_table.to_csv(index=False),
        file_name=f"{target_choice}_forecast.csv", mime="text/csv",
    )

    st.subheader("Key projected milestones")
    last = display_table.iloc[-1]
    st.markdown(
        f"- By **2027**, base case reaches **{last['base']:.1f}%** "
        f"(range {last['pessimistic']:.1f}–{last['optimistic']:.1f}%).\n"
        f"- See `reports/forecast_results.md` for the full written interpretation, including "
        f"which events drive each scenario and the key uncertainties."
    )

# ---------------------------------------------------------------------------
# Inclusion Projections
# ---------------------------------------------------------------------------
else:
    st.header("Inclusion Projections")
    st.write("Progress toward Ethiopia's financial inclusion targets, and answers to the "
             "consortium's core questions.")

    scenarios = load_scenarios()
    scenario_choice = st.radio(
        "Scenario", ["pessimistic", "base", "optimistic"], index=1, horizontal=True,
    )

    col_a, col_b = st.columns(2)
    for col, code, target in [
        (col_a, "ACC_OWNERSHIP", NFIS_II_TARGET),
        (col_b, "USG_DIGITAL_PAYMENT", None),
    ]:
        s = scenarios[code]
        projected_2027 = s[scenario_choice].iloc[-1]
        with col:
            st.subheader(INDICATOR_LABELS.get(code, code))
            if target:
                progress = progress_toward_target(projected_2027, target)
                st.progress(progress, text=f"{projected_2027:.1f}% of {target:.0f}% NFIS-II target "
                                            f"({progress*100:.0f}%)")
                frontier_progress = progress_toward_target(projected_2027, DASHBOARD_FRONTIER)
                st.progress(frontier_progress,
                           text=f"{frontier_progress*100:.0f}% of the way to a 60% frontier")
            else:
                st.metric("Projected 2027 value", f"{projected_2027:.1f}%")

    st.divider()
    st.subheader("Answers to the consortium's key questions")

    with st.expander("What drives financial inclusion in Ethiopia?", expanded=True):
        st.write(
            "Regulation opens the door (the 2020 PSP directive preceded all mobile money "
            "growth), products convert capability into registration (Telebirr, M-Pesa), "
            "mandated use cases convert registration into usage (the 2022 fuel-payment "
            "mandate), and infrastructure/ID (4G coverage, Fayda) set the ceiling. Usage "
            "responds to events within months; headline account ownership responds slowly "
            "and only through enabling preconditions."
        )

    with st.expander("How do events affect inclusion outcomes?"):
        matrix = build_association_matrix(links)
        st.write(
            "The event–indicator association matrix (Task 3) — signed percentage-point "
            "effects, fallback-filled where only a categorical magnitude was recorded:"
        )
        st.dataframe(matrix.round(1), width='stretch')

    with st.expander("How will inclusion look in 2026 and 2027?"):
        st.write(
            f"**Access** is projected essentially flat (49.0–50.8% by 2027) — its only "
            f"validated driver, Telebirr, fully matured in 2024, and no other cataloged "
            f"event has a direct link to headline ownership. **Usage** keeps growing "
            f"(36.9–40.5% base case by 2027) on the strength of M-Pesa's ongoing ramp and "
            f"EthioPay's Dec-2025 launch. Full reasoning: `reports/forecast_results.md`."
        )

    st.caption(
        "Data sources, enrichment methodology, event-impact calibration, and forecast "
        "assumptions are documented in `reports/data_enrichment_log.md`, "
        "`reports/impact_model_methodology.md`, and `reports/forecast_results.md`."
    )
