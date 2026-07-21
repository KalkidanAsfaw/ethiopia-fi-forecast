import pandas as pd
import pytest

from src.data_loader import get_impact_links, join_impact_links_with_events


def _sample_main():
    return pd.DataFrame({
        "record_id": ["EVT_A", "REC_A"],
        "record_type": ["event", "observation"],
        "observation_date": pd.to_datetime(["2021-01-01", "2021-06-01"]),
        "indicator": ["Some Event", "Some Indicator"],
        "category": ["policy", None],
    })


def _sample_impact():
    return pd.DataFrame({
        "record_id": ["IMP_A", "IMP_B"],
        "parent_id": ["EVT_A", "EVT_A"],
        "related_indicator": ["ACC_OWNERSHIP", "USG_DIGITAL_PAYMENT"],
    })


def test_join_impact_links_with_events_attaches_event_columns():
    joined = join_impact_links_with_events(_sample_main(), _sample_impact())
    assert "event_observation_date" in joined.columns
    assert (joined["event_indicator"] == "Some Event").all()
    assert len(joined) == 2


def test_join_impact_links_with_events_raises_on_orphan_parent_id():
    bad_impact = _sample_impact().copy()
    bad_impact.loc[0, "parent_id"] = "EVT_MISSING"
    with pytest.raises(ValueError, match="unknown events"):
        join_impact_links_with_events(_sample_main(), bad_impact)


def test_get_impact_links_raises_without_parent_id_column():
    df = pd.DataFrame({"record_type": ["event"], "record_id": ["EVT_A"]})
    with pytest.raises(ValueError, match="parent_id"):
        get_impact_links(df)
