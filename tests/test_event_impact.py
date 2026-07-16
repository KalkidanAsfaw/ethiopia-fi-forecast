import numpy as np
import pandas as pd

from src.event_impact import build_association_matrix, ramp_effect


def test_ramp_effect_zero_before_lag():
    assert ramp_effect(months_since_event=2, magnitude=5.0, lag_months=6) == 0.0


def test_ramp_effect_full_after_ramp():
    effect = ramp_effect(months_since_event=40, magnitude=5.0, lag_months=6, ramp_months=24)
    assert effect == 5.0


def test_ramp_effect_partial_during_ramp():
    effect = ramp_effect(months_since_event=18, magnitude=10.0, lag_months=6, ramp_months=24)
    assert 0.0 < effect < 10.0
    assert np.isclose(effect, 5.0)


def test_association_matrix_signs_and_shape():
    links = pd.DataFrame(
        {
            "parent_id": ["EVT001", "EVT001", "EVT002"],
            "related_indicator": ["ACC_MM_ACCOUNT", "USG_DIGITAL_PAYMENT", "ACC_MM_ACCOUNT"],
            "impact_direction": ["positive", "positive", "negative"],
            "impact_magnitude": [3.0, 2.0, 1.0],
        }
    )
    matrix = build_association_matrix(links)
    assert matrix.loc["EVT001", "ACC_MM_ACCOUNT"] == 3.0
    assert matrix.loc["EVT002", "ACC_MM_ACCOUNT"] == -1.0
    assert matrix.shape == (2, 2)
