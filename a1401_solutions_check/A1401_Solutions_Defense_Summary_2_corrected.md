# A-1401 — Two selected solutions for the defense

**Revised 15 November 2026: airborne sonic horns replace the contact-ultrasound array as Solution 1's primary trial architecture. Corrected 15 November 2026 (thermal results on the project's wet model; sources re-checked; see `CHANGES_v2.md`).** This summary and the companion protocol omit the requested economic and formal hazard registers. All numerical benefits below are conditional scenarios, not measured A-1401 results.

The main bundle has 276 nominal 25 × 2 mm stainless base tubes, 10.5 m long, six rows, 5,288.4 m² tabulated extended surface and three fans. The separate heating bank has carbon-steel base tubes and is excluded. The exact main fin alloy remains unverified. Sources: bundle drawing VP-3212-A-1401-0010, p.1/C–C/BOM item 31; main passport pp.3/5; fan certificate p.32.

**Plant basis (project wet model and full hourly history, Nov 2023 – Oct 2026).** Reference hot-day window 18 Jul 2025: inlet 159.4 °C, 17,444 Nm³/h dry gas, air 31.8 °C, fans 100 %. A clean bundle would give 4,244 kW (56 % from water condensation) and a 36.7 °C outlet. At the end of summer 2025 the plant behaved as 68.5 % equivalent blockage: 3,530 kW, 75.2 °C. About 59 % of that is a base present every spring; about 9 points (12 in 2024) is debris added from late April to late June. The existing cleaning removed at least that seasonal debris both times it was measured: October 2025 (to 55.7 %) and the 27 Jun – 7 Jul 2026 turnaround (to 57.4 % for Jul–Sep 2026). "Equivalent blockage" is the fraction of air passages the model must close to reproduce the measured outlet. It includes debris, louvres, fan wear and model offset; it is not a measured debris coverage. Both solutions are credited only on the seasonal debris.

## Solution 1 — Passive coating, airborne sonic horns and debris collection

### 1. Selected technology

**O2T8 octyl-silica research coating + three proposed Primasonics PAS-120 compressed-air acoustic horns + traversing vacuum collection.** O2T8 uses 20:80 molar OTES:TEOS. The film is passive. Horns transmit pressure oscillations through air; no piezoelectric array is attached to the bundle.

### 2. One-paragraph description

We propose testing a 0.30 µm O2T8 coating on the main bundle's external fin surfaces, targeting 80 % equivalent coverage of the tabulated extended area, or 4,230.72 m². Three independently sequenced acoustic horns, one per nominal fan sector, would loosen deposits through airborne sound while a traversing extraction hood removes released material toward the incoming-air face. The coating is intended to reduce adhesion; it cannot prevent fibres from mechanically interlocking. Initial application requires qualified workshop treatment of the removed bundle, including the published 200 °C cure. Routine cleaning would isolate one local fan at a time (about 20 min per sector) and use temporary acoustic skirts and collection. The full combination remains an experimental proposal.

### 3. Research or industrial precedent

Primasonics reports a Q1 horn (not the PAS-120) maintaining temperatures in BHSL's combustion-gas/air heat exchanger on a poultry-manure boiler, using 10-second bursts during the day. This is ash in an enclosed boiler pass, not outdoor cottonwood in an open fin fan, and no numerical result is given. On a nanosilica-coated flexible PVC film, sonic excitation (best at 64 Hz) improved optical transmittance by 77 % (Abubakar et al., 2020); this is not a passage-clearance percentage. O2T8 was dip-coated to about 0.31 µm on polished aluminium and cured at 200 °C for 2 h; it lost about 46 nm and part of its water repellency during 7 hours of steam condensation (Basso et al., 2023). No cited source validates the complete proposed system on A-1401.

### 4. Expected effectiveness (assumed)

**Evidence:** industrial sonic cleaning is credible for some dry deposits; the coating's incremental benefit and penetration through organic mats are unresolved. **Scenario assumptions:** net removal of 4 %, 21 % or 57.6 % of the reachable seasonal debris per event (c = 0.2 / 0.5 / 0.8 reached), 24 events per year spread over May–September, and a 1 % installed heat-transfer penalty. These are sensitivity cases, not literature-derived predictions. During July–September the bundle then holds 0.671 / 0.642 / 0.613 equivalent blockage instead of 0.685.

### 5. Performance (wet model, reference hot-day window)

| Case | Equivalent blockage | Air m³/h | UA kW/K | Q kW | Outlet °C | Max gas at 65 °C, Nm³/h |
| --- | --- | --- | --- | --- | --- | --- |
| Clean reference (model) | 0 | 342,000 | 106.5 | 4,244 | 36.7 | 32,110 |
| No action, end of summer 2025 | 0.685 | 153,400 | 62.5 | 3,530 | 75.2 | 15,430 |
| low | 0.671 | 159,400 | 63.9 | 3,585 | 72.5 | 15,920 |
| **base** | 0.642 | 171,400 | 67.2 | **3,696** | **67.1** | 17,000 |
| high | 0.613 | 183,000 | 70.2 | 3,787 | 62.4 | 18,050 |

Base benefit: **+166 kW (+4.7 %) and an 8.1 K lower outlet**, recovering 53 % of the seasonal duty loss and giving **+10 % gas capacity** at the outlet target (the same at 60, 65 or 70 °C). Over the 2025 season, hours above 65 °C fall from 2,651 to 1,921. Doubling to 52 events per year adds little (−0.4 K), because reach limits the benefit. If the horns clear nothing, the 1 % penalty makes the cooler slightly worse (+0.3 K). For comparison, the previous Solution 1 (Aculon coating + piezoelectric modules, daily) gave 64.2 °C and +221 kW on its own central assumptions.

Base material preparation is 110 L sol, retaining approximately 1.90 kg dry film. The proposed event uses 15.30 vendor-standard m³ compressed air and approximately 5.17 kWh including extraction; workshop curing (about 750 kWh, electric oven, base case) is a separate initial utility.

### 6. Main advantages and disadvantages

Advantages: commercial horn hardware, few bundle attachments, potentially repeatable dry cleaning during the debris season, short fan stops, and explicit collection of released debris. Disadvantages: open-air acoustic leakage, intrusive noise, uncertain removal of interlocked fibres, coating durability (tested only for 7 h of steam condensation), access limitations, and the weakest modeled benefit of the options considered. The 200 °C research cure exceeds A-1401's 170 °C design wall temperature. It needs OEM acceptance for unpressurised workshop treatment, depends on the unknown fin-to-tube bond type, and needs an oven for a 10.6 × 3.0 m, about 10.3 t bundle. Spray application alone does not establish coating compatibility or avoid curing.

### 7. References

- [Primasonics PAS-120 data pack](https://www.primasonics.com/wp-content/uploads/2022/10/PAS-120-Data-Pack.pdf), detailed specifications p.4; summary air-consumption units conflict (L/min vs L/s) and require confirmation.
- [BHSL industrial heat-exchanger case](https://www.primasonics.com/case-studies/bhsl/).
- Basso, M., Colusso, E., Tancon, M., Bortolin, S., Mirafiori, M., Guglielmi, M., Del Col, D., Martucci, A. (2023). Hydrophobic hybrid silica sol-gel coating on aluminium: stability evaluation during saturated vapour condensation. *J. Non-Cryst. Solids: X* 17, 100143. [DOI 10.1016/j.nocx.2022.100143](https://doi.org/10.1016/j.nocx.2022.100143).
- Abubakar, A. A., Yilbas, B. S., Al-Qahtani, H., et al. (2020). Environmental dust repelling from hydrophilic/hydrophobic surfaces under sonic excitations. *Sci. Rep.* 10, 19348. [Link](https://www.nature.com/articles/s41598-020-76418-2).
- Riera, E., Gallego-Juárez, J. A., Mason, T. J. (2006). Airborne ultrasound for the precipitation of smokes and powders and the destruction of foams. *Ultrason. Sonochem.* 13, 107–116. [PubMed](https://pubmed.ncbi.nlm.nih.gov/16112596/).

## Solution 2 — CTP DECAMEX dry cleaning

### 1. Selected technology

**CTP's proprietary DECAMEX powder-projection service**, its feed/lance equipment, compressed-air supply and a proposed local residue-collection arrangement. Powder chemistry and delivery settings remain supplier-controlled.

### 2. One-paragraph description

We propose a vendor-executed treatment of the main six-row bundle in three sequential fan sectors, covering approximately 31.56 m² gross projected footprint. A representative 0.50 m² full-depth patch establishes dose, fibre-mat removal and material compatibility before extending the treatment. Fine dry powder is projected using CTP's controlled low-pressure process; temporary extraction and catch trays collect released material where compatible with the vendor method. One forced-draft fan is stopped at a time: in the current bundle state that raises the outlet by about 30 K at constant gas flow for about 1.6 h per sector, so the campaign needs a cool (night) window or a temporary load reduction. Heating-bank treatment is excluded. Central schedule: two campaigns, 1 June and 1 July, matching the measured deposition period.

### 3. Research or industrial precedent

CTP's Malaysian LNG reference covers about 336 bundles, up to four bundles/day, and states that forced-draft units need only one fan stopped at a time. Its Thai mineral-scale comparison reports a 63 % airflow increase with DECAMEX versus 14 % with baking soda. CTP states treatment of air coolers with up to 12 tube rows from the platform underneath, and a Gulf Coast LNG campaign of 820 fin fans in 2023. These vendor results support industrial applicability, but do not establish cottonwood clearance, powder dose or A-1401 duty recovery.

### 4. Expected effectiveness (assumed)

**Evidence:** established industrial multi-row cooler cleaning; no quantified comparable organic-mat removal found. **Scenario assumptions:** 24.5 %, 64.8 % or 93.1 % net clearance of the seasonal debris per campaign. None is derived from the Thai 63 % airflow result. For comparison, the plant's existing cleaning removed at least 100 % of the seasonal debris each time it was measured. With two campaigns the bundle holds 0.658 / 0.620 / 0.599 during July–September.

### 5. Performance (wet model, same reference window)

| Case | Equivalent blockage | Air m³/h | UA kW/K | Q kW | Outlet °C | Max gas at 65 °C, Nm³/h |
| --- | --- | --- | --- | --- | --- | --- |
| Clean reference (model) | 0 | 342,000 | 106.5 | 4,244 | 36.7 | 32,110 |
| No action, end of summer 2025 | 0.685 | 153,400 | 62.5 | 3,530 | 75.2 | 15,430 |
| low | 0.658 | 164,900 | 65.8 | 3,645 | 69.6 | 16,480 |
| **base** | 0.620 | 180,200 | 69.9 | **3,772** | **63.2** | 17,860 |
| high | 0.599 | 188,500 | 72.0 | 3,830 | 60.1 | 18,600 |

Base recovery: **+242 kW (+6.9 %) and a 12.0 K lower outlet**, recovering 77 % of the seasonal duty loss and giving **+16 % gas capacity**. Over the 2025 season, hours above 65 °C fall from 2,651 to 1,605 (one campaign: 1,876; four campaigns: 1,433). Preliminary resource scenarios are 31.56 / 94.69 / 189.38 kg powder per complete campaign, with 94.69 kg, 1,920 reference m³ air and 258.73 kWh modeled utilities centrally. These are team assumptions, not CTP specifications. Base service occupation is seven hours, with sequential local fan unavailability.

### 6. Main advantages and disadvantages

Advantages: stronger industrial implementation evidence, dry treatment, no bundle removal and no permanent coating/actuation retrofit. Disadvantages: proprietary quantities, consumables, a one-fan stop that costs about 30 K or about 30 % capacity while it lasts, access/collection constraints and unverified performance on intertwined organic debris. Online process operation does not guarantee all fans stay running or that production is unaffected. Residue must be inspected and accounted for.

### 7. References

- [CTP process](https://www.ctp-environnement.com/en/decamex) and [multi-row application description](https://ctpenvironment.com/decamex/).
- [Malaysian LNG application](https://www.ctp-environnement.com/en/reference/33/online-cleaning-of-air-coolers).
- [Thai comparative trial](https://www.ctp-environnement.com/en/reference/34/online-cleaning-of-air-fin-coolers).

## Side-by-side (base cases, reference hot-day window)

| | O2T8 + horns | DECAMEX ×2 | Existing-type cleaning after the season |
|---|---|---|---|
| Outlet, °C (no action 75.2) | 67.1 | 63.2 | 59.6 (model, 1 Jul); 56.9 (measured after the 2026 turnaround) |
| Duty gain | +166 kW (+4.7 %) | +242 kW (+6.9 %) | +310 kW (model); +360 kW (measured state) |
| Gas capacity gain at the outlet target | +10 % | +16 % | +21 % / +26 % |
| Outage | Yes, once (bundle removal, 200 °C cure) | No; one fan at a time, about 1.6 h per sector | Yes (turnaround) |
| Evidence on organic fibres | None | None | Measured on A-1401 (2025, 2026) |

**Interpretation for the defense:** DECAMEX is the more mature near-term cleaning trial and gives the larger modeled benefit. Coating plus airborne sonic cleaning is the development concept. Numerical rankings are consequences of assumed clearance, not proof of field performance. Neither method, as assumed, does better than the existing cleaning performed right after the cottonwood season; their value is that they can be repeated online. The 59 % base, which no cleaning has removed so far, sets the limit of every method that only removes seasonal debris (about 59–60 °C on the reference day). The companion protocol supplies source locations, resource equations and failure cases; the thermal calculation is `a1401_solutions_check/simulate_solutions_v2.py` (`SIMULATION_REPORT_v2.md`).
