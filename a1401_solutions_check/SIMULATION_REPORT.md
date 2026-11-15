# A-1401: simulation of the two proposed cleaning solutions on the wet model

Calculation note, AIChE Student Hackathon 2026 (Air Liquide case). Revision 0, 14 Nov 2026.
All numbers come from `simulate_solutions.py` (run log `results/run_log.txt`, run time about 15 s). The thermal model is `a1401_clean_vs_fouled/a1401sim`, unchanged.

## 1. Result

Expected duty recovery at the summer reference window (18 Jul 2025 17–20 UTC: inlet 159.4 °C, 17,444 Nm³/h dry gas, air 31.8 °C, fans 100 %), for the bundle state each method maintains during July–September:

| State | Equivalent blockage | Airflow, m³/h | UA, kW/K | Duty, kW | Sensible / latent, kW | Outlet, °C | Max gas for 65 °C outlet, Nm³/h |
|---|---|---|---|---|---|---|---|
| No action (end of summer 2025, fitted) | 0.685 | 153,400 | 62.5 | 3,530 | 1,261 / 2,269 | 75.2 | 15,430 |
| S1 coating + vibration, conservative | 0.651 | 167,900 | 66.6 | 3,672 | 1,369 / 2,303 | 68.3 | 16,750 |
| **S1 coating + vibration, central** | 0.627 | 177,400 | 69.1 | **3,751** | 1,433 / 2,319 | **64.2** | **17,620** |
| S1 coating + vibration, optimistic | 0.613 | 182,900 | 70.6 | 3,792 | 1,466 / 2,326 | 62.1 | 18,110 |
| S2 DECAMEX ×2, conservative | 0.651 | 167,800 | 66.6 | 3,671 | 1,369 / 2,302 | 68.3 | 16,740 |
| **S2 DECAMEX ×2, central** | 0.617 | 181,300 | 70.2 | **3,781** | 1,457 / 2,324 | **62.7** | **17,970** |
| S2 DECAMEX ×2, optimistic | 0.599 | 188,500 | 72.0 | 3,830 | 1,498 / 2,333 | 60.1 | 18,600 |
| Existing-type cleaning moved to 1 Jul | 0.595 | 190,000 | 72.4 | 3,840 | 1,506 / 2,334 | 59.6 | 18,730 |
| Spring base 2025 (no seasonal debris) | 0.594 | 190,400 | 72.5 | 3,843 | 1,508 / 2,335 | 59.4 | 18,770 |
| Best state measured after a cleaning (Nov 2025) | 0.557 | 204,300 | 76.0 | 3,923 | 1,577 / 2,347 | 55.1 | 20,000 |
| Clean bundle (model) | 0 | 342,000 | 106.5 | 4,244 | 1,865 / 2,380 | 36.7 | 32,110 |

| Recovery vs no action | Duty gain | Share of the seasonal deficit recovered | Share of the clean deficit recovered | Capacity gain at 65 °C |
|---|---|---|---|---|
| S1 central (range cons.–opt.) | +221 kW, +6.3 % (+142 to +262) | 71 % (45–84 %) | 31 % (20–37 %) | +14 % (+9 to +17 %) |
| S2 central (range cons.–opt.) | +251 kW, +7.1 % (+141 to +301) | 80 % (45–96 %) | 35 % (20–42 %) | +16 % (+9 to +21 %) |
| Existing-type cleaning on 1 Jul | +310 kW, +8.8 % | 99 % | 43 % | +21 % |

Seasonal deficit = duty at the spring base minus duty at the end-of-summer state (313 kW). Clean deficit = clean duty minus end-of-summer duty (714 kW).

Season 2025, hour by hour (2,863 historian hours from 1 Apr to 30 Sep with fans at 100 % and air ≥ 10 °C; `results/season_2025_scenarios.csv`):

| Scenario | Mean blockage Jul–Sep | Mean outlet, °C | Mean outlet, air ≥ 30 °C | Hours above 65 °C | Mean duty gain at measured flow, kW |
|---|---|---|---|---|---|
| No in-season action (2025 as measured) | 0.686 | 74.6 | 80.1 | 2,651 | 0 |
| S1 central, daily cycles 1 May – 30 Sep | 0.627 | 65.9 | 70.1 | 1,589 | +185 |
| S2 central, campaigns 1 Jun and 1 Jul | 0.617 | 66.3 | 69.0 | 1,560 | +171 |
| S2 central, one campaign 1 Jul | 0.624 | 68.1 | 70.4 | 1,822 | +132 |
| S2 central, four campaigns 15 May – 1 Jul | 0.613 | 64.9 | 68.1 | 1,401 | +205 |
| Existing-type cleaning moved to 1 Jul | 0.595 | 65.7 | 66.8 | 1,530 | +178 |
| Limit: no seasonal debris at all | 0.594 | 61.6 | 65.3 | 1,032 | +275 |

What this means:
1. **With the central assumptions, the two methods give similar results**: about 63–64 °C instead of 75 °C on a hot day, and about 14–16 % more gas at a 65 °C outlet. The difference between them is smaller than the spread between their own conservative and optimistic cases.
2. **Neither method, as assumed, does better than the existing cleaning done at the right time.** In 2025 the debris built up from late April to late June and then stayed. The existing cleaning (October 2025) removed at least the whole seasonal increment. Moving a cleaning of that quality to 1 July gives 59.6 °C on the reference day, better than the central case of either method.
3. **The limit of any method that only removes the seasonal debris is about 59–60 °C on the reference day.** Going further needs a reduction of the 0.59 base. The best value ever measured after a cleaning (0.557, Nov 2025) would give 55 °C. A clean bundle would give 37 °C. Whether the base is debris that the existing cleaning does not reach, or model offset and permanent damage, is not known (see `REPORT.md` §8).
4. **Stopping one fan costs about 30 K** of outlet temperature with the bundle in its current state (§4). A DECAMEX campaign needs a cool window or a temporary load reduction.

## 2. Basis

| Item | Value | Source |
|---|---|---|
| Thermal model | 6 rows × 24 segments, 2 passes, wet syngas with condensation (W = 0.555), Briggs & Young air side, generic axial fan curve, Robinson–Briggs bundle Δp | `a1401_clean_vs_fouled/REPORT.md` §4 |
| Reference window | 18 Jul 2025 17:00–20:00 UTC | `REPORT.md` §3 |
| Plant state, end of summer 2025 | b = 0.685 (fitted on calibration weeks) | `REPORT.md` §6.5 |
| Spring base 2025 | b = 0.594 (median, 15 Mar – 20 Apr 2025) | This calculation, from `history_equivalent_blockage_hourly.csv` |
| Seasonal increment 2025 | 0.093 at its peak; built from late April to about 25 June, flat afterwards | Same |
| Existing cleaning anchor | 0.682 (Aug–Sep 2025) → 0.557 (Nov 2025, 40 h); drop between 1 Oct and 30 Oct 2025 | Same |
| Clearance parameters c, d, e | S1 (0.40, 0.25, 0.50) / (0.65, 0.50, 0.80) / (0.80, 0.70, 0.90); S2 (0.70, 0.60, 0.75) / (0.90, 0.85, 0.90) / (1.00, 0.95, 0.98) | Protocols file §6.1, §9.2 (assumptions, not measurements) |
| S1 hardware obstruction | 0.2 % of open face | Protocols file §5.2 (assumption) |
| S1 schedule | One full sequence per day, 1 May – 30 Sep | Protocols file S1-10 (assumption) |
| S2 schedule | Central: 1 Jun and 1 Jul; sensitivity 1 and 4 campaigns | This calculation. The protocols file proposes 1/2/4 per year; dates were chosen to cover the 2025 deposition period. |

## 3. Method

**Blockage that each method acts on.** The plant's equivalent blockage has a base of about 0.59 that is present every spring and survives the existing cleaning, plus a seasonal increment that appears every May–June and disappears after cleaning. Only the increment is credited to the cleaning methods:

b(t) = b_base + debris left from the seasonal increment (+ hardware obstruction for S1).

**Two-pool debris model.** New debris from the measured 2025 increment (smoothed, made non-decreasing) is split into a reachable pool (fraction c) and an unreachable pool (1 − c). Each cleaning event removes the fraction d·e of the reachable pool. The unreachable pool stays until the end of the season. For one event this gives the documents' net reopening η = c·d·e. For repeated events it prevents the unphysical result that daily cycles with a small η drive the blockage to zero: the benefit of frequent cleaning is capped by c.

**Thermal evaluation.** Steady state at the reference window with `rate()` for each state (§1, first table). For the season, the outlet of each historian hour is interpolated from the per-hour blockage grid that `a1401_clean_vs_fouled` computed with the same model (13 blockage values; 5,637 hours with the first export, 6,687 with the re-export of 15 Nov 2026; only 2025 hours are used here). Duty per hour = dry molar flow × wet enthalpy change, at the measured gas flow.

**One fan stopped.** Each running fan is taken to see the same per-fan system curve as before (sectors independent). Total air is then 2/3 of the three-fan value, and one third of the face carries no air: b′ = 1 − (2/3)(1 − b). Natural draft and leakage through the idle sector are neglected, so the penalty is an upper estimate.

## 4. Temporary state with one fan stopped (`results/one_fan_stopped.csv`)

| Air, °C | Bundle state | Outlet, 3 fans → 2 fans, °C | Duty, 3 fans → 2 fans, kW | Max gas for 65 °C, 3 fans → 2 fans, Nm³/h |
|---|---|---|---|---|
| 20.0 | Spring base (0.594) | 45.0 → 76.3 | 4,103 → 3,505 | 22,190 → 15,500 |
| 20.0 | End of summer (0.685) | 61.0 → 95.1 | 3,814 → 3,062 | 18,220 → 12,630 |
| 31.8 | Spring base (0.594) | 59.4 → 89.2 | 3,843 → 3,212 | 18,770 → 13,130 |
| 31.8 | End of summer (0.685) | 75.2 → 105.1 | 3,530 → 2,780 | 15,430 → 10,710 |

The protocols file estimates 1.6 h per fan sector for a central DECAMEX campaign. During that time the outlet would rise by about 30 K at the same gas flow, or the gas flow would have to drop by about 30 %. A night-time campaign at about 20 °C air with the gas flow held near 13,000–15,000 Nm³/h keeps the outlet near 65 °C. For S1, each sector window is about 10 minutes, which is short compared with the thermal response of the downstream system, but it repeats every day.

## 5. Checks

| Check | Result |
|---|---|
| Energy balance, process side vs air side, all reference-day states | Closes to < 10⁻¹² % |
| Outlet increases with blockage in all reference-day states | Yes |
| No scenario ends with more blockage than no action (apart from the 0.2 % S1 hardware) | Yes |
| Model outlet on the smoothed no-action path vs measured outlet, 2,863 h | MAE 2.7 K, bias +0.8 K |
| Field check, added 15 Nov 2026: real turnaround cleaning 27 Jun – 7 Jul 2026 (historian re-export) vs the "existing-type cleaning moved to 1 Jul" case | Predicted Jul–Sep blockage 0.595 (59.5 °C on the reference day). Measured 8 Jul – 30 Sep 2026: median 0.574 (281 h with fans at 100 % and air ≥ 10 °C, `a1401_clean_vs_fouled/results/history_equivalent_blockage_hourly.csv`), which gives 56.9 °C on the reference day. Spring base 2026 (15 Mar – 20 Apr): 0.605, close to 0.594 in 2025. |

The second-last check shows that the smoothed blockage path reproduces the measured season. The last check is the only field test available: it supports the existing-cleaning case (the real cleaning before the peak did slightly better than predicted). It does not test S1 or S2, whose clearance parameters still have no field data for A-1401. The 2026 sample is small (281 hours) because the outlet set point was moved in 2026 and the fans were less often at 100 %.

## 6. Limitations

1. Every post-treatment state depends on the clearance parameters c, d, e, which are assumptions from the protocols file. No cottonwood clearance data exist for either method.
2. The base of about 0.59 is not credited to either method. If DECAMEX (all-row treatment) or the shop cleaning that precedes the coating does reach debris that the existing cleaning misses, the gain could be larger. That can only be established by inspecting the bundle after a cleaning.
3. One season (2025) defines the deposition path. In 2024 the increment was larger (about 12 points, 0.53 → 0.65).
4. The coating's effect on new deposition is not credited in the base case (s = 1). With s = 0.8 or 0.6 the S1 central outlet on hot hours falls by about 1–2 K (`season_2025_scenarios.csv`).
5. The fan curve is generic, the fin geometry is assumed (64 mm pitch; the drawing gives 62 mm), and uniform blockage over the face is assumed. See `REPORT.md` §8 for the model's own limitations.
6. Costs, hazards and production value are outside this note.

## 7. Files

| File | Content |
|---|---|
| `simulate_solutions.py` | The simulation (imports `../a1401_clean_vs_fouled/a1401sim`) |
| `results/reference_day_states.csv` | §1 first table, with recovery percentages and single-event cases |
| `results/season_2025_scenarios.csv` | §1 season table, including schedule and coating sensitivities |
| `results/one_fan_stopped.csv` | §4 |
| `results/results.json`, `results/run_log.txt` | All results and the run log |
| `figures/fig1_season_2025.png` | Equivalent blockage and outlet through the 2025 season |
| `figures/fig2_reference_day.png` | Reference-day outlet and duty for each state |
