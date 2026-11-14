"""Synthetic A-1401 plants for training and backtesting.

We only have one week of real plant data, so the forecaster learns from many SIMULATED plants that all
use the REAL Atyrau weather (temperature, wind, rain) but differ in everything we are unsure about:
how fast debris arrives, when the debris season peaks, how often and how well the cooler is cleaned,
inlet temperature, gas flow and sensor noise. The physics (via core.Physics) is the same as the diagnosis.

Debris model (assumption, explained in the report):
  daily dose = (dust + organic season bump) x (wind / mean wind)^w x exp(-r x rain) x random day factor
  blockage  phi = phi_sat x (1 - exp(-cumulative dose since cleaning / D)) + residual left by the cleaning
"""
import numpy as np, pandas as pd

OFFICIAL = dict(name="official", cleanings=["2024-09-15", "2025-09-15", "2026-07-01"], residual=0.0,
                peak_doy=175, width=35, amp=3.0, wind_exp=1.0, rain_k=0.15, phi_sat=0.85, D=None,
                tin_before=145.0, tin_after=167.0, tin_switch="2026-07-01", flow=20800, seed=7)

def random_params(rng, i, start, end):
    # cleanings every 3-10 months, random phase
    cl, t = [], pd.Timestamp(start) - pd.Timedelta(days=int(rng.integers(30, 200)))
    while t < pd.Timestamp(end):
        cl.append(str(t.date())); t += pd.Timedelta(days=int(rng.integers(90, 300)))
    return dict(name=f"sim{i}", cleanings=cl, residual=float(rng.uniform(0, 0.6)), peak_doy=float(rng.normal(175, 12)),
                width=float(rng.uniform(25, 50)), amp=float(rng.uniform(1.5, 4.5)), wind_exp=float(rng.uniform(0.5, 1.5)),
                rain_k=float(rng.uniform(0.0, 0.3)), phi_sat=float(rng.uniform(0.72, 0.85)), D=float(rng.uniform(110, 320)),
                tin_before=float(rng.uniform(140, 168)), tin_after=float(rng.uniform(140, 170)),
                tin_switch=str((pd.Timestamp(start) + pd.Timedelta(days=int(rng.integers(0, 600)))).date()),
                flow=float(rng.uniform(17000, 26500)), seed=int(rng.integers(1e9)))

def daily_dose(days, wx, p, rng):
    d = np.asarray(days.dayofyear, float)
    base = 1.0 + p["amp"] * np.exp(-0.5 * ((d - p["peak_doy"]) / p["width"]) ** 2)
    wd = wx["wind"].resample("1D").mean().reindex(days)
    wd = wd.fillna(wd.mean() if wd.notna().any() else 15.0)
    windf = (wd / wd.mean()).clip(0.3, 3.0).values ** p["wind_exp"]
    if "rain" in wx and wx["rain"].notna().sum() > 300 * 24:
        rd = wx["rain"].resample("1D").sum().reindex(days).fillna(0).values
        rainf = np.exp(-p["rain_k"] * rd)
    else:
        rainf = 1.0
    return pd.Series(base * windf * rainf * rng.lognormal(-0.05, 0.3, len(days)), index=days)

def true_phi(times, dose, p):
    """vectorised: blockage at each time from the debris dose since the last cleaning"""
    times = pd.DatetimeIndex(times)
    cum = dose.cumsum()
    cl = np.array(sorted(pd.Timestamp(c) for c in p["cleanings"]), dtype="datetime64[ns]")
    tn = times.normalize()
    k = np.searchsorted(cl, times.values.astype("datetime64[ns]"), side="right") - 1
    has = k >= 0
    c_day = np.where(has, cl[np.clip(k, 0, None)], np.datetime64(dose.index[0], "ns")).astype("datetime64[ns]")
    c_day = pd.DatetimeIndex(c_day).normalize()
    dd = cum.reindex(tn).values - cum.reindex(c_day).values + dose.reindex(tn).values * times.hour.values / 24
    res = np.where(has, p["residual"], 0.0)
    return np.minimum(0.8, res + (p["phi_sat"] - res) * (1 - np.exp(-dd / p["D"])))

def simulate(phys, wx, p, start="2025-01-01", end=None, freq="6h", noise=True):
    rng = np.random.default_rng(p["seed"])
    end = end or str(wx.index.max())
    idx = pd.date_range(start, end, freq=freq)
    days = pd.date_range(pd.Timestamp(min(p["cleanings"])).normalize() - pd.Timedelta(days=1), idx[-1].normalize() + pd.Timedelta(days=1), freq="1D")
    dose = daily_dose(days, wx, p, rng)
    if p["D"] is None:   # official scenario: calibrate so the blockage is 65 % on 14 Nov 2026 (diagnosis)
        Ds = np.linspace(60, 600, 541)
        target = pd.Timestamp("2026-11-13 12:00")
        p = dict(p, D=float(Ds[np.argmin([abs(true_phi([target], dose, dict(p, D=d))[0] - 0.65) for d in Ds])]))
    phi = true_phi(idx, dose, p)
    tamb = wx["T_amb"].reindex(idx, method="nearest").values
    tin = np.where(idx < pd.Timestamp(p["tin_switch"]), p["tin_before"], p["tin_after"]) + rng.normal(0, 1.5, len(idx))
    flow = p["flow"] * (1 + rng.normal(0, 0.02, len(idx)))
    sp = phys.controller_speed(tin, tamb, phi, flow)
    tout = phys.T_out(tin, tamb, sp, phi, flow)
    df = pd.DataFrame(dict(T_in=tin, T_out=tout, flow=flow, fan=sp, T_amb=tamb, phi_true=phi), index=idx)
    if noise:   # what the historian would record
        df["T_in"] += rng.normal(0, 0.3, len(idx)); df["T_out"] += rng.normal(0, 0.3, len(idx))
        df["flow"] *= 1 + rng.normal(0, 0.01, len(idx)); df["fan"] = np.clip(df["fan"] + rng.normal(0, 0.005, len(idx)), 0.3, 1.0)
        df["T_amb_meas"] = df["T_amb"] + rng.normal(0, 1.5, len(idx))   # ERA5 vs real air at the fan inlet
    df["limited"] = (sp > 0.999) & (tout > 65.2)
    return df, p
