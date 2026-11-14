# A-1401 Syngas Air Cooler: Fouling Case Solution Plan

Air Liquide case, AIChE SC, 14–15 Nov 2026
Plan written 14 Nov 2026, ~15:00 Atyrau time (UTC+5)

---

## Start here: the problem and our solution in plain language

*Written for team members who are not engineers. The rest of the plan is the detailed version.*

### What is going on at the plant?

The plant in Atyrau makes **hydrogen**. Natural gas reacts with steam at high temperature (steam reforming, CH₄ + H₂O → CO + 3H₂). The CO then reacts with more steam to make extra hydrogen (water‑gas shift, CO + H₂O → CO₂ + H₂). What comes out is a hot mixture called **syngas**: about 74 % H₂, 18 % CO₂, a little CH₄ and CO, plus a lot of **water vapour** left over from the steam.

Before the hydrogen can be purified, this gas has to be **cooled** from about 140–170 °C down to about 65 °C. As it cools, the water vapour **condenses into liquid water**, just like steam fogging up a cold mirror. Condensation releases a lot of heat (latent heat of vaporisation, ~2,260 kJ/kg for water), so most of the heat the cooler has to remove comes from condensing water, not from simply cooling the gas.

### What is the "air cooler" A‑1401?

Think of a **car radiator, but the size of a small house**. The hot gas flows inside ~270 steel tubes. Each tube is covered with thousands of thin aluminium **fins** (like the thin plates on a radiator) to give it more surface area: 23 times more than the bare tube. Three big **fans** (2.4 m diameter) push outside air across the fins. Heat moves from the hot gas → through the tube wall → into the fins → into the air, which carries it away.

The fans have a "speed knob" (a **VFD**, variable frequency drive). A controller turns the fans faster when the gas comes out too hot and slower when it is cold enough.

### What is the problem?

The gaps between fins are only about **2 mm** wide. Every spring and summer, **poplar fluff, pollen, insects and dust** get sucked in by the fans and stuck in those gaps, like lint in a tumble‑dryer filter. This does two bad things:

1. **Less air gets through** ("airflow choking"). The blanket of debris resists the air, so the same fans move less air.
2. **The debris insulates the fins.** A layer of fluff is a poor heat conductor, so heat moves more slowly from fin to air.

Together these reduce the **heat transfer coefficient**, a number that says how easily heat moves from the gas to the air (units W per m² per °C; higher is better). On hot summer days the air is already warm, so the cooler has less "temperature difference" to work with. Once it is also clogged, even fans at full speed can't cool the gas enough. Then the plant has to **reduce production** of hydrogen, and that costs money.

### What does Air Liquide want from us?

1. **Diagnose:** how much air and how much cooling is lost because of the debris?
2. **Model:** a calculation (Excel or Python) that predicts cooler performance clean vs dirty.
3. **Monitor:** a tool that watches plant data and warns *"the cooler is getting dirty"* before it becomes a problem.
4. **Fix:** at least two practical solutions to stop or remove the debris, comparing pros, cons and safety.
5. **Money:** what each solution costs, how long it takes to get, and how fast it pays back.

### How we will solve it, in 6 steps

| Step | In plain words | Chemistry you already know that it uses |
|---|---|---|
| 1. Collect facts | Read the equipment drawings and the plant temperature/flow data; get the Atyrau weather. | – |
| 2. How much heat must be removed? | Work out how much heat leaves the gas when it cools from ~150 °C to 65 °C, including the water that condenses. | q = m·Cp·ΔT for cooling; m·ΔH_vap for condensing; Dalton's law / vapour pressure for when water starts condensing (dew point) |
| 3. Model the clean cooler | Calculate how much heat the clean cooler can pass to the air at a given air temperature and fan speed. | Heat flow = U × A × ΔT (like Newton's law of cooling); ideal gas law for air density |
| 4. Model the dirty cooler | Add a "debris blanket" to the model: less air, plus extra insulation. See how much cooling is lost, and on how many hot days per year production must be cut. | Same equations, with a smaller U and less airflow |
| 5. Build the warning tool | Each hour, compare what the cooler *actually* does with what a *clean* cooler would do. The ratio (the **cleanliness factor**, 100 % = clean) falling over time = fouling. | Like comparing an experimental yield with a theoretical yield |
| 6. Propose fixes and cost them | e.g. removable insect/pollen screens in season, an automatic air/water cleaning system, and adjusting the fan blades to push more air. Calculate cooling recovered, cost and payback. | Corrosion chemistry: chloride ions in wash water can crack stainless steel (stress‑corrosion cracking), so we must use demineralised water |

### Why we have to make assumptions

The plant data we were given covers only **a few hours to a few days in January**, even though the files say January–November. We have no summer data, no outside‑air temperature from the plant, and no fan performance curve. So, like in a lab report when a value is missing, we use **reasonable, clearly stated assumptions**, explain why each is reasonable, and show how much the answer changes if each assumption is a bit off. This is a **sensitivity analysis**. Section 8 lists them all.

### Word list

| Term | Meaning |
|---|---|
| Fouling | Dirt building up on a heat‑transfer surface |
| Duty | Amount of heat removed per unit time (kW or MW) |
| Heat transfer coefficient (U) | How easily heat passes from hot fluid to cold fluid, W/(m²·°C) |
| Fin efficiency | How well the fin tips do compared with the fin base. The tips are cooler, so they transfer less heat |
| Static pressure | The "push" a fan gives to force air through the fins, in pascals (Pa) |
| Fan curve | A graph of how much air a fan moves vs how much resistance it faces |
| Approach temperature | Gas outlet temperature minus outside air temperature: how close the cooler gets the gas to air temperature |
| Dew point | Temperature at which water vapour in the gas starts condensing |
| Debottlenecking | Removing the limit that stops the plant producing more |
| CAPEX / OPEX | One‑time purchase cost / yearly running cost |
| Payback | How many years until savings equal the purchase cost |
| PI data / tags | The plant's sensor history. A tag like TIA050 is one sensor (T = temperature, F = flow, P = pressure) |
| Backtest | Running our warning tool on past data to check whether it would have caught the problem |

---

## 0. What the case asks for

**Problem.** A-1401 is the forced/induced‑draft fin‑fan cooler that cools shifted syngas (MT shift outlet, via E‑1407 / E‑1408) before E‑1409 and separator D‑1403 → PSA M‑1405 (UPOV‑2 hydrogen unit, Atyrau). Organic debris (cottonwood fluff, pollen, insects, dust) blankets the fin gaps. Airflow drops and the air‑side coefficient drops, so in hot weather the cooler becomes the plant bottleneck.

**Deliverables (presentation):**
1. Thermal impact diagnosis: airflow choking + loss of effective U.
2. Solution comparison matrix: at least 2 solutions; pros/cons, quantified side effects, safety, material integrity.
3. Engineering / thermal model: clean vs fouled performance + duty recovered by each solution.
4. (Implied by scoring) Performance monitoring model backtested on historical data.
5. (Implied by scoring) CAPEX / OPEX, lead time, payback from debottlenecking.

**Scoring weights → where time goes:**

| Criterion | Weight | Plan phases |
|---|---|---|
| Technical accuracy (fin efficiency, air‑side h, fan curves, air mass balance) | 25 % | C, D |
| Solution practicality & innovation (organic debris) | 20 % | F |
| Problem & impact analysis (airflow restriction, thermal penalty) | 20 % | D |
| Performance monitoring model + backtest | 20 % | E |
| Economics & lead time | 15 % | G |

---

## 1. What we have (inventory, read 14 Nov)

Case files are in `~/catalyst/drive-download-…/` and `~/catalyst/AIChE SC November 14 & 15 2026.pdf`.

| File | What it gives us | Use |
|---|---|---|
| AIChE SC … .pdf | Case brief, deliverables, scoring | Scope |
| PFD.png / PFD.pdf | UPOV‑2 at 58.4 % load; syngas 20,588 Nm³/h to PSA‑1; H₂ export 12,200 Nm³/h @ 99.836 % | Production basis for economics |
| PID_A-1401.pdf | A‑1401 between E‑1408 (condensate preheater) and E‑1409; two‑phase flow; TT0055 → TY0055A/B/C fan VFDs; steam heating coil; design 33 kg/cm², 170 °C | Instrument map, control logic |
| 01.1.01 General drawing (GA) | **Full datasheet** (below) | Design basis |
| 01.1.1 Bundle, 01.1.6 Heating row | Tube layout, fin geometry | Geometry for model (still to read in detail) |
| 3.1 / 3.2 / 3.3 passports & certificates | Materials, hydrotest | Integrity / material constraints |
| Акт техосвидетельствования (16.10.2025) | Hydrotest 7.1 MPa passed; condition "satisfactory"; fit for service | Integrity baseline |
| DATA – FI010 | Dry syngas flow to M‑1405, Nm³/h | Process flow |
| DATA – TIA026 | Syngas out of E‑1407 (BFW preheater) | Upstream temp |
| DATA – TIA050 | Syngas **into A‑1401** | T_in |
| DATA – TICA0055 | A‑1401 outlet controlled temperature (fan controller PV) | T_out |
| DATA – TIA0059 | Syngas after A‑1401 / at E‑1409 | Downstream temp |
| DATA – PICA0017 | D‑1403 outlet pressure, MPa(g) | Pressure |
| DATA – TY0055A/B/C | Fan output % (VFD) | Airflow proxy |
| DATA – Syngas lab D‑1403 | Dry composition, Jan–Nov 2026, ~2×/week | Gas properties |

**Design datasheet extracted from the GA drawing:**

| Item | Value |
|---|---|
| Bundle type | GP10.5×3‑6‑226‑4.0SF‑23.4/DR‑IIa → 10.5 m × 3 m, **6 rows**, 2 tube passes |
| Bare / finned area | 226 m² / 5,288.4 m² (fin ratio 23.4) |
| Tubes | Ø25 × 2.0 mm, S30403 (304L), rolled (DR) fins, strength‑welded + expanded |
| Design / operating | 4.0 MPa, 170 °C / 2.69 MPa(g), **135 → 55 °C** |
| Fans | 3 × G‑ZFS24L4‑Vs11, Ø2,400 mm, 477 rpm, 4 blades at 9°, **114,000 m³/h and 190 Pa each** |
| Motors | 3 × 11 kW, YBBP‑160M‑4W, Ex d IIC T4, VFD 25–50 Hz |
| Steam heating row | Ø25×2.5 carbon steel, 21.3 m² bare / 498.4 m² finned (winterisation) |
| Louvres | Manual, SC10.5×3 |
| Volume | 1,088 L tube side |

**Quick derived numbers (to be verified in step C1):** face area ≈ 31.5 m²; total design air ≈ 342,000 m³/h ≈ 95 m³/s ≈ 110 kg/s; face velocity ≈ 3.0 m/s; ≈ 274 tubes (≈ 46 per row).

**Data snapshot (1 Jan 2026):** flow ≈ 22,860 Nm³/h, T_in ≈ 143 °C, A‑1401 outlet ≈ 70 °C, after E‑1409 ≈ 58 °C, P ≈ 2.55 MPa(g), all three fans at the same output ≈ 42–57 %.

**Second snapshot (PI Vision screenshot, 14 Nov 2026 15:16):** flow FI010 ≈ 20,800 Nm³/h, **T_in TIA050 = 166.8 °C**, A‑1401 outlet TICA0055 = 66.4 °C (set point 65.0 °C), controller output 87.6 %, all fans 87.9 %, after E‑1409 TI0059 = 56.3 °C, after E‑1410 (cooling water) TI0083 = 38.8 °C, D‑1403 pressure 2.56 MPa. Flow order confirmed: E‑1408 → **A‑1401** → E‑1409 → E‑1410 → D‑1403 → PSA.

Two things stand out:
- At +6 °C ambient the fans already run at 88 %, while on 1 Jan at −3 °C they ran at ~50 %. Part of that is the hotter inlet. The rest is lost air‑side performance, and step D3 will split the two.
- The inlet is now 167 °C, 32 K above the datasheet inlet (135 °C) and only 3 K below the design temperature (170 °C). That is an integrity point for the presentation, and it suggests E‑1408 upstream is also under‑performing.

---

## 2. Data gaps to close in the first hour (blocking)

1. **The PI exports are truncated.** Every file is titled 01.01–13.11.2026 but holds only 3,600 rows from **1 January** (2.5 h for FI010, 8 h for TICA0055, ~1 day for fans/pressure, 7.5 days for TIA026). There is no summer data, so no fouling season to backtest. **Ask the organisers today** for a re‑export with PI DataLink "Sampled Data" at a 1‑hour interval, 01.01–13.11.2026 (~7,500 rows per tag). Also ask for: ambient temperature tag, fan motor current (A), any air‑side ΔP, cleaning/wash dates, and the date of the last turnaround.
2. **No ambient temperature tag.** Solved with Open‑Meteo ERA5 reanalysis for Atyrau (see A8 in §8). Note: the CSV currently in `catalyst` (`open-meteo-47.98N68.02E383m`) is for **48 °N 68 °E, 383 m**, which is in the Ulytau region about 1,200 km east of Atyrau. Re‑run `atyrau.txt` with `latitude = 47.12`, `longitude = 51.92`.
3. **Water content of the syngas.** The lab gives dry gas after D‑1403. Wet inlet composition must be rebuilt (step B1).
4. **Fan curve.** Only the design point is known. Ask for the vendor curve; fallback is a typical axial‑fan curve scaled through 114,000 m³/h @ 190 Pa with fan laws.
5. **TY0055C sheet** contains A, B and C rows stacked, and all three fans carry identical values (one common controller output). Treat as one signal.
6. **Tag meaning check.** TICA0055 (~70 °C) is the A‑1401 outlet controller PV; TIA0059 (~58 °C) is downstream at E‑1409. Confirm with organisers; this decides which one is T_out.
7. Confirm forced vs induced draft from the GA (fan position), because it decides where screens can go.

If the re‑export does not arrive by tomorrow morning, the backtest runs on the January data plus a **simulated fouling year** (real weather + model + an assumed debris build‑up curve), and the slide states that clearly.

---

## 3. Step‑by‑step plan with time estimates

Times are **person‑hours** (team work) and **compute time** (how long the calculation itself runs on a laptop). Team of 4 assumed: P = process/thermo, H = heat‑transfer model, D = data/monitoring, E = solutions/economics.

### Phase A. Data intake and design basis (≈ 3.5 person‑h, wall‑clock ~1.5 h)

| # | Step | Method / skill from `hackathonIndustry` | Who | Person‑h | Compute |
|---|---|---|---|---|---|
| A1 | Send data request (gap list in §2) | email/WhatsApp to organisers | E | 0.25 | – |
| A2 | Atyrau hourly weather: re‑run `atyrau.txt` with lat 47.12, lon 51.92 (the current CSV is for the wrong site) | Open‑Meteo archive | D | 0.1 | < 30 s |
| A3 | Load, align and clean PI tags; resample to 1 min and 1 h; flag flatlines, spikes, shutdowns (flow < 30 % of normal) | **data-quality-auditor** (`data_profiler.py`, `missing_value_analyzer.py`, `outlier_detector.py`) | D | 1.0 | < 10 s now; ~1 min on full‑year data |
| A4 | Read bundle (0010) and heating‑row (0060) drawings: fin OD, fin pitch (fpi), fin thickness, fin material, transverse/longitudinal pitch, tubes per row, passes | manual read of PDFs | H | 1.0 | – |
| A5 | Write one "design basis" sheet (datasheet + geometry + process data) shared by all models | Excel / YAML | H | 1.0 | – |

### Phase B. Process side: what the cooler has to remove (≈ 4 person‑h)

| # | Step | Method | Who | Person‑h | Compute |
|---|---|---|---|---|---|
| B0 | True syngas flow from H₂ and carbon balances, because FI010 under‑reads when gas is flared (see §9) | balance in Excel | P | 1.0 | < 1 s |
| B1 | Rebuild wet syngas at A‑1401 inlet: dry composition (lab average + range) + water. Water from a steam balance (14,526 + 968 kg/h steam in, minus H₂O consumed in reforming + shift) and cross‑check by dew point | mass balance in Python/Excel | P | 1.5 | < 1 s |
| B2 | Condensation curve Q(T) from ~145 °C to ~40 °C at 2.6 MPa: dew point, vapour fraction, enthalpy vs T (Peng‑Robinson) | HYSYS if licensed; else Python `thermo`/CoolProp flash sweep | P | 1.5 | HYSYS: seconds; Python: ~10–30 s for 100 points |
| B3 | Duty time series Q(t) = ṁ·Δh(T_in, T_out) using FI010, TIA050, TICA0055 | vectorised lookup on the B2 curve | P | 0.5 | < 5 s |
| B4 | Sanity check: design duty at 135 → 55 °C vs measured duty | – | P | 0.5 | – |

Key point for the model: most of the duty is **latent heat of water condensing** (P&ID marks two‑phase flow). A gas‑only model will understate duty badly.

### Phase C. Clean thermal + air‑side model (≈ 7 person‑h, critical path)

| # | Step | Method | Who | Person‑h | Compute |
|---|---|---|---|---|---|
| C1 | Geometry: free‑flow area, minimum flow area, fin area per metre, hydraulic diameter, face velocity | API 661 / Kern & Kraus | H | 0.75 | – |
| C2 | Air‑side h: Briggs & Young correlation for helically finned tubes; fin efficiency: annular fin (Schmidt approximation); include fin‑to‑tube bond resistance for rolled fins | Python | H | 1.5 | < 1 s |
| C3 | Air‑side ΔP: Robinson & Briggs (staggered finned bank) + inlet/outlet/screen losses → system curve ΔP = k·V² | Python | H | 0.75 | < 1 s |
| C4 | Fan curve + fan laws (speed ∝ VFD %, air density from ambient T) → operating point = fan curve ∩ system curve; fan power | Python | H | 1.0 | < 1 s |
| C5 | Tube side: condensing h (Shah or Boyko–Kruzhilin with non‑condensable correction for H₂‑rich gas) + Gnielinski for gas sensible part; 2 passes | Python | P | 1.5 | < 1 s |
| C6 | Rating: row‑by‑row / segment‑by‑segment ε‑NTU (cross‑flow, both unmixed) marching along the condensation curve | Python (**zero-hallucination-coder** discipline: unit tests on each correlation against a textbook example) | H | 1.0 | ~0.1–0.5 s per case |
| C7 | Calibrate the clean model to the datasheet point (135 → 55 °C, 3 fans at 100 %) and to the cleanest real data | least‑squares on one correction factor | H | 0.5 | < 10 s |
| C8 (optional) | Cross‑check in Aspen EDR (ACOL) if a licence is available | EDR | P | 2.0 | seconds per run |

### Phase D. Fouled model: airflow choking + thermal penalty (≈ 5 person‑h)

| # | Step | Method | Who | Person‑h | Compute |
|---|---|---|---|---|---|
| D1 | Model the debris layer with two parameters: blocked fraction of fin gaps φ (raises system curve k → less air) and debris thermal resistance R_d,air (insulating mat on fins, also cuts fin efficiency) | extend C3, C2 | H | 1.0 | – |
| D2 | Sweep φ = 0–70 %, R_d = 0–0.002 m²K/W, T_amb = −30…+45 °C, fan 25–50 Hz: airflow, ΔP, U_eff, duty, T_out | grid sweep | H | 0.5 | ~10⁴ cases × 0.2 s ≈ **30–60 s** (≈ 5 min if row‑by‑row is fine) |
| D3 | Back‑calculate effective fouling from plant data: for each hour solve for φ (or UA) that reproduces measured T_out | root solve per hour | D | 1.0 | ~8,000 hours × 50 ms ≈ **10 min** on full data |
| D4 | Summer bottleneck: at Atyrau design summer (~40–42 °C, from A2), fans 100 %, find max syngas flow that keeps T_out at its limit, clean vs fouled → **lost H₂ (Nm³/h)** | optimisation over flow | P | 1.0 | < 1 min |
| D5 | Charts: airflow vs φ, U vs φ, duty vs T_amb (clean/fouled), hours per year the cooler limits production | **dataviz** guidance | D | 1.5 | seconds |

### Phase E. Performance monitoring model + backtest (≈ 7 person‑h)

| # | Step | Method | Who | Person‑h | Compute |
|---|---|---|---|---|---|
| E1 | KPIs: Cleanliness Factor CF = UA_actual / UA_clean,model at same conditions; normalised airflow; approach T_out − T_amb; "fan headroom" (100 % − VFD %) | from C + D3 | D | 1.0 | – |
| E2 | Baseline: physics model + data‑driven residual (linear / gradient‑boosting on T_amb, flow, T_in, fan %) trained on a clean period | scikit‑learn | D | 1.5 | training < 1 min |
| E3 | Alarm logic: EWMA / CUSUM on CF; warning and action thresholds; forecast "days until summer bottleneck" from CF trend + weather | **statistical-analyst** (`confidence_interval.py`, `hypothesis_tester.py`), **observability-designer** (`alert_optimizer.py`) | D | 1.5 | < 10 s |
| E4 | Backtest chronologically (train on early months, test later): detection delay vs cottonwood season (May–June), false alarm rate | walk‑forward | D | 1.0 | full year **< 2 min** |
| E5 | Live dashboard prototype (Streamlit) showing CF, airflow, alarm, forecast | Streamlit | D | 2.0 | starts in seconds |

If the full‑year data does not arrive: run E4 on a synthetic year (real weather + model + assumed debris build‑up) and validate E2 on the January data only.

### Phase F. Mitigation solutions + comparison matrix (≈ 6 person‑h)

Evaluate each with the D model: duty recovered, extra ΔP / fan power, water use, side effects, safety, integrity.

| Option | What it is | Main side effects to quantify |
|---|---|---|
| F‑1 Seasonal debris screens | Removable fine stainless/polymer mesh panels (on air inlet), installed for the cottonwood/insect season, cleaned by blow‑down on rotation | Screen ΔP → airflow loss (use C3/C4); screen clogging rate; access at height; wind load |
| F‑2 Online cleaning system | Rail‑mounted traversing nozzle: compressed‑air reverse blow (dry fluff) + low‑pressure **demineralised‑water** wash with mild detergent (sticky pollen/insects) | **Chloride SCC of 304L tubes** if chloride water is used on tubes above ~60 °C; thermal shock on hot rows; freezing in winter; corrosion of fins; water/air consumption |
| F‑3 Fan recovery | Raise blade pitch 9° → 12–14° and/or allow VFD overspeed within motor/fan limits | Motor load vs 11 kW, noise, blade stress, power cost |
| F‑4 Adiabatic pre‑cooling (peak days only) | Mist/pad cooling of inlet air | Wet pollen → mud, scaling, chlorides; water quality needed |
| F‑5 Turnaround redesign | Lower fin density (e.g. 11 → 7–8 fpi) or wider fin pitch bundle | Larger bundle or lower area; long lead time |
| F‑6 Procedure | Planned manual washing before season, guided by the E monitoring model | Labour, downtime risk, LOTO |

| # | Step | Who | Person‑h | Compute |
|---|---|---|---|---|
| F1 | Shortlist and size F‑1, F‑2, F‑3 (min. 2 required; plan to present 3) | E + H | 2.0 | sweeps < 1 min |
| F2 | Safety & integrity review per option: H₂ service (Ex zone, IIC T4), working at height, LOTO on fans, **flammable cottonwood near hot surfaces**, chloride SCC, thermal shock, condensate freezing | E | 1.5 | – |
| F3 | Weighted comparison matrix (viability, duty recovery, side effects, safety, cost, lead time) | E | 1.0 | – |
| F4 | Stress‑test the recommendation (**grill-me** skill as a red team) | all | 0.5 | – |
| F5 | Cleaning SOP / runbook for the chosen option | **runbook-generator** | E | 1.0 | seconds |

### Phase G. Economics and lead time (≈ 3 person‑h)

| # | Step | Method | Who | Person‑h | Compute |
|---|---|---|---|---|---|
| G1 | Value of lost production: lost H₂ Nm³/h (D4) × hours per year above the bottleneck temperature (A2 weather) × H₂ margin (state assumption, e.g. USD/kg) | Excel/Python | E | 1.0 | < 1 s |
| G2 | CAPEX / OPEX per option (screens, cleaning rig, blade pitch change, water, power, labour) + vendor lead time (weeks) | literature/vendor ranges; state assumptions | E | 1.0 | – |
| G3 | Payback, NPV, sensitivity (H₂ price, summer hours, fouling rate) | **financial-analyst** (`dcf_valuation.py`) | E | 1.0 | < 10 s |

### Phase H. Presentation and rehearsal (≈ 6 person‑h)

| # | Step | Who | Person‑h |
|---|---|---|---|
| H0 | Simple process diagram of the cooler section with sensor tags (**pfd-generator** skill) | D | 1.0 |
| H1 | Storyline: problem → diagnosis (numbers) → model → monitoring → solutions → economics → recommendation | all | 0.5 |
| H2 | Build slides (≈ 12–15) with charts from D5, E, F3, G3 | all | 3.0 |
| H3 | Check every number against the model output (**karpathy-coder** / `goal_verifier.py` style check of the code) | H, D | 1.0 |
| H4 | Two dry runs + Q&A prep | all | 1.5 |

---

## 4. Totals

| Phase | Person‑h | Compute (laptop) |
|---|---|---|
| A Data + design basis | 3.5 | ~1 min |
| B Process side | 4.0 | < 1 min (HYSYS: seconds) |
| C Clean model | 7.0 (+2 EDR optional) | seconds |
| D Fouled model | 5.0 | ~1 min sweep; ~10 min full‑year back‑calculation |
| E Monitoring + backtest | 7.0 | ~3–5 min |
| F Solutions | 6.0 | ~1 min |
| G Economics | 3.0 | seconds |
| H Deck + rehearsal | 6.0 | – |
| **Total** | **≈ 41.5 person‑h** | **≈ 15–20 min of computation in total** |

Computation is never the bottleneck. People‑time and the missing full‑year data are.

With 4 people in parallel, the wall‑clock time is **about 12–13 hours**.

---

## 5. Suggested schedule (Atyrau time)

**Saturday 14 Nov**
- 15:00–16:00: A1–A5 (all). Send the data request first.
- 16:00–19:00: P on B1–B4; H on C1–C4; D on A3 cleanup + E1 KPI code; E on F1 shortlist + F2 safety.
- 19:00–22:00: H + P on C5–C7 (clean model calibrated, critical path); D on E2/E3 with January data; E on G1–G2.
- 22:00–23:00: check‑in; freeze the clean model.

**Sunday 15 Nov**
- 08:00–11:00: D1–D5 fouled model and charts; E4 backtest (on real full‑year data if received, otherwise the synthetic year); F1 sizing with the model.
- 11:00–13:00: F3 matrix, G3 payback, E5 dashboard.
- 13:00–16:00: H1–H3 slides and number check.
- 16:00–17:00: H4 dry runs.

Adjust the Sunday block to the real submission deadline.

---

## 6. Critical path and risks

- **Critical path:** B2 condensation curve → C5–C7 calibrated model → D2/D3 → D4 lost H₂ → G1 payback. Start B and C first.
- **Risk 1, truncated data (high):** request the re‑export now; fallback is the synthetic backtest (§2).
- **Risk 2, unknown fan curve (medium):** use a generic curve and show sensitivity ±15 %.
- **Risk 3, water content (medium):** show the result for a range of water contents; the dew point sets most of the duty.
- **Risk 4, fin geometry unreadable on drawings (medium):** use typical API 661 values for 23.4 fin ratio (Ø57 fin OD, ~11 fpi, 0.4 mm Al) and state the assumption.

---

## 7. About the skills in `hackathonIndustry`

The `claude-skills` folder is a general software/data/business skill library; it has no chemical or heat‑transfer skill. The heat‑transfer method above comes from standard references (API 661, Kern & Kraus, Briggs & Young, Robinson & Briggs, Shah). The skills from the folder are used where they fit:

| Skill | Used in |
|---|---|
| data-quality-auditor | A3 PI data cleaning |
| zero-hallucination-coder | C6 model code with tested correlations |
| statistical-analyst | E3 control limits, E4 backtest statistics |
| observability-designer | E3 alarm thresholds, E5 dashboard |
| financial-analyst (`dcf_valuation.py`) | G3 NPV / payback |
| runbook-generator | F5 cleaning SOP |
| grill-me | F4 red‑team the recommendation |
| karpathy-coder | H3 final model and number check |
| dataviz | D5 charts |
| **pfd-generator** (from `claude-manufacturing-skills`, added 14 Nov) | New step **H0**: draw a clean, simple diagram of our part of the plant (E‑1408 → A‑1401 with its 3 fans → E‑1409 → E‑1410 → separator D‑1403 → PSA, plus the flare branch) with the sensor tags we use (TIA050, TICA0055, TY0055, TI0059, FI010, PICA0017). It goes on the first technical slide so the judges see exactly where each number comes from. ≈ 1 person‑h; the drawing script runs in seconds. |

---

## 8. Data limitations and the assumptions we use (with justification)

**We say this openly on the first technical slide:** the plant data provided is not enough for a full‑year analysis. Each PI export holds only 3,600 rows from 1 January (2.5 h to 7.5 days of one winter week), there is no ambient temperature tag, no fan curve, no fan current, no air‑side ΔP and no cleaning history. We have three anchor points (the datasheet, 1 Jan 2026 and 14 Nov 2026) plus 2 years of hourly weather. Every number we present is therefore marked as *measured*, *calculated from measured* or *assumed*, and every assumption below is varied in a sensitivity chart.

| # | Assumption | Value used | Why it is justified | Sensitivity shown |
|---|---|---|---|---|
| A1 | Fan speed is proportional to VFD output % (TY0055), and airflow is proportional to fan speed | Q_air = Q_design × (%/100) × system‑curve correction | Fan affinity laws: for a fixed system curve Q ∝ N, ΔP ∝ N², P ∝ N³. The VFDs run 25–50 Hz with 4‑pole motors, so frequency ∝ speed. Datasheet gives the 100 % point (114,000 m³/h, 190 Pa per fan). | ±10 % on airflow |
| A2 | All three fans run identically | One fan signal for all three | The PI data for TY0055A, B and C are identical to the decimal, and the 14 Nov screenshot shows 87.887 % on all three: they share one controller output (TICA0055). | – |
| A3 | Fan curve shape | Generic 4‑blade axial curve scaled through the design point, ΔP falling ~40 % from design to free delivery | Without a vendor curve, axial fans of this type (Ø2.4 m, 9° pitch) have a well‑known, fairly flat curve near the design point. Fouling moves the *system* curve, so the result is driven by the system curve more than the fan curve shape. | ±15 % on curve slope |
| A4 | Clean design point | 135 → 55 °C, 3 fans at 100 %, design ambient ≈ 35 °C | The datasheet gives the process temperatures. The design ambient is not stated. A common rule of thumb for air coolers is an approach (T_out − T_air) of roughly 15–25 K, so 55 − 20 ≈ 35 °C, which is close to Atyrau's 99 % hourly temperature (36 °C, A8). **Result (audit H2):** the model is *consistent* with the datasheet if the design ambient is ≈ 35 °C; this is a consistency check, not a validation. Re‑tuning to 30 °C or 38 °C moves the 14 Nov blockage from 65 % to 56 % or 67 %. | 30–38 °C |
| A5 | Dry syngas composition | Median of lab data Jan–Nov 2026: H₂ 74.4, CO₂ 17.9, CH₄ 4.96, CO 2.25, N₂ 0.6 mol % | 55 samples spread over 10 months. Variation is ±1 mol %, which changes Cp and molar mass by < 3 %. Three outliers are dropped (10 Mar, 28 May, and the empty row on 8 Jul) because they break the H₂ + CO₂ balance of a shift outlet. | lab min/max |
| A6 | Water content of wet syngas at A‑1401 inlet | From the steam balance on the PFD (14,526 + 968 kg/h steam) minus water consumed in reforming and shift, cross‑checked against the dew point | The lab only measures dry gas after D‑1403. Everything that condenses between A‑1401 and D‑1403 is water, so the steam balance is the only measured source. The P&ID marks the line as two‑phase, which confirms the dew point is above the outlet temperature. **Caveat (audit H3):** the carbon balance on the same PFD does not close (≈ 480 kmol C/h in the feed vs ≈ 229 kmol C/h in the syngas), so the water number rests on the steam balance alone. Ask Air Liquide for the D‑1403 condensate flow. | 0.24–0.555 mol/mol (duty 3.5–5.3 MW) |
| A7 | Outlet limit that makes A‑1401 the bottleneck | Plant cuts load when fans reach 100 % and TICA0055 can no longer hold the 65 °C set point | The set point (65.0 °C) is read from the 14 Nov screenshot. E‑1409 and E‑1410 downstream are sized for the A‑1401 outlet, and PSA performance falls with hotter, wetter feed. | 60–70 °C |
| A8 | Ambient temperature | Open‑Meteo ERA5 reanalysis, hourly, 47.12 °N 51.92 °E (Atyrau, −22 m), 1 Jan 2025 – 13 Nov 2026. Design summer = 38 °C; stress case = 41 °C | ERA5 (the European Centre's reanalysis, a weather model corrected with real observations) is widely used when no site station is available. We did not check it against an Atyrau station ourselves. The data file is `weather/atyrau_open-meteo_47.12N_51.92E_2025-01-01_2026-11-13.csv`, and `model/run_losses.py` reads it. Results: max 40.6 °C (Jul 2026), 99.6 % hourly percentile 37.9 °C, 99 % = 36.0 °C, hours ≥ 35 °C: 101 (2025) and 159 (2026); hours ≥ 30 °C: 673 and 744. ERA5 smooths peaks by 1–2 K and fin‑fan banks also suffer 1–3 K hot‑air recirculation, so +2–3 K is added for the stress case. | design 36 / 38 / 41 °C |
| A9 | Ambient on the anchor days | 1 Jan 2026: −3 to −8 °C (ERA5 hourly). 14 Nov 15:00: 6.5 °C | 1 Jan: same ERA5 series as A8. 14 Nov: ERA5 is only published about 5 days late, so this value comes from the Open‑Meteo forecast archive ("past days"), which is a weather model, not a measurement. | – |
| A10 | Fouling build‑up over the year | Blocked fin‑gap fraction φ grows during the debris season: dust all year, cottonwood/poplar fluff in May–June, insects June–August; reset only at manual cleaning | The debris types come from the visual inspection in the case brief; the season timing is general knowledge (poplars shed fluff in late spring, insects peak in summer), not a local study. **Caveat (audit H4):** the model gives about the same blockage on 1 Jan (≈ 68 %) and 14 Nov (≈ 65 %), so our two data points do **not** show build‑up. The fan‑speed rise is explained mostly by the hotter inlet. A cleaning date or a summer data point is needed to measure the build‑up rate. | linear vs S‑curve build‑up |
| A11 | Debris layer thermal resistance | R_d,air = 0.0005–0.002 m²K/W on the fin area | An order‑of‑magnitude guess for a loose fibrous mat; we did not find a firm published value. The model showed that explaining 14 Nov by insulation alone would need R_d ≈ 0.047 m²K/W, far above this range, so blocked airflow (φ) is the more likely cause. | full range |
| A12 | Fin geometry, if the bundle drawing is not readable (**used: assumed, not read from a drawing**) | Ø57 mm fin OD, ~11 fins/inch (2.3 mm pitch), 0.4 mm aluminium, 64 mm triangular pitch | These are common values that give a fin‑to‑bare area ratio of ~23 on a Ø25 mm tube, which is what the datasheet states (5,288 / 226 = 23.4). | ±1 fpi |
| A13 | Economics | H₂ value 1.5–2.5 USD/kg; lost production counted only in hours when the cooler limits load (A7 + A8) | This is the range for SMR hydrogen with low Kazakh gas prices plus a supply margin. Production lost is calculated hour by hour from the weather, so it is not a guess about "summer". | ±50 % on price |

> **Update, 14 Nov evening: full plant history received** (hourly, Nov 2023 – Mar 2026). It changes four assumptions; details are in Part 0 of `A-1401_PFD_and_thermal_diagnosis.md`.
> - **A7:** 65 °C is a target, not a hard limit. The outlet is above 66 °C in 74 % of running hours.
> - **A10:** the seasonal build-up is now measured: +10–15 points each May–August, −10–12 after the October 2025 cleaning. About 50–60 % is a constant offset that cleaning doesn't remove.
> - **Inlet temperature:** 158–166 °C is normal; the 145 °C of 1 Jan 2026 was the exception.
> - **Monitoring backtest:** now also run on the real history (`a1401_monitor/real_backtest.py`), not only on a synthetic year.

**Monitoring backtest without a full year of data.** We build a *synthetic year*: real hourly ERA5 weather (A8) + the calibrated clean model + the debris build‑up of A10, with sensor noise taken from the real January data. The monitoring model must detect the fouling we put in, and we report how many days it takes to detect it and how often it gives false alarms. Then we validate on the two real anchor points. If Air Liquide sends the hourly re‑export, the same code runs on real data without changes.

---

## 9. Hints from the Air Liquide representative (14 Nov) and what they change

**Hint 1: "The flowmeter reading is only correct when no gas is being flared (which is usually not the case)."**

FI010 measures the gas **after** the separator D‑1403, on the way to the PSA. When some gas is sent to the flare (through UV0071 / PV0017), that part goes through the cooler but is **not counted** by FI010. So FI010 usually **under‑reads** the true flow through A‑1401.

What we do instead (new step B0, ≈ 1 person‑h, compute < 1 s):
- **Hydrogen balance (limited use):** H₂ exported from the PSA (12,200 Nm³/h on the PFD) ÷ PSA recovery ÷ H₂ fraction in dry syngas (74.4 %) → dry syngas flow. *Correction (audit M6):* an earlier version used a "typical" 85–90 % recovery, which gives 18,000–19,500 Nm³/h, *less* than the 20,588 on the PFD, and that would mean FI010 *over*‑reads, the opposite of the hint. The diagnosis instead back‑calculates recovery = 12,200 ÷ (0.744 × 20,588) = **79.6 %** from the PFD, which agrees with 20,588 by construction. **So the H₂ balance cannot tell us the true flow on its own**: it needs an independent recovery figure. We use FI010 on a day with the flare closed (14 Nov) and test the flow +10 / +25 / +50 % in the uncertainty chart.
- **Carbon balance (cross‑check, done):** all carbon in the process feed should leave as CO₂ + CO + CH₄ in the syngas. Using the full NG + LPG on the PFD gives ≈ 480 kmol C/h in, but only ≈ 229 kmol C/h in 20,588 Nm³/h of syngas, a factor of 2. Most likely part of the feed is burner fuel, but the PFD doesn't show the split. So this check is **inconclusive** for now.
- Use FI010 only when the flare valves are closed (PV0017 = 0 %), and treat it as a **minimum** otherwise.
- New assumption A14: true flow = FI010 when not flaring, otherwise the H₂‑balance value; sensitivity ±10 %.

**Hint 2: "Think about why there is a separator vessel downstream of the heat exchangers."**

D‑1403 is there because **water condenses** in A‑1401, E‑1409 and E‑1410 and must be removed as liquid before the PSA. This confirms the key point of step B:
- The gas inside A‑1401 is **two‑phase** (gas + liquid water), and most of the heat removed is the **latent heat of condensing water**, not just cooling of the gas. A model that treats it as dry gas would be badly wrong.
- FI010 measures **dry** gas (after the water is removed). The real mass flowing through A‑1401 is dry gas **plus water vapour**, which is a large extra amount.
- The **condensate flow** from D‑1403 (level LI018 / drain) is a direct measure of how much water condensed. If Air Liquide can give the condensate flow, it is the best way to calculate the cooler's duty. Ask for it.
- Warmer A‑1401 outlet → more water stays as vapour (saturated water mole fraction y = p_sat/P: 0.28 % at 40 °C, 0.94 % at 65 °C, 1.17 % at 70 °C at 2.66 MPa abs). E‑1409 and E‑1410 (outlet 38.8 °C, TI0083) condense most of it, so the main effect is **extra load shifted to E‑1409 / E‑1410**. Only if they cannot keep up (hottest days) does wetter gas reach the PSA.
- Side effect to mention (chemistry): p_CO₂ ≈ 0.179 × 2.66 MPa ≈ 4.8 bar → by Henry's law ≈ 0.09 mol/kg dissolved CO₂ → pH ≈ 3.7 (estimate, ignores NH₃). The A‑1401 tubes are 304L and resist it. Downstream materials (E‑1409, E‑1410, D‑1403, piping) are **unknown**; if they are carbon steel, CO₂ ("sweet") corrosion is a risk. Ask Air Liquide.
