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
