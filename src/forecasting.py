"""Forecasting models for Access and Usage (Task 4).

Given only 5 Findex points over 13 years (3 for Usage), a pure trend
regression is unstable — see notebooks/04_forecasting.ipynb §2. The primary
forecast is therefore event-augmented: the last observed value plus (a) the
Task 3 calibrated event effects still unfolding, plus (b) a small residual
"background" trend for growth the cataloged events don't explain, estimated
directly from the same validation window Task 3 used.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.event_impact import combined_event_effect


def fit_trend(years, values, log=False):
    """Fit an OLS trend (linear, or log-linear when ``log=True``) to sparse points."""
    y = np.log(np.asarray(values, dtype=float)) if log else np.asarray(values, dtype=float)
    X = sm.add_constant(np.asarray(years, dtype=float))
    return sm.OLS(y, X).fit()


def forecast_trend(model, forecast_years, log=False, alpha=0.05):
    """Forecast with prediction intervals.

    Returns a DataFrame with columns: year, forecast, lower, upper. With very
    few data points (this project's series have 3-5), degrees of freedom are
    small (or zero for a 2-point series), so intervals can be extremely wide
    or undefined (NaN) — that is reported honestly rather than hidden.
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


def residual_background_rate(events, indicator_code, obs_start_date, obs_end_date,
                              observed_start, observed_end, calibration=1.0):
    """The pp/year growth NOT explained by cataloged, calibrated event effects.

    Computes the calibrated event model's predicted change between two
    observed dates, subtracts it from the actually observed change, and
    annualizes the residual. This is the same validation logic Task 3 used
    (``src/event_impact.py::validate_against_observed``), repurposed to
    estimate an "organic" background trend: growth from factors outside the
    12 cataloged events (smaller policies, general economic development)
    that should reasonably continue into the forecast horizon.
    """
    eff_start, eff_end = combined_event_effect(
        [obs_start_date, obs_end_date], events, indicator_code, calibration=calibration
    )
    predicted_delta = eff_end - eff_start
    observed_delta = observed_end - observed_start
    residual = observed_delta - predicted_delta
    years_elapsed = (pd.Timestamp(obs_end_date) - pd.Timestamp(obs_start_date)).days / 365.25
    return residual / years_elapsed


def event_augmented_forecast(last_value, last_date, forecast_dates, events, indicator_code,
                              calibration=1.0, background_pp_per_year=0.0, cap=100.0):
    """Project forward from the last observed value.

    forecast(t) = last_value
                  + [cumulative calibrated event effect at t, relative to last_date]
                  + background_pp_per_year * (years since last_date)

    Events dated after ``t`` automatically contribute 0 (see
    ``event_impact.ramp_effect``), so this naturally captures events still
    ramping up (e.g., a 2025 launch still building through 2027) alongside
    ones already fully matured by ``last_date``.
    """
    dates = pd.to_datetime(pd.Index(forecast_dates))
    last_date = pd.Timestamp(last_date)

    all_dates = pd.Index([last_date]).append(dates)
    cum_effect = combined_event_effect(all_dates, events, indicator_code, calibration=calibration)
    delta_from_events = cum_effect.iloc[1:].to_numpy() - cum_effect.iloc[0]

    years_elapsed = (dates - last_date).days / 365.25
    delta_from_background = background_pp_per_year * years_elapsed

    forecast = np.clip(last_value + delta_from_events + delta_from_background, 0.0, cap)
    return pd.DataFrame({"date": dates, "forecast": forecast}).reset_index(drop=True)


def scenario_forecasts(last_value, last_date, forecast_dates, events, indicator_code,
                        base_calibration, base_background_pp_per_year,
                        optimistic_multiplier=1.3, pessimistic_multiplier=0.5, cap=100.0):
    """Base/optimistic/pessimistic event-augmented forecasts from one set of scenario multipliers.

    The multiplier scales both the event calibration and the background
    trend together, so "optimistic" means faster realization of the same
    cataloged events *and* faster organic growth (e.g., smoother rollout,
    fewer macro shocks) — not a different, unrelated set of assumptions per
    scenario.
    """
    scenarios = {}
    for name, mult in [("pessimistic", pessimistic_multiplier),
                       ("base", 1.0),
                       ("optimistic", optimistic_multiplier)]:
        df = event_augmented_forecast(
            last_value, last_date, forecast_dates, events, indicator_code,
            calibration=base_calibration * mult,
            background_pp_per_year=base_background_pp_per_year * mult,
            cap=cap,
        )
        scenarios[name] = df.set_index("date")["forecast"]
    return pd.DataFrame(scenarios)


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
