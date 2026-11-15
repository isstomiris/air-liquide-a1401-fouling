# A-1401 — Two solutions for the defense

**15 November 2026 · Preliminary engineering proposal · Revision 1 (corrected 14 Nov 2026) · Parts 6 and 7 excluded as requested.**

The companion `A1401_Detailed_Engineering_Protocols_corrected.md` contains the source audit, dimensions, chronological protocols, resource calculations and simplification register. The thermal results in this revision come from the project's wet (condensing) rating model, `a1401_clean_vs_fouled/`, and the solution simulation `a1401_solutions_check/simulate_solutions.py` (`SIMULATION_REPORT.md`). What was changed from revision 0, and why, is listed in `CHANGES.md`. Neither file is a released plant operating procedure. Cost assessment and formal hazard assessment are reserved for other teammates.

**Recommendation:** advance DECAMEX to a vendor-defined field trial, timed at the end of the cottonwood season (late June) and carried out in a cool window, because stopping one fan raises the outlet by about 30 K. Retain coating plus vibration as the innovation/pilot option. There is no verified evidence that either method clears interlocked cottonwood from A-1401. With the assumed clearance, neither method does better than the existing cleaning performed once at the end of June; their advantage is that they can be applied online and repeated during the season. The largest remaining gain lies in the base blockage of about 0.59 that no cleaning has removed so far; an inspection of the bundle after a cleaning is needed to find out what it is.

## Starting point: what the plant data show

| Quantity | Value | Source |
|---|---|---|
| Reference hot-day window | 18 Jul 2025, 17–20 UTC: inlet 159.4 °C, 17,444 Nm³/h dry gas, air 31.8 °C, fans 100 %, measured outlet 72.9 °C | Historian; `a1401_clean_vs_fouled/REPORT.md` §3 |
| Clean bundle at that window (model) | Duty 4,244 kW (56 % condensation), outlet 36.7 °C, UA 106.5 kW/K | `REPORT.md` §5 |
| Plant at end of summer 2025 | Equivalent blockage 0.685; duty 3,530 kW; outlet 75.2 °C; 45 % of rated airflow | `REPORT.md` §5, §6.5 |
| Spring base 2025 | 0.594 | Historian, this check |
| Debris added in one season | +9 points (2025), +12 points (2024), built up from late April to late June | Historian |
| Existing cleaning, October 2025 | 0.682 → 0.557: removed at least the whole seasonal increment; about 24 % recovery of overall U | Historian; diagnosis Part 0 |
| Hypothetical 30 % blockage | Outlet 41.1 °C (+4.4 K vs clean), duty −1.7 %. Mild for this exchanger; used only as an example. | `REPORT.md` §5 |

"Equivalent blockage" is the fraction of air passages that the model must close to reproduce the measured outlet. It includes debris, louvres, fan wear and model offset; it is not a measured debris coverage.

## Solution 1 — Low-adhesion coating plus mechanically coupled piezoelectric vibration

### 1. Selected technology

**Aculon AL-B hydrophobic/oleophobic monolayer** (with AL-A pretreatment only if Aculon requires it for the fin metal), combined with **12 independently addressed, bolt-clamped PZT ultrasonic transducer modules**, compliant fin-contact coupling combs and a movable underside extraction hood. The coating is passive; the actuators supply the cleaning motion.

### 2. One-paragraph description

We propose shop treatment of A-1401's existing 276-tube, six-row main bundle, followed by installation of twelve removable piezoelectric cleaning modules distributed across the three fan sectors. The selected application is immersion, targeting 80 % of the tabulated 5,288.4 m² extended surface, or **4,231 m²**, at a provisional **3 nm** AL-B film thickness. The modules excite the lower-row fins through compliant contacts; performance is credited only where fin-motion mapping confirms useful coupling. During a cleaning window (about 10 min per sector), the affected fan is stopped and local extraction draws loosened material downward into a collector, opposite to the normal upward airflow. Deep-row clearance is not guaranteed. Removing the approximately 10.3-tonne bundle (drawing value, not re-checked in this project) and providing a shop bath are substantial installation requirements.

### 3. Research or industrial precedent

- Aculon's AL-B data sheet gives **2–4 nm thickness** and a **225 °C coating degradation temperature**, recommends dipping, and advises against spraying because the film is "autophobic" [R1]. It names "most metals" as substrates; AL-A pretreatment is stated for certain polymers. No service-temperature, UV or outdoor durability rating is given.
- Wang et al. (2026) recovered **over 97 % of short-circuit current** on a 570 × 540 mm photovoltaic module at about **28 kHz and 10 W** [R2]. Recovery relied on gravity: 97.5–98.5 % at 30–45° tilt but 81 % at 15°. Dust was finer than 48 µm. A horizontal fin bundle has no comparable slope, so this is evidence for the vibration mechanism, not for fin-pack cleaning.
- Neither source establishes A-1401 cottonwood clearance or coating life. The actuator architecture and all clearance values below are proposed, not published results.

### 4. Expected effectiveness (assumed)

Clearance is described by c (fraction of debris reached), d (fraction of reached debris detached per cycle) and e (fraction that leaves the bundle). Conservative / central / optimistic: c = 0.40 / 0.65 / 0.80, d·e = 0.125 / 0.40 / 0.63. These are assumptions. They act on the seasonal debris only, not on the 0.59 base. With daily cycles from May to September, the reachable debris is kept near zero and the bundle holds an equivalent blockage of **0.651 / 0.627 / 0.613** during July–September, instead of 0.685. Permanent hardware adds 0.2 % obstruction of the open face.

### 5. Performance (wet model, reference hot-day window)

| State | Equivalent blockage | Airflow, m³/h | UA, kW/K | Duty, kW | Outlet, °C | Max gas at 65 °C, Nm³/h |
|---|---:|---:|---:|---:|---:|---:|
| No action (end of summer 2025) | 0.685 | 153,400 | 62.5 | 3,530 | 75.2 | 15,430 |
| Conservative | 0.651 | 167,900 | 66.6 | 3,672 | 68.3 | 16,750 |
| **Central** | 0.627 | 177,400 | 69.1 | **3,751** | **64.2** | 17,620 |
| Optimistic | 0.613 | 182,900 | 70.6 | 3,792 | 62.1 | 18,110 |
| Clean bundle (model) | 0 | 342,000 | 106.5 | 4,244 | 36.7 | 32,110 |

Central duty recovery: **+221 kW (+6.3 %)**, 71 % of the seasonal duty loss and 31 % of the loss against a clean bundle; **+14 % gas capacity** at a 65 °C outlet. Over the 2025 season (2,863 hours at full fan speed), hours with an outlet above 65 °C fall from 2,651 to 1,589. If the coating also reduced new deposition by 20–40 % (not evidenced), the outlet on hot hours would fall by a further 1–2 K.

### 6. Main advantages and disadvantages

**Advantages:** acts every day during the cottonwood season; negligible calculated film conduction penalty; measurable zone-level response; no process-side modification.

**Disadvantages:** unproven fibre release from a horizontal bundle; mainly reaches the lower rows (c ≤ 0.8); possible fin-contact wear; daily fan stops; the coating needs an outage, bundle lifting and a large immersion bath (24.2 m³ gross proposed). The shop cleaning before coating is itself a full off-line cleaning; its effect on the base blockage is unknown and not credited. No positive payback is claimed.

### 7. References

- **[R1]** [Aculon AL-B technical data sheet](https://www.aculon.com/pdfs/Aculon%20AL-B%20TDS.pdf).
- **[R2]** Wang, Y., Gao, T., Jiang, M., Gong, J., Xie, X., Song, Z. (2026). [*Efficient Dust Removal and Energy Recovery of PV Modules via Low-Frequency Ultrasonic Vibration: Experiment and Dynamic Analysis*](https://doi.org/10.3390/acoustics8020033). *Acoustics* 8(2), 33.
- Equipment: Air Liquide drawings VP-3212-A-1401-0001 sheet 1 and VP-3212-A-1401-0010 sheet 1, vessel passport (as transcribed in `AUDIT_report.md`).

## Solution 2 — CTP DECAMEX dry chemical cleaning

### 1. Selected technology

**CTP environnement DECAMEX dry chemical cleaning service:** supplier-controlled biodegradable product, dosing/delivery unit, regulated compressed air, treatment lance, optional finishing air blow and a site-specific debris arrangement. It is not generic soda blasting.

### 2. One-paragraph description

We propose a CTP campaign covering the entire main six-row A-1401 bundle through three sequential fan sectors, each divided into four inspection patches. The treatment envelope is about **10.5 × 2.95 m (31 m² projected face)**. The separate winter heating bank is excluded. Supplier personnel apply DECAMEX from below, verify penetration through the rows and perform any finishing blow. For this forced-draft unit the planning case stops one fan at a time [R4]. In the current bundle state that raises the outlet by about 30 K at constant gas flow, so the campaign should run at night or with a temporary load reduction. The illustrative central campaign (our assumptions, not CTP data) uses **46.5 kg product, 1,452 m³ free air, 145 kWh compressor energy** and about **8.8 h** including preparation and checks. Central schedule: two campaigns, 1 June and 1 July, matching the 2025 deposition period.

### 3. Research or industrial precedent

- In CTP's Thai cogeneration case, airflow increased **63 % with DECAMEX versus 14 % with baking soda** at matched product quantity, pressure, duration and distance [R3]. The deposit was mainly limestone from hard-water washing; this does not establish organic-fibre removal.
- CTP's Malaysian LNG contract covers about **336 bundles**, cleaned at up to **four bundles per day**; forced-draft units require **one fan stopped at a time** [R4].
- CTP states the process removes deposits "from all tube rows" and reaches up to 10 m from accessible work areas [R5]. In a dusty steelworks it reports gains "above 15 %" compared with conventional cleaning, applied from below with a final air blow [R6].

### 4. Expected effectiveness (assumed)

Conservative / central / optimistic: c = 0.70 / 0.90 / 1.00, d·e = 0.45 / 0.765 / 0.93 per campaign, giving a net reopening of 31.5 / 69 / 93 % of the seasonal debris per campaign. These are assumptions, deliberately independent of CTP's 63 % airflow result. For comparison, the existing cleaning in October 2025 removed at least 100 % of the seasonal increment, so the central DECAMEX case is below what the plant already achieves per cleaning. With campaigns on 1 June and 1 July, the bundle holds **0.651 / 0.617 / 0.599** during July–September.

### 5. Performance (wet model, same reference window)

| State | Equivalent blockage | Airflow, m³/h | UA, kW/K | Duty, kW | Outlet, °C | Max gas at 65 °C, Nm³/h |
|---|---:|---:|---:|---:|---:|---:|
| No action (end of summer 2025) | 0.685 | 153,400 | 62.5 | 3,530 | 75.2 | 15,430 |
| Conservative | 0.651 | 167,800 | 66.6 | 3,671 | 68.3 | 16,740 |
| **Central** | 0.617 | 181,300 | 70.2 | **3,781** | **62.7** | 17,970 |
| Optimistic | 0.599 | 188,500 | 72.0 | 3,830 | 60.1 | 18,600 |
| Existing-type cleaning moved to 1 Jul | 0.595 | 190,000 | 72.4 | 3,840 | 59.6 | 18,730 |
| Clean bundle (model) | 0 | 342,000 | 106.5 | 4,244 | 36.7 | 32,110 |

Central duty recovery: **+251 kW (+7.1 %)**, 80 % of the seasonal duty loss and 35 % of the loss against a clean bundle; **+16 % gas capacity** at a 65 °C outlet. Over the 2025 season, hours above 65 °C fall from 2,651 to 1,560 (one campaign: 1,822; four campaigns: 1,401).

During a campaign, with one fan stopped: outlet 75 → 105 °C on the reference day; 45 → 76 °C at 20 °C air with the bundle at its spring state.

### 6. Main advantages and disadvantages

**Advantages:** direct industrial air-cooler precedent; online, no bundle removal; temporary service equipment; all-row treatment claimed by the vendor; dry process without a wash-water circuit.

**Disadvantages:** proprietary quantities and settings; organic mats may behave differently from mineral deposits; one fan stopped costs about 30 K or about 30 % gas capacity for the duration of each sector; removed debris and product still need a site-specific material balance. Repeat frequency depends on seasonal loading.

### 7. References

- **[R3]** [CTP Thai comparative trial](https://www.ctp-environnement.com/en/reference/34/online-cleaning-of-air-fin-coolers).
- **[R4]** [CTP Malaysian LNG maintenance case](https://www.ctp-environnement.com/en/reference/33/online-cleaning-of-air-coolers).
- **[R5]** [CTP DECAMEX process and FAQ](https://www.ctp-environnement.com/en/decamex).
- **[R6]** [CTP French steelworks case](https://www.ctp-environnement.com/en/reference/19/online-cleaning-of-air-coolers).

## Side-by-side (central cases, reference hot-day window)

| | Coating + vibration | DECAMEX ×2 | Existing-type cleaning on 1 Jul |
|---|---|---|---|
| Blockage held Jul–Sep | 0.627 | 0.617 | 0.595 |
| Outlet, °C | 64.2 | 62.7 | 59.6 |
| Duty gain vs no action | +221 kW (+6.3 %) | +251 kW (+7.1 %) | +310 kW (+8.8 %) |
| Gas capacity gain at 65 °C | +14 % | +16 % | +21 % |
| Outage needed | Yes, once (bundle removal for coating) | No (one fan at a time) | Depends on the existing method (not documented) |
| Evidence for organic fibre removal | None | None | Measured on A-1401 (Oct 2025) |

## Simplifications to disclose during the defense

1. All clearance values (c, d, e), schedules and resource quantities are scenarios, not vendor or field data.
2. The cleaning methods are credited only on the seasonal debris (about 9 points in 2025). The base of about 0.59 equivalent blockage is not credited; it may include model offset, louvres or permanent damage.
3. One season (2025) defines the debris build-up. The fan curve is generic, fin geometry is assumed, and blockage is taken as uniform over the face.
4. One-fan-stopped results neglect natural draft through the idle sector and are an upper estimate of the penalty.
5. No guaranteed full-scale recovery, coating service life, annual hydrogen gain or financial return is established.
