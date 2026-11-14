"""
Historian parser and data-quality audit.

Signals (workbook column -> meaning used here):
  1400TIA050        A-1401 inlet temperature, C          (P&ID: upstream of A-1401)
  1400TICA0055_pv   A-1401 outlet temperature, C         (P&ID: TT0055 on the outlet line)
  1400TICA0055_mv   outlet temperature controller output, %.  Used as fan speed command ONLY
                    because the 14 Nov 2026 PI Vision screen showed OP 87.6 % with VFD speed
                    TY0055 87.9 % (project audit); not independently verified for other dates.
  1400PICA0017_mv   pressure controller output to PV0017 (flare), %.  Not a pressure.
                    Used only to exclude hours in which gas may bypass FI010 to the flare.
  1400FI010         dry gas to PSA, Nm3/h (downstream of D-1403, after water knock-out)
Timestamps in the workbook column 'timestamp' are UTC; weather is joined in UTC.
"""
import os
import numpy as np
import pandas as pd

RENAME = {"1400TIA050": "T_in", "1400TICA0055_pv": "T_out", "1400TICA0055_mv": "ctrl_out",
          "1400PICA0017_mv": "pv0017", "1400FI010": "flow"}


def load_historian(path):
    d = pd.read_excel(path)
    d.index = pd.to_datetime(d["timestamp"].str.replace("Z", ""))
    d = d.sort_index()
    return d[list(RENAME)].rename(columns=RENAME)


def find_frozen(d, min_run=24):
    """Detect the start of a run in which ALL signals repeat the same value (frozen export)."""
    same = (d.diff().abs().fillna(1) < 1e-9).all(axis=1)
    run = same.groupby((~same).cumsum()).cumsum()
    long = run[run >= min_run]
    if long.empty:
        return None, 0
    end_of_first_long = long.index[0]
    start = d.index[d.index.get_loc(end_of_first_long) - min_run]
    n = int(same[start:].sum())
    return start, n


def load_weather(path):
    w = pd.read_csv(path, skiprows=3)
    w.index = pd.to_datetime(w["time"])                    # GMT (file metadata)
    col = [c for c in w.columns if c.startswith("temperature")][0]
    return w[[col]].rename(columns={col: "T_amb"})


def prepare(hist_path, wx_path):
    d = load_historian(hist_path)
    frozen_start, n_frozen = find_frozen(d)
    valid = d[d.index < frozen_start].copy() if frozen_start is not None else d.copy()
    valid = valid.join(load_weather(wx_path), how="left")
    valid["speed"] = valid["ctrl_out"] / 100.0
    valid["ok"] = ((valid.flow > 12000) & (valid.pv0017 < 1.0) & (valid.T_in > valid.T_out + 10) &
                   (valid.speed > 0.3) & valid[["T_in", "T_out", "flow", "speed", "T_amb"]].notna().all(axis=1))
    audit = dict(
        rows_total=int(len(d)), first=str(d.index.min()), last=str(d.index.max()),
        frozen_from_utc=str(frozen_start), frozen_rows=n_frozen,
        frozen_values={k: round(float(v), 3) for k, v in d.loc[frozen_start].items()} if frozen_start is not None else None,
        valid_rows=int(len(valid)), usable_hours=int(valid.ok.sum()),
        hours_fans_100pct=int(((valid.speed >= 0.995) & valid.ok).sum()),
        missing_T_out_pct=round(100 * valid.T_out.isna().mean(), 1),
        missing_flow_pct=round(100 * valid.flow.isna().mean(), 1),
        flare_open_hours=int((valid.pv0017 >= 1).sum()),
    )
    return valid, audit


def steady_window(d, start, end, hours=4, fans100=True, T_amb_range=None, prefer=None):
    """Pick one real, contiguous, steady window (all hours usable) inside [start, end).
    'prefer' = dict of target values; the window closest to them (normalised) is chosen."""
    x = d[start:end]
    best, best_score = None, np.inf
    for i in range(len(x) - hours + 1):
        w = x.iloc[i:i + hours]
        if (w.index[-1] - w.index[0]) != pd.Timedelta(hours=hours - 1) or not w.ok.all():
            continue
        if fans100 and (w.speed < 0.995).any():
            continue
        if w.T_in.std() > 1.0 or w.flow.std() > 400 or w.T_out.std() > 1.5:
            continue
        if T_amb_range and not (T_amb_range[0] <= w.T_amb.mean() <= T_amb_range[1]):
            continue
        score = 0.0
        if prefer:
            score = sum(abs(w[k].mean() - v) / s for k, (v, s) in prefer.items())
        if score < best_score:
            best, best_score = w, score
    return best
