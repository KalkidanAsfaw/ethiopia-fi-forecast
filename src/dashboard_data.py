"""Pure data-prep helpers for the Streamlit dashboard (Task 5).

Kept separate from ``dashboard/app.py`` so the logic is unit-testable without
a Streamlit runtime. ``app.py`` should only import from here and call
``st.*`` for layout/rendering.
"""

import pandas as pd

INDICATOR_LABELS = {
    "ACC_OWNERSHIP": "Account Ownership",
    "ACC_MM_ACCOUNT": "Mobile Money Accounts",
    "ACC_4G_COV": "4G Population Coverage",
    "ACC_MOBILE_PEN": "Mobile Subscription Penetration",
    "ACC_FAYDA": "Fayda Digital ID Enrollment",
    "USG_DIGITAL_PAYMENT": "Digital Payment Usage",
    "USG_P2P_COUNT": "P2P Transaction Count",
    "USG_ATM_COUNT": "ATM Transaction Count",
    "USG_TELEBIRR_USERS": "Telebirr Registered Users",
    "USG_MPESA_USERS": "M-Pesa Registered Users",
    "GEN_GAP_ACC": "Account Ownership Gender Gap",
}

TARGET_INDICATORS = ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT"]


def latest_value(obs, indicator_code, gender="all"):
    """Most recent observation for an indicator, or None if there isn't one."""
    d = obs[(obs.indicator_code == indicator_code) & (obs.gender == gender)]
    d = d.sort_values("observation_date")
    if d.empty:
        return None
    row = d.iloc[-1]
    return {"value": row.value_numeric, "date": row.observation_date, "unit": row.unit}


def previous_value(obs, indicator_code, gender="all"):
    """Second-most-recent observation, for computing a period-over-period delta."""
    d = obs[(obs.indicator_code == indicator_code) & (obs.gender == gender)]
    d = d.sort_values("observation_date")
    if len(d) < 2:
        return None
    row = d.iloc[-2]
    return {"value": row.value_numeric, "date": row.observation_date}


def overview_metrics(obs):
    """Key metric cards for the Overview page: latest value + period-over-period delta."""
    cards = []
    for code in ["ACC_OWNERSHIP", "ACC_MM_ACCOUNT", "USG_DIGITAL_PAYMENT", "USG_CROSSOVER"]:
        latest = latest_value(obs, code)
        if latest is None:
            continue
        prev = previous_value(obs, code)
        delta = (latest["value"] - prev["value"]) if prev else None
        cards.append({
            "indicator_code": code,
            "label": INDICATOR_LABELS.get(code, code),
            "value": latest["value"],
            "unit": latest["unit"],
            "date": latest["date"],
            "delta": delta,
        })
    return cards


def growth_rate_table(obs, indicator_code, gender="all"):
    """pp-per-year growth rate between each consecutive pair of observations."""
    d = obs[(obs.indicator_code == indicator_code) & (obs.gender == gender)].sort_values(
        "observation_date"
    )
    if len(d) < 2:
        return pd.DataFrame(columns=["period", "pp_per_year"])
    years = d.observation_date.dt.year.to_numpy()
    values = d.value_numeric.to_numpy()
    rates = (values[1:] - values[:-1]) / (years[1:] - years[:-1])
    periods = [f"{years[i]}–{years[i+1]}" for i in range(len(years) - 1)]
    return pd.DataFrame({"period": periods, "pp_per_year": rates})


def indicator_series(obs, indicator_code, gender="all"):
    """Tidy time series for one indicator, sorted by date."""
    d = obs[(obs.indicator_code == indicator_code) & (obs.gender == gender)]
    return d.sort_values("observation_date")[["observation_date", "value_numeric"]].reset_index(
        drop=True
    )


def filter_by_date_range(series, start_date, end_date):
    """Restrict a date-indexed observation series to [start_date, end_date]."""
    start_date, end_date = pd.Timestamp(start_date), pd.Timestamp(end_date)
    return series[
        (series.observation_date >= start_date) & (series.observation_date <= end_date)
    ]


def progress_toward_target(current_value, target_value):
    """Fraction of the way from 0 to a target a current value represents, clipped to [0, 1]."""
    if target_value == 0:
        return 0.0
    return max(0.0, min(1.0, current_value / target_value))
