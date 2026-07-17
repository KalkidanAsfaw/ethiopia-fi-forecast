"""Task 1 — Dataset enrichment.

Defines all records added to the starter dataset (observations, events,
impact links), each with source, original text, and confidence, and builds
the enriched analysis-ready files in ``data/processed/``.

Run as a script to regenerate the processed files:

    python -m src.enrichment
"""

from pathlib import Path

import pandas as pd

RAW_XLSX = Path(__file__).resolve().parents[1] / "data" / "raw" / "ethiopia_fi_unified_data.xlsx"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

COLLECTED_BY = "KalkidanAsfaw"
COLLECTION_DATE = "2026-07-17"


def _obs(record_id, pillar, indicator, code, value, unit, value_type, date,
         source_name, source_type, source_url, confidence, original_text, notes,
         gender="all", location="national"):
    return {
        "record_id": record_id, "record_type": "observation", "pillar": pillar,
        "indicator": indicator, "indicator_code": code,
        "indicator_direction": "higher_better", "value_numeric": value,
        "value_type": value_type, "unit": unit, "observation_date": date,
        "fiscal_year": str(pd.Timestamp(date).year), "gender": gender,
        "location": location, "source_name": source_name,
        "source_type": source_type, "source_url": source_url,
        "confidence": confidence, "collected_by": COLLECTED_BY,
        "collection_date": COLLECTION_DATE, "original_text": original_text,
        "notes": notes,
    }


# --------------------------------------------------------------------------
# New observations
# --------------------------------------------------------------------------
NEW_OBSERVATIONS = [
    _obs("REC_0034", "ACCESS", "Account Ownership Rate", "ACC_OWNERSHIP", 14.0, "%",
         "percentage", "2011-12-31", "Global Findex 2011", "survey",
         "https://www.worldbank.org/en/publication/globalfindex", "high",
         "Ethiopia account ownership 2011: 14% of adults",
         "Missing 2011 baseline; needed for full 13-year trend"),
    _obs("REC_0035", "ACCESS", "Mobile Money Account Rate", "ACC_MM_ACCOUNT", 0.03, "%",
         "percentage", "2014-12-31", "Global Findex 2014", "survey",
         "https://www.worldbank.org/en/publication/globalfindex", "medium",
         "Mobile money account (% age 15+), Ethiopia 2014: 0.03%",
         "Pre-Telebirr baseline for mobile money penetration"),
    _obs("REC_0036", "ACCESS", "Mobile Money Account Rate", "ACC_MM_ACCOUNT", 0.3, "%",
         "percentage", "2017-12-31", "Global Findex 2017", "survey",
         "https://www.worldbank.org/en/publication/globalfindex", "medium",
         "Mobile money account (% age 15+), Ethiopia 2017: 0.3%",
         "Shows near-zero mobile money before the 2020 PSP directive"),
    _obs("REC_0037", "USAGE", "Made or Received Digital Payment", "USG_DIGITAL_PAYMENT",
         11.9, "%", "percentage", "2017-12-31", "Global Findex 2017", "survey",
         "https://www.worldbank.org/en/publication/globalfindex", "medium",
         "Made or received digital payments in the past year (% age 15+), 2017: ~12%",
         "USG_DIGITAL_PAYMENT is a core forecast target with no starter observations"),
    _obs("REC_0038", "USAGE", "Made or Received Digital Payment", "USG_DIGITAL_PAYMENT",
         20.0, "%", "percentage", "2021-12-31", "Global Findex 2021", "survey",
         "https://www.worldbank.org/en/publication/globalfindex", "medium",
         "Fewer than one in four adults used digital payments in 2021 (~20%)",
         "Core Usage forecast target, 2021 survey point"),
    _obs("REC_0039", "USAGE", "Made or Received Digital Payment", "USG_DIGITAL_PAYMENT",
         35.0, "%", "percentage", "2024-11-29", "Global Findex 2025", "survey",
         "https://shega.co/news/findex-2025-and-ethiopias-digital-financial-leap-momentum-without-maturity",
         "medium",
         "About a third of Ethiopian adults used digital payments in 2024 (~35%)",
         "Core Usage forecast target, latest survey point"),
    _obs("REC_0040", "USAGE", "Received Wages Into Account", "USG_WAGES", 15.0, "%",
         "percentage", "2024-11-29", "Global Findex 2025", "survey",
         "https://www.worldbank.org/en/publication/globalfindex", "medium",
         "Used account to receive wages, Ethiopia 2024: ~15%",
         "Payment use-case decomposition for Usage analysis"),
    _obs("REC_0041", "USAGE", "Telebirr Registered Users", "USG_TELEBIRR_USERS",
         20.0e6, "users", "count", "2022-06-30", "Ethio Telecom 2021/22 Report",
         "operator", "https://www.ethiotelecom.et/", "medium",
         "Telebirr surpassed 20 million subscribers by July 2022",
         "Fills the Telebirr adoption ramp between launch (2021) and 54.8M (2025)"),
    _obs("REC_0042", "USAGE", "Telebirr Registered Users", "USG_TELEBIRR_USERS",
         34.3e6, "users", "count", "2023-06-30", "Ethio Telecom 2022/23 Report",
         "operator",
         "https://www.ethiotelecom.et/ethio-telecom-2022-23-annual-business-performance/",
         "high",
         "Ethio Telecom's mobile money reaches 34.3 million subscribers, ETB 679.2 billion transacted",
         "Telebirr adoption ramp, FY2022/23"),
    _obs("REC_0043", "USAGE", "Telebirr Registered Users", "USG_TELEBIRR_USERS",
         47.5e6, "users", "count", "2024-06-30", "Ethio Telecom 2023/24 Report",
         "operator",
         "https://www.ethiotelecom.et/ethio-telecom-2023-2024-annual-business-performance-report/",
         "high",
         "Telebirr users rose to 47.5 million by end of FY2023/24",
         "Telebirr adoption ramp, FY2023/24"),
    _obs("REC_0044", "USAGE", "M-Pesa Registered Users", "USG_MPESA_USERS",
         4.5e6, "users", "count", "2024-03-31", "Safaricom FY2024 Results",
         "operator", "https://www.safaricom.co.ke/investor-relations", "medium",
         "M-Pesa Ethiopia reached ~4.5 million customers by March 2024",
         "Earlier M-Pesa point; with Dec-2024 10.8M shows acceleration"),
    _obs("REC_0045", "ACCESS", "Account Ownership Rate", "ACC_OWNERSHIP", 58.0, "%",
         "percentage", "2024-11-29", "Derived from Global Findex 2025", "calculated",
         "https://www.worldbank.org/en/publication/globalfindex", "estimated",
         "Derived: overall 49% with reported 18pp gender gap implies male ~58%",
         "Male disaggregation 2024 (derived, consistent with REC_0006 and REC_0028)",
         gender="male"),
    _obs("REC_0046", "ACCESS", "Account Ownership Rate", "ACC_OWNERSHIP", 40.0, "%",
         "percentage", "2024-11-29", "Derived from Global Findex 2025", "calculated",
         "https://www.worldbank.org/en/publication/globalfindex", "estimated",
         "Derived: overall 49% with reported 18pp gender gap implies female ~40%",
         "Female disaggregation 2024 (derived, consistent with REC_0006 and REC_0028)",
         gender="female"),
]

# --------------------------------------------------------------------------
# New events (category set, pillar left empty per schema rules)
# --------------------------------------------------------------------------
NEW_EVENTS = [
    {
        "record_id": "EVT_0011", "record_type": "event", "category": "regulation",
        "indicator": "NBE Payment Instrument Issuers Directive (ONPS/01/2020)",
        "observation_date": "2020-04-01", "gender": "all", "location": "national",
        "source_name": "National Bank of Ethiopia", "source_type": "regulator",
        "source_url": "https://nbe.gov.et/files/licensing-and-authorization-of-payment-instrument-issuers-directive-no-onps-01l2020/",
        "confidence": "high", "collected_by": COLLECTED_BY,
        "collection_date": COLLECTION_DATE,
        "original_text": "Directive No. ONPS/01/2020 issued 1 April 2020, licensing non-bank payment instrument issuers",
        "notes": "The regulatory door-opener for Telebirr and M-Pesa; predates all mobile money growth",
    },
    {
        "record_id": "EVT_0012", "record_type": "event", "category": "regulation",
        "indicator": "Mandatory Digital Payment for Fuel Purchases",
        "observation_date": "2022-07-01", "gender": "all", "location": "national",
        "source_name": "The Reporter Ethiopia / Addis Fortune", "source_type": "news",
        "source_url": "https://addisfortune.news/trade-ministry-foresees-mandatory-cashless-fuel-payment-systems/",
        "confidence": "medium", "collected_by": COLLECTED_BY,
        "collection_date": COLLECTION_DATE,
        "original_text": "Digital fuel payments began in Addis Ababa May 2022, expanding nationwide; stations accept only Telebirr/CBE electronic payment",
        "notes": "A forced-adoption use case that pushed millions into first digital payments",
    },
]

# --------------------------------------------------------------------------
# New impact links
# --------------------------------------------------------------------------
def _link(record_id, parent_id, pillar, indicator, related, direction, magnitude,
          estimate, lag, relationship, evidence, country, confidence, notes):
    return {
        "record_id": record_id, "parent_id": parent_id, "record_type": "impact_link",
        "pillar": pillar, "indicator": indicator, "related_indicator": related,
        "relationship_type": relationship, "impact_direction": direction,
        "impact_magnitude": magnitude, "impact_estimate": estimate,
        "lag_months": lag, "evidence_basis": evidence,
        "comparable_country": country, "confidence": confidence,
        "collected_by": COLLECTED_BY, "collection_date": COLLECTION_DATE,
        "notes": notes,
    }


NEW_IMPACT_LINKS = [
    _link("IMP_0015", "EVT_0001", "ACCESS", "Telebirr effect on Mobile Money Accounts",
          "ACC_MM_ACCOUNT", "increase", "medium", 4.5, 12, "direct", "empirical",
          None, "high",
          "Empirical: ACC_MM_ACCOUNT went 4.7% (2021) to 9.45% (2024) post-launch"),
    _link("IMP_0016", "EVT_0001", "USAGE", "Telebirr effect on Digital Payment Usage",
          "USG_DIGITAL_PAYMENT", "increase", "medium", 12.0, 12, "direct", "empirical",
          None, "medium",
          "Empirical: digital payment usage ~20% (2021) to ~35% (2024); Telebirr is the dominant channel"),
    _link("IMP_0017", "EVT_0011", "ACCESS", "PSP directive enables mobile money market",
          "ACC_MM_ACCOUNT", "increase", "high", None, 12, "enabling", "literature",
          "Kenya", "high",
          "Enabling regulation preceded all subsequent mobile money growth; analogous to Kenya's 2009 e-money framework"),
    _link("IMP_0018", "EVT_0012", "USAGE", "Fuel mandate effect on Telebirr adoption",
          "USG_TELEBIRR_USERS", "increase", "high", None, 3, "direct", "empirical",
          None, "medium",
          "Telebirr users roughly doubled in the year following the mandate (20M to 34.3M)"),
    _link("IMP_0019", "EVT_0012", "USAGE", "Fuel mandate effect on Digital Payment Usage",
          "USG_DIGITAL_PAYMENT", "increase", "medium", 5.0, 6, "direct", "empirical",
          None, "medium",
          "Forced digital use case creates first-time digital payers"),
    _link("IMP_0020", "EVT_0009", "ACCESS", "NFIS-II effect on Account Ownership",
          "ACC_OWNERSHIP", "increase", "medium", 5.0, 24, "enabling", "theoretical",
          None, "low",
          "National strategy coordinates enablers; long lag, hard to isolate"),
    _link("IMP_0021", "EVT_0003", "USAGE", "M-Pesa entry effect on Digital Payment Usage",
          "USG_DIGITAL_PAYMENT", "increase", "low", 3.0, 12, "direct", "literature",
          "Kenya", "medium",
          "Second provider grows the category via competition and agent expansion"),
    _link("IMP_0022", "EVT_0008", "USAGE", "EthioPay IPS effect on Digital Payment Usage",
          "USG_DIGITAL_PAYMENT", "increase", "medium", 5.0, 12, "indirect", "literature",
          "India", "medium",
          "Instant payment rails lower friction; India UPI precedent"),
    _link("IMP_0023", "EVT_0004", "ACCESS", "Fayda eKYC effect on Mobile Money Accounts",
          "ACC_MM_ACCOUNT", "increase", "low", 3.0, 18, "enabling", "literature",
          "India", "medium",
          "Digital ID lowers onboarding cost; complements existing IMP_0008 on ACC_OWNERSHIP"),
]


def load_raw():
    """Load the two raw sheets from the starter xlsx."""
    main = pd.read_excel(RAW_XLSX, sheet_name="ethiopia_fi_unified_data")
    impact = pd.read_excel(RAW_XLSX, sheet_name="Impact_sheet")
    return main, impact


def build_enriched(write=True):
    """Append enrichment records to the raw data; optionally write processed CSVs.

    Returns (main_enriched, impact_enriched).
    """
    main, impact = load_raw()

    additions_main = pd.DataFrame(NEW_OBSERVATIONS + NEW_EVENTS)
    additions_impact = pd.DataFrame(NEW_IMPACT_LINKS)

    main_out = pd.concat([main, additions_main], ignore_index=True)
    impact_out = pd.concat([impact, additions_impact], ignore_index=True)

    for df in (main_out, impact_out):
        df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")

    assert main_out["record_id"].is_unique, "duplicate record_id in main sheet"
    assert impact_out["record_id"].is_unique, "duplicate record_id in impact sheet"
    event_ids = set(main_out.loc[main_out.record_type == "event", "record_id"])
    orphans = set(impact_out["parent_id"]) - event_ids
    assert not orphans, f"impact links reference unknown events: {orphans}"

    if write:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        main_out.to_csv(PROCESSED_DIR / "ethiopia_fi_unified_data_enriched.csv", index=False)
        impact_out.to_csv(PROCESSED_DIR / "impact_links_enriched.csv", index=False)
    return main_out, impact_out


if __name__ == "__main__":
    main_df, impact_df = build_enriched()
    print(f"main sheet: {len(main_df)} records "
          f"({len(NEW_OBSERVATIONS)} observations + {len(NEW_EVENTS)} events added)")
    print(f"impact sheet: {len(impact_df)} records ({len(NEW_IMPACT_LINKS)} links added)")
