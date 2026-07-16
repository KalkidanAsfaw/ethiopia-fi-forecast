import numpy as np
import pandas as pd

from src.forecasting import apply_scenario, fit_trend, forecast_trend

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
