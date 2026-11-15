# A-1401 solution documents: source check and change log

Checked 14 Nov 2026 against (a) the cited web sources, opened on that date, and (b) the project's own results in `a1401_clean_vs_fouled/`, `A-1401_PFD_and_thermal_diagnosis.md` (Part 0), `AUDIT_report.md`, `model/` and `a1401_monitor/`.

Files checked: `A1401_Solutions_Defense_Summary.md` and `A1401_Detailed_Engineering_Protocols.md` (supplied in the project thread).
Corrected versions: `A1401_Solutions_Defense_Summary_corrected.md` and `A1401_Detailed_Engineering_Protocols_corrected.md` (this folder).
New simulation: `simulate_solutions.py`, results in `results/`, write-up in `SIMULATION_REPORT.md`.

## 1. Cited sources

| Ref | What the documents claim | What the source says | Status |
|---|---|---|---|
| R1 Aculon AL-B TDS | 2–4 nm; 225 °C degradation; 0.98 kg/L; < 5 % proprietary solids; ethanol/fluorosolvent; 116°/80° contact angles; spray not recommended; dip application | All confirmed. Spray: "not recommended … as it is 'autophobic'". Dip: 1 min immersion (5 min with sonication). | Confirmed |
| R1 Aculon AL-B TDS | "The TDS calls for AL-A pretreatment" | The TDS says AL-B is for "most metals, semiconductors, and certain polymers that have been pretreated with Aculon AL-A". The AL-A pretreatment refers to polymers. No pretreatment requirement is stated for metals. | **Corrected.** For aluminium fins the AL-A stage, and the second 24.2 m³ bath that came with it, is not required by the source. It is now listed as "confirm with Aculon". |
| R1 Aculon AL-B TDS | Not stated in the documents | No service-temperature rating, no UV or outdoor durability claim. Curing guidance mentions 120 °C peak metal temperature. | Added |
| R2 Wang et al. 2026 | *Acoustics* 8(2) 33, DOI 10.3390/acoustics8020033; 570 × 540 mm module; about 28 kHz, about 10 W; > 97 % short-circuit-current recovery | All confirmed (10.68 W in the body). Recovery depends on tilt: 97.5 % at 30°, 98.5 % at 45°, **81 % at 15°**. Gravity provides the transport. Dust was sieved below 48 µm. | Confirmed. Tilt dependence added: the A-1401 bundle is horizontal, so the gravity-driven removal mechanism of the paper does not carry over. |
| R3 CTP Thailand | +63 % airflow with DECAMEX vs +14 % with baking soda, matched settings; limestone; < 1 day | Confirmed. Cogeneration plant; hard mineral scale from earlier hard-water jet washing. Matched product quantity, pressure, duration and nozzle distance. | Confirmed |
| R4 CTP Malaysia LNG | 336 bundles; up to 4 bundles/day; forced draft: one fan stopped at a time | Confirmed ("about 336"). The page does not say which draft type that plant has. Contract 2 years, renewed for 3. | Confirmed |
| R5 CTP DECAMEX page | Multi-row treatment; low-pressure | "Remove all types of deposits from all tube rows" confirmed; "non-hazardous and biodegradable" confirmed. "Low-pressure" is **not** on this page (it is on R6). Added: reach up to 10 m from accessible work areas. | Attribution corrected |
| R6 CTP French steelworks | > 15 % vs conventional cleaning; from below; final air blow | Confirmed: oil coolers, dusty site, "low-pressure cleaning", gains "above 15 % compared with conventional cleaning" confirmed by client airspeed checks. | Confirmed |
| R7 Aculon Multi-Surface TDS | 200–300 nm by spray; not for long-term abrasion; no continuous temperature rating | Confirmed (30 nm by dip). | Confirmed |
| R8 Heresite P-413 TDS | "typically about 25 µm" | Two-coat immersion on heat-transfer parts gives **25–50 µm**. Vendor states heat-transfer loss < 1 % as applied. | Corrected to 25–50 µm |
| R9 Lee et al. 2020 | 178.5° / 159.2°, 5B, spray on aluminium | Confirmed (12 nm silica, 46 wt %, 150 °C for 5 h). | Confirmed |
| D1–D6, M1, M2 | Links to `chatgpt.com/library?...` | These are private links in someone's ChatGPT file library. Neither we nor the judges can open them. | **Removed.** Replaced with project file names. |

## 2. Equipment and plant-data figures

| Figure in the documents | Project files | Status |
|---|---|---|
| 276 tubes, 6 rows, 2 passes, 25 × 2 mm, S30403, 226 / 5,288.4 m², 3 fans × 114,000 m³/h, 190 Pa total, 477 rpm, 11 kW, 25–50 Hz, 2.69 MPa(g), 4.0 MPa / 170 °C, 135 / 55 °C, heating row 21.3 / 498.4 m², manual louvres | Same values in `AUDIT_report.md` §1 (checked there against the GA drawing table) | Consistent |
| Transverse pitch 62 mm, widths 2,980 / 2,950 mm, frame height 590 mm, envelope 10,592 mm, bundle mass 10,277 kg | Bundle drawing 0010 is not in the project files | Kept, labelled "from drawing 0010, not re-checked in this project". Our model assumes 64 mm pitch (`config.py`, assumption A12). If 62 mm is correct, our assumed face area is about 3 % too large; this is noted for the next model revision. |
| Hourly CSV: 20,176 rows, 14 Nov 2023 – 11 Mar 2026 | `plant_history/a1401_history_hourly.csv` has 20,176 data rows over that range | Consistent |
| Excel file: 5,949 frozen records from 11 Mar 2026 12:00 UTC | `REPORT.md` §3: 5,948 frozen rows from the same time | Consistent (one row difference in counting) |
| 1 Jan 2026 00–02 UTC: 144.30 °C, 69.68 °C, 22,610 Nm³/h, OP 53.85 % | `REPORT.md` §3 | Consistent |
| 14 Nov snapshot: 166.78 °C, 66.4 °C, 87.9 % fans, 20,801 Nm³/h | Diagnosis Part 0 confirms the same hour in the history | Consistent |
| "September versus October 2025 cleaning dates conflict" | Equivalent blockage is still 0.68 on 25 Sep and 1 Oct 2025 and is 0.58 on 30 Oct 2025 (`history_equivalent_blockage_hourly.csv`) | **Clarified**: the data place the cleaning between 1 and 30 Oct 2025. |

## 3. Contradictions with our earlier findings, and what was changed

| # | Document statement | Our finding | Change |
|---|---|---|---|
| C1 | The wet/condensing model is "unavailable"; only a sensible-only model could be run | The wet model exists: `a1401_clean_vs_fouled/` (current) and `model/` (earlier) | Statement removed. All thermal results now come from `a1401_clean_vs_fouled`. |
| C2 | Thermal comparison with the sensible-only model: clean UA 13.95 kW/K, clean duty 800 kW, 30 °C air, no condensation | At the summer reference window (18 Jul 2025, 159.4 °C, 17,444 Nm³/h, air 31.8 °C): clean duty **4,244 kW**, of which 56 % is condensation; clean UA 106.5 kW/K. 13.95 kW/K is a dry-gas-only artefact and should not be used (`REPORT.md` §6.3). | Sensible-model tables (Summary §5; Detailed §10, §11.1 code, §9.4) replaced with wet-model results. |
| C3 | Starting state: hypothetical 30 % blockage | 30 % is mild for this exchanger: outlet 41.1 °C vs 36.7 °C clean (+4.4 K), duty −1.7 %. The plant is at a fitted equivalent blockage of **0.594** (spring 2025) rising to **0.685** (end of summer 2025). | Starting state is now the fitted plant state. 30 % is kept only as a labelled example. |
| C4 | Airflow = clean airflow × (1 − b) | Fan and system curves (generic fan curve, stated as such): 30 % blockage gives 17 % less air, not 30 %; at 0.685 the fans move 45 % of rated air. | Replaced by the fan/system intersection of the wet model. |
| C5 | Clearance fractions applied to the whole blockage | Only the seasonal increment (about 9 points in 2025) is measured to come and go. The base of about 0.59 is not removed by the existing cleaning and includes model offset. | Clearance now acts on the seasonal increment only. Effect on the base is shown separately as an upper bound, not credited. |
| C6 | Clearance scenarios judged without a measured anchor | The existing October 2025 cleaning took the equivalent blockage from 0.682 (Aug–Sep) to 0.557 (Nov, 40 h): it removed at least the whole seasonal increment, and a few points more. The diagnosis gives about 24 % recovery of overall U for that cleaning. | Added as the benchmark. Note: the DECAMEX central case (69 % of the increment per campaign) is **below** what the existing cleaning already achieved. |
| C7 | Earlier wet results quoted as "3.5–5.3 MW; clean UA about 119 kW/K; blockage 50–72 %" | Current model: 4.24 MW clean and 3.53 MW at end of summer 2025 (reference window); UA 106.5 kW/K at summer conditions (119 at the design point); b 0.53–0.69 on fans-100 % hours | Numbers updated. |
| C8 | Temporary one-fan-stopped screening: 84.7 °C (sensible model) | Wet model, end-of-summer state: outlet **75 → 105 °C** on the reference day; spring state at 20 °C air: 45 → 76 °C | Replaced. This is a real operating constraint for DECAMEX campaigns. |
| C9 | "Central gains: S1 +5.0 %, S2 +12.2 % sensible duty" | Wet model, reference window, in-season state: S1 central **+221 kW (+6.3 %)**, S2 central **+251 kW (+7.1 %)** total duty | Replaced (see `SIMULATION_REPORT.md`). |
| C10 | Recommendation: DECAMEX first, coating + vibration as pilot | Unchanged in direction. Added: on the anchored basis the two methods give similar results, and neither beats an existing-type full cleaning done at the end of the cottonwood season (late June). | Recommendation text extended. |

## 4. Which numbers are sourced and which are scenarios

**Sourced (vendor or literature, confirmed above):** AL-B 2–4 nm, 225 °C, 0.98 kg/L, no spray, 1-min dip; Wang et al. 28 kHz, about 10 W, > 97 % at ≥ 30° tilt; CTP +63 % vs +14 % airflow (limestone), 336 bundles, up to 4/day, one fan stopped at a time (forced draft), > 15 % vs conventional cleaning (dust).

**From drawings or plant data:** all items in §2.

**Proposed or assumed by the document authors (P), not from any source:** 12 actuator modules, 50 W/channel, 2 min/channel, daily cycles; 500 m³/h and 1.5 kW extractor; 0.2 % hardware obstruction; 60/80/100 % coating coverage; 3 nm design thickness (inside the vendor range); 1,500 kg/m³ dry density and 0.2 W/m·K film conductivity; 24.2 m³ bath per stage; 1/3/5 % bath loss; DECAMEX dose 0.5/1.5/3 kg/m² (giving **46.5 kg** central); productivity 12/8/4 m²/h (3.87 h); air 3/5/8 m³/min (**1,452 m³**); 0.08–0.12 kWh/m³ (**145 kWh**); **8.8 h** campaign; crews; debris loading 0.05–0.5 kg/m²; 80 % mass removal and 70 % capture; 1/2/4 campaigns per year; **all c, d, e clearance values** (S1 5 / 26 / 50 %, S2 31.5 / 69 / 93 % per event).

The arithmetic on these assumptions was re-checked and is correct (for example 30.975 × 1.5 = 46.5 kg; 4 + 1.25 × 3.87 = 8.84 h; 10.8 × 3.2 × 0.7 = 24.19 m³). The documents' own Python code was run and reproduces their tables. Those tables are now superseded because the model underneath them is the sensible-only one (C2).
