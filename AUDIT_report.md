# Audit of the A-1401 work: how honest, how correct, what is overstated

*Independent check, 14 Nov 2026. I did not change any of the original files.*
*Files checked: `A-1401_solution_plan.md`, `A-1401_PFD_and_thermal_diagnosis.md`, `model/`, `pfd/`, `a1401-3d/`, against the case files in `catalyst/`.*

---

## The short answer

**Nothing was made up.** Every number labelled as plant data matches the real files: the PI exports, the PI Vision screenshot, the datasheet on the GA drawing, the inspection act and the lab sheet. The code runs, and when I re-ran it I got the same results to the last digit. I also checked the heat-balance numbers with my own separate calculation, and they agree.

**The weak spot is confidence, not honesty.** The work says some things are "robust" or "validated" when they rest on one snapshot and a few assumptions that were never tested. Three conclusions are much shakier than they sound:

1. **"65 % of the fin gaps are blocked"** really means "65 %, *if* the flowmeter is right and the model is right". If the real gas flow is 25–50 % higher than FI010 shows (and the Air Liquide representative said FI010 usually under-reads), the same data gives **31–50 %** blockage. The 25 % flow case is my own estimate, not a measurement.
2. **"The model matches the design within 3 %"** is not an independent check. The design air temperature is not on the datasheet. The work picked 35 °C, and 35 °C happens to give the 3 %. At 30 °C the gap is 15 %, and at 38 °C it is 4 %.
3. **"540 t of H₂ lost per year"** is a worst case. It assumes today's fouling, today's 167 °C inlet and today's gas flow stay the same all year. The document does call it an "upper bound", but it is shown in bold as a headline.

What I would say on stage: *"Today the cooler has almost no reserve left. Our model says production becomes limited above about 13 °C outside air if nothing changes. Our best estimate of the cause is heavy air-side blockage, about 50–65 %, but this rests on one data point."*

### Severity scale

| Level | Meaning |
|---|---|
| 🔴 High | Could change a headline conclusion, or a judge could take it apart |
| 🟠 Medium | Overstated or unsupported, but the main story survives |
| 🟡 Low | A wording slip or a small inconsistency |

---

## 1. Plant-data claims checked against the source files

| Claim in the work | Source checked | Result |
|---|---|---|
| 1 Jan: T_in 144.7 °C, T_out 69.7 °C, flow 22,862 Nm³/h, fans 54.4 % | PI xlsx files (00–08 h means) | ✅ 144.73 / 69.66 / 22,862 / 54.42 |
| TI026 ≈ 164–165 °C, TI0059 ≈ 58 °C, P ≈ 2.55 MPa | PI xlsx | ✅ 164.9 / 58.3 / 2.55 |
| Each export has 3,600 rows from 1 Jan only (FI010 2.5 h … TIA026 7.5 days) | PI xlsx | ✅ correct |
| TY0055A/B/C identical; sheet C holds 3 stacked copies | PI xlsx | ✅ max difference 0.0; sheet C has 10,800 rows |
| 14 Nov 15:16: TIA050 166.78 °C, TICA0055 66.4 °C, SP 65.0 °C, OP 87.6 %, fans 87.887 %, FI010 20,801, TI0059 56.3 °C, TI083 38.8 °C, PICA0017 2.56 MPa, PV0017 0 % | PI Vision screenshot | ✅ all match |
| Datasheet: 226 / 5,288.4 m², 4.0 MPa, 170 °C, 135/55 °C, 2.69 MPa(g), 3 fans × 114,000 m³/h, 190 Pa, 477 rpm, 9°, Ø2,400, 11 kW, 25–50 Hz, 1,088 L, steam row 21.3 / 498.4 m², manual louvres | GA drawing table | ✅ all match. One detail: the 190 Pa is labelled **total** pressure (полное давление), not static. |
| 276 tubes (worked out from the bare area) | Bundle drawing, bill of materials item 31 "finned tube", qty **276** | ✅ confirmed by the drawing. This was a good inference. |
| TICA0055 is the A-1401 outlet; TIA050 is the inlet | P&ID | ✅ TT0055 sits on the outlet line. (The organisers' xlsx header for TIA0059 says "after A-1401", which is confusing, but the P&ID settles it.) |
| P&ID: two-phase flow; A-1401 design 33 kg/cm², 170 °C | P&ID | ✅ The P&ID also gives operating values of **137 → 60 °C**, which the work did not mention. |
| PFD: 58.385 % load; steam 14,526 + 967.7 kg/h; syngas 20,588; H₂ 12,200 Nm³/h @ 99.836 % | PFD.png | ✅ |
| Hydrotest 7.1 MPa, condition "satisfactory", fit for service (16.10.2025) | Inspection act | ✅ |
| Lab data: Jan–Nov, 55 samples; outliers 10 Mar, 28 May, empty 8 Jul; medians H₂ 74.4, CO₂ 17.9, CO 2.2, N₂ 0.6, CH₄ 4.8 | Lab xlsx (the file name says "Jan_Mar", but it does run to 12 Nov) | ✅ Small slip: the CH₄ median is **4.96**, not 4.8. The effect is negligible. |
| Weather: Atyrau ERA5 statistics (hours ≥ 30 °C 673/744, ≥ 35 °C 101/159, 99 % = 36 °C, max 40.6 °C) | ❓ **No Atyrau weather file exists in either folder.** The only CSV is for the wrong site (48 °N 68 °E), and the histogram is typed directly into the code. | ⚠️ Cannot verify; see M1 |
| Ambient on 14 Nov = 6.5 °C | ❓ The weather script ends on 12 Nov. The plan says this value was taken from the afternoon of **13 Nov**. | ⚠️ See L1 |

**Verdict on honesty:** no plant number was invented or changed. Where a number was assumed, it was usually tagged ⚠️, which is good practice.

---

## 2. Recalculations

I re-ran `run_diagnosis.py` and `run_losses.py` (about 5 minutes) and wrote my own separate heat balance.

| Headline number | Their value | My re-run | My separate calculation | Comment |
|---|---|---|---|---|
| Duty, 14 Nov | 5.3 MW | 5.29 MW | 5.29 MW | ✅ |
| Duty, 1 Jan / design | 3.4 / 2.7 MW | 3.35 / 2.72 | 3.36 / 2.72 | ✅ |
| Share that is condensation | "about 70 %" | 68 % (14 Nov) | 69 % (14 Nov), **56 % (1 Jan), 47 % (design)** | 🟠 M2: only true on 14 Nov |
| Water vapour in, 1 Jan → 14 Nov | 3.2 → 6.1 t/h | 3.24 → 6.07 | same | ✅ |
| Dew point if all the water were vapour | 179 °C | 179.1 °C | 179.1 °C | ✅ |
| Blocked fraction φ, 14 Nov | 65 % | 65.0 % | – | ✅ reproduces, but see H1 |
| φ, 1 Jan | 68 % | 68.4 % | – | ✅ but see H4 |
| Match to design | "within 3 %" | 36,300 vs 35,262 Nm³/h = 2.9 % | – | ✅ arithmetic right, but see H2 |
| Limited from | 13 °C | 13 °C | – | ✅ |
| Hours limited / H₂ lost (2025) | 4,384 h / 540 t | 4,384 h / 541 t | 4,384 = every hour ≥ 13 °C in the histogram | ✅ |
| PSA recovery | 79.6 % | 79.65 % | 12,200 ÷ (0.744 × 20,588) | ✅ |
| Inlet back to 145 °C cuts duty by | "~35 %" | – | **41 %** (5.29 → 3.13 MW) | 🟡 they *under*-stated it |
| "Dry-gas model underestimates duty by 3–4×" | 3–4× | – | **4.2× to 6.4×** | 🟡 L3 |

**The arithmetic and the code are correct.** The problems are in which assumptions were chosen and how sure the text sounds.

---

## 3. Findings

### 🔴 H1. "59–67 % in every case, the conclusion doesn't depend on the guesses" is overstated

The 65 % comes from **one snapshot** (14 Nov, 15:16). There is one equation and one unknown, so **every error in the model, and every wrong input, ends up inside φ.** The sensitivity table changed each input only a little, and it left out the most uncertain ones. I re-ran the model with wider, still realistic, changes:

| Change (one at a time) | φ |
|---|---|
| Base | 65 % |
| Air-side coefficient (Briggs & Young) 20 % lower / higher; these correlations are typically only good to about ±20 % | **58 % / 69 %** |
| Flatter / steeper fan curve | 62 % / 67 % |
| Design ambient 30 °C instead of 35 °C (model re-tuned to match the design) | **56 %** |
| Real gas flow +25 % | **50 %** |
| Real gas flow +50 % | **31 %** |

Only +10 % flow was tested, yet §9 of the plan says the representative told us FI010 is "only correct when no gas is flared, which is usually not the case". On 14 Nov PV0017 was at 0 %, but the screenshot also shows a second flare route (**UV0071**) whose position we cannot see, and a second flow reading of **20,949 Nm³/h**. So "FI010 is OK that day" is likely but not proven.

**Why it matters:** because of the "cliff", 35 % blockage gives **zero** lost production and 65 % gives 540 t. A few points of error in φ swing the economics from nothing to everything.

**Fix:** show φ as a range (about 30–70 %, most likely 55–65 %), and say plainly that it comes from one data point.

### 🔴 H2. The "3 % match to design" is not a validation

- The datasheet gives 135 → 55 °C, but **no design air temperature and no design gas flow**.
- The design flow was inferred as 20,588 ÷ 0.58385 = 35,262 Nm³/h. This assumes the syngas flow scales with "plant load", which is reasonable but is still an assumption.
- The design air temperature of 35 °C was **chosen** by the work. The model's capacity is 40,382 Nm³/h at 30 °C (15 % off), 36,300 at 35 °C (3 % off) and 33,776 at 38 °C (4 % off).

So "our equations are trustworthy" is circular: one free choice (35 °C) was set, and that choice produced the 3 %. It shows the model is *plausible*, not that it is *validated*.

**Fix:** say "consistent with the datasheet if the design air temperature was about 35 °C, which is typical for the region".

### 🔴 H3. Water content: a number from the PFD was used, and a conflicting number on the same PFD was ignored

The water-to-dry-gas ratio (0.555) comes from the PFD steam flows. The same PFD also shows the hydrocarbon feed (NG 4,127 Nm³/h + LPG 4,168 kg/h). When I did the **carbon balance** that the plan itself proposed (§9) but never carried out:

- carbon in the feed ≈ 480 kmol/h
- carbon in the syngas at 20,588 Nm³/h ≈ 229 kmol/h

That is a **factor of 2 mismatch**, and it would imply a steam-to-carbon ratio of about 1.8, which is unusually low for steam reforming. So the PFD numbers do not agree with each other. Something on that slide means something we don't understand (perhaps part of the feed goes elsewhere).

**Why it matters:** the "~70 % condensation" result needs at least **0.36 mol water per mol dry gas**, so that the gas is saturated at 167 °C. If the real dry flow were 1.5× higher, the same steam balance would leave only about 0.24, and the 14 Nov duty would drop from 5.3 MW toward about 4 MW. The ±20 % range shown in the plan does not cover this. Within ±20 % the duty only moves 5.1–5.5 MW, so the claim survives *if* the steam balance is right.

**Fix:** state that the water content rests on the steam balance alone, that the PFD carbon balance does not close, and ask Air Liquide for the condensate flow from D-1403. The work already suggests asking for this.

### 🔴 H4. The January result was explained away, and it actually weakens the "debris season" story

The model gives **68 % blockage in January** and **65 % in November**. Taken at face value, that means the cooler did **not** get dirtier through the 2026 cottonwood and insect season. The rise in fan speed from 54 % to 88 % is explained almost entirely by the hotter inlet (3.4 → 5.3 MW of duty), not by new fouling.

The document waves this away: "in winter the manual louvres are usually partly closed". There is **no louvre-position data** to support that. Two other explanations were not mentioned:
- the bundle was already fouled from summer 2025 and never cleaned (quite plausible)
- the clean model is simply too optimistic, so it "sees" fouling that isn't there

Also, the plan says the fan rise is "part hotter inlet, the rest lost air-side performance". The model's own numbers say almost all of it is the hotter inlet.

**Fix:** present the January result honestly. "Both dates show similar air-side loss. The bundle may have been fouled all year, or our clean model is optimistic. The big change between January and November is the inlet temperature."

### 🟠 M1. Weather statistics can't be reproduced

Every "hours per year" number comes from a histogram typed into `run_losses.py` / `run_diagnosis.py`. **No Atyrau weather file is saved** in either folder; the only CSV is for the wrong location. The `atyrau.txt` script stops at 12 Nov. The histograms do add up correctly (8,760 h for 2025, 7,584 h for 2026), and the hours ≥ 30/35 °C match the text. I could not re-download ERA5 to check, because the network here blocks Open-Meteo.

**Fix:** re-run `atyrau.txt`, save the CSV in the folder, and have the code read it instead of typed-in numbers.

### 🟠 M2. "About 70 % of the cooler's work is condensing water" is only true for 14 Nov

The share is 69 % on 14 Nov, 56 % on 1 Jan and 47 % at the design point. The correct general statement is: "**half to two-thirds** of the duty is condensation, rising with inlet temperature".

### 🟠 M3. "540 t H₂/yr" depends on worst-case choices

The bottleneck *temperature* (about 13 °C) is fairly solid. It is anchored to a real observation: fans at 88 % at about 6.5 °C leave little room. When I re-tuned the model for a 30 °C or 38 °C design, the threshold stayed at 13 °C. But the 540 t also assumes:
- the inlet is 167 °C **all year**, although it was 145 °C in January and the summer value is unknown
- fouling is constant all year, although the work itself says fouling builds up and is reset at cleaning
- the plant would otherwise run at 20,800 Nm³/h for every one of those hours

There is no summer plant data to show production was actually cut in 2025 or 2026. The caveat is in the text, but the bold headline invites the judges to take it as a forecast.

**Fix:** give a range ("from about 0 t if the inlet is restored, up to about 540 t if today's conditions persist") and put "upper bound" right next to the number.

### 🟠 M4. "Fan power falls as the bundle clogs → free monitoring signal" comes from the assumed fan curve

This comes from the made-up generic fan curve (a = 1.6, b = 0.6), not from fan data. Many real axial fans draw about the same power, or even more, as flow drops toward stall. Even inside the model the signal is tiny until blockage is severe: 9.26 kW clean, 9.18 kW at 30 % blocked, 8.47 kW at 50 %, 7.24 kW at 65 %. It cannot give an *early* warning.

**Fix:** say "may fall; to be confirmed with fan current data", and don't rely on it for early detection.

### 🟠 M5. "Fix E-1408, it's the cheapest solution" skips why the inlet is hot

The P&ID shows a **temperature-controlled bypass on E-1408** (TIC053 / TV053). The 167 °C inlet may be a deliberate operating choice (for example, to protect the condensate or deaerator side), not E-1408 fouling. TI026 for November is unknown, so we can't tell. Restoring 145 °C would cut A-1401 duty by about 41 %, which is a real lever, but its cost and side effects are unknown.

**Fix:** frame it as "an upstream lever to investigate", not "the cheapest solution".

### 🟠 M6. Flow and PSA recovery contradict each other between the two documents

The plan (§9) says that with "typical 85–90 % PSA recovery" the H₂ balance gives 18,000–19,500 Nm³/h, "consistent with 20,588". In fact that would mean FI010 *over*-reads, which is the opposite of the representative's hint. The diagnosis then uses **79.6 %** recovery, back-calculated from the same PFD numbers, so it agrees with 20,588 by construction.

**Fix:** use one consistent story, and admit that the H₂ balance cannot tell us the true flow on its own.

### 🟠 M7. Uncited "literature" values

- "R_d 0.0005–0.002 m²K/W … range in the literature, consistent with API 661" has no citation.
- "0.047 is 25× more than any realistic dust layer" depends on that uncited upper bound.
- "ERA5 … validated against WMO stations" and "the regional flowering/insect calendar of the lower Ural valley" are also unsourced.

The *conclusion* (blocked airflow matters more than insulation) is physically sensible, but the "25×" sounds more precise than it is.

**Fix:** cite a source or soften to "much larger than typical published values".

### 🟡 Low-severity items

- **L1.** The 14 Nov ambient (6.5 °C) is from 13 Nov. Its effect is small: +2 K changes φ by 1 point.
- **L2.** The January ambient is −2 °C in the code, but the plan says −3 to −8 °C. Its effect is small.
- **L3.** "Underestimate by 3–4×" should be 4–6×.
- **L4.** Fin geometry (57 mm, 0.4 mm Al, 423/m) is an *assumption* (A12), but the 3D viewer says "**Real scale**: fins 57 mm across". The work never read the fin detail from the bundle drawing, which the plan listed as a to-do (A4).
- **L5.** "Fan power 9.3 kW, consistent with the 11 kW motor ✓" is circular, because the fan efficiency (65 %) was assumed to make it fit.
- **L6.** In `results.json` the key `"CF"` holds 2.06 (the inverse). The document correctly reports 0.49, but anyone reading the JSON will be confused.
- **L7.** The flow anchor for 1 Jan averages only 00:00–02:34 (all of the FI010 data), while the temperatures use 00:00–08:00.
- **L8.** The model uses the datasheet's 190 Pa as if it were static pressure; the datasheet says total pressure.
- **L9.** The P&ID operating values (inlet 137 °C, outlet 60 °C) are a second design reference that wasn't used.

---

## 4. What the work did well

- All plant numbers are traceable and correct. Assumptions are numbered and mostly labelled.
- It spotted real data problems: truncated PI exports, the wrong-location weather file, and the stacked TY0055C sheet.
- The core physics is right. Treating the gas as saturated and two-phase is supported by the P&ID "two-phase flow" note and by the D-1403 separator. That is the most important insight in the work, and a dry-gas model would be badly wrong.
- The code is readable, reproducible and gives identical results on re-run.
- It already contains honest caveats ("equivalent blockage includes everything", "upper bound"). The problem is that the headlines don't carry them.

## 5. What to change before presenting (in priority order)

1. Show **φ as a range** with a tornado chart that includes flow ±50 %, air-side h ±20 % and design ambient 30–38 °C (H1).
2. Replace "validated within 3 %" with "consistent with the datasheet at an assumed 35 °C design ambient" (H2).
3. Add one line: "water content from the steam balance; the PFD carbon balance does not close; we need the condensate flow" (H3).
4. Present January honestly: similar blockage in both months, and the main change is the hotter inlet (H4).
5. Show H₂ loss as a **range with the conditions attached** (M3).
6. Save the Atyrau weather CSV and make the code read it (M1).

## How I checked

- Copied the case files and the model into a separate sandbox, so nothing in your folders changed.
- Read all PI xlsx files and the lab sheet with Python. Read the GA, bundle, P&ID, PFD and inspection act as images.
- Re-ran `run_diagnosis.py` (3 min) and `run_losses.py` (1.8 min). Results matched `results.json`.
- Wrote my own heat balance (separate code, same CoolProp property data) for the duties and water numbers.
- Wrote a stress-test script for φ (fan curve, air-side h, design ambient, water content, flow).
- Could **not** check: the ERA5 weather (Open-Meteo is blocked from both machines) and the PSA/flare situation (no data).
