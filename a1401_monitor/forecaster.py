"""Data-driven part: forecast the health indicator 7 / 14 / 30 days ahead, with an honest uncertainty band.

Idea borrowed from Benaggoune et al. (Applied Energy 313, 2022): multi-step-ahead prediction of a health
indicator plus a model of the uncertainty. Instead of their deep CNN (which needs long lab ageing records)
we use gradient-boosted trees, which work with small data, and CONFORMALISED QUANTILE REGRESSION (CQR):
  1. train a 10 % and a 90 % quantile model on simulated plants A
  2. measure how often they miss on different simulated plants B and widen the band until 80 % of B is inside
This gives a band that is calibrated on plants the model never saw.
"""
import pickle, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

H = [7, 14, 30]
FEAT = ["hi7", "slope14", "slope30", "since_clean", "doy_s", "doy_c", "tamb7", "tamb30", "wind7", "rain7", "fan7"]

def daily_features(hourly, cleanings, wx=None):
    """hourly: DataFrame with phi_hat, fan, T_amb (and ok flag). Returns one row per day."""
    h = hourly[hourly.get("ok", True) == True] if "ok" in hourly else hourly
    d = pd.DataFrame({"hi": h["phi_hat"].resample("1D").median(), "fan": h["fan"].resample("1D").mean(),
                      "T_amb": hourly["T_amb"].resample("1D").mean()})
    if wx is not None:
        if "wind" in wx: d["wind"] = wx["wind"].resample("1D").mean().reindex(d.index)
        if "rain" in wx and wx["rain"].notna().sum() > 300 * 24: d["rain"] = wx["rain"].resample("1D").sum().reindex(d.index)
    cl = sorted(pd.Timestamp(c) for c in cleanings)
    def since(t):
        prev = [c for c in cl if c <= t]
        return (t - prev[-1]).days if prev else 400
    d["since_clean"] = [since(t) for t in d.index]
    # rolling windows restart after a cleaning (old dirt is gone)
    grp = np.cumsum([1 if any(c.normalize() == t for c in cl) else 0 for t in d.index])
    g = d.groupby(grp)
    d["hi7"] = g["hi"].transform(lambda s: s.rolling(7, min_periods=3).median())
    d["slope14"] = g["hi7"].transform(lambda s: s.diff(14) / 14)
    d["slope30"] = g["hi7"].transform(lambda s: s.diff(30) / 30)
    d["doy_s"] = np.sin(2 * np.pi * d.index.dayofyear / 365.25); d["doy_c"] = np.cos(2 * np.pi * d.index.dayofyear / 365.25)
    d["tamb7"] = d["T_amb"].rolling(7, min_periods=3).mean(); d["tamb30"] = d["T_amb"].rolling(30, min_periods=10).mean()
    d["wind7"] = d["wind"].rolling(7, min_periods=3).mean() if "wind" in d else np.nan
    d["rain7"] = d["rain"].rolling(7, min_periods=3).sum() if "rain" in d else np.nan
    d["fan7"] = d["fan"].rolling(7, min_periods=3).mean()
    nxt = [min([c for c in cl if c > t], default=pd.Timestamp("2100-01-01")) for t in d.index]
    for hz in H:
        ok = np.array([(n - t).days > hz for n, t in zip(nxt, d.index)])
        d[f"y{hz}"] = np.where(ok, d["hi7"].shift(-hz), np.nan)
    return d

def _hgb(loss, q=None):
    kw = dict(loss=loss, max_iter=400, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=0.1, random_state=1)
    if q is not None: kw["quantile"] = q
    return HistGradientBoostingRegressor(**kw)

class Forecaster:
    def __init__(self, coverage=0.8):
        self.coverage = coverage; self.models = {}; self.Q = {}

    def fit(self, train_days, calib_days):
        self.feat = [f for f in FEAT if train_days[f].notna().mean() > 0.5]   # e.g. drop rain if no rain file
        for hz in H:
            tr = train_days.dropna(subset=[f"y{hz}", "hi7"]); ca = calib_days.dropna(subset=[f"y{hz}", "hi7"])
            ytr = tr[f"y{hz}"] - tr["hi7"]
            m50 = _hgb("absolute_error").fit(tr[self.feat], ytr)
            lo = _hgb("quantile", 0.1).fit(tr[self.feat], ytr); hi = _hgb("quantile", 0.9).fit(tr[self.feat], ytr)
            yca = ca[f"y{hz}"] - ca["hi7"]
            score = np.maximum(lo.predict(ca[self.feat]) - yca, yca - hi.predict(ca[self.feat]))
            n = len(score); self.Q[hz] = float(np.quantile(score, min(1, np.ceil((n + 1) * self.coverage) / n)))
            self.models[hz] = (m50, lo, hi)
        return self

    def predict(self, days):
        out = pd.DataFrame(index=days.index)
        sel = days["hi7"].notna()
        for hz in H:
            m50, lo, hi = self.models[hz]
            X = days.loc[sel, self.feat]; base = days.loc[sel, "hi7"]
            med = base + m50.predict(X)
            low = np.minimum(base + lo.predict(X), med) - self.Q[hz]      # keep low <= median <= high
            high = np.maximum(base + hi.predict(X), med) + self.Q[hz]
            out.loc[sel, f"q50_{hz}"] = med.clip(0, 0.85); out.loc[sel, f"q10_{hz}"] = low.clip(0, 0.85); out.loc[sel, f"q90_{hz}"] = high.clip(0, 0.85)
        return out

    def save(self, path): pickle.dump(self, open(path, "wb"))
    @staticmethod
    def load(path): return pickle.load(open(path, "rb"))

def days_until(row, thr):
    """Rough 'days until blockage reaches thr' from the 7/14/30-day forecasts (median and pessimistic)."""
    res = {}
    for q in ("q50", "q90"):
        pts = [(0, row["hi7"])] + [(hz, row[f"{q}_{hz}"]) for hz in H]
        val = None
        for (d0, v0), (d1, v1) in zip(pts, pts[1:]):
            if v0 >= thr: val = d0; break
            if v1 >= thr and v1 > v0: val = d0 + (thr - v0) / (v1 - v0) * (d1 - d0); break
        res[q] = None if val is None else round(float(val), 1)
    return res
