import pandas as pd
import pytest

from src.data_loader import load_reference_codes, load_unified_data
from src.enrichment import NEW_EVENTS, NEW_IMPACT_LINKS, NEW_OBSERVATIONS, build_enriched
from src.schema import validate_records


def test_loader_raises_on_missing_file():
    with pytest.raises(FileNotFoundError, match="data/raw"):
        load_unified_data("data/raw/does_not_exist.csv")


def test_loader_raises_on_wrong_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"foo": [1]}).to_csv(bad, index=False)
    with pytest.raises(ValueError, match="missing required"):
        load_unified_data(bad)


def test_reference_codes_load():
    ref = load_reference_codes()
    assert {"field", "code"} <= set(ref.columns)
    assert len(ref) > 50


def test_addition_ids_are_unique():
    ids = [r["record_id"] for r in NEW_OBSERVATIONS + NEW_EVENTS + NEW_IMPACT_LINKS]
    assert len(ids) == len(set(ids))


def test_new_events_have_no_pillar():
    assert all("pillar" not in e or not e.get("pillar") for e in NEW_EVENTS)
    assert all(e["category"] for e in NEW_EVENTS)


def test_enriched_dataset_is_schema_valid():
    main, impact = build_enriched(write=False)
    assert validate_records(main) == []
    assert main["record_id"].is_unique
    assert impact["record_id"].is_unique

    event_ids = set(main.loc[main.record_type == "event", "record_id"])
    assert set(impact["parent_id"]) <= event_ids


def test_usage_target_now_has_observations():
    main, _ = build_enriched(write=False)
    usage = main[
        (main.record_type == "observation")
        & (main.indicator_code == "USG_DIGITAL_PAYMENT")
    ]
    assert len(usage) >= 3
    assert pd.to_numeric(usage.value_numeric).between(0, 100).all()
