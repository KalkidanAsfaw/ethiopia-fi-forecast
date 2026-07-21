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

from src.event_impact import combined_event_effect, events_for_indicator


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


# Single source of truth for the two headline forecasts, reproducing
# notebooks/04_forecasting.ipynb exactly so the dashboard never shows
# different numbers than the documented report (reports/forecast_results.md).
FORECAST_CONFIG = {
    "ACC_OWNERSHIP": {
        "last_date": "2024-11-29", "last_value": 49.0,
        "calibration": 0.25, "background_pp_per_year": 0.0,
        # ACC_OWNERSHIP's only validated (direct/indirect) driver, Telebirr,
        # was already fully matured by 2024 -> pessimistic == base (flat).
        # Optimistic instead asks "what if the *enabling* links Task 3
        # excluded (Fayda, NFIS-II) finally convert to account-opening?",
        # at a steeper, explicitly-discounted calibration.
        "strategy": "enabling_upside",
        "optimistic_enabling_calibration": 0.15,
    },
    "USG_DIGITAL_PAYMENT": {
        "last_date": "2024-11-29", "last_value": 35.0,
        "calibration": 0.80, "background_pp_per_year": 0.403,
        "strategy": "symmetric",
    },
}


def standard_scenario_forecast(indicator_code, links, forecast_dates,
                                optimistic_multiplier=1.4, pessimistic_multiplier=0.4,
                                config=None):
    """The project's one definition of the Access/Usage scenario forecasts.

    Shared by ``notebooks/04_forecasting.ipynb`` and ``dashboard/app.py`` so
    the two surfaces present identical numbers. ``links`` must be event-
    joined impact links (``data_loader.join_impact_links_with_events``).

    Two scenario strategies, per ``FORECAST_CONFIG``:

    - ``"symmetric"``: pessimistic/base/optimistic scale the same validated
      events' calibration and background rate together (faster/slower
      realization of the same story).
    - ``"enabling_upside"``: pessimistic and base trust only validated
      (direct/indirect) events; optimistic additionally includes `enabling`
      links at a steep, separately-specified discount, since those were
      excluded from Task 3's validation and represent a distinct upside
      story ("preconditions finally pay off"), not just a faster version of
      the base case.
    """
    cfg = (config or FORECAST_CONFIG)[indicator_code]
    validated_events = events_for_indicator(links, indicator_code)
    background = max(cfg["background_pp_per_year"], 0.0)

    if cfg["strategy"] == "enabling_upside":
        pessimistic = event_augmented_forecast(
            cfg["last_value"], cfg["last_date"], forecast_dates, validated_events,
            indicator_code, calibration=cfg["calibration"], background_pp_per_year=0.0,
        )
        base = event_augmented_forecast(
            cfg["last_value"], cfg["last_date"], forecast_dates, validated_events,
            indicator_code, calibration=cfg["calibration"], background_pp_per_year=background,
        )
        all_events = events_for_indicator(links, indicator_code, relationship_types=None)
        validated_ids = {e["record_id"] for e in validated_events}
        optimistic_events = [
            {**e, "magnitude": e["magnitude"] * (
                cfg["calibration"] if e["record_id"] in validated_ids
                else cfg["optimistic_enabling_calibration"]
            )}
            for e in all_events
        ]
        optimistic = event_augmented_forecast(
            cfg["last_value"], cfg["last_date"], forecast_dates, optimistic_events,
            indicator_code, calibration=1.0, background_pp_per_year=0.0,
        )
        out = pd.DataFrame({
            "date": pessimistic["date"],
            "pessimistic": pessimistic["forecast"],
            "base": base["forecast"],
            "optimistic": optimistic["forecast"],
        })
    else:
        out = scenario_forecasts(
            cfg["last_value"], cfg["last_date"], forecast_dates, validated_events, indicator_code,
            base_calibration=cfg["calibration"], base_background_pp_per_year=background,
            optimistic_multiplier=optimistic_multiplier, pessimistic_multiplier=pessimistic_multiplier,
        ).reset_index().rename(columns={"index": "date"})

    return out.reset_index(drop=True)


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
