"""Unified schema constants and validation helpers.

The starter dataset uses a unified schema where every row shares the same
columns and `record_type` determines interpretation.
"""

RECORD_TYPES = ["observation", "event", "impact_link", "target"]

PILLARS = ["access", "usage"]

CONFIDENCE_LEVELS = ["high", "medium", "low"]

# Core Findex indicators the system forecasts
KEY_INDICATORS = {
    "ACC_OWNERSHIP": "Account ownership rate (% adults 15+)",
    "ACC_MM_ACCOUNT": "Mobile money account ownership (% adults)",
    "USG_DIGITAL_PAYMENT": "Made or received digital payment (% adults)",
}


def validate_records(df):
    """Return a list of schema problems found in a unified-schema DataFrame.

    Checks record_type validity, that events have no pillar assigned, and
    that impact_links reference a parent event.
    """
    problems = []

    bad_types = set(df["record_type"].dropna()) - set(RECORD_TYPES)
    if bad_types:
        problems.append(f"Unknown record_type values: {sorted(bad_types)}")

    if "pillar" in df.columns:
        events_with_pillar = df[
            (df["record_type"] == "event") & df["pillar"].notna()
        ]
        if len(events_with_pillar):
            problems.append(
                f"{len(events_with_pillar)} event rows have a pillar assigned "
                "(events must stay pillar-neutral; use impact_links instead)"
            )

    if "parent_id" in df.columns:
        links = df[df["record_type"] == "impact_link"]
        event_ids = set(df.loc[df["record_type"] == "event", "record_id"].dropna()) \
            if "record_id" in df.columns else set()
        orphans = links[~links["parent_id"].isin(event_ids)]
        if len(orphans) and event_ids:
            problems.append(
                f"{len(orphans)} impact_link rows reference a parent_id "
                "that is not a cataloged event"
            )

    return problems
