"""Loading helpers for the unified-schema dataset."""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def load_unified_data(path=None):
    """Load the unified dataset (observations, events, targets, impact links)."""
    path = Path(path) if path else RAW_DIR / "ethiopia_fi_unified_data.csv"
    df = pd.read_csv(path)
    for col in ("observation_date", "event_date", "collection_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def load_reference_codes(path=None):
    """Load valid values for categorical fields."""
    path = Path(path) if path else RAW_DIR / "reference_codes.csv"
    return pd.read_csv(path)


def split_by_record_type(df):
    """Split a unified DataFrame into a dict keyed by record_type."""
    return {rt: g.copy() for rt, g in df.groupby("record_type")}


def get_observations(df, indicator_code=None):
    """Return observation rows, optionally filtered to one indicator."""
    obs = df[df["record_type"] == "observation"].copy()
    if indicator_code is not None:
        obs = obs[obs["indicator_code"] == indicator_code]
    return obs.sort_values("observation_date")


def get_events(df):
    """Return event rows sorted by date."""
    events = df[df["record_type"] == "event"].copy()
    date_col = "event_date" if "event_date" in events.columns else "observation_date"
    return events.sort_values(date_col)


def get_impact_links(df):
    """Return impact_link rows joined with their parent event details."""
    links = df[df["record_type"] == "impact_link"].copy()
    events = df[df["record_type"] == "event"]
    if "record_id" in events.columns and "parent_id" in links.columns:
        links = links.merge(
            events.add_prefix("event_"),
            left_on="parent_id",
            right_on="event_record_id",
            how="left",
        )
    return links
