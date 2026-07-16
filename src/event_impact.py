"""Event impact modeling (Task 3).

Translates impact_link records into time-varying effect functions and builds
the event-indicator association matrix.
"""

import numpy as np
import pandas as pd


def ramp_effect(months_since_event, magnitude, lag_months=0, ramp_months=24):
    """Effect of an event at a point in time, as a gradual adoption ramp.

    The effect is 0 before ``lag_months``, then builds linearly to the full
    ``magnitude`` over ``ramp_months``, and persists afterwards. This models
    adoption dynamics (e.g., a product launch takes time to reach users)
    rather than an instantaneous step.
    """
    active = np.clip((months_since_event - lag_months) / ramp_months, 0.0, 1.0)
    return magnitude * active


def build_association_matrix(impact_links, magnitude_col="impact_magnitude"):
    """Pivot impact links into an event x indicator matrix of signed effects.

    Expects a DataFrame of impact_link rows already joined to parent events
    (see ``data_loader.get_impact_links``), with columns for the event name,
    ``related_indicator``, ``impact_direction`` and ``impact_magnitude``.
    """
    df = impact_links.copy()
    sign = df["impact_direction"].map({"positive": 1, "negative": -1}).fillna(1)
    df["signed_magnitude"] = pd.to_numeric(df[magnitude_col], errors="coerce") * sign

    event_col = next(
        (c for c in ("event_name", "event_title", "parent_id") if c in df.columns),
        "parent_id",
    )
    return df.pivot_table(
        index=event_col,
        columns="related_indicator",
        values="signed_magnitude",
        aggfunc="sum",
    )


def combined_event_effect(dates, events, indicator_code):
    """Total effect of all events on one indicator at each date in ``dates``.

    ``events`` is an iterable of dicts with keys: event_date, indicator_code,
    magnitude, lag_months, ramp_months. Effects are summed additively.
    """
    dates = pd.to_datetime(pd.Index(dates))
    total = np.zeros(len(dates))
    for ev in events:
        if ev["indicator_code"] != indicator_code:
            continue
        months = (dates - pd.to_datetime(ev["event_date"])).days / 30.44
        total += ramp_effect(
            months,
            ev["magnitude"],
            ev.get("lag_months", 0),
            ev.get("ramp_months", 24),
        )
    return pd.Series(total, index=dates)
