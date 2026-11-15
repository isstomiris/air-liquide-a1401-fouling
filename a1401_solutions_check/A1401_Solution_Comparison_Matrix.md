# A-1401: comparison of cleaning methods

Calculation note, AIChE Student Hackathon 2026 (Air Liquide case). Revision 0, 15 Nov 2026.

Scope: air-side fouling of A-1401 by cottonwood/poplar fluff, dust and insects (season May–September). Four methods are compared, with the plant's own cleaning as a measured reference:

| Code | Method |
|---|---|
| **M1** | Compressed-air blowing (manual lance, reverse to airflow) |
| **M2** | Water washing, potable water, low or high pressure; **M2d** = the same with a detergent |
| **S1** | Team solution 1: O2T8 octyl-silica coating (0.3 µm, 200 °C cure) + three Primasonics PAS-120 horns + vacuum hood, 24 events/year |
| **S2** | Team solution 2: CTP DECAMEX dry chemical cleaning, 2 campaigns/year (1 Jun, 1 Jul) |
| **REF** | The plant's existing cleaning: autumn 2025 and turnaround 27 Jun – 7 Jul 2026. **Method not stated in any case file** (Air Liquide gave dates only). |

Evidence labels used in every cell: **[M]** measured on A-1401 (historian + our wet model); **[S]** our simulation on assumed clearance; **[L]** peer-reviewed literature; **[G]** industry guideline; **[V]** vendor claim; **[A]** team assumption, not evidenced; **n/d** no data found.

---

## 1. What the two supplied papers show

| Paper | What it tested | What it actually shows | What it does **not** show |
|---|---|---|---|
| **Shin et al. 2024** [P1] (ASim2024, IBPSA, conference paper) | 200 × 200 mm samples of residential AC outdoor coils (16–17 FPI, wavy and louver fins). ISO A2 mineral dust, 300 g/h, 2.0 m/s. Three cycles of 60 min fouling, 10 min water washing, drying. | Water washing **recovered** the pressure drop; recovery was "overwhelmingly higher" on the corrugated 17 FPI fin than on the louver fin. Maximum pressure-drop rise 157 % (corrugated 16 FPI), 259 % (corrugated 17 FPI), 283 % (louver 17 FPI). Wider fin spacing fouls less. The authors **recommend periodic water washing** and say the coil must be fully dried before restart, because residual water promotes dust adhesion. | It does not show washing is ineffective. Residual (post-wash) fouling is not tabulated. No organic fibre, no industrial bundle. The paper is internally inconsistent (drying 10 min in the abstract, 30 min in the method; section 2 says the louver recovered better, section 1 says the opposite). |
| **Zhan et al. 2018** [P2] (Int. J. Heat Mass Transfer 124, 1230–1244) | Wet (condensing) evaporator samples, plate/wavy/louver fins, synthetic dust (75 % SiO₂), RH 50–90 %. | Particles stick far more on **wet** fins: deposit mass under dehumidifying conditions was 4.7–7.4 times that under dry conditions. Raising RH from 50 to 90 % cut heat transfer by 46–69 % and raised Δp by 93–120 %. "Dry particulate fouling is more easily blown away by the air flow." Wet deposits sit on the leading edge of the fins and front of the tubes. | It does not test washing at all. It is about condensate on cold evaporator fins, not wash water on a hot bundle. |

**Fair conclusion from P1 and P2:** neither paper shows that water washing is ineffective. P1 shows it works on mineral dust, if the coil is dried before restart. P2 shows that a **wet surface collects 5–7 times more debris** than a dry one. Together they support one narrower claim: water left on fins while debris is still arriving increases re-fouling, so wet cleaning during the debris season needs complete drying, and dry cleaning avoids that. On A-1401 this effect is probably small, because the bundle runs hot (inlet 158–168 °C [M]) and wash water will evaporate within minutes [A].

---

## 2. Full matrix

| Criterion | M1 Compressed air | M2 / M2d Water (± detergent) | S1 O2T8 + horns | S2 DECAMEX | Basis |
|---|---|---|---|---|---|
| **Cleaning effect on A-1401, hot day 18 Jul 2025 (no action: outlet 75.2 °C, 3,530 kW)** | n/d for A-1401 | n/d per method. REF (method unknown) reached **56.9 °C, +360 kW, +26 % gas capacity** [M] | **67.1 °C**, +166 kW, +10 % gas (range 62.4–72.5 °C) [S] | **63.2 °C**, +242 kW, +16 % gas (range 60.1–69.6 °C) [S] | [R1] §1 |
| Share of the 2025 seasonal loss recovered | n/d | REF ≥ 100 % [M] | 53 % (18–82 %) [S] | 77 % (37–96 %) [S] | [R1] |
| Effectiveness in general literature/guidance | "Complete removal … unlikely"; "not suitable as a routine method" [G] | Standard method for finned air coolers, typically about once a year [G]. Restored a cottonwood-fouled ACC to "full operating efficiency" [V] (no numbers). P1: recovers Δp on mineral dust [L]. Detergent: effectiveness "has not yet been determined" [G] | Horns: ash in an enclosed boiler exchanger, no numbers [V]. Vibration releases dust from hydrophobic glass/PVC, 80 % vs < 20 % area cleared [L]. **No data on finned bundles or fibre** | +63 % airflow vs +14 % baking soda on limestone scale [V]; 336 bundles at an LNG plant [V]; "> 15 %" vs conventional cleaning at a steelworks [V]. **No data on organic fibre** | [G1], [V1], [P1], [V2], [L1], [V3]–[V5] |
| Evidence on cottonwood-type fibre | n/d | One plant precedent (Saranac, high-pressure water) [V] | None | None | [V1] |
| Reach into the 6 rows | Limited; depends on operator and nozzle [G, qualitative] | Multi-row coils may need up to 10.3 MPa (1,500 psi) [G] | Assumed reach c = 0.5 (0.2–0.8) [A]. Hood collects only at the face. | Vendor: "up to 12 tube rows", applied from below [V] | [G1], [R1], [V3] |
| Where debris actually sits | Windward (air-entry) face and front of tubes [L]. For A-1401 (forced draft) that is the **underside**. Full-depth reach therefore matters less than access to the underside. | | | | [P2], [D1] |
| Needs a plant shutdown? | No; one fan off per cell [G] | No in principle; ACC practice is one cell's fan off during washing [G]. REF 2026 was done in the turnaround [M]. | **Yes, once**: bundle out, 200 °C cure, above the 170 °C design temperature; needs OEM acceptance and a 10.3 t oven [A/D]. Then online. | No; one fan at a time, about 1.6 h per sector [V/A] | [G1], [R2], [R3] |
| Cost in output during cleaning | One fan off: about +30 K outlet or −30 % gas while it lasts [S] | Same one-fan penalty, for the wash and drying time | 3 sectors × 20 min × 24 events ≈ **24 h/yr** one fan off [A]; can be scheduled at night | 3 sectors × 1.6 h × 2 ≈ **9.6 h/yr** one fan off [A] | [R1] §4, [R2] |
| Repeatable during the debris season | Yes, manual | Yes, but each wash needs drying before debris contact (P1) | Yes, 24×/yr, automatic [A] | 2–4 campaigns/yr modelled; vendor service [A] | [P1], [R1] |
| Effect of more frequent cleaning | n/d | n/d | Small: 52 vs 24 events lowers season-mean outlet by only 0.4 K, because reach caps it [S] | 4 campaigns vs 2 lowers the season mean by 1.5 K [S] | [R1] |
| Fin damage | Possible at high pressure; no limit published [G] | Pressure must be "not so high that fins are damaged" (no number) [G]; high-pressure washing "often destroy[s] the fins" [V, competitor] | Contact-free (sound) [V]; long-term fatigue of fins under 148 dB n/d | Vendor: low-pressure compressed air, compatible with fins [V] | [G1], [V6], [V2] |
| Corrosion and scaling | None | **Chloride SCC of 304L tubes** is rare below 60 °C but reported at chlorides as low as 10 ppm where water evaporates and concentrates [L]; A-1401 tubes run 60–160 °C [M]. Hard-water washing left limestone scale on a Thai air cooler [V]. Detergent: aluminium fins tolerate "only the mildest" chemicals [G]; chlorine-containing cleaners attack aluminium coils [G] | Coating may add protection; only tested for 7 h in steam condensation, not UV, heat, abrasion [L] | No water. Product formulation not disclosed; compatibility with aluminium fins to be confirmed [V] | [L2], [V4], [G2], [G3], [L3] |
| Freezing (Atyrau) | Not relevant | **Not relevant in season**: no hour below 0 °C in May–Sep 2023–2025 (April minimum −1.1 °C). Relevant for autumn/winter washing: 11 % of November hours and 67–81 % of Dec–Feb hours were below 0 °C [M] | Not relevant | Not relevant | [D2] |
| Re-fouling just after cleaning | Dry surface | Wet surface collects 4.7–7.4× more particles than dry [L]; on a hot bundle drying is fast [A] | Coating intended to lower adhesion; deposition benefit **not credited** in our model (s = 1) [A] | Dry surface | [P2], [R2] |
| Waste and effluent | Debris blown into the surroundings; flammable fluff near hot surfaces [A] | Contaminated wash water to collect and treat; detergent adds load [A] | Debris captured by the vacuum hood [A] | No liquid effluent; debris + product residue to collect [V] | [R2], [R3] |
| Personnel safety | Compressed air for cleaning must be below 30 psi (207 kPa) at a dead-ended nozzle, with chip guarding and PPE [G]; work at height near fans; LOTO | High-pressure jet injection injury risk; work at height; LOTO; slippery platforms [A] | Horns 148 dB sound power [V]: hearing-protection zone during bursts; LOTO per sector; remote operation, fewer people at height [A] | Powder exposure (SDS not seen); work at height under the bundle; LOTO per fan [A] | [G4], [V7] |
| Hydrogen plant (Ex zone) | Pneumatic, no ignition source [A] | Pumps/electrics must be Ex-rated [A] | Pneumatic horns; vacuum hood fan must be Ex-rated [A] | Pneumatic delivery; static from powder flow to check [A] | — |
| Technology readiness | Common practice | Common practice | Each part is commercial; the combination is **untested** | Commercial service on industrial air coolers | — |
| Main failure risk | Incomplete removal | Fin damage, scale, chloride on hot 304L | Coating cannot be cured at 200 °C; horns do not release fibre (then 75.0 °C, slightly worse than no action) [S] | Weak on organic mats (low case 69.6 °C) [S] | [R1] |
| Capex / opex | Low (qualitative) | Low–medium (qualitative) | Highest: coating + oven + 3 horns + hood (teammates' estimate pending) | Service fee per campaign (quote needed) | — |

### Where our methods win, and on what evidence

| Claim | Status |
|---|---|
| S2 cleans without a shutdown, one fan at a time | **Evidenced** (vendor reference projects [V3], [V4]). M1 and M2 can also be done one fan at a time [G1], so this is not unique. |
| S1 and S2 use no water: no chloride on hot 304L, no hard-water scale, no effluent, no freezing | **Evidenced** for the hazards of water [L2], [V4], [G2]. The freezing point is weak, because the debris season has no frost [D2]. |
| S1 can be repeated 24×/yr without people at height | **Design intent**, no field proof. Our model shows extra frequency adds little. |
| S2 reaches all six rows | **Vendor claim** [V3]. Debris sits mostly on the air-entry face [P2], so this matters less than it sounds. |
| Less fin damage than high-pressure water | **Plausible**: guideline confirms the risk of water [G1]; the vendor [V2] states low pressure; no comparative measurement exists. |
| Dry deposits are easier to remove than wet ones | **Evidenced** in the lab with mineral dust [P2]. |
| Either solution removes cottonwood fibre | **Not evidenced.** No published test on organic fibre for S1 or S2. Poplar seed fibre is hydrophobic and oleophilic [L4]: water wets it poorly, and its effect on dry methods is unknown. |

### Where our methods do not win

1. **Cleaning power.** The plant's own shutdown cleaning reached 56.9 °C; S2 gives 63.2 °C and S1 gives 67.1 °C on the same hot day [R1].
2. **Evidence on fibre.** Water washing has one cottonwood precedent [V1]; ours have none.
3. **S1 needs an outage once,** with a cure 30 K above the design temperature [R3].
4. **Fan-off hours.** S1 stops a fan about 24 h/yr in total, more than S2 (about 9.6 h/yr).

**Recommended framing for the judges:** our methods do not compete with the turnaround clean; they **add to** it. They keep the seasonal debris from building up between turnarounds (season-mean outlet 74.6 → 66.6 °C with S2, 68.5 °C with S1 [S]), dry, online and without water on hot stainless tubes. The best case is a turnaround clean plus S2 during the season. That combination is not yet simulated.

---

## 3. Open items

| Item | Ask whom |
|---|---|
| How the plant cleaned in autumn 2025 and in the 2026 turnaround (air, water, detergent; from above or below) | Air Liquide |
| Wash-water chloride and hardness, if water is used | Air Liquide |
| DECAMEX SDS and fin-compatibility statement | CTP |
| A fin-section test with real cottonwood fluff for S1 and S2 | Team (pilot plan in the protocols) |

---

## 4. Sources

**Supplied papers**
- [P1] Shin D.H., Kang Y.H., Song H.E., Woo S.M., Park J.H., Sung H.K., Ahn Y.C. (2024). *Analysis of air side fouling and cleaning characteristics of air conditioning heat exchanger.* ASim2024, 5th Asia Conference of IBPSA, Osaka. (Uploaded file `shin.pdf`.)
- [P2] Zhan F., Zhuang D., Ding G., Ju P., Tang J. (2018). *Influence of wet-particle deposition on air-side heat transfer and pressure drop of fin-and-tube heat exchangers.* Int. J. Heat Mass Transfer 124, 1230–1244. doi:10.1016/j.ijheatmasstransfer.2018.04.049. (Uploaded file `zhan.pdf`.)

**Guidelines and standards**
- [G1] ACC Users Group, *ACC02 Guidelines for Finned Tube Cleaning in Air Cooled Condensers* (2018). https://acc-usersgroup.org/wp-content/uploads/2018/11/ACC02-Guidelines-for-Finned-Tube-Cleaning-in-Air-Cooled-Condensers.pdf. Water: nozzles about 200 mm from fins, 4.1–7.6 MPa (single row), up to 10.3 MPa (multi-row), 150–190 L/min, potable-quality water. Air: complete removal "unlikely", "not suitable as a routine method". Detergent effectiveness "has not yet been determined". Typical frequency about once a year; more than four a year "unusual".
- [G2] Wermac, *Cleaning Air Cooled Heat Exchangers*. https://wermac.org/equipment/air-cooled_heatexchanger_cleaning.html. Aluminium fins "can withstand only the mildest chemical solutions"; deposits thickest on the air-entry side.
- [G3] Goodman, *SA-026 Aluminum Coil Cleaning Recommendations*. Chlorine-containing cleaners harm aluminium coils; rinse well after any chemical cleaner.
- [G4] US OSHA 29 CFR 1910.242(b): compressed air for cleaning limited to below 30 psi with effective chip guarding and PPE.

**Literature**
- [L1] Abubakar A.A. et al. (2020). Sci. Rep. 10, 14346. doi:10.1038/s41598-020-71356-5. Glass plates, about 80 % vs < 20 % area cleared (hydrophobic vs hydrophilic) under vibration.
- [L2] SSINA, *Chloride Stress Corrosion Cracking*. https://www.ssina.com/education/corrosion/chloride-stress-corrosion-cracking/. 304/304L: rare below 60 °C; failures with as little as 10 ppm chloride; evaporation concentrates chloride locally.
- [L3] Basso M. et al. (2023). J. Non-Cryst. Solids: X 17, 100143. doi:10.1016/j.nocx.2022.100143. O2T8 coating, 7 h steam-condensation durability only.
- [L4] *Physicochemical and sorption characteristics of poplar seed fiber as a natural oil sorbent.* Textile Research Journal (2019). doi:10.1177/0040517519829001. Hydrophobic/oleophilic fibre, 54–68 g/g oil uptake.
- [L5] Zhao B. et al. (2021). *Reduction of dust deposition in air-cooled condensers in thermal power plants by Ni–P-based coatings.* Clean Technol. Environ. Policy 23, 1727–1736. Coated finned tubes: fouling resistance −83.3 %. (Supports the principle of anti-fouling fin coatings; not the O2T8 coating.)

**Vendor and trade**
- [V1] Fayard E.H. (Conco Systems), *ACC Pressure Cleaning*, Power Engineering, May 2010. https://www.power-eng.com/coal/acc-pressure-cleaning/. Saranac Power, cottonwood seed fouling; high-pressure water up to 1,800 psi; fire hoses, hand lances and chemicals rejected for fin-damage and environmental reasons; "full operating efficiency" restored (no numbers).
- [V2] CTP, DECAMEX process. https://www.ctp-environnement.com/en/decamex and https://ctpenvironment.com/decamex/
- [V3] CTP, Malaysian LNG reference (336 bundles, one fan at a time). https://www.ctp-environnement.com/en/reference/33/online-cleaning-of-air-coolers
- [V4] CTP, Thai cogeneration reference (+63 % vs +14 %, limestone from hard-water washing). https://www.ctp-environnement.com/en/reference/34/online-cleaning-of-air-fin-coolers
- [V5] CTP, French steelworks reference (> 15 %). https://www.ctp-environnement.com/en/reference/19/online-cleaning-of-air-coolers
- [V6] Baker Hughes, *SureFOAM fin fan cleaning service* (competitor statement on high-pressure washing). https://www.bakerhughes.com/processing-services/downstream-chemical-solutions/flexible-downstream-chemical-refining-solutions/surefoam-fin-fan-cleaning-service
- [V7] Primasonics PAS-120 data pack (148 dB sound power, 120 Hz) and BHSL case study. https://www.primasonics.com/wp-content/uploads/2022/10/PAS-120-Data-Pack.pdf, https://www.primasonics.com/case-studies/bhsl/

**Project files**
- [R1] `a1401_solutions_check/SIMULATION_REPORT_v2.md` and `results_v2/` (hot-day and 2025 season results).
- [R2] `a1401_solutions_check/A1401_Detailed_Engineering_Protocols_2_corrected.md`, `A1401_Solutions_Defense_Summary_2_corrected.md` (S1).
- [R3] `a1401_solutions_check/A1401_Detailed_Engineering_Protocols_corrected.md`, `A1401_Solutions_Defense_Summary_corrected.md`, `CHANGES_v2.md` §2 (S2, 200 °C vs 170 °C).
- [D1] `A-1401_PFD_and_thermal_diagnosis.md` (forced draft, fans blow upward; cleaning dates from Air Liquide; method not stated). `A-1401_solution_plan.md` (304L tubes, aluminium rolled fins, 6 rows).
- [D2] `weather/atyrau_precip_temp_2023-01-01_2026-11-14.csv`, hourly 2 m temperature, 2023–2025: monthly minimum ≥ 5.1 °C in May–Sep; share of hours below 0 °C: Nov 11 %, Dec 67 %, Jan 75 %, Feb 81 %, Mar 19 %.
