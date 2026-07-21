"""Loading helpers for the unified-schema dataset.

All loaders raise ``FileNotFoundError`` with an actionable message when the
expected file is absent, and ``ValueError`` when a file loads but is missing
the columns the rest of the pipeline depends on.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

# Columns every unified-schema frame must expose for downstream code to work
REQUIRED_COLUMNS = {"record_id", "record_type", "pillar", "indicator_code",
                    "value_numeric", "observation_date", "confidence"}

DATE_COLUMNS = ("observation_date", "period_start", "period_end", "collection_date")


def _read_table(path, sheet_name=None):
    """Read a CSV or Excel file into a DataFrame with clear failure modes."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Expected data file not found: {path}. "
            "Place the starter dataset in data/raw/ (see README) or pass an explicit path."
        )
    try:
        if path.suffix.lower() in (".xlsx", ".xls"):
            return pd.read_excel(path, sheet_name=sheet_name or 0)
        return pd.read_csv(path)
    except Exception as exc:  # surface file+reason together for notebook users
        raise ValueError(f"Could not parse {path.name}: {exc}") from exc


def _check_columns(df, path, required=REQUIRED_COLUMNS):
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{Path(path).name} is missing required unified-schema columns: {sorted(missing)}"
        )


def _parse_dates(df):
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def load_unified_data(path=None, sheet_name="ethiopia_fi_unified_data"):
    """Load the unified main sheet (observations, events, targets).

    Defaults to the raw starter workbook; pass ``path`` for the enriched CSV.
    """
    path = Path(path) if path else RAW_DIR / "ethiopia_fi_unified_data.xlsx"
    df = _read_table(path, sheet_name=sheet_name if path.suffix == ".xlsx" else None)
    _check_columns(df, path)
    return _parse_dates(df)


def load_impact_links(path=None, sheet_name="Impact_sheet"):
    """Load the impact-link sheet (event → indicator relationships)."""
    path = Path(path) if path else RAW_DIR / "ethiopia_fi_unified_data.xlsx"
    df = _read_table(path, sheet_name=sheet_name if path.suffix == ".xlsx" else None)
    _check_columns(df, path, required={"record_id", "parent_id", "record_type",
                                       "related_indicator", "impact_direction"})
    return _parse_dates(df)


def load_reference_codes(path=None):
    """Load valid values for categorical fields."""
    path = Path(path) if path else RAW_DIR / "reference_codes.xlsx"
    df = _read_table(path)
    _check_columns(df, path, required={"field", "code"})
    return df


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
    """Return impact_link rows from ``df``, joined to parent events also in ``df``.

    Only useful if impact links and events live in the *same* frame under a
    shared ``record_type`` column. In this project's data, impact links are
    published as a separate sheet/file with no ``record_type``/``parent_id``
    overlap against the main sheet — use ``join_impact_links_with_events``
    for that (real) two-file shape instead.
    """
    if "parent_id" not in df.columns:
        raise ValueError(
            "This DataFrame has no 'parent_id' column, so it cannot contain "
            "impact_link rows joined to events. If you have separate main/"
            "impact DataFrames (the shape used in this project), call "
            "join_impact_links_with_events(main, impact) instead."
        )
    links = df[df["record_type"] == "impact_link"].copy()
    events = df[df["record_type"] == "event"]
    return links.merge(
        events.add_prefix("event_"),
        left_on="parent_id",
        right_on="event_record_id",
        how="left",
    )


def join_impact_links_with_events(main, impact):
    """Join the impact-links sheet to event details from the main sheet.

    This matches the dataset's actual two-file shape: ``main`` holds
    observations/events/targets, ``impact`` holds impact_link rows with a
    ``parent_id`` pointing at an event's ``record_id`` in ``main``. Event
    columns are prefixed with ``event_`` to avoid name collisions (e.g.
    ``event_indicator`` is the event's name, ``event_observation_date`` its date).

    Raises ``ValueError`` if any ``parent_id`` does not resolve to a known event.
    """
    events = main[main["record_type"] == "event"].copy()
    joined = impact.merge(
        events.add_prefix("event_"),
        left_on="parent_id",
        right_on="event_record_id",
        how="left",
    )
    orphans = joined.loc[joined["event_record_id"].isna(), "parent_id"].unique()
    if len(orphans):
        raise ValueError(f"impact links reference unknown events: {sorted(orphans)}")
    return joined
