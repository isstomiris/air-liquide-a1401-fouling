"""Health indicator + forecaster on the REAL plant history (Data (full history).xlsx).

Usable data: 14 Nov 2023 - 11 Mar 2026 (after that the export repeats one frozen value until 14 Nov 2026).
Two forecasters are compared on the real 2025-26 data (never used for training):
  A) trained on simulated plants only            B) trained on simulated plants, uncertainty band calibrated on real data up to 31 Dec 2024
"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from core import Physics
from data import load_weather, find_weather
from forecaster import Forecaster, daily_features, H
from simulate import random_params, simulate
import monitor as M

FROZEN_FROM = "2026-03-11 17:00"
def load_history():
    d = pd.read_excel(os.path.join(HERE, "..", "plant_history", "Data (full history).xlsx"))
    d.index = pd.to_datetime(d["local_time"].str[:19]); d = d.sort_index()
    d = d.rename(columns={"1400TIA050": "T_in", "1400TICA0055_pv": "T_out", "1400TICA0055_mv": "fan", "1400PICA0017_mv": "pv0017", "1400FI010": "flow"})
    d = d[["T_in", "T_out", "fan", "pv0017", "flow"]]; d["fan"] = d["fan"] / 100
    return d

if __name__ == "__main__":
    phys = Physics(); wx = load_weather(find_weather(HERE))
    raw = load_history(); d = raw[raw.index < FROZEN_FROM].copy()
    d["T_amb"] = wx["T_amb"].reindex(d.index)
    d["ok"] = (d.flow > 12000) & (d.pv0017 < 1) & (d.T_in > d.T_out + 10) & (d.fan > 0.3) & d[["T_in", "T_out", "flow", "fan", "T_amb"]].notna().all(axis=1)
    d = M.health(phys, d, use_meas=False)
    # shutdowns longer than 5 days = cleaning opportunities seen in the data
    down = (raw.flow < 8000)[raw.index < FROZEN_FROM].resample("1D").mean() > 0.5
    blocks = (down != down.shift()).cumsum()[down]
    shut = [(g.index[0], g.index[-1]) for _, g in blocks.groupby(blocks) if len(g) >= 5]
    cleanings = [str((b + pd.Timedelta(days=1)).date()) for a, b in shut]
    days = daily_features(d, cleanings, wx)
    # ---- forecasters
    fcA = Forecaster.load(M.MODEL)
    rng = np.random.default_rng(2026); sims = []
    for i in range(60):
        p = random_params(rng, i, "2025-01-01", "2026-11-13 23:00"); s, p = simulate(phys, wx, p, "2025-01-01", "2026-11-13 23:00"); s["ok"] = True
        sims.append(daily_features(M.health(phys, s), p["cleanings"], wx))
    real_tr = days[days.index < "2025-01-01"]
    fcB = Forecaster().fit(pd.concat(sims), real_tr)   # learn the shape from simulations, set the band width from REAL 2023-24 data
    fcB.save(os.path.join(HERE, "forecaster_real.pkl"))
    test = days[days.index >= "2025-01-01"]
    res = dict(usable_period=[str(d.index.min()), str(d.index[-1])], hours_used=int(d.ok.sum()), shutdowns=[(str(a.date()), str(b.date())) for a, b in shut],
               note="values after 11 Mar 2026 17:00 are one frozen sample repeated; not used")
    for name, fc in (("sim_only", fcA), ("sim_trained_real_calibrated", fcB)):
        t = test.join(fc.predict(test)); r = {}
        for hz in H:
            x = t.dropna(subset=[f"y{hz}", f"q50_{hz}", "slope14"])
            r[f"h{hz}"] = dict(n=len(x), model_MAE_pct=round(100 * (x[f"q50_{hz}"] - x[f"y{hz}"]).abs().mean(), 2),
                               persistence_MAE_pct=round(100 * (x["hi7"] - x[f"y{hz}"]).abs().mean(), 2),
                               linear_trend_MAE_pct=round(100 * (x["hi7"] + hz * x["slope14"] - x[f"y{hz}"]).abs().mean(), 2),
                               band_coverage=round(float(((x[f"y{hz}"] >= x[f"q10_{hz}"]) & (x[f"y{hz}"] <= x[f"q90_{hz}"])).mean()), 2))
        res[name] = r
        if name == "sim_trained_real_calibrated": tB = t
    # monthly summary + seasonal rise + what the plant did when hot
    mm = pd.DataFrame({"blockage_pct": (100 * d.phi_hat.resample("1MS").median()).round(0), "fan_pct": (100 * d.fan.where(d.ok).resample("1MS").median()).round(0),
                       "flow": d.flow.where(d.ok).resample("1MS").median().round(0), "T_out": d.T_out.where(d.ok).resample("1MS").median().round(1),
                       "T_amb": d.T_amb.resample("1MS").mean().round(1), "hours_fans_100": ((d.fan >= 0.995) & d.ok).resample("1MS").sum()})
    mm.to_csv(os.path.join(M.OUT, "real_monthly.csv"))
    x = d[d.ok]
    res["flow_vs_air_temp"] = {f"{lo} to {hi} C": dict(hours=int(len(s)), flow_median=int(s.flow.median()), fans_at_100_pct=int(round(100 * (s.fan >= 0.995).mean())), outlet_median=round(float(s.T_out.median()), 1))
                               for lo, hi in ((-30, 0), (0, 10), (10, 20), (20, 30), (30, 45)) for s in [x[(x.T_amb >= lo) & (x.T_amb < hi)]]}
    res["corr_flow_air_temp"] = round(float(x.flow.corr(x.T_amb)), 2)
    json.dump(res, open(os.path.join(M.OUT, "real_backtest.json"), "w"), indent=1, default=str)
    days.join(tB[[c for c in tB.columns if c.startswith("q")]]).to_csv(os.path.join(M.OUT, "real_daily.csv"))
    # ---- chart
    C1, C2, C3, C4, INK, INK2 = M.C1, M.C2, M.C3, M.C4, M.INK, M.INK2
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.plot(days.index, 100 * days.hi, color=C2, lw=0, marker="o", ms=1.6, alpha=0.6)
    ax.plot(days.index, 100 * days.hi7, color=C2, lw=1.6, label="Health indicator, 7-day median (real plant data)")
    f = tB[["q10_30", "q50_30", "q90_30"]].shift(30)
    ax.fill_between(f.index, 100 * f.q10_30, 100 * f.q90_30, color=C1, alpha=0.18, lw=0)
    ax.plot(f.index, 100 * f.q50_30, color=C1, lw=1.4, label="30-day forecast made 30 days earlier + 80 % band")
    for a, b in shut:
        ax.axvspan(a, b, color=C3, alpha=0.25, lw=0)
    ax.axvspan(pd.Timestamp("2025-01-01"), days.index.max(), ymin=0, ymax=0.03, color=INK2, alpha=0.5)
    ax.text(pd.Timestamp("2025-01-10"), 42.2, "test period (never used for training)", fontsize=9, color=INK2)
    if shut: ax.text(shut[-1][0] - pd.Timedelta(days=5), 84, "shutdown /\ncleaning", fontsize=9, color=C3, ha="right", va="top")
    ax.set_ylim(40, 85); ax.set_ylabel("Equivalent fin blockage (%)"); ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_title("Real plant: A-1401 health indicator, Nov 2023 - Mar 2026", loc="left", fontsize=13, fontweight="bold", color=INK, pad=22)
    ax.text(0, 1.02, "Blockage rises every May-August and drops after the October 2025 shutdown (green).", transform=ax.transAxes, fontsize=9.5, color=INK2)
    fig.tight_layout(); fig.savefig(os.path.join(M.OUT, "real_history.png"), dpi=200); plt.close(fig)
    print(json.dumps(res, indent=1, default=str)); print(mm.to_string())
