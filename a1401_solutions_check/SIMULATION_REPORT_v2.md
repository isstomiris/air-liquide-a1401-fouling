# A-1401: simulation of the revised solutions (team protocols revision 2)

Calculation note, AIChE Student Hackathon 2026 (Air Liquide case). Revision 1 of this note, 15 Nov 2026.
All numbers come from `simulate_solutions_v2.py` (run log `results_v2/run_log_v2.txt`, about 30 s). The wet thermal model (`a1401_clean_vs_fouled/a1401sim`) and the method are the same as in `SIMULATION_REPORT.md`, which covers the revision-1 solutions and stays unchanged for comparison.

What changed in the team documents (revision 2):
- **Solution 1** is now an O2T8 octyl-silica coating (0.30 µm, 200 °C cure), three Primasonics PAS-120 acoustic horns and a traversing vacuum hood, cleaning 24 times a year. It replaces the Aculon AL-B coating with 12 piezoelectric modules cycled daily.
- **Solution 2** is still CTP DECAMEX, with new assumed clearance: 24.5 / 64.8 / 93.1 % per campaign, against 31.5 / 68.85 / 93.1 % before.

## 1. Result

Reference hot-day window (18 Jul 2025, 17–20 UTC: inlet 159.4 °C, 17,444 Nm³/h dry gas, air 31.8 °C, fans 100 %). The table shows the bundle state each method holds during July–September 2025.

| State | Equivalent blockage | Airflow, m³/h | UA, kW/K | Duty, kW | Sensible / latent, kW | Outlet, °C | Max gas for 65 °C outlet, Nm³/h |
|---|---|---|---|---|---|---|---|
| No action (end of summer 2025, fitted) | 0.685 | 153,400 | 62.5 | 3,530 | 1,261 / 2,269 | 75.2 | 15,430 |
| S1 new: O2T8 + horns, low | 0.671 | 159,400 | 63.9 | 3,585 | 1,302 / 2,283 | 72.5 | 15,920 |
| **S1 new: O2T8 + horns, base** | 0.642 | 171,400 | 67.2 | **3,696** | 1,388 / 2,308 | **67.1** | **17,000** |
| S1 new: O2T8 + horns, high | 0.613 | 183,000 | 70.2 | 3,787 | 1,462 / 2,325 | 62.4 | 18,050 |
| S1 old: Aculon + piezo, central (for comparison) | 0.627 | 177,400 | 69.1 | 3,751 | 1,433 / 2,319 | 64.2 | 17,620 |
| S2 new: DECAMEX ×2, low | 0.658 | 164,900 | 65.8 | 3,645 | 1,348 / 2,297 | 69.6 | 16,480 |
| **S2 new: DECAMEX ×2, base** | 0.620 | 180,200 | 69.9 | **3,772** | 1,450 / 2,323 | **63.2** | **17,860** |
| S2 new: DECAMEX ×2, high | 0.599 | 188,500 | 72.0 | 3,830 | 1,498 / 2,333 | 60.1 | 18,600 |
| S2 old: DECAMEX ×2, revision-1 central | 0.617 | 181,300 | 70.2 | 3,781 | 1,457 / 2,324 | 62.7 | 17,970 |
| Existing-type cleaning moved to 1 Jul (model) | 0.595 | 189,900 | 72.4 | 3,840 | 1,506 / 2,334 | 59.6 | 18,730 |
| Measured after the 2026 turnaround cleaning (Jul–Sep 2026) | 0.574 | 198,000 | 74.4 | 3,889 | 1,547 / 2,342 | 56.9 | 19,450 |
| Clean bundle (model) | 0 | 342,000 | 106.5 | 4,244 | 1,865 / 2,380 | 36.7 | 32,110 |

S1 new rows include the documents' 1 % installed penalty (g1 = 0.99), applied to the air-side coefficient. The blockage shown for S1 new excludes that penalty.

| Recovery vs no action (reference window) | Duty gain | Share of seasonal loss recovered | Share of loss vs clean recovered | Gas capacity gain |
|---|---|---|---|---|
| S1 new base (low–high) | +166 kW, +4.7 % (+55 to +257) | 53 % (18–82 %) | 23 % (8–36 %) | +10 % (+3 to +17 %) |
| S1 old central | +221 kW, +6.3 % | 71 % | 31 % | +14 % |
| S2 new base (low–high) | +242 kW, +6.9 % (+115 to +301) | 77 % (37–96 %) | 34 % (16–42 %) | +16 % (+7 to +21 %) |
| S2 old central | +251 kW, +7.1 % | 80 % | 35 % | +16 % |
| Existing-type cleaning on 1 Jul | +310 kW, +8.8 % | 99 % | 43 % | +21 % |
| Measured, 2026 turnaround cleaning | +360 kW, +10.2 % | 115 % | 50 % | +26 % |

Seasonal loss = 313 kW (spring base minus end of summer). Loss vs clean = 714 kW. The plant used outlet targets of 60, 65 and 70 °C in 2026. The capacity gains are the same to within 0.2 points at all three targets, so the 65 °C column stands for all of them (`reference_day_states_v2.csv`).

Season 2025, hour by hour (2,863 historian hours, 1 Apr – 30 Sep, fans at 100 %, air ≥ 10 °C; `results_v2/season_2025_scenarios_v2.csv`):

| Scenario | Mean blockage Jul–Sep | Mean outlet, °C | Mean outlet, air ≥ 30 °C | Hours > 60 / 65 / 70 °C | Mean duty gain, kW |
|---|---|---|---|---|---|
| No in-season action (2025 as measured) | 0.686 | 74.6 | 80.1 | 2,849 / 2,651 / 2,082 | 0 |
| S1 new base, 24 events (1 May – 30 Sep) | 0.644 | 68.5 | 72.7 | 2,441 / 1,921 / 1,237 | +130 |
| S1 new base, 12 events | 0.648 | 69.3 | 73.6 | 2,515 / 2,014 / 1,367 | +112 |
| S1 new base, 52 events | 0.642 | 68.1 | 72.4 | 2,411 / 1,874 / 1,155 | +139 |
| S1 new fails (no clearance, 1 % penalty) | 0.688 | 75.0 | 80.6 | 2,852 / 2,680 / 2,150 | −10 |
| S1 old central, daily | 0.627 | 65.9 | 70.1 | 2,152 / 1,589 / 882 | +185 |
| S2 new base, 1 Jun + 1 Jul | 0.620 | 66.6 | 69.5 | 2,171 / 1,605 / 1,045 | +164 |
| S2 new base, one campaign 1 Jul | 0.627 | 68.4 | 70.9 | 2,330 / 1,876 / 1,274 | +126 |
| S2 new base, four campaigns 15 May – 1 Jul | 0.615 | 65.1 | 68.4 | 2,005 / 1,433 / 836 | +200 |
| S2 old central | 0.617 | 66.3 | 69.0 | 2,122 / 1,560 / 1,016 | +171 |
| Existing-type cleaning moved to 1 Jul | 0.595 | 65.8 | 66.8 | 1,932 / 1,532 / 1,073 | +178 |
| Limit: no seasonal debris at all | 0.594 | 61.6 | 65.3 | 1,588 / 1,032 / 479 | +275 |

What this means:
1. **The new Solution 1 is weaker than the old one on the documents' own assumptions.** Base case 67 °C on the hot day (old central 64 °C), +166 kW instead of +221 kW. The authors assume less reach and detachment for airborne sound than for contact vibration, and cleaning 24 times a year instead of daily. More events help little (52 instead of 24 events: −0.4 K mean outlet over the season), because the reach c = 0.5 caps the benefit.
2. **DECAMEX is almost unchanged:** 63 °C, +242 kW, +16 % gas (old: 62.7 °C, +251 kW).
3. **Neither method beats a cleaning of the existing type done right after the cottonwood season.** The model gives 59.6 °C for that case. The real 2026 turnaround cleaning (27 Jun – 7 Jul) did slightly better: 0.574 measured, 56.9 °C on the reference day. The new methods' value is online repetition without a shutdown, not a better clean.
4. **If Solution 1 clears nothing, it makes things slightly worse** (−0.3 K, −7 kW) because of the assumed 1 % installed penalty.
5. **The one-fan-stopped penalty is unchanged** (`SIMULATION_REPORT.md` §4): about +30 K at constant flow. It matters for DECAMEX (1.6 h per sector in the base case). For the horns, each sector stop is 20 minutes, 24 times a year.

## 2. Basis

| Item | Value | Source |
|---|---|---|
| Model, reference window, base 0.594, end-of-summer 0.685, 2025 deposition path | as `SIMULATION_REPORT.md` §2 | `a1401_clean_vs_fouled/REPORT.md`; historian |
| S1 new c, d, e | low (0.20, 0.40, 0.50), base (0.50, 0.60, 0.70), high (0.80, 0.80, 0.90); net 4 / 21 / 57.6 % per event | Protocols revision 2, §9.2 (assumptions) |
| S1 new installed penalty | g1 = 0.99 on UA (sensitivity 0.97–1.00) | Protocols §5.2 (assumption). Applied here to the air-side coefficient; equivalent to +0.002 blockage (0.97: +0.006). |
| S1 new schedule | 24 events per year (sensitivity 12 / 52), spread evenly over 1 May – 30 Sep | Protocols S1-10 gives the count; the dates are a choice of this simulation |
| S1 new hardware obstruction | none (horns off-bundle, skirts removed after each event) | Protocols §3.2 |
| S2 new c, d, e | low (0.70, 0.50, 0.70), base (0.90, 0.80, 0.90), high (1.00, 0.95, 0.98); net 24.5 / 64.8 / 93.1 % | Protocols §9.2 (assumptions) |
| S2 schedule | 2 campaigns, 1 Jun and 1 Jul (sensitivity 1 / 4) | Count from protocols S2-08; dates as revision 1 |
| Field anchor | 2026 turnaround cleaning 27 Jun – 7 Jul: Jul–Sep 2026 median 0.574 (281 h) | `SIMULATION_REPORT.md` §5 |

Method: two-pool debris model on the seasonal increment, steady-state rating at the reference window, hour-by-hour season from the per-hour blockage grid. All are unchanged from `SIMULATION_REPORT.md` §3.

## 3. Checks

| Check | Result |
|---|---|
| Energy balance, process vs air side, all reference-window states | < 10⁻¹² % |
| Outlet increases with blockage (states without the g1 penalty) | Yes |
| S1 failure case is worse than no action (penalty, no clearance) | Yes |
| Revision-1 central cases reproduced by this script | S1 old 64.2 °C, S2 old 62.7 °C, identical to `SIMULATION_REPORT.md` |

## 4. Limitations

As `SIMULATION_REPORT.md` §6. In addition:
1. The horn reach and detachment values are guesses with no fin-bundle data. The cited precedents are ash in an enclosed boiler exchanger (BHSL) and dust on a flexible PVC film (Abubakar et al.).
2. The installed penalty g1 is an allowance, not a measured coating effect. The O2T8 film is 0.3 µm, and its conduction resistance alone is negligible.
3. Whether the 10.3 t bundle can be cured at 200 °C is not established (design temperature 170 °C). If it cannot, Solution 1 as specified cannot be built, and these results do not apply.

## 5. Files

| File | Content |
|---|---|
| `simulate_solutions_v2.py` | This simulation (imports helper functions from `simulate_solutions.py`) |
| `results_v2/reference_day_states_v2.csv` | Reference-window states, capacities at 60 / 65 / 70 °C, single-event and failure cases, 30 % example |
| `results_v2/season_2025_scenarios_v2.csv` | Season table with all sensitivities |
| `results_v2/results_v2.json`, `results_v2/run_log_v2.txt` | All results and the run log |
| `figures_v2/fig1_season_2025_v2.png` | Blockage and outlet through the 2025 season, old and new Solution 1, new DECAMEX |
| `figures_v2/fig2_reference_day_v2.png` | Reference-window outlet and duty per state |
| `results/`, `figures/`, `SIMULATION_REPORT.md` | Revision-1 solutions, unchanged |
