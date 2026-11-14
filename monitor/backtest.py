"""Steps 2-3 of the monitoring model: predict fouling ahead of time, and backtest it.

Plain-language idea
-------------------
1. A "synthetic plant" runs from Jan 2025 to Nov 2026 with real Atyrau weather (or a placeholder pattern
   until the weather CSV is in ../weather/). Debris builds up on the fins, faster in May-August, and is
   reset at the two real cleanings (Sep 2025 and the July 2026 turnaround). The fan controller speeds the
   fans up to hold 65 C, exactly like TY0055 does.
2. We add realistic sensor noise and give the monitoring model ONLY what the plant historian would see:
   inlet T, outlet T, fan speed and outside air T. It never sees the true blockage.
3. Health indicator (step 1): invert the physics model to get the equivalent blockage, every 6 hours.
4. Data-driven forecaster (inspired by the multi-step-ahead + uncertainty idea in Benaggoune et al. 2022):
   gradient-boosted quantile regression predicts the blockage 7, 14 and 30 days ahead with a 10-90 % band.
   Trained on the first two fouling cycles, tested on the last one (Jul-Nov 2026), which it never saw.
5. Alarm: "plan a cleaning" when the 90 % upper band for 14 days ahead crosses 40 % (the cliff).

Run time: ~1 min once surrogate_Tout.json exists (build_surrogate.py, ~10 min, once).
"""
import os, json, glob, math
import numpy as np, pandas as pd
from scipy.interpolate import RegularGridInterpolator
from sklearn.ensemble import GradientBoostingRegressor

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(42)

# ---------- physics surrogate ----------
S = json.load(open(os.path.join(HERE, "surrogate_Tout.json")))
grid = np.array(S["T_out"]).reshape(len(S["TIN"]), len(S["TAMB"]), len(S["SPEED"]), len(S["PHI"]))
f_Tout = RegularGridInterpolator((S["TIN"], S["TAMB"], S["SPEED"], S["PHI"]), grid, bounds_error=False, fill_value=None)
def T_out(tin, tamb, sp, phi):
    return f_Tout(np.column_stack([tin, tamb, sp, phi]))

def bisect(fun, lo, hi, N, n=30):
    """vectorised bisection: fun(x) > 0 means the answer is below x"""
    lo = np.full(N, lo, float); hi = np.full(N, hi, float)
    for _ in range(n):
        mid = 0.5 * (lo + hi); up = fun(mid) > 0
        lo = np.where(up, lo, mid); hi = np.where(up, mid, hi)
    return 0.5 * (lo + hi)

# ---------- weather ----------
NAME = "atyrau_open-meteo_47.12N_51.92E_2025-01-01_2026-11-13.csv"
cands = [os.path.join(HERE, "..", "weather", NAME)] + glob.glob("/mnt/user-data/uploads/**/" + NAME, recursive=True)
src = next((p for p in cands if os.path.exists(p)), None)
idx = pd.date_range("2025-01-01", "2026-11-13 18:00", freq="6h")
if src:
    rows = open(src).read().splitlines()
    k = next(i for i, r in enumerate(rows) if r.startswith("time"))
    w = pd.read_csv(src, skiprows=k)
    w.index = pd.to_datetime(w.iloc[:, 0]); tamb = w.iloc[:, 1].reindex(idx).interpolate().values
    WIND = w.iloc[:, 3].resample("1D").mean()            # km/h, daily mean
    WEATHER = "real ERA5 hourly (Open-Meteo), " + NAME
else:
    # PLACEHOLDER until the CSV is available: seasonal + daily cycle + 3-day weather noise,
    # matched to Atyrau ERA5 stats we already have (mean ~10 C, Jan ~ -6 C, Jul ~ +26 C, max ~40 C)
    doy = idx.dayofyear.values; hr = idx.hour.values
    ar = np.zeros(len(idx)); a = math.exp(-0.25 / 3)
    for i in range(1, len(idx)):
        ar[i] = a * ar[i - 1] + math.sqrt(1 - a * a) * rng.normal(0, 4.0)
    tamb = 10 + 16 * np.cos(2 * np.pi * (doy - 200) / 365) + 5 * np.cos(2 * np.pi * (hr - 15) / 24) + ar
    WIND = pd.Series(15 + 5 * rng.standard_normal(700), index=pd.date_range("2025-01-01", periods=700, freq="1D"))
    WEATHER = "PLACEHOLDER pattern (seasonal + daily + noise); replace by the Atyrau CSV in ../weather/"

# ---------- true fouling (unknown to the monitor) ----------
CLEAN = [pd.Timestamp("2024-09-15"), pd.Timestamp("2025-09-15"), pd.Timestamp("2026-07-01")]
def dose_rate(ts):
    """debris arriving per day: dust all year + organic season (May-Aug: poplar fluff, pollen, insects)"""
    d = np.asarray(ts.dayofyear, float)
    season = np.exp(-0.5 * ((d - 175) / 35.0) ** 2)  # peak late June
    return 1.0 + 3.0 * season
ALLDAYS = pd.date_range("2024-09-01", "2026-11-30", freq="1D")
# day-to-day randomness: windy days bring more fluff, rainy days less (log-normal, sigma 0.6)
# windy days carry more fluff/insects onto the fins: dose scales with daily mean wind (real ERA5 wind when available)
wind_f = (WIND.reindex(ALLDAYS).fillna(WIND.mean()) / WIND.mean()).clip(0.3, 3.0).values
DAYDOSE = pd.Series(dose_rate(ALLDAYS) * wind_f * rng.lognormal(-0.05, 0.3, len(ALLDAYS)), index=ALLDAYS)
CUM = DAYDOSE.cumsum()
def true_phi(times, D, phi_sat=0.85):
    out = []
    for t in times:
        c = max(cc for cc in CLEAN if cc <= t)
        dose = CUM[t.normalize()] - CUM[c.normalize()] + DAYDOSE[t.normalize()] * (t.hour / 24)
        out.append(phi_sat * (1 - math.exp(-dose / D)))
    return np.array(out)
# calibrate D so the true blockage on 14 Nov 2026 equals our estimate (65 %)
Ds = np.linspace(50, 600, 221)
D = Ds[np.argmin([abs(true_phi([pd.Timestamp("2026-11-14")], d)[0] - 0.65) for d in Ds])]
phi_t = true_phi(idx, D)

# ---------- plant + controller ----------
tin = np.where(idx < pd.Timestamp("2026-07-01"), 145.0, 167.0) + rng.normal(0, 1.5, len(idx))
need = lambda sp: T_out(tin, tamb, sp, phi_t) - 65.0      # >0 means too hot at that speed
sp = np.clip(bisect(lambda s: -need(s), 0.3, 1.0, len(idx)), 0.3, 1.0)   # slowest speed that holds 65 C
tout = T_out(tin, tamb, sp, phi_t)
limited = (sp > 0.999) & (tout > 65.2)

# ---------- what the historian sees (with noise) ----------
m_tin = tin + rng.normal(0, 0.3, len(idx)); m_tout = tout + rng.normal(0, 0.3, len(idx))
m_sp = np.clip(sp + rng.normal(0, 0.005, len(idx)), 0.3, 1.0)
m_tamb = tamb + rng.normal(0, 1.5, len(idx))           # ERA5 vs site air + recirculation
# ---------- step 1: health indicator = invert the model ----------
phi_hat = bisect(lambda p: T_out(m_tin, m_tamb, m_sp, p) - m_tout, 0.0, 0.8, len(idx))
df = pd.DataFrame(dict(T_amb=tamb, T_in=tin, speed=sp, T_out=tout, phi_true=phi_t, phi_hat=phi_hat, limited=limited), index=idx)
day = df.resample("1D").agg(dict(phi_true="mean", phi_hat="median", T_amb="mean", limited="sum"))

# ---------- step 2: features + quantile forecaster ----------
def last_clean(t): return max(c for c in CLEAN if c <= t)
day["hi7"] = day.phi_hat.rolling(7, min_periods=3).median()
day["slope14"] = day.hi7.diff(14) / 14
day["since_clean"] = [(t - last_clean(t)).days for t in day.index]
day["doy_s"] = np.sin(2 * np.pi * day.index.dayofyear / 365); day["doy_c"] = np.cos(2 * np.pi * day.index.dayofyear / 365)
day["tamb7"] = day.T_amb.rolling(7, min_periods=3).mean()
day["wind7"] = WIND.reindex(day.index).fillna(WIND.mean()).rolling(7, min_periods=3).mean()
FEAT = ["hi7", "slope14", "since_clean", "doy_s", "doy_c", "tamb7", "wind7"]
H = [7, 14, 30]
for h in H:
    y = day.hi7.shift(-h)
    # a cleaning inside the horizon makes the target meaningless: drop those rows
    nxt = [min([c for c in CLEAN if c > t], default=pd.Timestamp("2100-01-01")) for t in day.index]
    ok = np.array([(n - t).days > h for n, t in zip(nxt, day.index)])
    day[f"y{h}"] = np.where(ok, y, np.nan)
train = day[day.index < pd.Timestamp("2026-07-01")].dropna(subset=FEAT)
test = day[day.index >= pd.Timestamp("2026-07-15")].dropna(subset=FEAT)
def cycle_of(t): return max(i for i, c in enumerate(CLEAN) if c <= t)
day["cycle"] = [cycle_of(t) for t in day.index]
def gbm():
    return GradientBoostingRegressor(loss="absolute_error", n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=1)
for h in H:
    tr = day.loc[train.index].dropna(subset=[f"y{h}"])
    # out-of-cycle residuals: train on one fouling cycle, predict the other (how wrong are we on a NEW cycle?)
    resid = []
    for cyc in tr.cycle.unique():
        a_, b_ = tr[tr.cycle != cyc], tr[tr.cycle == cyc]
        if len(a_) < 30 or len(b_) < 10: continue
        g = gbm().fit(a_[FEAT], a_[f"y{h}"] - a_["hi7"])
        resid += list(b_[f"y{h}"] - (b_["hi7"] + g.predict(b_[FEAT])))
    lo_, hi_ = np.quantile(resid, [0.1, 0.9]) if resid else (-0.02, 0.02)
    g = gbm().fit(tr[FEAT], tr[f"y{h}"] - tr["hi7"])      # learn the CHANGE over h days
    sel = day.dropna(subset=FEAT).index
    med = day.loc[sel, "hi7"] + g.predict(day.loc[sel, FEAT])
    for col in ("q10", "q50", "q90"): day[f"{col}_{h}"] = np.nan
    day.loc[sel, f"q50_{h}"] = med; day.loc[sel, f"q10_{h}"] = med + lo_; day.loc[sel, f"q90_{h}"] = med + hi_

# ---------- step 3: backtest scores on the unseen cycle (Jul-Nov 2026) ----------
res = dict(weather=WEATHER, debris_D=float(D), train="Jan 2025 - Jun 2026 (2 fouling cycles)", test="15 Jul - 13 Nov 2026 (unseen cycle after the TAR cleaning)",
           health_indicator_error_pct=float(100 * np.sqrt(np.nanmean((day.phi_hat - day.phi_true) ** 2))),
           health_indicator_error_pct_test=float(100 * np.sqrt(np.nanmean(((day.phi_hat - day.phi_true)[test.index]) ** 2))))
for h in H:
    t = day.loc[test.index].dropna(subset=[f"y{h}"])
    err = 100 * (t[f"q50_{h}"] - t[f"y{h}"]).abs().mean()
    naive = 100 * (t["hi7"] - t[f"y{h}"]).abs().mean()                 # "tomorrow = today"
    trend = 100 * (t["hi7"] + h * t["slope14"] - t[f"y{h}"]).abs().mean()  # straight-line extrapolation
    cover = float(((t[f"y{h}"] >= t[f"q10_{h}"]) & (t[f"y{h}"] <= t[f"q90_{h}"])).mean())
    res[f"h{h}"] = dict(n=len(t), model_MAE_pct=round(err, 2), persistence_MAE_pct=round(naive, 2), linear_trend_MAE_pct=round(trend, 2), band_10_90_coverage=round(cover, 2))
THR = 0.40
cross = day.index[(day.index >= pd.Timestamp("2026-07-01")) & (day.phi_true >= THR)]
day["alarm"] = (day[["q90_7", "q90_14", "q90_30"]] >= THR).any(axis=1) & (day.hi7 < THR)
alarm = day.index[(day.index >= pd.Timestamp("2026-07-15")) & day["alarm"]]
res["true_cross_40pct"] = str(cross[0].date()) if len(cross) else None
res["first_alarm"] = str(alarm[0].date()) if len(alarm) else None
res["alarm_lead_days"] = (cross[0] - alarm[0]).days if len(cross) and len(alarm) else None
# false alarms in training-free sense: alarm days when the truth stays below 40 % for the next 30 days
fa = [a for a in alarm if day.phi_true[a:a + pd.Timedelta(days=30)].max() < THR]
res["false_alarm_days"] = len(fa)
res["hours_limited_true"] = int(df.limited.sum() * 6)
json.dump(res, open(os.path.join(HERE, "backtest_results.json"), "w"), indent=1, default=str)
day.to_csv(os.path.join(HERE, "backtest_daily.csv"))
print(json.dumps(res, indent=1, default=str))
