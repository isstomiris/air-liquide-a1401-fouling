"""A-1401 predictive monitoring program.

    python monitor.py train                       # simulate plants, train + calibrate forecaster, backtest   (~2-5 min)
    python monitor.py run --plant PATH [--asof YYYY-MM-DD] [--method sonication|dry_projection]
    python monitor.py demo [--asof 2026-07-20]    # run on the simulated plant as if it were live on that date

PATH = folder of PI .xlsx exports (as sent by Air Liquide) or a CSV with time,T_in,T_out,flow,fan[,pv0017].
Outputs go to ./out/: report_<date>.html (dashboard), health_<date>.csv, status_<date>.json.
"""
import os, sys, json, argparse, base64, io, datetime as dt
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from core import Physics, h2_t_per_h
from data import load_plant, load_weather, find_weather, clean
from simulate import OFFICIAL, random_params, simulate
from forecaster import Forecaster, daily_features, days_until, H

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
MODEL = os.path.join(HERE, "forecaster.pkl")
TRIGGER_OVERRIDE = None
CLEANINGS_REAL = ["2025-10-22", "2026-07-01"]          # end of the Oct 2025 shutdown seen in the data; Jun/Jul 2026 TAR (Air Liquide)
MODEL_REAL = os.path.join(HERE, "forecaster_real.pkl")  # band calibrated on real 2023-24 data (real_backtest.py)
METHODS = {   # trigger = blockage at which each cleaning method should be run (assumption, see report)
    "sonication": dict(label="Solution A: monitoring + sonication", trigger=0.30,
                       why="Acoustic/ultrasonic cleaning removes loose, fresh deposits best, so it is run early and often."),
    "dry_projection": dict(label="Solution B: monitoring + dry projection", trigger=0.40,
                           why="Dry projection removes compacted debris, so it can wait until just before the 40 % cliff."),
}
C1, C2, C3, C4, INK, INK2, SURF, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF, "axes.grid": True, "grid.color": GRID,
                     "axes.spines.top": False, "axes.spines.right": False})

def weather():
    paths = find_weather(HERE)
    return load_weather(paths), paths

def health(phys, df, use_meas=True):
    tamb = df["T_amb_meas"] if (use_meas and "T_amb_meas" in df) else df["T_amb"]
    df = df.copy(); df["phi_hat"] = np.nan
    ok = df.get("ok", pd.Series(True, index=df.index)).astype(bool)
    d = df[ok]
    df.loc[ok, "phi_hat"] = phys.invert_phi(d["T_in"].values, tamb[ok].values, d["fan"].values, d["T_out"].values, d["flow"].values)
    return df

# ------------------------------------------------------------------ train + backtest
def cmd_train(args):
    phys = Physics(); wx, wpaths = weather(); rng = np.random.default_rng(2026)
    print("weather files:", wpaths, "| rain:", "rain" in wx and wx["rain"].notna().sum() > 300 * 24, "| 5-D physics:", phys.has_flow)
    start, end = "2025-01-01", str(wx["T_amb"].dropna().index.max())
    plants = []
    for i in range(args.n):
        p = random_params(rng, i, start, end)
        df, p = simulate(phys, wx, p, start, end); df["ok"] = True
        df = health(phys, df); days = daily_features(df, p["cleanings"], wx); days["plant"] = i; days["phi_true"] = df["phi_true"].resample("1D").mean()
        plants.append(days)
        print(f"  plant {i+1}/{args.n} simulated", flush=True) if (i + 1) % 10 == 0 else None
    k = int(0.75 * args.n)
    fc = Forecaster().fit(pd.concat(plants[:k]), pd.concat(plants[k:]))
    fc.save(MODEL)
    # ---------- backtest on the official scenario (never used in training): real cleanings, 65 % on 14 Nov
    df, p = simulate(phys, wx, dict(OFFICIAL), start, end); df["ok"] = True
    df = health(phys, df); days = daily_features(df, p["cleanings"], wx)
    days["phi_true"] = df["phi_true"].resample("1D").mean(); pr = fc.predict(days); days = days.join(pr)
    test = days[days.index >= pd.Timestamp("2026-07-01")]
    res = dict(trained_on=f"{k} simulated plants, calibrated on {args.n-k} others", weather=[os.path.basename(x) for x in wpaths],
               debris_D_official=p["D"], health_indicator_rmse_pct=round(100 * float(np.sqrt(((test.hi - test.phi_true) ** 2).mean())), 2),
               conformal_widening={str(h): round(100 * q, 2) for h, q in fc.Q.items()})
    for hz in H:
        t = test.dropna(subset=[f"y{hz}", f"q50_{hz}"])
        res[f"h{hz}"] = dict(n=len(t), model_MAE_pct=round(100 * (t[f"q50_{hz}"] - t[f"y{hz}"]).abs().mean(), 2),
                             persistence_MAE_pct=round(100 * (t["hi7"] - t[f"y{hz}"]).abs().mean(), 2),
                             linear_trend_MAE_pct=round(100 * (t["hi7"] + hz * t["slope14"] - t[f"y{hz}"]).abs().mean(), 2),
                             band_coverage=round(float(((t[f"y{hz}"] >= t[f"q10_{hz}"]) & (t[f"y{hz}"] <= t[f"q90_{hz}"])).mean()), 2))
    # coverage over ALL calibration-style plants (fresh ones), the honest number for the band
    fresh = []
    for i in range(10):
        pp = random_params(rng, 1000 + i, start, end); d2, pp = simulate(phys, wx, pp, start, end); d2["ok"] = True
        d2 = health(phys, d2); dd = daily_features(d2, pp["cleanings"], wx).join(fc.predict(daily_features(d2, pp["cleanings"], wx)))
        fresh.append(dd)
    fr = pd.concat(fresh)
    res["band_coverage_10_new_plants"] = {str(hz): round(float(((fr[f"y{hz}"] >= fr[f"q10_{hz}"]) & (fr[f"y{hz}"] <= fr[f"q90_{hz}"]))[fr[f"y{hz}"].notna() & fr[f"q50_{hz}"].notna()].mean()), 2) for hz in H}
    for mname, m in METHODS.items():
        thr = m["trigger"]
        cross = test.index[test.phi_true >= thr]
        alarm = test.index[(test[[f"q90_{h}" for h in H]] >= thr).any(axis=1) & (test.hi7 < thr)]
        fa = [a for a in alarm if test.phi_true[a:a + pd.Timedelta(days=30)].max() < thr]
        res[f"alarm_{mname}"] = dict(trigger_pct=100 * thr, true_cross=str(cross[0].date()) if len(cross) else None,
                                     first_alarm=str(alarm[0].date()) if len(alarm) else None,
                                     lead_days=(cross[0] - alarm[0]).days if len(cross) and len(alarm) else None, false_alarm_days=len(fa))
    json.dump(res, open(os.path.join(OUT, "backtest.json"), "w"), indent=1, default=str)
    days.to_csv(os.path.join(OUT, "backtest_official_daily.csv"))
    backtest_chart(days, res)
    print(json.dumps(res, indent=1, default=str))

def backtest_chart(days, res):
    t = days["2026-06-15":]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    f = t[["q10_14", "q50_14", "q90_14"]].shift(14); f = f[f.index >= pd.Timestamp("2026-07-25")]
    ax.fill_between(f.index, 100 * f.q10_14, 100 * f.q90_14, color=C1, alpha=0.18, lw=0)
    ax.plot(f.index, 100 * f.q50_14, color=C1, lw=1.8, label="14-day forecast (made 14 days earlier) + 80 % band")
    ax.plot(t.index, 100 * t.phi_true, color=INK, lw=1.5, ls="--", label="True blockage (simulated)")
    ax.plot(t.index, 100 * t.hi, color=C2, lw=0, marker="o", ms=2.2, label="Health indicator from plant readings")
    for m, col in (("sonication", C3), ("dry_projection", C4)):
        a = res[f"alarm_{m}"]
        ax.axhline(a["trigger_pct"], color=col, lw=1, ls=":")
        if a["first_alarm"]:
            ax.plot(pd.Timestamp(a["first_alarm"]), a["trigger_pct"], marker="v", color=col, ms=9)
            ax.text(pd.Timestamp(a["first_alarm"]) + pd.Timedelta(days=2), a["trigger_pct"] + 1.2,
                    f"{'Sonication' if m == 'sonication' else 'Dry projection'} alarm, {a['lead_days']} d early", color=col, fontsize=9)
    ax.set_ylabel("Equivalent fin blockage (%)"); ax.set_ylim(0, 85); ax.legend(frameon=False, fontsize=8.8, loc="lower right")
    ax.set_title("Backtest on an unseen fouling cycle (Jul-Nov 2026)", loc="left", fontsize=13, fontweight="bold", color=INK, pad=22)
    ax.text(0, 1.02, "Simulated plant with real Atyrau weather and the real cleaning dates; forecaster never saw it.", transform=ax.transAxes, fontsize=9.5, color=INK2)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "backtest.png"), dpi=200); plt.close(fig)

# ------------------------------------------------------------------ live run
def impact_next_30(phys, wx, asof, phi_path, flow_now, tin_now):
    """Expected production limit in the next 30 days: last year's weather for the same dates + forecast blockage."""
    hrs = pd.date_range(asof + pd.Timedelta(hours=1), asof + pd.Timedelta(days=30), freq="1h")
    past = hrs - pd.DateOffset(years=1)
    tamb = wx["T_amb"].reindex(past, method="nearest").values
    phi = np.interp((hrs - asof).days, [0] + H, phi_path)
    if phys.has_flow:
        mf = phys.max_flow(np.full(len(hrs), tin_now), tamb, phi)
        lost = np.clip(flow_now - mf, 0, None)
        return dict(hours_limited=int((lost > 0).sum()), h2_lost_t=round(float(h2_t_per_h(lost).sum()), 1), basis="max flow at fans 100 %")
    tout = phys.T_out(tin_now, tamb, 1.0, phi, flow_now)
    return dict(hours_limited=int((tout > 65).sum()), h2_lost_t=None, basis="outlet above 65 C at fans 100 % (flow fixed)")

def fig_b64(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=150, bbox_inches="tight"); plt.close(fig)
    return base64.b64encode(b.getvalue()).decode()

def analyse(phys, wx, plant, cleanings, asof, method, source_label, truth=None):
    fc = Forecaster.load(MODEL_REAL if (truth is None and os.path.exists(MODEL_REAL)) else MODEL)
    plant = plant[plant.index <= asof]
    df, dropped = clean(plant)
    df = health(phys, df, use_meas=False)
    days = daily_features(df, cleanings, wx[wx.index <= asof + pd.Timedelta(days=1)]).join(fc.predict(daily_features(df, cleanings, wx[wx.index <= asof + pd.Timedelta(days=1)])))
    last = days.dropna(subset=["hi7"]).iloc[-1] if days["hi7"].notna().any() else None
    m = METHODS[method]; thr = TRIGGER_OVERRIDE if TRIGGER_OVERRIDE else m["trigger"]
    status = dict(asof=str(asof), source=source_label, method=m["label"], trigger_pct=100 * thr, hours_used=int(df["ok"].sum()), hours_rejected=dropped)
    if last is None:
        status.update(level="NO DATA", message="Not enough clean data in the last 7 days to compute the health indicator.")
        return status, df, days, None
    du = days_until(last, thr)
    hi = float(last["hi7"])
    recent_limited = bool(((df["fan"] > 0.99) & (df["T_out"] > 65.5)).tail(72).any())
    if hi >= thr or recent_limited or (du["q50"] is not None and du["q50"] <= 14):
        level, msg = "RED", "Clean now: the blockage is at or will reach the trigger within 2 weeks (median forecast)."
    elif du["q90"] is not None and du["q90"] <= 30:
        level, msg = "AMBER", "Plan a cleaning: the pessimistic forecast reaches the trigger within 30 days."
    else:
        level, msg = "GREEN", "No action: even the pessimistic forecast stays below the trigger for 30 days."
    path = [hi] + [float(last[f"q50_{h}"]) for h in H]; path90 = [hi] + [float(last[f"q90_{h}"]) for h in H]
    lastrow = df[df["ok"]].iloc[-24:]
    imp50 = impact_next_30(phys, wx, asof, path, float(lastrow["flow"].mean()), float(lastrow["T_in"].mean()))
    imp90 = impact_next_30(phys, wx, asof, path90, float(lastrow["flow"].mean()), float(lastrow["T_in"].mean()))
    status.update(level=level, message=msg, health_blockage_pct=round(100 * hi, 1), cleanliness_note="equivalent blocked fin area (debris + anything else that cuts airflow)",
                  forecast_pct={str(h): dict(low=round(100 * last[f"q10_{h}"], 1), median=round(100 * last[f"q50_{h}"], 1), high=round(100 * last[f"q90_{h}"], 1)) for h in H},
                  days_to_trigger=dict(median=du["q50"], pessimistic=du["q90"]),
                  impact_next_30_days=dict(median_forecast=imp50, pessimistic_forecast=imp90),
                  fan_7d_mean_pct=round(100 * float(last["fan7"]), 1) if pd.notna(last["fan7"]) else None)
    return status, df, days, truth

def report(status, df, days, truth, fname):
    lvl_col = {"GREEN": C3, "AMBER": C4, "RED": "#d03b3b", "NO DATA": INK2}[status["level"]]
    fig, ax = plt.subplots(figsize=(9.5, 4.3))
    d = days[days.index >= days.index.max() - pd.Timedelta(days=150)]
    ax.plot(d.index, 100 * d["hi"], color=C2, lw=0, marker="o", ms=2.5, label="Health indicator (daily)")
    ax.plot(d.index, 100 * d["hi7"], color=C2, lw=1.6, label="7-day median")
    if truth is not None:
        tt = truth[(truth.index >= d.index.min()) & (truth.index <= d.index.max())]
        ax.plot(tt.index, 100 * tt, color=INK, lw=1.2, ls="--", label="True blockage (simulation only)")
    if "forecast_pct" in status:
        t0 = pd.Timestamp(status["asof"]); xs = [t0] + [t0 + pd.Timedelta(days=h) for h in H]
        f = status["forecast_pct"]; hi = status["health_blockage_pct"]
        ax.fill_between(xs, [hi] + [f[str(h)]["low"] for h in H], [hi] + [f[str(h)]["high"] for h in H], color=C1, alpha=0.18, lw=0)
        ax.plot(xs, [hi] + [f[str(h)]["median"] for h in H], color=C1, lw=2, marker="o", ms=4, label="Forecast + 80 % band")
    ax.axhline(status["trigger_pct"], color=lvl_col, lw=1.2, ls=":"); ax.text(d.index.min(), status["trigger_pct"] + 1.5, f"Cleaning trigger {status['trigger_pct']:.0f} %", color=lvl_col, fontsize=9)
    ax.axhline(40, color=INK2, lw=0.8, ls="--") if status["trigger_pct"] != 40 else None
    ax.set_ylabel("Equivalent fin blockage (%)"); ax.set_ylim(0, 85); ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    img = fig_b64(fig)
    f = status.get("forecast_pct", {}); imp = status.get("impact_next_30_days", {})
    rows = "".join(f"<tr><td>{h} days</td><td>{f[str(h)]['low']:.0f} %</td><td><b>{f[str(h)]['median']:.0f} %</b></td><td>{f[str(h)]['high']:.0f} %</td></tr>" for h in H) if f else ""
    def imp_txt(x):
        if not x: return "-"
        return f"{x['hours_limited']} h limited" + (f", ≈ {x['h2_lost_t']} t H₂" if x.get("h2_lost_t") is not None else "")
    dtt = status.get("days_to_trigger", {})
    rej = ", ".join(f"{k}: {v}" for k, v in status["hours_rejected"].items() if v)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>A-1401 health report</title><style>
:root{{--ink:{INK};--ink2:{INK2};--bg:{SURF};--card:#fff;--line:{GRID}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
.wrap{{max-width:980px;margin:0 auto;padding:20px 16px}} h1{{font-size:22px;margin:0 0 4px}} .sub{{color:var(--ink2);font-size:13px}}
.banner{{border-left:6px solid {lvl_col};background:var(--card);padding:14px 16px;margin:16px 0;border-radius:6px}}
.banner b{{color:{lvl_col};font-size:18px}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}}
.k{{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:12px}} .k .v{{font-size:24px;font-weight:700}} .k .n{{color:var(--ink2);font-size:12.5px}}
table{{border-collapse:collapse;width:100%;background:var(--card)}} td,th{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;font-size:14px}}
img{{width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff}} h2{{font-size:16px;margin:22px 0 8px}} .note{{color:var(--ink2);font-size:13px}}
</style></head><body><div class="wrap">
<h1>A-1401 air cooler: health report</h1><div class="sub">As of {status['asof']} · {status['method']} · data: {status['source']}</div>
<div class="banner"><b>{status['level']}</b> &nbsp; {status['message']}</div>
<div class="grid">
<div class="k"><div class="v">{status.get('health_blockage_pct','-')} %</div><div class="n">Equivalent fin blockage now (7-day median)</div></div>
<div class="k"><div class="v">{dtt.get('median') if dtt.get('median') is not None else '> 30'} d</div><div class="n">Days until the {status['trigger_pct']:.0f} % trigger (median; pessimistic: {dtt.get('pessimistic') if dtt.get('pessimistic') is not None else '> 30'} d)</div></div>
<div class="k"><div class="v">{imp_txt(imp.get('median_forecast'))}</div><div class="n">Expected production limit, next 30 days (pessimistic: {imp_txt(imp.get('pessimistic_forecast'))}). Weather = same dates last year.</div></div>
<div class="k"><div class="v">{status.get('fan_7d_mean_pct','-')} %</div><div class="n">Average fan speed, last 7 days</div></div>
</div>
<h2>Blockage history and forecast</h2><img alt="history and forecast" src="data:image/png;base64,{img}">
<h2>Forecast</h2><table><tr><th>Ahead</th><th>Low (10 %)</th><th>Median</th><th>High (90 %)</th></tr>{rows}</table>
<h2>How this is computed</h2><p class="note">1) Each hour, the physics model of A-1401 (fin efficiency, Briggs &amp; Young air side, fan and system curves, condensing gas side)
finds the blocked fraction that explains the measured outlet temperature, given inlet temperature, gas flow, fan speed and outside air. This removes the effect of weather and load.
2) Gradient-boosted trees forecast that number 7/14/30 days ahead; the band is calibrated (conformal) on simulated plants the model never saw.
3) {METHODS[[k for k in METHODS if METHODS[k]['label']==status['method']][0]]['why']}</p>
<p class="note">Hours used: {status['hours_used']} · rejected: {rej or 'none'} (rules: missing data, load &lt; 30 %, flaring, unsteady, inlet not hotter than outlet).
Limits: the blockage is an equivalent figure (it also includes louvres, fan wear and recirculation); the forecaster was trained on simulated fouling cycles because only one week of real data was available.</p>
</div></body></html>"""
    open(os.path.join(OUT, fname), "w").write(html)

def cmd_run(args, plant=None, cleanings=None, label=None, truth=None):
    phys = Physics(); wx, _ = weather()
    if plant is None:
        plant = load_plant(args.plant)
        tamb = wx["T_amb"].reindex(plant.index, method="nearest"); plant["T_amb"] = tamb
        label = os.path.basename(os.path.normpath(args.plant)); cleanings = CLEANINGS_REAL
    asof = pd.Timestamp(args.asof) if args.asof else plant.dropna().index.max()
    status, df, days, _ = analyse(phys, wx, plant, cleanings, asof, args.method, label, truth)
    tag = f"{asof:%Y-%m-%d}_{args.method}"
    report(status, df, days, truth, f"report_{tag}.html")
    df.to_csv(os.path.join(OUT, f"health_{tag}.csv")); json.dump(status, open(os.path.join(OUT, f"status_{tag}.json"), "w"), indent=1, default=str)
    print(json.dumps(status, indent=1, default=str)); return status

def cmd_demo(args):
    phys = Physics(); wx, _ = weather()
    df, p = simulate(phys, wx, dict(OFFICIAL), "2025-01-01", str(wx["T_amb"].dropna().index.max()), freq="1h")
    plant = df[["T_in", "T_out", "flow", "fan"]].copy(); plant["T_amb"] = df["T_amb_meas"]
    return cmd_run(args, plant=plant, cleanings=p["cleanings"], label="simulated plant (real Atyrau weather, real cleaning dates)", truth=df["phi_true"].resample("1D").mean())

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train"); t.add_argument("--n", type=int, default=60)
    for name in ("run", "demo"):
        r = sub.add_parser(name); r.add_argument("--asof"); r.add_argument("--method", default="dry_projection", choices=list(METHODS)); r.add_argument("--trigger", type=float, help="override the cleaning trigger, in % blockage")
        if name == "run": r.add_argument("--plant", required=True)
    a = ap.parse_args()
    if getattr(a, "trigger", None): TRIGGER_OVERRIDE = a.trigger / 100.0
    {"train": cmd_train, "run": cmd_run, "demo": cmd_demo}[a.cmd](a)
