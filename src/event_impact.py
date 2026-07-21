"""Event impact modeling (Task 3).

Translates impact_link records into time-varying effect functions and builds
the event-indicator association matrix.

Schema note: ``impact_direction`` takes values ``increase`` / ``decrease`` /
``stabilize`` / ``mixed`` (see ``data/raw/reference_codes.xlsx``); the
percentage-point estimate lives in ``impact_estimate`` (numeric, may be
missing), while ``impact_magnitude`` is a *categorical* severity label
(``high`` / ``medium`` / ``low`` / ``negligible``) used as a fallback when no
numeric estimate was recorded.
"""

import numpy as np
import pandas as pd

DIRECTION_SIGN = {"increase": 1, "decrease": -1, "stabilize": 0, "mixed": np.nan}

# Midpoint pp fallback per reference_codes.xlsx band definitions, used only
# when impact_estimate is missing (e.g. links measured in raw user counts).
MAGNITUDE_FALLBACK_PP = {"high": 20.0, "medium": 10.0, "low": 3.0, "negligible": 0.5}


def ramp_effect(months_since_event, magnitude, lag_months=0, ramp_months=24):
    """Effect of an event at a point in time, as a gradual adoption ramp.

    The effect is 0 before ``lag_months``, then builds linearly to the full
    ``magnitude`` over ``ramp_months``, and persists afterwards. This models
    adoption dynamics (e.g., a product launch takes time to reach users)
    rather than an instantaneous step. Dates before the event itself
    (``months_since_event`` negative) also resolve to 0, so callers do not
    need to filter out not-yet-happened events.
    """
    active = np.clip((months_since_event - lag_months) / ramp_months, 0.0, 1.0)
    return magnitude * active


def _signed_estimate(links, use_fallback=True):
    """Signed pp effect per link: impact_estimate if present, else a
    magnitude-band fallback, always oriented by impact_direction."""
    sign = links["impact_direction"].map(DIRECTION_SIGN)
    estimate = pd.to_numeric(links.get("impact_estimate"), errors="coerce")
    if use_fallback:
        fallback = links["impact_magnitude"].map(MAGNITUDE_FALLBACK_PP)
        estimate = estimate.fillna(fallback)
    return estimate * sign


def build_association_matrix(impact_links, use_fallback=True):
    """Pivot impact links into an event x indicator matrix of signed pp effects.

    Expects impact_link rows with ``related_indicator``, ``impact_direction``,
    ``impact_estimate`` (numeric pp, may be missing) and ``impact_magnitude``
    (categorical severity, used as a fallback when ``use_fallback=True``).
    Rows are indexed by event name if present (``event_name``/``event_title``
    from a join against events), else by ``parent_id``.
    """
    df = impact_links.copy()
    df["signed_pp"] = _signed_estimate(df, use_fallback=use_fallback)

    event_col = next(
        (c for c in ("event_name", "event_title", "parent_id") if c in df.columns),
        "parent_id",
    )
    return df.pivot_table(
        index=event_col,
        columns="related_indicator",
        values="signed_pp",
        # min_count=1 so a cell with only NaN inputs stays NaN instead of
        # collapsing to 0 (pandas' default sum-of-empty behavior); dropna=False
        # keeps all-NaN rows/columns (e.g. an event whose only link has no
        # numeric estimate and use_fallback=False) instead of silently dropping them
        aggfunc=lambda s: s.sum(min_count=1),
        dropna=False,
    )


def combined_event_effect(dates, events, indicator_code, calibration=1.0):
    """Total effect of all events on one indicator at each date in ``dates``.

    ``events`` is an iterable of dicts with keys: event_date, indicator_code,
    magnitude (signed pp), lag_months, ramp_months. Effects are summed
    additively (the working assumption documented in Task 3 methodology).
    ``calibration`` uniformly scales all effects, for validating/adjusting
    against observed history without editing every event dict.
    Events whose date is after a given evaluation date contribute 0 at that
    date automatically (ramp_effect clips negative elapsed time to 0).
    """
    dates = pd.to_datetime(pd.Index(dates))
    total = np.zeros(len(dates))
    for ev in events:
        if ev["indicator_code"] != indicator_code:
            continue
        months = (dates - pd.to_datetime(ev["event_date"])).days / 30.44
        total += ramp_effect(
            months,
            ev["magnitude"] * calibration,
            ev.get("lag_months", 0),
            ev.get("ramp_months", 24),
        )
    return pd.Series(total, index=dates)


def events_for_indicator(links_with_events, indicator_code, ramp_months=24,
                          relationship_types=("direct", "indirect")):
    """Build the ``events`` list ``combined_event_effect`` expects, for one indicator.

    ``links_with_events`` must already be joined to event dates (see
    ``data_loader.join_impact_links_with_events``, which prefixes event
    columns with ``event_``).

    ``relationship_types`` restricts which link types are summed additively.
    Defaults to ``direct`` and ``indirect`` only, excluding ``enabling``
    links: an enabling link (e.g. a regulation that makes a product
    possible) is a *precondition* for other events' effects, not an
    independent pp contribution — including it alongside the events it
    enables double-counts the same adoption. Pass ``None`` to include all
    relationship types.
    """
    df = links_with_events[links_with_events["related_indicator"] == indicator_code].copy()
    if relationship_types is not None:
        df = df[df["relationship_type"].isin(relationship_types)]
    df["signed_pp"] = _signed_estimate(df, use_fallback=True)
    date_col = "event_observation_date" if "event_observation_date" in df.columns else "event_date"

    out = []
    for _, r in df.iterrows():
        if pd.isna(r["signed_pp"]) or pd.isna(r[date_col]):
            continue
        out.append({
            "indicator_code": indicator_code,
            "event_date": r[date_col],
            "magnitude": float(r["signed_pp"]),
            "lag_months": float(r.get("lag_months", 0) or 0),
            "ramp_months": ramp_months,
            "record_id": r.get("record_id"),
        })
    return out


def validate_against_observed(predicted_delta, observed_delta, label=""):
    """Compare a model's predicted change to the actually observed change.

    Returns a dict with the predicted/observed deltas, the residual, and a
    calibration factor (observed / predicted) that would make the model fit
    exactly — useful for the Task 3 refinement step.
    """
    residual = observed_delta - predicted_delta
    calibration_factor = (observed_delta / predicted_delta) if predicted_delta else np.nan
    return {
        "label": label,
        "predicted_delta_pp": predicted_delta,
        "observed_delta_pp": observed_delta,
        "residual_pp": residual,
        "calibration_factor": calibration_factor,
    }
