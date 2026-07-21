# Forecasting Access and Usage, 2025–2027 — Results (Task 4)

Companion documentation to `notebooks/04_forecasting.ipynb`. Implementation in
`src/forecasting.py` (trend regression, event-augmented model, scenario combination), built on
the calibrated event-impact model from Task 3 (`src/event_impact.py`,
`reports/impact_model_methodology.md`).

## 1. Targets

- **Access** — Account Ownership Rate (`ACC_OWNERSHIP`)
- **Usage** — Digital Payment Adoption (`USG_DIGITAL_PAYMENT`)

`ACC_MM_ACCOUNT` (mobile money accounts) is carried as supporting context only — it is the
indicator most cataloged events directly move, and explains why Access and Usage diverge.

## 2. Approach selected: event-augmented model as primary, trend as reference baseline

A pure linear-trend baseline was fit and is reported (§3), but **not used as the primary
forecast** — with 5 points (Access) and 3 points (Usage), it is provably unstable:

- `ACC_OWNERSHIP`'s full-history trend projects 60.5% by 2027, pulled up by the fast 2014–2017
  growth years, directly contradicting the documented 2021–24 deceleration (+1.0pp/yr).
- `USG_DIGITAL_PAYMENT`'s trend (1 residual degree of freedom) produces a prediction interval of
  **−48pp to +134pp** by 2027 — statistically correct, practically useless.

The **event-augmented model** is used instead: the last observed value, plus Task 3's calibrated
event effects continued forward through the horizon, plus a small residual "background" growth
rate estimated directly from the same 2021→2024 validation window (observed change minus the
calibrated model's predicted change, annualized) — see `src/forecasting.py::residual_background_rate`.

## 3. Forecast table (2025–2027)

| Indicator | Year | Event-augmented base | Scenario low–high | Trend baseline | Trend 95% CI |
|---|---|---|---|---|---|
| `ACC_OWNERSHIP` | 2025 | 49.0% | 49.0–49.3% | 54.8% | 42.2–67.5% |
| `ACC_OWNERSHIP` | 2026 | 49.0% | 49.0–50.0% | 57.7% | 44.5–70.8% |
| `ACC_OWNERSHIP` | 2027 | 49.0% | 49.0–50.8% | 60.5% | 46.8–74.2% |
| `USG_DIGITAL_PAYMENT` | 2025 | 36.9% | 35.8–37.7% | 36.3% | −40.0–112.6% |
| `USG_DIGITAL_PAYMENT` | 2026 | 38.1% | 36.2–39.3% | 39.5% | −43.6–122.7% |
| `USG_DIGITAL_PAYMENT` | 2027 | 40.5% | 37.2–42.7% | 42.8% | −48.0–133.5% |

Machine-readable version: `reports/forecast_table.csv`. The trend columns are included for
transparency (the brief asks for a baseline explicitly) but the **event-augmented columns are
the actionable forecast** — the trend CIs above are wide enough (including impossible negative
percentages) to demonstrate why on their own.

## 4. Scenario design

Optimistic/pessimistic scale the *same* calibrated model rather than introducing unrelated
assumptions:

- **`USG_DIGITAL_PAYMENT`**: symmetric ×0.4 (pessimistic) / ×1.0 (base) / ×1.4 (optimistic) on
  both the calibration factor and the background rate — faster/slower realization of the same
  cataloged events (M-Pesa's ongoing ramp, EthioPay's Dec-2025 launch) and organic growth.
- **`ACC_OWNERSHIP`**: base/pessimistic use only the one *validated* driver (Telebirr, ×0.25,
  already fully matured — hence flat at 49% in both). Optimistic additionally includes the two
  `enabling` links excluded from Task 3's validated model (Fayda digital ID, NFIS-II strategy),
  at a steeper 0.15× discount — explicitly priced as unproven, since neither has ever been
  checked against an Ethiopian data point. This is the only scenario in which ownership moves at
  all (49.0% → 50.8% by 2027).

## 5. Interpretation

**What the model predicts.** `ACC_OWNERSHIP` is essentially flat through 2027 (49.0–50.8%) — its
only validated driver matured in 2024 and nothing else in the event catalog has a direct link to
headline ownership. `USG_DIGITAL_PAYMENT` keeps growing (36.9–40.5% base case) on the strength of
M-Pesa's continuing ramp and EthioPay's 2025 launch.

**Which events matter most.** Usage: Telebirr already delivered the largest realized effect;
M-Pesa's ramp (through ~2026) and EthioPay (launched Dec 2025) are the largest *remaining*
levers inside the forecast window. Access: only Fayda and NFIS-II have any plausible path to
moving ownership further, and only if their enabling links — never yet validated against
Ethiopian data — convert into real account-opening.

**Key uncertainties.**
1. Both calibration factors (§ Task 3) rest on a single validation window — one data point of
   evidence per pillar.
2. `ACC_OWNERSHIP`'s forecast is fragile by construction: it hangs on exactly one impact link.
3. The trend baseline is reported for completeness but is not decision-usable at this sample size.
4. No forecast accounts for a repeat of a macro shock like the 2024 FX liberalization — a
   plausible unmodeled downside for 2025–2027.

**Bottom line.** Absent new Access-specific policy, Ethiopia is projected to reach roughly
49–51% account ownership by 2027 — far short of the NFIS-II 70% target and short of even a 60%
"realistic frontier." Digital payment usage is projected to reach 37–43%, continuing on the
strength of already-launched products. The clearest lever this analysis identifies: converting
Fayda/NFIS-II's *enabling* groundwork into a measurable, direct effect on account ownership —
the model currently has no validated pathway for that conversion to happen on its own.
