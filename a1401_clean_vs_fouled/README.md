# A-1401 clean vs fouled simulation

A steady-state rating model of the Air Liquide A-1401 air-cooled syngas exchanger (Atyrau). Wet syngas flows inside the tubes and condenses as it cools. Ambient air is blown up through the finned bundle by three fans. The model compares a clean exchanger with fouled ones under identical conditions.

Read `REPORT.md` for the equations, results, verification and limitations.

## Folder contents

| Path | What it is |
|---|---|
| `a1401sim/config.py` | All inputs, with sources (register) |
| `a1401sim/thermo.py` | Wet-syngas enthalpy, water condensation, gas transport properties |
| `a1401sim/airside.py` | Geometry, Briggs & Young air side, fin efficiency, Robinson–Briggs Δp, fan/system curve, blockage model |
| `a1401sim/exchanger.py` | Segmented 6-row × 24-segment, 2-pass crossflow rating |
| `a1401sim/history.py` | Historian parser, frozen-data detection, steady-window selection |
| `run_all.py` | Runs everything: audit, cases, sweep, history fit and hold-out, sensitivity, design check, verification, figures |
| `verify.py` | Energy, material and limit checks; grid check; Peng–Robinson cross-check |
| `figures.py` | All figures |
| `tests/test_model.py` | 7 numerical tests |
| `data/` | Historian workbook and Atyrau ERA5 weather used as inputs |
| `results/` | CSV and JSON results, run log |
| `figures/` | PNG figures (fig0–fig8) |

## How to run on Windows

1. Install Python 3.11 or newer from python.org. Tick "Add python.exe to PATH" during setup.
2. Open the folder in File Explorer, click the address bar, type `cmd` and press Enter.
3. Install the libraries (once):

   ```
   python -m pip install -r requirements.txt
   ```

4. Run the tests (about 10 s):

   ```
   python tests\test_model.py
   ```

5. Run the full study:

   ```
   python run_all.py
   ```

   This takes about 15 s, because the hourly history results are cached in `results\_history_grid_cache.npz`. To recompute the history from scratch (about 10 min on 4 cores), delete that file or run `python run_all.py --fresh`.

On macOS or Linux, use the same commands with `python3` and `/` in paths.

## Main inputs to change

All inputs are in `a1401sim/config.py`. For example:
- `WATER_TO_DRY_BASE`: water per mole of dry gas
- `H_CONDENSATE_FILM`: condensate film coefficient
- `FAN`: fan curve shape
- `SYSTEM_SHARE_OTHER`: share of fan pressure lost outside the bundle

The cases and the blockage values are set in `run_all.py`, section 4.

To rate one condition from Python:

```python
from a1401sim.exchanger import rate, scalar
r = rate(T_in_C=159.4, flow_nm3h=17444, T_amb_C=31.8, speed=1.0, b=0.30)   # b = blocked fraction of air passages
print(r["T_out_C"], r["Q_total_kW"], r["air_m3h"], r["UA_total_kW_K"])
```

## What was not done

DWSIM was not available in the environment where this was built, so it was not run. `REPORT.md` §6.2 gives an independent Peng–Robinson cross-check instead, and the steps to repeat the check in DWSIM.
