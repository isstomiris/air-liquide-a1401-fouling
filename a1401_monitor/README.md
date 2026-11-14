# A-1401 predictive monitoring program

Tells operators **how blocked the A-1401 fins are now**, **when the blockage will reach the cleaning trigger**, and **how much production is at risk in the next 30 days**. It serves both solutions:

| | Solution A: monitoring + sonication | Solution B: monitoring + dry projection |
|---|---|---|
| Cleaning trigger | 30 % equivalent blockage | 40 % (just before the "cliff") |
| Why | Acoustic/ultrasonic cleaning works best on loose, fresh deposits, so it runs early and often | Dry projection removes compacted debris, so it can wait longer |

The triggers are assumptions that the team can change in `METHODS` in `monitor.py`.

## How to use it

```bash
pip install numpy pandas scipy scikit-learn matplotlib openpyxl
python monitor.py train                    # once: simulate 60 plants, train and calibrate, backtest (a few minutes)
python monitor.py run --plant "<folder with PI .xlsx exports>" --method dry_projection
python monitor.py demo --asof 2026-07-20 --method sonication    # pretend it is live on that date (simulated plant)
```

Outputs go to `out/`:
- `report_<date>_<method>.html`: the dashboard
- `status_<date>_<method>.json`: the same numbers for a DCS or PI link
- `health_<date>_<method>.csv`: the hourly health indicator
- `backtest.json` + `backtest.png`: the backtest

Weather is read automatically from `../weather/*.csv` (Open-Meteo, Atyrau 47.1 N 51.9 E): temperature and wind are required, precipitation is optional.

## What happens inside (plain words)

1. **Clean the data** (`data.py`). Drop hours with missing tags, low load (< 30 %), flaring (FI010 under-reads then), sudden outlet jumps (not steady), or an inlet that isn't hotter than the outlet.
2. **Health indicator** (`core.py`). For each hour, find the blocked fraction that makes our physics model reproduce the measured outlet temperature, given inlet temperature, gas flow, fan speed and outside air. This takes out the effect of weather, load and fan speed. The physics is the diagnosis model (fin efficiency, Briggs & Young air side, fan and system curves, condensing gas side). It is pre-computed on a 5-D grid (`surrogate5d.json`) so a year of hourly data takes under a second.
3. **Forecast** (`forecaster.py`). Gradient-boosted trees predict the 7-day median blockage 7, 14 and 30 days ahead. The inputs are the current level, its 14- and 30-day slopes, days since the last cleaning, season, recent air temperature, wind, rain and fan speed. The 80 % band uses **conformalised quantile regression**: it is widened until 80 % of outcomes on *other* simulated plants fall inside it. This follows the multi-step-ahead + uncertainty idea of Benaggoune et al. (2022), with a model suited to small data.
4. **Training data** (`simulate.py`). We have only one week of real data, so the forecaster learns from 60 simulated plants. They all use the real Atyrau weather but differ in debris rate, season timing, wind and rain sensitivity, cleaning dates and quality, inlet temperature, flow and sensor noise.
5. **Alarm** (`monitor.py`):
   - **RED**: clean now. The blockage is at the trigger, or the median forecast reaches it within 14 days, or the cooler was flow-limited in the last 3 days.
   - **AMBER**: plan a cleaning. The pessimistic forecast reaches the trigger within 30 days.
   - **GREEN**: no action.
6. **Production at risk**. Last year's weather for the same 30 days, plus the forecast blockage, gives the hours when the cooler cannot hold 65 °C at full fans, and the hydrogen that would be lost.

## Backtest on the simulated plant

`python monitor.py train` ends with a backtest on the **official scenario**: real weather, cleanings in Sep 2025 and Jul 2026, calibrated to 65 % blockage on 14 Nov. The forecaster never saw it. Results: `out/backtest.json`, `out/backtest.png`.

## Backtest on the REAL plant history (`python real_backtest.py`)

Input: `../plant_history/Data (full history).xlsx` (hourly, Nov 2023 - Nov 2026). **Usable: 14 Nov 2023 - 11 Mar 2026** (19,065 clean hours). After 11 Mar 2026 the file repeats one frozen value until 14 Nov, so those rows are not used.

What the real data shows (`out/real_history.png`, `out/real_monthly.csv`):
- **The health indicator rises every May-August:** 54 -> 70 % in 2024 and 62 -> 72 % in 2025. It dropped from 72 % to 60 % after the October 2025 shutdown. So the debris season is real, and a cleaning recovers about 10-12 points.
- **It never goes below about 50 %,** even right after a cleaning. So roughly 50-60 % is a permanent offset (model bias, louvres, or damage that cleaning doesn't fix). Only the part above that baseline is seasonal debris. Triggers on real data must therefore be set relative to the baseline; we used 63 % (sonication) and 66 % (dry projection) with `--trigger`.
- **The plant already loses production in hot weather.** Above 30 C the fans are at 100 % in 100 % of hours and the median flow is 18,800 Nm3/h; at 0-10 C it is 25,500 Nm3/h. Flow and air temperature have a correlation of -0.52.

Forecast accuracy on real 2025-26 data (never used for training; average error in % blockage):

| | 7 days | 14 days | 30 days |
|---|---|---|---|
| Our forecaster | 1.4 | 1.7 | 2.2 |
| "No change" | 1.35 | 1.7 | 2.25 |
| Straight-line trend | 1.7 | 2.7 | 4.3 |
| True value inside the 80 % band | 94 % | 98 % | 96 % |

Honest reading: real fouling moves slowly (about 2 points a month), so the forecaster is **no better than "no change"** and 20-50 % better than a straight-line trend. Its band, calibrated on real 2023-24 data, is safe but a little too wide. The value on real data is the **health indicator and the alarm**, more than the forecast.

## Limits

- The health indicator is an *equivalent* blockage. It also picks up louvre closure, fan wear and hot-air recirculation; only an inspection separates these.
- The forecaster learns its shape from simulated fouling; only its band is calibrated on real data. Real data after 11 Mar 2026 is frozen, so the July 2026 cleaning cycle cannot be checked yet.
- The trigger levels and the debris model are engineering assumptions, and the report states them.
