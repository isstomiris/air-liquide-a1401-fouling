# A-1401 Air-Cooled Syngas Exchanger: Clean vs Fouled Rating Calculation

Calculation note, AIChE Student Hackathon 2026 (Air Liquide case). Revision 0, 14 Nov 2026.
All numbers in this note come from `run_all.py` (results in `results/`, figures in `figures/`). Run time is about 15 s if `results/_history_grid_cache.npz` exists, or about 10 min on 4 cores without it.

---

## 1. Summary

| Item | Result |
|---|---|
| Reference condition | Real historian window, 18 Jul 2025, 17:00–20:00 UTC. Inlet 159.4 °C, dry gas 17,444 Nm³/h, air 31.8 °C, fans at 100 %, measured outlet 72.9 °C. |
| Clean exchanger (b = 0) | Outlet **36.7 °C**, duty **4,242 kW** (56 % condensation), UA 106.5 kW/K, airflow 342,000 m³/h. |
| Plant state, end of summer 2025 (b_eq = 68.5 %, fitted) | Outlet **75.2 °C**, duty 3,529 kW (−16.8 %), UA 62.5 kW/K (−41 %), airflow 153,400 m³/h (45 % of clean). |
| Plant state, spring 2025 (b_eq = 60.5 %, fitted) | Outlet 60.9 °C, duty 3,814 kW (−10.1 %), airflow 54 % of clean. |
| Assumed 30 % blockage (team brief input) | Outlet 41.1 °C (+4.3 K), duty −1.7 %, airflow −17 %, UA −12 %. |
| Capacity at 65 °C outlet, same day | Clean 32,100 Nm³/h. 30 % blocked: 26,900 (−16 %). Spring state: 18,400 (−43 %). End-of-summer state: 15,400 (−52 %). |
| One summer of debris (spring → end of summer, both years) | +8 to +10 points of equivalent blockage. On the reference day that is +14 K outlet and −16 % capacity. |
| Verification | Energy balance closes to < 0.001 %, water balance to < 10⁻⁶ %. Trends are monotonic. The grid is converged (24 vs 48 segments differ by 0.03 K). |
| Hold-out comparison with history | MAE 2.4 K (summer periods) and 3.5 K (spring 2025) on withheld weeks, against 5.6–7.4 K for a constant predictor. Spring 2024 is poor (MAE 8.2 K). |

What this means:
1. **30 % blockage is mild for this exchanger.** At fans 100 % a clean A-1401 has a large reserve, and the outlet only starts to climb steeply above about 45–50 % blockage (Figure 5). Because the effect is non-linear, the 30 % case is not representative of the plant.
2. **The plant behaves like an exchanger with 55–69 % of its air passages blocked.** This "equivalent blockage" is everything the clean model does not explain: debris, louvres, fan wear, recirculation, and any optimism in the model itself. It is not a measured debris coverage.
3. **The part that is clearly debris is the seasonal rise.** It is measured in the data: 55 → 65.5 % in 2024 and 60.5 → 68.5 % in 2025. The constant base of about 55–60 % cannot be attributed with the data available.
4. **Fouling shows up mainly as a hotter outlet and lost capacity, not as lost duty at a fixed flow.** Most of the condensation happens near the hot end, so the latent duty barely changes (−5 %). The cooling that is lost is the sensible cooling of gas and condensate at the cold end.

## 2. Sources and assumptions register

| # | Input | Value | Source | Status |
|---|---|---|---|---|
| S1 | Tubes, rows, passes | 276 tubes, 6 rows, 2 passes | Datasheet/bundle BOM (as transcribed in `AUDIT_report.md`) | Original drawings were not available to this calculation, so they could not be re-checked |
| S2 | Tube OD × wall, material | 25 × 2 mm, S30403 | Datasheet | as S1 |
| S3 | Bare / extended area | 226 / 5,288.4 m² | Datasheet | as S1. The model reproduces 225.9 / 5,289.0 m² |
| S4 | Effective tube length | 10.42 m | Derived: 226 / (π · 0.025 · 276) | Derived (brief says "≈ 10.5 m") |
| S5 | Fans | 3 × 114,000 m³/h, 190 Pa **total**, 477 rpm, Ø 2.4 m, 11 kW | Datasheet | as S1 |
| S6 | Design temperatures | 135 / 55 °C | Datasheet | as S1 |
| S7 | Process pressure | 2.75 MPa abs (2.65 MPa g) | Between datasheet inlet 2.69 MPa g and D-1403 2.56 MPa g | Assumed, small effect |
| S8 | Dry composition | H₂ 74.4, CO₂ 17.9, CH₄ 4.96, CO 2.25, N₂ 0.6 mol % (normalised) | Plant lab medians | The brief's 74.3/17.8/5.0/2.2/0.6 differs by ≤ 0.1 point; the difference is negligible |
| S9 | Water / dry gas | 0.555 mol/mol (base); 0.284 and 0.24 tested | PFD steam balance | **Unverified.** The PFD carbon balance is off by about 2× |
| S10 | Fin geometry | Al, Ø 57 mm, 0.4 mm, 423 fins/m (gap 1.96 mm); 64 mm triangular pitch | Assumed so that S3 is reproduced | **Assumed.** Other fin sizes could also fit S3 |
| S11 | Pass arrangement | Pass 1 = top rows 4–6, pass 2 = bottom rows 1–3 | Assumed (usual counter-crossflow) | Assumed |
| S12 | Fan curve | Generic axial: Δp/Δp_r = 1.6 n² − 0.6 q² | No vendor curve available | **Assumed**, tested (flatter/steeper) |
| S13 | Bundle share of 190 Pa | 0.79 = (190 − 29.4 velocity pressure − 10 inlet) / 190 | Derived | Robinson–Briggs gives 219 Pa for the bundle; see §6.4. Tested 0.65–0.95 |
| S14 | Air-side h | Briggs & Young (1963), ±20 % | Correlation | Tested ±20 % |
| S15 | Tube-side h | Gnielinski gas film + Silver–Bell–Ghaly; condensate film 8,000 W/m²K | Correlation + assumed film | Film tested 4,000–16,000 |
| S16 | Inside fouling | 0.0002 m²K/W | Assumed (TEMA-type) | Small |
| S17 | Historian | `Data (full history).xlsx`, hourly, 14 Nov 2023 – 14 Nov 2026 | Plant | Frozen from 11 Mar 2026 12:00 UTC (§3) |
| S18 | Air temperature | ERA5 2 m, 47.14 N 51.89 E (Open-Meteo) | Reanalysis | Not the fan-inlet temperature; ±2 K tested |
| S19 | Fan speed | `1400TICA0055_mv` / 100 = fraction of 50 Hz | One PI Vision screen: OP 87.6 % vs VFD 87.9 % | Only valid at that screen. The history fits use fans at 100 % only, so this assumption is not needed there |

**Not available to this calculation:** the older `A1401_simulation_package.zip`, the original pasted request, and the Aksel Schmidt drawings and fan documents. Values S1–S6 were taken from the project's own transcription, which was checked against the drawings in an earlier audit. The "13.95 kW/K" of the old package is reconciled in §6.3 from first principles, without its code.

## 3. Historian audit

| Check | Result |
|---|---|
| Rows | 26,126 hourly rows, 14 Nov 2023 15:00 – 14 Nov 2026 09:00 UTC |
| Frozen block | From **11 Mar 2026 12:00 UTC**, all five signals repeat one sample (T_in 168.873, T_out 68.024, OP 79.542 %, PV0017 0.047 %, FI010 19,170) for 5,948 rows. **Excluded.** |
| Usable hours | 19,065 (flow > 12,000 Nm³/h, flare valve output < 1 %, T_in > T_out + 10 K, OP > 30 %, all signals present) |
| Flare open | 266 h excluded (gas may bypass FI010) |
| Hours with fans at 100 % | 7,651 (40 % of usable) |
| Hours used for the fits | 5,637 (usable, fans ≥ 99.5 %, air ≥ 10 °C so that the winter louvres are probably open) |
| Brief's 1 Jan interval | 1 Jan 2026 00:00–02:00 UTC: T_in 144.30 °C, T_out 69.68 °C, FI010 22,610 Nm³/h, OP 53.85 % (confirmed). Air −2.3 °C (ERA5). |

The summer reference window was picked automatically: the steady 4-hour window in Jul–Aug 2025 with fans at 100 %, air between 28 and 32 °C, std(T_in) < 1 K and std(flow) < 400 Nm³/h, closest to the summer medians. The result is **18 Jul 2025, 17:00–20:00 UTC**: T_in 159.4 (std 0.3) °C, T_out 72.9 °C, flow 17,444 (std 51) Nm³/h, PV0017 0 %, air 31.8 °C. All values are averages of the same four hours. No values were mixed from different dates.

Missing variables, for every interval: wet-gas flow, water content, actual air inlet temperature, louvre position, fan current, condensate flow at D-1403.

## 4. Model

### 4.1 Process side: wet syngas (`a1401sim/thermo.py`)

The basis is per mole of dry gas, with the dry flow from FI010 (Nm³ at 0 °C, 1 atm). FI010 sits downstream of the water knock-out, so it measures **dry** gas. The total wet flow at A-1401 is the dry flow × (1 + W).

- Dry gas is an ideal-gas mixture: h_dry(T) = Σ yᵢ ∫ c_p,i⁰ dT (CoolProp ideal-gas c_p).
- Water is the only condensable component. Saturated vapour content is y_w = f · p_sat(T) / P, with f = 1. Vapour n_v = min(W, y_w / (1 − y_w)) and liquid n_l = W − n_v (mol per mol dry gas).
- H(T) = h_dry + n_v · h_v,sat(T) + n_l · h_l,sat(T) (IAPWS-95). The latent heat h_v − h_l is therefore counted once.
- Duty split, exact for every 0.35 K step: Q = dry-gas sensible + vapour sensible + liquid sensible + latent, where latent = moles condensed in the step × (h_v − h_l). The split closes to < 10⁻⁶.

**Inlet VLE check.** With W = 0.555 at 2.75 MPa, the dew point is **179.1 °C**. At the 159.4 °C inlet the gas can hold only 0.284 mol/mol, so 3.8 t/h of liquid water already enters with the gas (that condensed in E-1407/E-1408 upstream; the P&ID marks this line as two-phase). Its sensible cooling is 984 kW in the clean case. If that liquid were knocked out before A-1401, the "just saturated" scenario applies (W = 0.284): duty is 12 % lower, and the conclusions on blockage barely change (§7).

### 4.2 Air side and blockage (`a1401sim/airside.py`)

- Air-side heat transfer: h from Briggs & Young, Nu = 0.134 Re^0.681 Pr^1/3 (s/l)^0.2 (s/t)^0.1134, with Re at the minimum free area (σ = 0.525) and Ø_o. Annular fin efficiency by the Schmidt method (η_f = 0.86 clean). Surface efficiency η_o = 1 − (A_f/A)(1 − η_f).
- **Blockage b** = fraction of air passages closed. Three effects follow from it, each applied once:
  1. Air flows only through the open fraction, so the local velocity is V/(1 − b), which **raises** h. This partly compensates.
  2. Active area = (1 − b) · A (the blocked surface carries no air).
  3. Bundle Δp ∝ [q/(1 − b)]^1.684 (Robinson–Briggs velocity exponent).
- Fan/system intersection: 1.6 n² − 0.6 q² = 0.21 q² + 0.79 [q/(1 − b)]^1.684, with q = airflow / 342,000 m³/h. Air density cancels out. So **30 % blocked area gives 17 % less air**, not 30 %.
- UA_air = h · η_o · A · (1 − b).

### 4.3 Tube side and wall

The gas film coefficient comes from Gnielinski, with Wilke / Mason–Saxena mixture properties from CoolProp pure components (CO approximated by N₂). Condensation in the presence of hydrogen uses Silver–Bell–Ghaly: 1/h_i = 1/h_film + Z/h_gas, where Z = (gas sensible dQ)/(total dQ) at the local temperature. The wall is R = ln(D_o/D_i)/(2π k L), with k = 16 W/mK.

In the clean case, the resistance shares are air 48 %, tube side 46 % and wall 6 %. At end-of-summer fouling they are air 73 %, tube side 23 % and wall 4 %.

### 4.4 Segmented crossflow rating (`a1401sim/exchanger.py`)

The bundle is modelled as 6 rows × 24 segments. Pass 1 runs along +x in rows 4–6, a header mixes it, and pass 2 runs along −x in rows 1–3. Each cell exchanges heat with the air column crossing it:

Q_cell = C_air,cell [1 − exp(−UA_cell / C_air,cell)] (T_p − T_air,in), with a predictor–corrector on the cell-midpoint process temperature.

Process enthalpy is carried along each tube, and T = H⁻¹(H) by table lookup, so condensation is included automatically. Air temperatures are updated row by row (bottom to top) and the whole field is iterated (under-relaxed) until the outlet changes by less than 0.001 K. This takes 15–20 iterations and about 0.03 s per case.

"Effective UA" in the tables is the physical series conductance at the mean process temperature. The "apparent UA" = Q/LMTD (counterflow) is shown only for comparison with hand methods. It is not the same quantity for a condensing stream.

## 5. Results at the summer reference window

### 5.1 Comparison table (`results/clean_vs_fouled_table.csv`)

All four cases use the same inlet (159.4 °C, 17,444 Nm³/h dry, W = 0.555), the same air (31.8 °C) and fans at 100 %.

| Parameter | A Clean | B 30 % (assumed) | C Spring 2025 (b = 60.5 %) | D End of summer 2025 (b = 68.5 %) | D − A |
|---|---|---|---|---|---|
| Air volumetric flow, m³/h | 342,000 | 282,662 | 186,201 | 153,415 | −188,585 |
| Air mass flow, kg/s | 110.4 | 91.2 | 60.1 | 49.5 | −60.9 |
| Effective UA, kW/K | 106.5 | 93.8 | 71.4 | 62.5 | −44.0 |
| Total heat duty, kW | 4,242 | 4,169 | 3,814 | 3,529 | −714 |
| Sensible duty, kW | 1,864 | 1,796 | 1,485 | 1,261 | −603 |
| Condensation (latent) duty, kW | 2,378 | 2,373 | 2,329 | 2,268 | −110 |
| Syngas inlet, °C | 159.4 | 159.4 | 159.4 | 159.4 | 0 |
| Syngas outlet, °C | 36.7 | 41.1 | 60.9 | 75.2 | +38.4 |
| Air inlet, °C | 31.8 | 31.8 | 31.8 | 31.8 | 0 |
| Air outlet (mixed), °C | 70.0 | 77.2 | 94.9 | 102.6 | +32.6 |
| Water condensed in A-1401, kg/h | 3,949 | 3,941 | 3,874 | 3,780 | −169 |
| Duty loss vs clean, % | 0 | 1.7 | 10.1 | 16.8 | |
| UA loss vs clean, % | 0 | 11.9 | 32.9 | 41.3 | |
| Max dry gas for 65 °C outlet, Nm³/h | 32,122 | 26,869 | 18,400 | 15,438 | −16,684 |
| Capacity loss vs clean, % | 0 | 16.4 | 42.7 | 51.9 | |

Additional detail (`results/clean_vs_fouled_full.csv`):

| Quantity | A | B | C | D |
|---|---|---|---|---|
| Air-side h, W/m²K | 48.9 | 54.5 | 60.0 | 61.1 |
| Velocity in the open passages, m/s | 5.9 | 7.0 | 8.1 | 8.4 |
| Active finned area, m² | 5,289 | 3,702 | 2,089 | 1,666 |
| Fan total pressure, Pa | 190 | 226 | 270 | 281 |
| Fan shaft power each, kW (η = 0.65 assumed) | 9.3 | 9.1 | 7.2 | 6.1 |

Notes:
- Case D is applied at the reference conditions and gives 75.2 °C, against the 72.9 °C measured in that window. Fitted to that window alone, b = 67.4 %. The 2.3 K difference is within the hold-out scatter.
- Water condensed changes little, because 95 % of the vapour has already condensed by 75 °C. The extra vapour leaving in case D (201 kg/h, against 32 kg/h clean) goes on to E-1409/E-1410.
- With the brief's simple approximation (airflow × (1 − b), area unchanged), 30 % gives an outlet of 42.4 °C and a duty of 4,146 kW. That is close to the physical model, which predicts less airflow loss but also loses active area.

### 5.2 Blockage sweep (`results/blockage_sweep.csv`, Figure 5)

| b, % | 0 | 10 | 20 | 30 | 40 | 50 | 60 | 70 |
|---|---|---|---|---|---|---|---|---|
| Airflow, % of rated | 100 | 95 | 89 | 83 | 75 | 66 | 55 | 43 |
| UA, kW/K | 106.5 | 102.9 | 98.8 | 93.8 | 87.9 | 80.8 | 71.9 | 60.6 |
| Duty, kW | 4,242 | 4,227 | 4,204 | 4,169 | 4,112 | 4,013 | 3,827 | 3,455 |
| Outlet, °C | 36.7 | 37.7 | 39.0 | 41.1 | 44.4 | 50.0 | 60.2 | 78.6 |

All trends are monotonic. The curve steepens because the exchanger is "oversized" at this load: in the clean state, the cold end of the bundle has a near-zero temperature difference (outlet only 5 K above the air). Lost surface first eats into that reserve and only then into the duty.

### 5.3 1 January 2026 interval (team brief; `results/clean_vs_fouled_1jan2026.csv`)

Conditions: inlet 144.3 °C, 22,610 Nm³/h, air −2.3 °C, OP 53.85 % (treated as 54 % fan speed). Clean: 18.7 °C. 30 %: 32.0 °C. Spring state: 68.6 °C. End-of-summer state: 84.2 °C. Measured: 69.7 °C. The equivalent blockage is 61 %.

This interval is **not used for calibration**. In winter, louvre position and fan-speed mapping are unknown, and a clean outlet of 19 °C would risk freezing. That is why the plant throttles the fans, so this point says little about fouling.

## 6. Verification and design consistency

### 6.1 Numerical checks (`results/results.json` → `verification`, `tests/test_model.py`)

| Check | Result | Pass |
|---|---|---|
| A. Energy: process ΔH = Σ cell Q = air gain = ΔH from outlet temperature = sum of duty parts | max deviation 0.0000 % in all four cases | yes |
| B. Water: water in = vapour out + liquid out; condensed = vapour in − vapour out | 0.000000 % | yes |
| B. Dry gas | carried unchanged (no reaction; gas solubility in condensate neglected) | yes |
| C. Limits: T_air,in < T_out < T_in; T_air,out < T_in; Q < Q_max (cool to air inlet); converged | all true | yes |
| C. Trends with b: airflow ↓, UA ↓, duty ↓, outlet ↑ | monotonic 0–70 % | yes |
| D. Grid: outlet at b = 50 % with 6/12/24/48 segments | 50.68 / 50.13 / 50.01 / 49.99 °C | yes |
| Unit tests (7) | `python tests/test_model.py` | 7/7 pass |

An energy balance that closes shows the model is internally consistent. It does not show the model agrees with the plant.

### 6.2 Independent property-package check (in place of DWSIM)

**DWSIM was not executed.** This calculation ran in a Linux cloud container and a Linux VM on the user's laptop; neither has DWSIM or its automation interface installed. No DWSIM file was produced.

As an independent thermodynamic check, the same inlet and outlet states were flashed with the **Peng–Robinson EOS** (Caleb Bell's `thermo` library, ChemSep binary interaction parameters), 159.4 → 36.7 °C at 2.75 MPa:

| | This model (ideal gas + Raoult) | Peng–Robinson flash | Difference |
|---|---|---|---|
| Water vapour at inlet, mol/mol dry | 0.284 | 0.310 | +9 % |
| Water vapour at outlet, mol/mol dry | 0.00226 | 0.00233 | +3 % |
| ΔH, J/mol dry gas | 19,624 | 21,359 | **+8.8 %** |

PR predicts more water in the vapour at 27 bar (an enhancement factor of about 1.09, against about 1.03 usually quoted for H₂–H₂O at this pressure). PR is also not well validated for liquid-water enthalpy. So the property uncertainty on duty is about **±5–9 %**. It affects clean and fouled cases alike: in the sensitivity, f = 1.03 shifts b_eq by −0.9 points.

To repeat the check in DWSIM: build a material stream with the dry composition above plus water at W = 0.555 (mole fractions ÷ 1.555), 2.75 MPa, 159.4 °C and 17,444 Nm³/h dry (= 216.4 kmol/h dry, 336.5 kmol/h total). Pass it through a Cooler to 36.7 °C (clean) and 75.2 °C (case D) with Peng–Robinson (or SRK). Compare the duty and vapour fraction with Table 5.1. A plain DWSIM cooler needs the outlet temperature or duty as an input, so it cannot predict fouling. It only checks the enthalpies.

### 6.3 Design consistency and the 13.95 vs 119 kW/K question

- **Design point** (135 → 55 °C at 100 % load = 20,588/0.584 = 35,262 Nm³/h dry, fans 100 %): a clean exchanger meets it exactly with air at **35.1 °C**. The design air temperature is not on the datasheet, so this is a consistency check, not a validation. With 35 °C air the clean model gives 54.9 °C.
- **UA reconciliation** (design temperatures, 35 °C air, rated airflow, counterflow LMTD):

| Way of getting UA | kW/K |
|---|---|
| Dry-gas-only duty (ṁ c_p ΔT, no water) at PFD flow 20,588 Nm³/h: Q = 644 kW | **13.5** |
| Same, at 100 % load flow: Q = 1,104 kW | 23.7 |
| Full wet duty at 100 % load (Q = 4,654 kW) | 131 |
| From geometry and correlations, clean (this model, design point) | **119** |
| Air side alone, clean | 222 |

The old 13.95 kW/K is what you get by dividing a **dry-gas-only** duty at the 58 % load PFD flow by an LMTD. It omits water condensation and liquid cooling, which are about 75 % of the duty at these temperatures, so it underestimates UA by about 9×. The 119 kW/K comes from the exchanger geometry. A UA back-calculated from the full wet duty at design (131 kW/K) agrees with it to 10 %, and that agreement is the reconciliation. **13.95 kW/K should not be used.**

### 6.4 Fan and pressure-drop consistency

At rated flow, Robinson–Briggs with the assumed fin geometry gives a bundle Δp of **219 Pa**, against at most about 150 Pa available (190 Pa total minus 29 Pa velocity pressure and about 10 Pa inlet losses). Either the real fins are less dense or thicker than assumed, or the correlation over-predicts for this geometry by about 30 %. It does not affect the clean thermal results. It only affects how airflow responds to blockage, which is covered by the bundle-share sensitivity (0.65–0.95 moves b_eq by ±2.5 points). The fan shaft power of 9.3 kW (at an assumed η = 0.65) is below the 11 kW motor rating. That is consistent, but not an independent check.

### 6.5 Comparison with historian data (Figure 8, `results/history_periods_calibration_validation.csv`)

Method: for each period, one blockage value b is fitted by least squares to the hours in **even ISO weeks** (calibration). The model then predicts the outlet for every hour in the **odd weeks** (withheld), using the measured T_in, flow and ERA5 air. Hours used: fans ≥ 99.5 %, air ≥ 10 °C, flare closed.

| Period | Cal. / withheld h | b fitted | MAE withheld, K | Bias, K | MAE constant predictor, K | MAE clean model, K |
|---|---|---|---|---|---|---|
| Spring 2024 (1 Apr–15 May) | 215 / 76 | 0.550 | 8.2 | +3.3 | 5.6 | 37.1 |
| End of summer 2024 (1 Aug–15 Sep) | 278 / 275 | 0.655 | **2.4** | +1.7 | 6.7 | 34.5 |
| Spring 2025 (1 Apr–15 May) | 204 / 190 | 0.605 | 3.5 | −2.6 | 5.6 | 40.6 |
| End of summer 2025 (1 Aug–15 Sep) | 449 / 362 | 0.685 | **2.4** | +1.2 | 7.4 | 40.1 |

What this shows:
- With one fixed b per period, the model reproduces how the outlet responds to changes in air temperature, flow and inlet temperature within 2.4–3.5 K, in three of the four periods. That is 2–3× better than a constant.
- Spring 2024 is the exception. It ran at 31,900 Nm³/h, 70 % more gas than the summers, and blockage was changing within the period (Figure 8a). The model is worse than a constant there, so its flow sensitivity is not fully confirmed at high load.
- **Without blockage the model is 35–41 K too cold.** Clean-model predictions are shown for scale. They are not a test of anything.
- This shows the model reproduces the measured outlets. It does not show the exchanger is 55–69 % blocked by debris (see §1, point 2).

## 7. Sensitivity (one at a time, summer reference window; `results/sensitivity.csv`, Figure 7)

For each assumption, the clean case is re-run and b is re-fitted to the same measured window (72.9 °C).

| Assumption changed | Clean outlet, °C | Clean duty, kW | b_eq fitted | Duty loss, actual vs clean | Airflow, actual |
|---|---|---|---|---|---|
| Base case | 36.7 | 4,242 | 67 % | 15.7 % | 46 % |
| W = 0.24 (carbon-balance case) | 33.5 | 3,287 | 75 % | 15.8 % | 36 % |
| W = 0.284 (saturated inlet, no free liquid) | 34.1 | 3,727 | 72 % | 14.5 % | 40 % |
| Enhancement factor 1.03 | 37.0 | 4,327 | 67 % | 15.4 % | 47 % |
| Air-side h −20 % | 38.7 | 4,210 | 63 % | 15.1 % | 51 % |
| Air-side h +20 % | 35.7 | 4,261 | 70 % | 16.1 % | 43 % |
| Condensate film 4,000 / 16,000 W/m²K | 38.0 / 36.2 | 4,221 / 4,252 | 66 / 68 % | 15.3 / 15.9 % | 48 / 46 % |
| Air +2 K / −2 K | 38.9 / 34.6 | 4,206 / 4,278 | 66 / 69 % | 15.0 / 16.4 % | 48 / 45 % |
| Gas flow +10 % (FI010 reads low) | 38.9 | 4,627 | 63 % | 15.0 % | 51 % |
| Gas flow +25 % | 42.8 | 5,173 | 56 % | 13.6 % | 59 % |
| Bundle share 0.65 / 0.95 | 36.7 | 4,242 | 70 / 65 % | 15.7 % | 47 / 45 % |
| Fan curve flatter / steeper | 36.7 | 4,242 | 65 / 70 % | 15.7 % | 45 / 47 % |

Measurement uncertainty here comes from the FI010 flow, the ERA5 air temperature and the transmitter accuracy of T_in/T_out (not given, typically ±1 K). Model-assumption uncertainty comes from W, h_air, the condensate film, the fan curve and the bundle share. The largest single effects are **gas flow** (b_eq −11 points if FI010 reads 25 % low) and **water content** (+8 points). In every case the actual exchanger is at 56–75 % equivalent blockage and moves 36–59 % of the clean airflow. The duty loss at fixed flow is 14–16 % in all cases.

## 8. Limitations

1. Equivalent blockage lumps together debris, louvre closure, fan or belt wear, recirculation and model error. Only an inspection of a freshly cleaned bundle can split them.
2. Uniform blockage is assumed over the face. Real debris sits under row 1 and may be patchy, and patchy blockage behaves differently from uniform blockage.
3. No vendor fan curve and no fin drawing: S10–S13 are assumptions.
4. Water content (S9) is not measured. The D-1403 condensate flow would settle it.
5. Steady state only. No fouling growth, no cleaning model, no economics (out of scope).
6. Two-phase pressure drop and header maldistribution are neglected. Process pressure is constant.
7. DWSIM was not run (§6.2).

## 9. Differences from the earlier project model (`model/a1401_model.py`)

| Item | Earlier | Now | Effect |
|---|---|---|---|
| Rating method | Zone method along the cooling curve, counterflow with F = 0.95 | 6-row × 24-segment crossflow, 2 passes, row-by-row air heating | Arrangement represented explicitly; no F-factor |
| Blockage Δp | (1 − b)^−1.684 multiplying a q² system curve | Bundle Δp ∝ [q/(1−b)]^1.684, with the other losses ∝ q² | Consistent exponent; slightly more air at a given b |
| Bundle share of 190 Pa | 0.75 assumed | 0.79 derived from velocity pressure; Robinson–Briggs cross-check reported | Small |
| Gas transport properties | Linear blend of rough constants | Wilke / Mason–Saxena from CoolProp pure components | Tube-side h about 10 % lower; clean UA 119 → 106 kW/K at summer conditions (119 at design) |
| Duty split | Mean latent heat between end points | Exact stepwise split into 4 parts | Liquid sensible now shown separately |
| History | Every hour, all fan speeds | Fans 100 % and air ≥ 10 °C only; hold-out by alternate weeks | Removes fan-mapping and louvre ambiguity |
| Equivalent blockage, summer 2025 | 72 % | 68.5 % | Mostly from the new Δp form |

The earlier package `A1401_simulation_package.zip` (13.95 kW/K, dry c_p) was not available. Its UA is explained in §6.3.

## 10. Acceptance criteria (brief §14)

| Criterion | Status | Evidence |
|---|---|---|
| Program runs and produces numerical results | Pass | `run_all.py`, `results/`, `results/run_log.txt` |
| Syngas = process stream (tubes), air = cooling stream | Pass | §4, Figure 0; no water cooling medium anywhere |
| Wet-syngas enthalpy and condensation treated explicitly | Pass | §4.1; latent, vapour, liquid and dry-gas terms reported separately |
| Actual A-1401 geometry and operating data drive the calculation | Pass | S1–S6 and a real historian window. Fin details are assumed (S10) |
| Clean and fouled cases use identical conditions | Pass | §5.1 |
| 30 % is an input assumption, not an observation | Pass | Case B labelled as assumed; the plant states are fitted, and the fit is described as including model offset |
| Airflow and UA changes have a physical explanation | Pass | Fan/system intersection; area × (1 − b); h at local velocity; no double counting (§4.2) |
| Energy and material balances close | Pass | §6.1 |
| Checked against independent design or historical evidence | Partial pass | Design point consistent at 35 °C air (design air temperature unknown); hold-out history MAE 2.4–3.5 K in 3 of 4 periods, 8.2 K in spring 2024 |
| Major uncertainties quantified or disclosed | Pass | §7, §8; PR property check ±9 % |
| Graphs generated from the executed model | Pass | `figures.py` called by `run_all.py` |
| Reproducible by another student | Pass | README; pinned inputs in `data/`; about 10 min run |
| DWSIM (optional, "if available") | Not done | Not executable in this environment; reproduction steps in §6.2 |

## 11. Figures

| File | Content |
|---|---|
| `fig0_A1401_schematic.png` | Stream arrangement |
| `fig1_duty.png` | Total duty, cases A–D |
| `fig2_outlet_T.png` | Syngas outlet temperature, A–D |
| `fig3_airflow.png` | Airflow, A–D |
| `fig4_UA.png` | Effective UA, A–D |
| `fig5_duty_vs_blockage.png` | Duty and outlet vs blockage 0–70 % |
| `fig6_duty_split.png` | Sensible vs condensation duty |
| `fig7_sensitivity.png` | One-at-a-time sensitivity |
| `fig8_history_comparison.png` | Equivalent blockage history; withheld measured vs predicted |
