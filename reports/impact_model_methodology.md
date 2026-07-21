# Event Impact Model — Methodology (Task 3)

Companion documentation to `notebooks/03_event_impact_modeling.ipynb`. Implementation lives in
`src/event_impact.py` (functional form, association matrix, validation) and
`src/data_loader.py::join_impact_links_with_events` (joining the impact-links file to events).

## 1. Functional form chosen

Each event's effect on an indicator is modeled as a **lagged linear adoption ramp**, not an
instantaneous step:

```
effect(t) = magnitude × clip((t − lag_months) / ramp_months, 0, 1)
```

- Zero before `lag_months` (time for the event to reach the market).
- Linear growth to full `magnitude` over `ramp_months` (default 24).
- Flat thereafter.

**Why not a step function:** Ethiopia's own data rules it out. Telebirr took four years to go
from 0 to 54.8M users, accelerating in year two rather than appearing at launch. A step function
would claim the full effect on day one, which the adoption curve directly contradicts.

**Combining multiple events:** effects on the same indicator are **summed additively**. This is
a simplifying assumption (no interaction terms between simultaneous events) appropriate to a
model with five-or-fewer historical data points per indicator; it is revisited in §5.

**Enabling links are excluded from the sum.** Four impact links have `relationship_type =
enabling` (e.g., the 2020 PSP directive → `ACC_MM_ACCOUNT`). These describe *preconditions*
regulation or infrastructure that make other events possible — not independent pp
contributions. Summing an enabling link alongside the events it enabled would double-count the
same adoption twice. They are shown in the association matrix for completeness but excluded from
the additive combination used for prediction and validation.

## 2. Sources for all impact estimates

Every impact link's `evidence_basis` and `comparable_country` field is preserved from Task 1/2
and displayed in notebook §2 and §5. Summary:

| Evidence basis | Count | Use |
|---|---|---|
| `empirical` | based on observed Ethiopian data | highest confidence |
| `literature` | comparable-country evidence (Kenya, Rwanda, Tanzania, India) | treated as an upper bound, not a point estimate — see §4 |
| `theoretical` | economic reasoning, no direct precedent | lowest confidence |

Where a link has no numeric `impact_estimate` (only a categorical `impact_magnitude`), the
association matrix (notebook §4) fills a band-midpoint fallback (high→20pp, medium→10pp,
low→3pp, negligible→0.5pp) and flags the cell explicitly as lower-precision — these fallback
values are never used silently.

## 3. Validation results: predicted vs. observed

The only window with pre/post survey data for all three target indicators is the 2021 → 2024
Findex round, bracketing the Telebirr launch (May 2021) and much of the M-Pesa/regulatory
activity. Model vs. actual over that window:

| Indicator | Predicted Δ (unrestricted) | Observed Δ | Calibration factor |
|---|---|---|---|
| `ACC_MM_ACCOUNT` | +6.6pp | +4.75pp (4.70%→9.45%) | **0.72** |
| `USG_DIGITAL_PAYMENT` | +17.3pp | +15.0pp (20%→35%) | **0.87** |
| `ACC_OWNERSHIP` | +15.0pp | +3.0pp (46%→49%) | **0.20** |

USAGE-side predictions (mobile money accounts, digital payments) are reasonably close
out-of-the-box. The sole ACCESS link — Telebirr → `ACC_OWNERSHIP`, sourced from Kenya's M-Pesa
experience — overshoots by roughly 5×.

## 4. Refinement: why ACCESS and USAGE get different calibration

Applied pillar-specific multipliers, derived directly from §3:

- **ACCESS events × 0.25** (rounded down from the empirical 0.20 for a small margin of
  conservatism, since it rests on a single validation point).
- **USAGE events (mobile money, digital payments) × 0.80** (midpoint of 0.72 and 0.87).

**Reasoning, not just curve-fitting:** the imported Kenya magnitude assumes mobile money is the
*primary banking on-ramp* for previously unbanked adults — true in Kenya, not in Ethiopia. Per
the Market Nuances guide (Sheet D) and the Task 2 EDA, mobile-money-*only* Ethiopian adults are
~0.5%: nearly every new wallet belongs to someone who already had a bank account. The same
registration event therefore moves usage substantially but barely moves headline ownership. The
calibration factor is a documented, interpretable adjustment for this structural difference — not
an opaque per-link tweak.

Post-calibration residuals (notebook §8) are within ±1.5pp of observed for all three indicators.

## 5. Key assumptions and uncertainties

| Assumption | Risk if wrong |
|---|---|
| Additive combination of simultaneous events (no interaction/diminishing-returns terms) | Could overstate combined effects when multiple events target the same indicator in the same window (e.g., 2021–2024 has 4+ USAGE events overlapping) |
| Single linear ramp shape, default 24-month length, for all events absent indicator-specific evidence | Real adoption curves may be S-shaped or event-specific; 24 months is a judgment call, not derived from data |
| One calibration factor per pillar, not per event | Coarse — a future event within a pillar may not share the same discount as Telebirr did |
| Validation rests on a single pre/post window (2021→2024) | Thin evidence base for any calibration factor; will strengthen once Findex 2027 data lands |
| No counterfactual/control group exists for any Ethiopian event | This is observational, not causally identified — the model describes association consistent with timing, not proven causation |

**Confidence ranking for Task 4 (forecasting), highest to lowest:**
1. USAGE event effects with empirical evidence_basis and a validated calibration factor (Telebirr, fuel mandate).
2. USAGE effects with literature evidence_basis, same calibration factor applied (M-Pesa, EthioPay).
3. The single ACCESS link with empirical grounding, at its validated 0.25× calibration.
4. Any link relying on the magnitude-band fallback, or any `theoretical`/uncalibrated
   `literature` ACCESS link (Fayda→`ACC_OWNERSHIP`, NFIS-II→`ACC_OWNERSHIP`) — these carry the
   widest uncertainty and should produce the widest forecast intervals in Task 4.
