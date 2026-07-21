import numpy as np
import pandas as pd

from src.forecasting import (
    FORECAST_CONFIG,
    apply_scenario,
    event_augmented_forecast,
    fit_trend,
    forecast_trend,
    residual_background_rate,
    scenario_forecasts,
    standard_scenario_forecast,
)

FINDEX_YEARS = [2011, 2014, 2017, 2021, 2024]
FINDEX_OWNERSHIP = [14, 22, 35, 46, 49]


def test_trend_forecast_is_increasing_and_bounded():
    model = fit_trend(FINDEX_YEARS, FINDEX_OWNERSHIP)
    result = forecast_trend(model, [2025, 2026, 2027])
    assert list(result["year"]) == [2025, 2026, 2027]
    assert result["forecast"].is_monotonic_increasing
    assert (result["lower"] <= result["forecast"]).all()
    assert (result["forecast"] <= result["upper"]).all()


def test_log_trend_returns_positive_values():
    model = fit_trend(FINDEX_YEARS, FINDEX_OWNERSHIP, log=True)
    result = forecast_trend(model, [2025, 2026, 2027], log=True)
    assert (result["forecast"] > 0).all()


def test_apply_scenario_caps_at_100():
    baseline = pd.DataFrame(
        {"year": [2026], "forecast": [95.0], "lower": [90.0], "upper": [99.0]}
    )
    result = apply_scenario(baseline, event_effects=np.array([10.0]))
    assert result.loc[0, "forecast"] == 100.0
    assert result.loc[0, "upper"] == 100.0


def _sample_events():
    return [{
        "indicator_code": "ACC_MM_ACCOUNT", "event_date": "2021-05-17",
        "magnitude": 4.5, "lag_months": 12, "ramp_months": 24,
    }]


def test_residual_background_rate_zero_when_model_matches_observed():
    # predicted delta at calibration=1.0 over 2021-05-17 -> 2024-05-17 (36mo since
    # event, i.e. fully ramped: magnitude 4.5 in full) equals the observed delta
    rate = residual_background_rate(
        _sample_events(), "ACC_MM_ACCOUNT",
        obs_start_date="2021-05-17", obs_end_date="2024-05-17",
        observed_start=4.7, observed_end=4.7 + 4.5, calibration=1.0,
    )
    assert np.isclose(rate, 0.0, atol=1e-6)


def test_event_augmented_forecast_matches_last_value_with_no_events_or_background():
    result = event_augmented_forecast(
        last_value=49.0, last_date="2024-11-29",
        forecast_dates=["2025-12-31", "2026-12-31"],
        events=[], indicator_code="ACC_OWNERSHIP",
    )
    assert np.allclose(result["forecast"], 49.0)


def test_event_augmented_forecast_applies_background_trend():
    result = event_augmented_forecast(
        last_value=49.0, last_date="2024-01-01",
        forecast_dates=["2025-01-01", "2026-01-01"],
        events=[], indicator_code="ACC_OWNERSHIP", background_pp_per_year=1.0,
    )
    assert np.isclose(result["forecast"].iloc[0], 50.0, atol=0.1)
    assert np.isclose(result["forecast"].iloc[1], 51.0, atol=0.1)


def test_event_augmented_forecast_respects_cap():
    result = event_augmented_forecast(
        last_value=98.0, last_date="2024-01-01",
        forecast_dates=["2027-01-01"],
        events=[], indicator_code="ACC_OWNERSHIP", background_pp_per_year=10.0,
    )
    assert result["forecast"].iloc[0] == 100.0


def test_scenario_forecasts_orders_pessimistic_base_optimistic():
    events = _sample_events()
    df = scenario_forecasts(
        last_value=4.7, last_date="2021-05-17", forecast_dates=["2025-01-01"],
        events=events, indicator_code="ACC_MM_ACCOUNT",
        base_calibration=1.0, base_background_pp_per_year=1.0,
        optimistic_multiplier=1.3, pessimistic_multiplier=0.5,
    )
    row = df.iloc[0]
    assert row["pessimistic"] <= row["base"] <= row["optimistic"]


def _sample_links_for_standard_forecast():
    return pd.DataFrame({
        "record_id": ["IMP_A", "IMP_B"],
        "parent_id": ["EVT_A", "EVT_B"],
        "related_indicator": ["ACC_OWNERSHIP", "ACC_OWNERSHIP"],
        "relationship_type": ["direct", "enabling"],
        "impact_direction": ["increase", "increase"],
        "impact_magnitude": ["high", "medium"],
        "impact_estimate": [15.0, 10.0],
        "lag_months": [12, 24],
        "event_record_id": ["EVT_A", "EVT_B"],
        "event_observation_date": pd.to_datetime(["2021-05-17", "2024-01-01"]),
    })


def test_standard_scenario_forecast_enabling_upside_matches_notebook_shape():
    links = _sample_links_for_standard_forecast()
    config = {
        "ACC_OWNERSHIP": {
            "last_date": "2024-11-29", "last_value": 49.0,
            "calibration": 0.25, "background_pp_per_year": -0.26,
            "strategy": "enabling_upside", "optimistic_enabling_calibration": 0.15,
        },
    }
    df = standard_scenario_forecast(
        "ACC_OWNERSHIP", links, ["2025-12-31", "2026-12-31", "2027-12-31"], config=config
    )
    # only the validated direct link (already matured) drives pessimistic/base -> flat
    assert (df["pessimistic"] == df["pessimistic"].iloc[0]).all()
    assert (df["base"] == df["pessimistic"]).all()
    # the enabling link only benefits the optimistic case
    assert (df["optimistic"] >= df["base"]).all()
    assert df["optimistic"].iloc[-1] > df["optimistic"].iloc[0]


def test_standard_scenario_forecast_symmetric_orders_scenarios():
    links = _sample_links_for_standard_forecast()
    config = {
        "ACC_OWNERSHIP": {
            "last_date": "2024-11-29", "last_value": 49.0,
            "calibration": 0.5, "background_pp_per_year": 0.5,
            "strategy": "symmetric",
        },
    }
    df = standard_scenario_forecast(
        "ACC_OWNERSHIP", links, ["2026-12-31"], config=config
    )
    row = df.iloc[0]
    assert row["pessimistic"] <= row["base"] <= row["optimistic"]


def test_forecast_config_has_both_targets():
    assert set(FORECAST_CONFIG) == {"ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT"}
