"""Forecasting models for Access and Usage (Task 4).

Given only 5 Findex points over 13 years, models are deliberately simple:
trend regression with prediction intervals, optionally augmented with
event effects from ``event_impact``.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm


def fit_trend(years, values, log=False):
    """Fit an OLS trend (linear, or log-linear when ``log=True``) to sparse points."""
    y = np.log(np.asarray(values, dtype=float)) if log else np.asarray(values, dtype=float)
    X = sm.add_constant(np.asarray(years, dtype=float))
    return sm.OLS(y, X).fit()


def forecast_trend(model, forecast_years, log=False, alpha=0.05):
    """Forecast with prediction intervals.

    Returns a DataFrame with columns: year, forecast, lower, upper.
    """
    X_new = sm.add_constant(np.asarray(forecast_years, dtype=float), has_constant="add")
    pred = model.get_prediction(X_new)
    frame = pred.summary_frame(alpha=alpha)

    out = pd.DataFrame(
        {
            "year": forecast_years,
            "forecast": frame["mean"],
            "lower": frame["obs_ci_lower"],
            "upper": frame["obs_ci_upper"],
        }
    ).reset_index(drop=True)
    if log:
        out[["forecast", "lower", "upper"]] = np.exp(out[["forecast", "lower", "upper"]])
    return out


def apply_scenario(baseline, event_effects, multiplier=1.0, cap=100.0):
    """Combine a baseline forecast with event effects under a scenario.

    ``multiplier`` scales event effects (e.g., 1.25 optimistic, 0.5
    pessimistic). Rates are capped at ``cap`` (percentages cannot exceed 100).
    """
    out = baseline.copy()
    effects = np.asarray(event_effects, dtype=float) * multiplier
    for col in ("forecast", "lower", "upper"):
        out[col] = np.clip(out[col] + effects, 0.0, cap)
    return out
