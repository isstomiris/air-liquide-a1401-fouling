# A-1401 solution documents, revision 2: source check and change log

Checked 15 Nov 2026 against the cited web sources (opened that day) and the project's own results (`a1401_clean_vs_fouled/`, `A-1401_PFD_and_thermal_diagnosis.md` Part 0, `a1401_solutions_check/SIMULATION_REPORT.md`).

Files checked: `A1401_Solutions_Defense_Summary 2.md`, `A1401_Detailed_Engineering_Protocols 2.md`.
Corrected versions: `A1401_Solutions_Defense_Summary_2_corrected.md`, `A1401_Detailed_Engineering_Protocols_2_corrected.md`.
New simulation: `simulate_solutions_v2.py`, `SIMULATION_REPORT_v2.md`. The revision-1 files (`CHANGES.md`, `SIMULATION_REPORT.md`, `results/`, `figures/`, `*_corrected.md`) are kept unchanged for comparison.

## 1. New and changed sources

| Ref | What the documents claim | What the source says | Status |
|---|---|---|---|
| A1 Primasonics PAS-120 data pack | 120 Hz; 4.8–6.2 bar; 21.25 L/s (about 45 SCFM) in the detailed specification, summary prints L/min; 148 dB sound power; 150 dB summary; overall height 1.365 m | All confirmed. Summary: "21.25 l/min 42/50 SCFM"; detailed: "21.25 l/s 45 SCFM @ 5.5 bar". 148 dB is sound power measured in an anechoic chamber; the 150 dB summary figure is labelled sound pressure without context. 21.25 L/s = 1.275 m³/min = 45 cfm, so the detailed value is self-consistent. Weight not stated. | Confirmed |
| A2 Primasonics BHSL case | Q1 horn; combustion-gas/air heat exchanger; 10 s bursts; temperatures maintained, less offline cleaning | Confirmed: August 2020, poultry-manure boiler, ash fouling, 10 s bursts "every number of hours" in daytime. No numerical results; a different horn model (Q1, not PAS-120). | Confirmed |
| R1 Basso et al. 2023 (O2T8) | J. Non-Cryst. Solids: X 17, 100143; 20:80 OTES:TEOS; AW1050 aluminium; about 0.31 µm; 200 °C, 2 h cure after ageing; 1.3 mol/L; 7 h condensation at 106 °C; about 46 nm loss; receding angle decreased | All confirmed (open-access PDF on the Padova repository). Added: the paper's deposition was **dip coating at 4.8 cm/min** on polished aluminium; 24 h ageing; receding angle fell by about 33°; localised "spiderweb" degradation; testing stopped before total failure. | Confirmed. The documents' flow coating of a whole bundle is an adaptation (already labelled P). |
| R1 author thesis | Detailed methods on printed pp. 62–66 | Thesis opens; the extracted part did not reach those pages, so the page reference was not verified. | Could not be verified |
| A4 Abubakar et al. 2020, Sci. Rep. 10, 19348 | Coated PVC film; strong response at 64 Hz; 77 % improvement in optical transmittance | Confirmed (35–300 Hz at 80–100 dB; dust from PV panels, about 1.2 µm). The paper's body gives about 57 % and 87 % relative transmittance for hydrophilic and hydrophobic surfaces, which does not obviously match the 77 % in the abstract. | Confirmed, with the internal inconsistency noted |
| R2 Abubakar et al. 2020, Sci. Rep. 10, 14346 | Hydrophobic surface: 80 % vs 20 % cleaned under vibration | Confirmed: glass plates, loudspeaker-driven plate vibration, best at 30 Hz and 5 mm amplitude; about 80 % of area cleared after 0.36 s vs below 20 % hydrophilic. | Confirmed |
| A5 Riera et al. 2006 | Air attenuation and gas/solid impedance mismatch | Confirmed (Ultrason. Sonochem. 13(2):107–116). | Confirmed |
| A3 Cao et al. 2018 | Strongest modeled tube response around 200 Hz | The paper exists (J. Northeast Electric Power Univ. 38(3), 24–31), but the abstract page shows no content, so the 200 Hz figure could not be checked. | **Could not be verified**; marked as such |
| V2 ctpenvironment.com/decamex | Up to 12 rows; applied from below; Gulf Coast LNG, 820 fin fans, summer 2023 | Confirmed: "up to 12 tube rows", technicians work from the platform underneath, 820 fin fans after five years of operation, "low-pressure compressed air". The page also has an unlabelled comparison table (100 % for DECAMEX) that is vendor marketing. | Confirmed |
| V1, V3–V5 CTP | As revision 1 (336 bundles, 4/day, one fan at a time; 63 % vs 14 %; > 15 %) | Checked in revision 1 (`CHANGES.md`) | Confirmed |
| R3 Li et al. 2022, R5 Blygold, R6 SYLGARD 184, R7 MathWorks, A6 TU Darmstadt array paper | Comparators and background only; not used in any number | Not re-opened in this check | Not verified; they do not affect the selected designs or the simulation |
| H09 and other links to `chatgpt.com/library` | Source workbook link | Private links that nobody else can open | **Removed**; replaced by the project file name |
| E01–E08 drawings, passport, certificates | 62 mm pitch, 10,277 kg, 170 °C design wall temperature, fan certificate 170 Pa vs drawing 190 Pa, heating bank 26 tubes 25 × 2.5 mm carbon steel | 170 °C design temperature, 190 Pa and the carbon-steel heating row agree with `AUDIT_report.md` and `A-1401_solution_plan.md`. The fan certificate (170 Pa) and the 62 mm / 10,277 kg values are not in the project files. | Consistent where checkable; others labelled "not re-checked in this project" |

## 2. The 200 °C cure against the 170 °C design wall temperature

The documents' statement is correct and is kept. 200 °C is 30 K above the passport design temperature (170 °C). The documents already require unpressurised workshop curing with OEM acceptance. Added points:
- The fin type and fin-to-tube bond are unknown. Wrapped or tension-wound fins are the bond type most sensitive to a heat cycle; extruded or embedded fins tolerate it better. The plant already runs at an inlet of 158–168 °C, so the fins see close to 170 °C in service.
- The oven must take a 10.6 × 3.0 m bundle of about 10.3 t. Availability of such an oven is not established.
- The Basso paper tested durability only under 7 h of steam condensation. The air side of A-1401 sees dry heat up to about 160 °C, UV, rain and abrasion by debris and by the cleaning itself. None of these was tested.

## 3. Contradictions with our findings (same as revision 1), and what was changed

| # | Revision-2 statement | Our finding | Change |
|---|---|---|---|
| C1 | Thermal results from the supplied sensible-only script (clean UA 13.95 kW/K, about 800 kW, 30 °C air, 1 Jan inlet) | The wet model exists and is the project's basis. Clean duty at the reference window is 4,244 kW (56 % condensation), UA 106.5 kW/K. 13.95 kW/K is a dry-gas-only artefact (`REPORT.md` §6.3). | Tables in Summary §5 and Detailed §9.1, §9.3–9.5 and §10.3 replaced by wet-model results |
| C2 | Starting state: assumed 30 % blockage | Fitted plant state 0.685 at the end of summer 2025, spring base 0.594, seasonal increment about 9 points. 30 % is mild here (+4.4 K over clean). | Replaced. 30 % kept only as a labelled example (on the wet model: S1 base 39.8 °C, S2 base 37.8 °C, clean 36.7 °C). |
| C3 | Airflow = clean airflow × (1 − b); "no fan curve" | Fan/system intersection with a generic fan curve (stated as such) | Replaced. The documents' remark that Δp ∝ K V² with V ∝ (1 − b) gives a constant Δp is correct for their model and is the reason we use a fan curve. |
| C4 | §2.2: "Seasonal performance has not been analyzed in this revision"; summer data lack the measurements needed | The project has analysed the full history (2023–2026) with the wet model: seasonal rise 9–12 points, October 2025 cleaning 0.682 → 0.557, 2026 turnaround cleaning to 0.574 | Statement corrected; findings added. The missing measurements they list (airflow, wet flow, condensate) are still missing and are kept as limitations. |
| C5 | Clearance applied to the whole blockage | Only the seasonal increment is measured to come and go | Clearance applied to the increment only |
| C6 | Clearance scenarios judged without a field anchor | The 2026 turnaround cleaning brought the indicator to 0.574 for Jul–Sep 2026; the October 2025 cleaning to 0.557. Both removed at least the whole seasonal increment. | Added. S2 base (64.8 %) and S1 base (21 %) are both below what the plant's existing cleaning achieved. |
| C7 | 65 °C outlet as the operating basis | The plant ran at targets of 60, 65 and 70 °C in 2026 | Capacity reported at all three targets (gains are the same to within 0.2 points) |
| C8 | "Base Solution 1: 25.05 kW and 2.73 K; base DECAMEX: 79.72 kW and 8.68 K" (sensible model) | Wet model, reference window, state held Jul–Sep: S1 base **+166 kW, 75.2 → 67.1 °C**; S2 base **+242 kW, 75.2 → 63.2 °C** | Replaced |

## 4. Which numbers are sourced and which are scenarios

**Sourced (checked):** PAS-120 120 Hz, 4.8–6.2 bar, 21.25 L/s, 148 dB sound power, 1.365 m; BHSL 10 s bursts on ash; O2T8 composition, 0.31 µm, 200 °C/2 h, 1.3 M, 46 nm loss in 7 h of condensation; Abubakar 64 Hz and 77 % transmittance (PVC), 30 Hz and 80 % vs 20 % (glass); CTP 12 rows, 820 fans, 336 bundles, 4/day, one fan at a time, 63 % vs 14 %.

**Proposed or assumed by the authors (P):** three horns, one per sector; 24 pulses × 10 s per sector; 24 events per year; 1.0 × 0.5 m hood; 1 m³/s at 2,000 Pa collector; 0.12 kWh/m³ air; 80 % coverage; 0.30 µm; 1.5 kg/L dry density; 0.6 retention; 110 L sol; oven cp, efficiency and hold power (746 kWh); g1 = 0.99; DECAMEX 1/3/6 kg/m² (**94.69 kg** base), 4/8/12 m³/min, 2/4/8 h (**1,920 m³**, **258.73 kWh**), 7 h occupation; 0.50 m² pilot patch; **all c, d, e values** (S1 4 / 21 / 57.6 %, S2 24.5 / 64.8 / 93.1 %).

The arithmetic on these was re-checked and is correct (for example 31.564 × 3 = 94.69 kg; 8 × 240 = 1,920 m³; 1,920 × 0.12 + 5 + 23.33 = 258.73 kWh; 3 × 24 × 10 s × 0.02125 m³/s = 15.3 m³; 10,277 × 0.6 × 175 / 3,600 / 0.45 + 80 = 746.1 kWh; 1.3 × (0.8 × 60.08 + 0.2 × 165.3) / 1,000 = 0.1055 kg/L).
