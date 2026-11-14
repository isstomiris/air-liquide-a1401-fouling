# A-1401 Performance Monitoring Model (hybrid: physics + data-driven)

*Shared by Solution A (monitoring + sonication) and Solution B (monitoring + dry projection). It tells operators **when** to clean.*

## The idea in one paragraph

Fouling can't be measured directly, and outlet temperature alone is misleading: it changes with weather, load and fan speed. So we first use our **physics model** to turn every reading into one **health number**, the equivalent fin blockage (%). Then a **data-driven forecaster** predicts that number 7, 14 and 30 days ahead, with an uncertainty band. When the upper band says the blockage will cross **40 %** (the "cliff"), the system raises a **"plan cleaning"** alarm.

The forecaster borrows the idea of *multi-step-ahead prediction with uncertainty* from Benaggoune et al., *Applied Energy* 313 (2022) 118835, a fuel-cell prognostics paper. We did **not** copy its deep network (a dilated CNN). That network learned from about 1,000 hours of lab ageing data. We have only one week of plant data, so a deep network would memorise noise. We use gradient boosting instead, which is suited to small data, and we are open about this choice.

## Steps and files (`monitor/`)

| Step | What it does | File | Run time |
|---|---|---|---|
| 1. Health indicator | Physics model → cleanliness factor CF and equivalent blockage φ, from TIA050, TICA0055, FI010, TY0055 + air temperature | `health_indicator.py` | ~2 min once, then 0.2 s per reading |
| 2a. Fast lookup | Pre-computes the model on a 1,080-point grid so a year of data takes seconds | `build_surrogate.py` → `surrogate_Tout.json` | ~10 min once |
| 2b + 3. Forecaster + backtest | Synthetic plant (Jan 2025 – Nov 2026), real cleanings (Sep 2025, Jul 2026), sensor noise; trains on the first two fouling cycles and tests on the unseen Jul–Nov 2026 cycle | `backtest.py` → `backtest_results.json`, `backtest_daily.csv` | ~10 s |
| 4. Charts | Backtest picture and error vs simple methods | `make_monitor_charts.py` → `chart6_backtest.png`, `chart7_forecast_error.png` | ~5 s |

## Results

**On real plant data (1 Jan 2026, 00:00–02:32, every 2 min, 45 points):** the health indicator is steady. CF = 0.40 ± 0.007 and blockage = 64 % ± 0.6 %. The full solver gave 68 % for the same data; the 4-point gap comes from the quick lookup table, which was built at November conditions. The indicator moves much less than a real fouling trend would, so a trend would be visible.

**Backtest on the unseen cycle (15 Jul – 13 Nov 2026), real Atyrau weather:**

| | 7 days ahead | 14 days ahead | 30 days ahead |
|---|---|---|---|
| Our forecaster, average error | **1.7 %** | **2.5 %** | **3.5 %** |
| "No change" (today = future) | 2.4 % | 4.6 % | 9.1 % |
| Straight-line trend | 2.2 % | 4.5 % | 12.1 % |
| True value inside the 10–90 % band | 39 % of days | 50 % | 60 % |

- **Alarm:** raised on 16 Jul, **17 days before** the blockage crossed 40 % (2 Aug). There were **0 false alarms**.
- **Health indicator error vs the true blockage:** about 1 % (RMS).

## Honest limits (say these on the slide)

1. **Weather is real:** hourly ERA5 temperature and wind for Atyrau (`weather/` CSV). Debris arrives faster on windy days, using the real daily wind, and the forecaster uses 7-day wind as an input.
2. **The plant is synthetic.** The debris build-up is our guess: dust all year, plus organic debris peaking in late June. It is calibrated so the blockage reaches 65 % on 14 Nov. The backtest checks the *method* (noise handling, forecasting, alarm logic). It does not check whether the physics model is exactly right; that uncertainty is the 31–78 % range in the diagnosis.
3. **The uncertainty band is too narrow.** The true value falls inside the 10–90 % band 39–60 % of the time instead of 80 %, because we had only two training cycles. More real cycles will fix this.
4. **The alarm can't fire in the first 14 days after a cleaning,** because the trend needs data. In peak season the blockage can reach 40 % within about a month of a cleaning.

## What would make it real

Hourly data for **1 Jul – 14 Nov 2026** (TIA050, TICA0055, FI010, TY0055, PV0017) gives one real clean-to-dirty cycle after the TAR. The same code runs on it: replace the synthetic plant with the real readings in `backtest.py`.
