# Data Enrichment Log

Documentation of all additions to the starter dataset (Task 1).
Machine-readable definitions live in `src/enrichment.py`; enriched outputs are
`data/processed/ethiopia_fi_unified_data_enriched.csv` (main sheet) and
`data/processed/impact_links_enriched.csv` (impact links).

**Collected by:** KalkidanAsfaw · **Collection date:** 2026-07-17

## Summary

| Addition type | Count | Result |
|---|---|---|
| Observations | 13 | 30 → 43 observations |
| Events | 2 | 10 → 12 events |
| Impact links | 9 | 14 → 23 links |

No starter records were modified or deleted; all raw files are preserved unchanged in `data/raw/`.

## Why these additions

Three gaps in the starter data directly blocked the forecasting task:

1. **`USG_DIGITAL_PAYMENT` — the Usage forecast target — had zero observations.** Added the
   three available Findex survey points (2017, 2021, 2024).
2. **`ACC_OWNERSHIP` was missing its 2011 baseline (14%)**, shortening the trend history from
   13 years to 10. Added it.
3. **The event catalog missed the two regulatory shocks that best explain mobile money timing:**
   the April 2020 NBE directive that legalized non-bank e-money (without which Telebirr could not
   exist), and the 2022 mandatory digital fuel-payment rule (forced first-time adoption).

Additionally, annual Telebirr user counts (2022–2024) turn a two-point mobile money series into a
five-point adoption curve — the key calibration data for event-effect shapes in Task 3.

## Observations added

| ID | Indicator | Value | Date | Source | Confidence |
|---|---|---|---|---|---|
| REC_0034 | ACC_OWNERSHIP | 14% | 2011-12-31 | Global Findex 2011 | high |
| REC_0035 | ACC_MM_ACCOUNT | 0.03% | 2014-12-31 | Global Findex 2014 | medium |
| REC_0036 | ACC_MM_ACCOUNT | 0.3% | 2017-12-31 | Global Findex 2017 | medium |
| REC_0037 | USG_DIGITAL_PAYMENT | 11.9% | 2017-12-31 | Global Findex 2017 | medium |
| REC_0038 | USG_DIGITAL_PAYMENT | 20% | 2021-12-31 | Global Findex 2021 | medium |
| REC_0039 | USG_DIGITAL_PAYMENT | 35% | 2024-11-29 | Global Findex 2025 (via Shega/DFS Ethiopia) | medium |
| REC_0040 | USG_WAGES | 15% | 2024-11-29 | Global Findex 2025 | medium |
| REC_0041 | USG_TELEBIRR_USERS | 20.0M | 2022-06-30 | Ethio Telecom 2021/22 report | medium |
| REC_0042 | USG_TELEBIRR_USERS | 34.3M | 2023-06-30 | Ethio Telecom 2022/23 report | high |
| REC_0043 | USG_TELEBIRR_USERS | 47.5M | 2024-06-30 | Ethio Telecom 2023/24 report | high |
| REC_0044 | USG_MPESA_USERS | 4.5M | 2024-03-31 | Safaricom FY2024 results | medium |
| REC_0045 | ACC_OWNERSHIP (male) | 58% | 2024-11-29 | Derived (49% overall + 18pp gap) | estimated |
| REC_0046 | ACC_OWNERSHIP (female) | 40% | 2024-11-29 | Derived (49% overall + 18pp gap) | estimated |

Notes on selected records:

- **REC_0038/0039 (digital payments):** sources report "fewer than one in four adults" (2021) and
  "about a third" (2024); the recorded values (20%, 35%) are the commonly cited Findex figures and
  match the challenge brief. Marked *medium* pending verification against the Findex data portal.
- **REC_0041 (Telebirr 2022):** press coverage reports "surpassed 20 million by July 2022";
  recorded conservatively as 20.0M, *medium*.
- **REC_0045/0046:** flagged `estimated` and `calculated` — derived from two high-confidence
  records (REC_0006 overall rate, REC_0028 gender gap), not independently surveyed.

## Events added

| ID | Category | Event | Date | Source | Confidence |
|---|---|---|---|---|---|
| EVT_0011 | regulation | NBE Payment Instrument Issuers Directive (ONPS/01/2020) | 2020-04-01 | [nbe.gov.et](https://nbe.gov.et/files/licensing-and-authorization-of-payment-instrument-issuers-directive-no-onps-01l2020/) | high |
| EVT_0012 | regulation | Mandatory digital payment for fuel purchases | 2022-07-01 | [Addis Fortune](https://addisfortune.news/trade-ministry-foresees-mandatory-cashless-fuel-payment-systems/) | medium |

Per schema rules, both events have `category` set and `pillar` left empty; their effects are
expressed through impact links.

- **EVT_0011:** issued 1 April 2020; licensed non-bank payment instrument issuers, replacing the
  bank-led mobile banking regime. This is the regulatory precondition for Telebirr (2021) and
  M-Pesa (2023).
- **EVT_0012:** digital-only fuel payments started in Addis Ababa May 2022 and expanded nationwide;
  date recorded as 2022-07-01 (nationwide expansion), *medium* confidence on the exact date.

## Impact links added

| ID | Event | Indicator | Direction | Magnitude | Est. (pp/%) | Lag (mo) | Evidence |
|---|---|---|---|---|---|---|---|
| IMP_0015 | Telebirr launch | ACC_MM_ACCOUNT | increase | medium | +4.5pp | 12 | empirical (4.7%→9.45%, 2021–2024) |
| IMP_0016 | Telebirr launch | USG_DIGITAL_PAYMENT | increase | medium | +12pp | 12 | empirical (~20%→~35%, 2021–2024) |
| IMP_0017 | PSP directive 2020 | ACC_MM_ACCOUNT | increase | high | — | 12 | literature (Kenya e-money framework) |
| IMP_0018 | Fuel mandate 2022 | USG_TELEBIRR_USERS | increase | high | — | 3 | empirical (20M→34.3M in following year) |
| IMP_0019 | Fuel mandate 2022 | USG_DIGITAL_PAYMENT | increase | medium | +5pp | 6 | empirical |
| IMP_0020 | NFIS-II strategy | ACC_OWNERSHIP | increase | medium | +5pp | 24 | theoretical (low confidence) |
| IMP_0021 | M-Pesa launch | USG_DIGITAL_PAYMENT | increase | low | +3pp | 12 | literature (Kenya competition effects) |
| IMP_0022 | EthioPay IPS | USG_DIGITAL_PAYMENT | increase | medium | +5pp | 12 | literature (India UPI) |
| IMP_0023 | Fayda rollout | ACC_MM_ACCOUNT | increase | low | +3pp | 18 | literature (India Aadhaar eKYC) |

Rationale: the starter links connected Telebirr to `ACC_OWNERSHIP` and P2P counts but **not** to
the two indicators it most obviously moved (`ACC_MM_ACCOUNT`, `USG_DIGITAL_PAYMENT`); NFIS-II had
no links at all; and the two new events needed links to be usable in the impact model.

## Corrections

None — no starter values conflicted with sources checked so far. One anomaly to revisit in EDA:
the NFIS-II target (REC_0031) of 70% account ownership by 2025 is far above the observed 2024
value (49%), which matters for interpreting "progress toward target" in the dashboard.

## Full per-record documentation

Auto-generated from `src/enrichment.py` (the machine-readable source of truth) so the
log can never drift from the dataset.

### Observations

#### REC_0034 — Account Ownership Rate (ACC_OWNERSHIP)
- **record_type:** observation
- **pillar:** ACCESS
- **value:** 14.0
- **unit:** %
- **observation_date:** 2011-12-31
- **gender:** all
- **location:** national
- **source_name:** Global Findex 2011
- **source_type:** survey
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** high
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Ethiopia account ownership 2011: 14% of adults"
- **notes (why useful):** Missing 2011 baseline; needed for full 13-year trend

#### REC_0035 — Mobile Money Account Rate (ACC_MM_ACCOUNT)
- **record_type:** observation
- **pillar:** ACCESS
- **value:** 0.03
- **unit:** %
- **observation_date:** 2014-12-31
- **gender:** all
- **location:** national
- **source_name:** Global Findex 2014
- **source_type:** survey
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Mobile money account (% age 15+), Ethiopia 2014: 0.03%"
- **notes (why useful):** Pre-Telebirr baseline for mobile money penetration

#### REC_0036 — Mobile Money Account Rate (ACC_MM_ACCOUNT)
- **record_type:** observation
- **pillar:** ACCESS
- **value:** 0.3
- **unit:** %
- **observation_date:** 2017-12-31
- **gender:** all
- **location:** national
- **source_name:** Global Findex 2017
- **source_type:** survey
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Mobile money account (% age 15+), Ethiopia 2017: 0.3%"
- **notes (why useful):** Shows near-zero mobile money before the 2020 PSP directive

#### REC_0037 — Made or Received Digital Payment (USG_DIGITAL_PAYMENT)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 11.9
- **unit:** %
- **observation_date:** 2017-12-31
- **gender:** all
- **location:** national
- **source_name:** Global Findex 2017
- **source_type:** survey
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Made or received digital payments in the past year (% age 15+), 2017: ~12%"
- **notes (why useful):** USG_DIGITAL_PAYMENT is a core forecast target with no starter observations

#### REC_0038 — Made or Received Digital Payment (USG_DIGITAL_PAYMENT)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 20.0
- **unit:** %
- **observation_date:** 2021-12-31
- **gender:** all
- **location:** national
- **source_name:** Global Findex 2021
- **source_type:** survey
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Fewer than one in four adults used digital payments in 2021 (~20%)"
- **notes (why useful):** Core Usage forecast target, 2021 survey point

#### REC_0039 — Made or Received Digital Payment (USG_DIGITAL_PAYMENT)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 35.0
- **unit:** %
- **observation_date:** 2024-11-29
- **gender:** all
- **location:** national
- **source_name:** Global Findex 2025
- **source_type:** survey
- **source_url:** https://shega.co/news/findex-2025-and-ethiopias-digital-financial-leap-momentum-without-maturity
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "About a third of Ethiopian adults used digital payments in 2024 (~35%)"
- **notes (why useful):** Core Usage forecast target, latest survey point

#### REC_0040 — Received Wages Into Account (USG_WAGES)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 15.0
- **unit:** %
- **observation_date:** 2024-11-29
- **gender:** all
- **location:** national
- **source_name:** Global Findex 2025
- **source_type:** survey
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Used account to receive wages, Ethiopia 2024: ~15%"
- **notes (why useful):** Payment use-case decomposition for Usage analysis

#### REC_0041 — Telebirr Registered Users (USG_TELEBIRR_USERS)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 20000000.0
- **unit:** users
- **observation_date:** 2022-06-30
- **gender:** all
- **location:** national
- **source_name:** Ethio Telecom 2021/22 Report
- **source_type:** operator
- **source_url:** https://www.ethiotelecom.et/
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Telebirr surpassed 20 million subscribers by July 2022"
- **notes (why useful):** Fills the Telebirr adoption ramp between launch (2021) and 54.8M (2025)

#### REC_0042 — Telebirr Registered Users (USG_TELEBIRR_USERS)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 34300000.0
- **unit:** users
- **observation_date:** 2023-06-30
- **gender:** all
- **location:** national
- **source_name:** Ethio Telecom 2022/23 Report
- **source_type:** operator
- **source_url:** https://www.ethiotelecom.et/ethio-telecom-2022-23-annual-business-performance/
- **confidence:** high
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Ethio Telecom's mobile money reaches 34.3 million subscribers, ETB 679.2 billion transacted"
- **notes (why useful):** Telebirr adoption ramp, FY2022/23

#### REC_0043 — Telebirr Registered Users (USG_TELEBIRR_USERS)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 47500000.0
- **unit:** users
- **observation_date:** 2024-06-30
- **gender:** all
- **location:** national
- **source_name:** Ethio Telecom 2023/24 Report
- **source_type:** operator
- **source_url:** https://www.ethiotelecom.et/ethio-telecom-2023-2024-annual-business-performance-report/
- **confidence:** high
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Telebirr users rose to 47.5 million by end of FY2023/24"
- **notes (why useful):** Telebirr adoption ramp, FY2023/24

#### REC_0044 — M-Pesa Registered Users (USG_MPESA_USERS)
- **record_type:** observation
- **pillar:** USAGE
- **value:** 4500000.0
- **unit:** users
- **observation_date:** 2024-03-31
- **gender:** all
- **location:** national
- **source_name:** Safaricom FY2024 Results
- **source_type:** operator
- **source_url:** https://www.safaricom.co.ke/investor-relations
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "M-Pesa Ethiopia reached ~4.5 million customers by March 2024"
- **notes (why useful):** Earlier M-Pesa point; with Dec-2024 10.8M shows acceleration

#### REC_0045 — Account Ownership Rate (ACC_OWNERSHIP)
- **record_type:** observation
- **pillar:** ACCESS
- **value:** 58.0
- **unit:** %
- **observation_date:** 2024-11-29
- **gender:** male
- **location:** national
- **source_name:** Derived from Global Findex 2025
- **source_type:** calculated
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** estimated
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Derived: overall 49% with reported 18pp gender gap implies male ~58%"
- **notes (why useful):** Male disaggregation 2024 (derived, consistent with REC_0006 and REC_0028)

#### REC_0046 — Account Ownership Rate (ACC_OWNERSHIP)
- **record_type:** observation
- **pillar:** ACCESS
- **value:** 40.0
- **unit:** %
- **observation_date:** 2024-11-29
- **gender:** female
- **location:** national
- **source_name:** Derived from Global Findex 2025
- **source_type:** calculated
- **source_url:** https://www.worldbank.org/en/publication/globalfindex
- **confidence:** estimated
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **original_text:** "Derived: overall 49% with reported 18pp gender gap implies female ~40%"
- **notes (why useful):** Female disaggregation 2024 (derived, consistent with REC_0006 and REC_0028)

### Events

#### EVT_0011 — NBE Payment Instrument Issuers Directive (ONPS/01/2020)
- **record_type:** event
- **category:** regulation
- **observation_date:** 2020-04-01
- **source_name:** National Bank of Ethiopia
- **source_type:** regulator
- **source_url:** https://nbe.gov.et/files/licensing-and-authorization-of-payment-instrument-issuers-directive-no-onps-01l2020/
- **confidence:** high
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **pillar:** (empty — events are never pre-assigned to pillars)
- **original_text:** "Directive No. ONPS/01/2020 issued 1 April 2020, licensing non-bank payment instrument issuers"
- **notes (why useful):** The regulatory door-opener for Telebirr and M-Pesa; predates all mobile money growth

#### EVT_0012 — Mandatory Digital Payment for Fuel Purchases
- **record_type:** event
- **category:** regulation
- **observation_date:** 2022-07-01
- **source_name:** The Reporter Ethiopia / Addis Fortune
- **source_type:** news
- **source_url:** https://addisfortune.news/trade-ministry-foresees-mandatory-cashless-fuel-payment-systems/
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **pillar:** (empty — events are never pre-assigned to pillars)
- **original_text:** "Digital fuel payments began in Addis Ababa May 2022, expanding nationwide; stations accept only Telebirr/CBE electronic payment"
- **notes (why useful):** A forced-adoption use case that pushed millions into first digital payments

### Impact links

#### IMP_0015 — Telebirr effect on Mobile Money Accounts
- **record_type:** impact_link
- **parent_id:** EVT_0001
- **pillar:** ACCESS
- **related_indicator:** ACC_MM_ACCOUNT
- **relationship_type:** direct
- **impact_direction:** increase
- **impact_magnitude:** medium
- **impact_estimate:** 4.5
- **lag_months:** 12
- **evidence_basis:** empirical
- **comparable_country:** (n/a)
- **confidence:** high
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Empirical: ACC_MM_ACCOUNT went 4.7% (2021) to 9.45% (2024) post-launch

#### IMP_0016 — Telebirr effect on Digital Payment Usage
- **record_type:** impact_link
- **parent_id:** EVT_0001
- **pillar:** USAGE
- **related_indicator:** USG_DIGITAL_PAYMENT
- **relationship_type:** direct
- **impact_direction:** increase
- **impact_magnitude:** medium
- **impact_estimate:** 12.0
- **lag_months:** 12
- **evidence_basis:** empirical
- **comparable_country:** (n/a)
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Empirical: digital payment usage ~20% (2021) to ~35% (2024); Telebirr is the dominant channel

#### IMP_0017 — PSP directive enables mobile money market
- **record_type:** impact_link
- **parent_id:** EVT_0011
- **pillar:** ACCESS
- **related_indicator:** ACC_MM_ACCOUNT
- **relationship_type:** enabling
- **impact_direction:** increase
- **impact_magnitude:** high
- **impact_estimate:** (n/a)
- **lag_months:** 12
- **evidence_basis:** literature
- **comparable_country:** Kenya
- **confidence:** high
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Enabling regulation preceded all subsequent mobile money growth; analogous to Kenya's 2009 e-money framework

#### IMP_0018 — Fuel mandate effect on Telebirr adoption
- **record_type:** impact_link
- **parent_id:** EVT_0012
- **pillar:** USAGE
- **related_indicator:** USG_TELEBIRR_USERS
- **relationship_type:** direct
- **impact_direction:** increase
- **impact_magnitude:** high
- **impact_estimate:** (n/a)
- **lag_months:** 3
- **evidence_basis:** empirical
- **comparable_country:** (n/a)
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Telebirr users roughly doubled in the year following the mandate (20M to 34.3M)

#### IMP_0019 — Fuel mandate effect on Digital Payment Usage
- **record_type:** impact_link
- **parent_id:** EVT_0012
- **pillar:** USAGE
- **related_indicator:** USG_DIGITAL_PAYMENT
- **relationship_type:** direct
- **impact_direction:** increase
- **impact_magnitude:** medium
- **impact_estimate:** 5.0
- **lag_months:** 6
- **evidence_basis:** empirical
- **comparable_country:** (n/a)
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Forced digital use case creates first-time digital payers

#### IMP_0020 — NFIS-II effect on Account Ownership
- **record_type:** impact_link
- **parent_id:** EVT_0009
- **pillar:** ACCESS
- **related_indicator:** ACC_OWNERSHIP
- **relationship_type:** enabling
- **impact_direction:** increase
- **impact_magnitude:** medium
- **impact_estimate:** 5.0
- **lag_months:** 24
- **evidence_basis:** theoretical
- **comparable_country:** (n/a)
- **confidence:** low
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** National strategy coordinates enablers; long lag, hard to isolate

#### IMP_0021 — M-Pesa entry effect on Digital Payment Usage
- **record_type:** impact_link
- **parent_id:** EVT_0003
- **pillar:** USAGE
- **related_indicator:** USG_DIGITAL_PAYMENT
- **relationship_type:** direct
- **impact_direction:** increase
- **impact_magnitude:** low
- **impact_estimate:** 3.0
- **lag_months:** 12
- **evidence_basis:** literature
- **comparable_country:** Kenya
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Second provider grows the category via competition and agent expansion

#### IMP_0022 — EthioPay IPS effect on Digital Payment Usage
- **record_type:** impact_link
- **parent_id:** EVT_0008
- **pillar:** USAGE
- **related_indicator:** USG_DIGITAL_PAYMENT
- **relationship_type:** indirect
- **impact_direction:** increase
- **impact_magnitude:** medium
- **impact_estimate:** 5.0
- **lag_months:** 12
- **evidence_basis:** literature
- **comparable_country:** India
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Instant payment rails lower friction; India UPI precedent

#### IMP_0023 — Fayda eKYC effect on Mobile Money Accounts
- **record_type:** impact_link
- **parent_id:** EVT_0004
- **pillar:** ACCESS
- **related_indicator:** ACC_MM_ACCOUNT
- **relationship_type:** enabling
- **impact_direction:** increase
- **impact_magnitude:** low
- **impact_estimate:** 3.0
- **lag_months:** 18
- **evidence_basis:** literature
- **comparable_country:** India
- **confidence:** medium
- **collected_by:** KalkidanAsfaw
- **collection_date:** 2026-07-17
- **notes (evidence reasoning):** Digital ID lowers onboarding cost; complements existing IMP_0008 on ACC_OWNERSHIP
