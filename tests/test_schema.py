import pandas as pd

from src.schema import RECORD_TYPES, validate_records


def test_record_types_defined():
    assert set(RECORD_TYPES) == {"observation", "event", "impact_link", "target"}


def test_validate_flags_unknown_record_type():
    df = pd.DataFrame({"record_type": ["observation", "bogus"], "pillar": [None, None]})
    problems = validate_records(df)
    assert any("bogus" in p for p in problems)


def test_validate_flags_event_with_pillar():
    df = pd.DataFrame(
        {"record_type": ["event"], "pillar": ["access"], "record_id": ["EVT001"]}
    )
    problems = validate_records(df)
    assert any("pillar" in p for p in problems)


def test_validate_clean_data_passes():
    df = pd.DataFrame(
        {
            "record_type": ["observation", "event"],
            "pillar": ["access", None],
            "record_id": ["OBS001", "EVT001"],
        }
    )
    assert validate_records(df) == []
