import numpy as np
import pandas as pd

from src.event_impact import (
    build_association_matrix,
    combined_event_effect,
    events_for_indicator,
    ramp_effect,
    validate_against_observed,
)


def test_ramp_effect_zero_before_lag():
    assert ramp_effect(months_since_event=2, magnitude=5.0, lag_months=6) == 0.0


def test_ramp_effect_zero_for_future_event():
    # negative months_since_event = event hasn't happened yet at this date
    assert ramp_effect(months_since_event=-5, magnitude=5.0, lag_months=0) == 0.0


def test_ramp_effect_full_after_ramp():
    effect = ramp_effect(months_since_event=40, magnitude=5.0, lag_months=6, ramp_months=24)
    assert effect == 5.0


def test_ramp_effect_partial_during_ramp():
    effect = ramp_effect(months_since_event=18, magnitude=10.0, lag_months=6, ramp_months=24)
    assert 0.0 < effect < 10.0
    assert np.isclose(effect, 5.0)


def _sample_links():
    return pd.DataFrame({
        "parent_id": ["EVT001", "EVT001", "EVT002"],
        "related_indicator": ["ACC_MM_ACCOUNT", "USG_DIGITAL_PAYMENT", "ACC_MM_ACCOUNT"],
        "impact_direction": ["increase", "increase", "decrease"],
        "impact_magnitude": ["medium", "medium", "low"],
        "impact_estimate": [4.5, 12.0, np.nan],
    })


def test_association_matrix_uses_numeric_estimate_and_sign():
    matrix = build_association_matrix(_sample_links())
    assert matrix.loc["EVT001", "ACC_MM_ACCOUNT"] == 4.5
    assert matrix.loc["EVT001", "USG_DIGITAL_PAYMENT"] == 12.0
    assert matrix.shape == (2, 2)


def test_association_matrix_falls_back_to_magnitude_band():
    # EVT002 has no numeric impact_estimate; "low" + decrease -> -3.0 pp fallback
    matrix = build_association_matrix(_sample_links(), use_fallback=True)
    assert matrix.loc["EVT002", "ACC_MM_ACCOUNT"] == -3.0


def test_association_matrix_without_fallback_is_nan():
    matrix = build_association_matrix(_sample_links(), use_fallback=False)
    assert pd.isna(matrix.loc["EVT002", "ACC_MM_ACCOUNT"])


def test_combined_event_effect_excludes_future_events():
    events = [{"indicator_code": "ACC_MM_ACCOUNT", "event_date": "2025-01-01",
               "magnitude": 10.0, "lag_months": 0, "ramp_months": 12}]
    result = combined_event_effect(["2024-01-01"], events, "ACC_MM_ACCOUNT")
    assert result.iloc[0] == 0.0


def test_combined_event_effect_sums_multiple_events():
    events = [
        {"indicator_code": "ACC_MM_ACCOUNT", "event_date": "2020-01-01",
         "magnitude": 4.0, "lag_months": 0, "ramp_months": 12},
        {"indicator_code": "ACC_MM_ACCOUNT", "event_date": "2020-01-01",
         "magnitude": 6.0, "lag_months": 0, "ramp_months": 12},
    ]
    result = combined_event_effect(["2022-01-01"], events, "ACC_MM_ACCOUNT")
    assert np.isclose(result.iloc[0], 10.0)


def test_events_for_indicator_skips_missing_estimate_and_date():
    links = pd.DataFrame({
        "related_indicator": ["ACC_MM_ACCOUNT", "ACC_MM_ACCOUNT"],
        "impact_direction": ["increase", "increase"],
        "impact_magnitude": ["medium", "medium"],
        "impact_estimate": [5.0, np.nan],
        "relationship_type": ["direct", "direct"],
        "lag_months": [12, 12],
        "event_observation_date": pd.to_datetime(["2021-05-17", None]),
        "record_id": ["IMP_A", "IMP_B"],
    })
    events = events_for_indicator(links, "ACC_MM_ACCOUNT")
    assert len(events) == 1
    assert events[0]["magnitude"] == 5.0


def test_events_for_indicator_excludes_enabling_links_by_default():
    links = pd.DataFrame({
        "related_indicator": ["ACC_MM_ACCOUNT", "ACC_MM_ACCOUNT"],
        "impact_direction": ["increase", "increase"],
        "impact_magnitude": ["medium", "high"],
        "impact_estimate": [5.0, 20.0],
        "relationship_type": ["direct", "enabling"],
        "lag_months": [12, 12],
        "event_observation_date": pd.to_datetime(["2021-05-17", "2020-04-01"]),
        "record_id": ["IMP_A", "IMP_B"],
    })
    events = events_for_indicator(links, "ACC_MM_ACCOUNT")
    assert len(events) == 1
    assert events[0]["record_id"] == "IMP_A"

    events_all = events_for_indicator(links, "ACC_MM_ACCOUNT", relationship_types=None)
    assert len(events_all) == 2


def test_validate_against_observed_computes_calibration_factor():
    result = validate_against_observed(predicted_delta=15.0, observed_delta=3.0, label="test")
    assert result["residual_pp"] == -12.0
    assert np.isclose(result["calibration_factor"], 0.2)
