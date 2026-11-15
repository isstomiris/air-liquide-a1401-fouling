# Air cooler A-1401: why it loses cooling, and how to fix it

Our team's solution to the **Air Liquide process-engineering case** (AIChE Student Chapter hackathon, 14–15 Nov 2026).

**The problem in one paragraph.** A hydrogen plant in Atyrau cools its hot syngas in an air cooler called A-1401: fans blow outside air across finned tubes. Dust, plant fluff and insects clog the fins every summer, so less air gets through, the gas leaves the cooler too hot, and the plant has to cut production on hot days. We worked out how much the clogging costs, built a model of the cooler, checked it against three years of real plant data, and designed a cleaning plus monitoring programme that tells operators when to clean before production is lost.

> This repository is **private**. The plant history in `plant_history/` is Air Liquide data given to us for the hackathon. Please do not make the repository public without checking that it is allowed.

## Start here

| File | What it is |
|---|---|
| [`A-1401_solution_plan.md`](A-1401_solution_plan.md) | The full solution. Its first section explains everything in plain language. |
| [`A-1401_PFD_and_thermal_diagnosis.md`](A-1401_PFD_and_thermal_diagnosis.md) | The process flow diagram and the heat-transfer diagnosis: how much airflow and cooling the clogging takes away. |
| [`AUDIT_report.md`](AUDIT_report.md) | Our own check of the numbers and assumptions. |
| [`deck/index.html`](deck/index.html) | The presentation slides (open in a browser). |
| [`a1401-3d/index.html`](a1401-3d/index.html) | An interactive 3D model of the cooler (open in a browser). |

## What each folder holds

| Folder | Contents |
|---|---|
| `model/` | The heat-transfer model of the cooler (`a1401_model.py`), the scripts that run the diagnosis, the losses and the uncertainty check, their results (`.json`) and the charts. |
| `a1401_monitor/` | The monitoring program: it estimates how clogged the fins are from plant readings and weather, forecasts when cleaning is needed, and makes an HTML dashboard. See its own `README.md`. The `.pkl` files are the trained forecaster, saved so you don't have to retrain it (training takes several minutes). `out/` holds example dashboards and backtest results. |
| `monitor/` | An earlier, simpler version of the monitoring model and its backtest. Kept for reference. |
| `pfd/` | The process flow diagram of the A-1401 section (`.png`, `.svg`) and the script that draws it. |
| `plant_history/` | Hourly plant data, Nov 2023 – Nov 2026: the original Excel export, a cleaned CSV, and two cached `.pkl` versions the scripts load faster. |
| `weather/` | Hourly weather for Atyrau (temperature, humidity, wind, rain) from Open-Meteo, used by the model and the monitor. |

## Running the code

You need Python 3 and these libraries:

```bash
pip install numpy pandas scipy scikit-learn matplotlib openpyxl
```

Then, for example:

```bash
cd model && python run_diagnosis.py          # heat-transfer diagnosis
cd a1401_monitor && python real_backtest.py  # test the monitor on the real plant history
```

## Tools and outside material we used (not included here)

- PFD drawing helper `pfd/pid_lib.py` comes from [claude-manufacturing-skills](https://github.com/ScottDuncanAI/claude-manufacturing-skills) by Scott Duncan (MIT licence).
- Slide and design skills: [anthropics/skills](https://github.com/anthropics/skills), [frontend-slides](https://github.com/zarazhangrui/frontend-slides) and [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill).
- Weather data: [Open-Meteo](https://open-meteo.com/) (ERA5 reanalysis).

## Final presentation and calculations (15 Nov 2026)

| File | What it is |
|---|---|
| [`deck/final.html`](deck/final.html) | Final 20-slide deck. Open in a browser; arrow keys to move, **N** for speaker notes. |
| [`docs/calculations.pdf`](docs/calculations.pdf) | Every calculation on the slides with its justification (LaTeX source: `docs/calculations.tex`). |
| [`a1401_solutions_check/`](a1401_solutions_check/) | Solution simulation (`simulate_solutions_v2.py`), comparison matrix, protocols and defence summaries. |

## Plant data

The raw Air Liquide plant exports (historian workbook, hourly history, hourly model inputs) are not published in this repository because the data belongs to Air Liquide. Scripts that read `plant_history/` or `a1401_clean_vs_fouled/data/historian_full.xlsx` need those files placed back locally. Derived daily and monthly results, figures and all code are included.
