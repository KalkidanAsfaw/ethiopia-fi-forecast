import pandas as pd

from src.dashboard_data import (
    filter_by_date_range,
    growth_rate_table,
    indicator_series,
    latest_value,
    overview_metrics,
    previous_value,
    progress_toward_target,
)


def _sample_obs():
    return pd.DataFrame({
        "indicator_code": ["ACC_OWNERSHIP", "ACC_OWNERSHIP", "ACC_OWNERSHIP", "USG_CROSSOVER"],
        "gender": ["all", "all", "all", "all"],
        "observation_date": pd.to_datetime(["2017-12-31", "2021-12-31", "2024-11-29", "2025-07-07"]),
        "value_numeric": [35.0, 46.0, 49.0, 1.08],
        "unit": ["%", "%", "%", "ratio"],
    })


def test_latest_value_returns_most_recent():
    result = latest_value(_sample_obs(), "ACC_OWNERSHIP")
    assert result["value"] == 49.0


def test_latest_value_none_when_missing():
    assert latest_value(_sample_obs(), "NOT_A_CODE") is None


def test_previous_value_returns_second_to_last():
    result = previous_value(_sample_obs(), "ACC_OWNERSHIP")
    assert result["value"] == 46.0


def test_previous_value_none_with_single_point():
    assert previous_value(_sample_obs(), "USG_CROSSOVER") is None


def test_overview_metrics_includes_delta():
    cards = overview_metrics(_sample_obs())
    acc = next(c for c in cards if c["indicator_code"] == "ACC_OWNERSHIP")
    assert acc["value"] == 49.0
    assert acc["delta"] == 3.0


def test_growth_rate_table_computes_pp_per_year():
    table = growth_rate_table(_sample_obs(), "ACC_OWNERSHIP")
    assert list(table["period"]) == ["2017–2021", "2021–2024"]
    assert table["pp_per_year"].iloc[0] == (46.0 - 35.0) / (2021 - 2017)


def test_indicator_series_sorted_and_tidy():
    series = indicator_series(_sample_obs(), "ACC_OWNERSHIP")
    assert list(series.columns) == ["observation_date", "value_numeric"]
    assert series.value_numeric.is_monotonic_increasing


def test_filter_by_date_range():
    series = indicator_series(_sample_obs(), "ACC_OWNERSHIP")
    filtered = filter_by_date_range(series, "2020-01-01", "2024-12-31")
    assert len(filtered) == 2


def test_progress_toward_target_clips_to_one():
    assert progress_toward_target(49.0, 60.0) < 1.0
    assert progress_toward_target(70.0, 60.0) == 1.0
    assert progress_toward_target(0.0, 60.0) == 0.0
