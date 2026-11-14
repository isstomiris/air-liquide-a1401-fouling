"""Loading plant and weather data, and cleaning it before the physics sees it.

Plant data, either:
  * a folder of PI exports in the format Air Liquide sent (one .xlsx per tag, header rows, Time/Value), or
  * one tidy CSV with columns: time, T_in, T_out, flow, fan (%), and optionally pv0017 (%, flare valve).
Weather: Open-Meteo CSV(s). Temperature + wind are required; precipitation is optional.
All times are converted to local plant time (Asia/Almaty, UTC+5).
"""
import os, glob
import numpy as np, pandas as pd

PI_TAGS = {"T_in": ["TIA050"], "T_out": ["TICA0055"], "flow": ["FI010"], "fan": ["TY0055"], "pv0017": ["PV0017", "PIC0017_OUT"]}

def _read_pi_xlsx(path):
    d = pd.read_excel(path, sheet_name=0, skiprows=2)
    d = d.iloc[:, -2:]; d.columns = ["time", "value"]
    s = pd.Series(pd.to_numeric(d["value"], errors="coerce").values, index=pd.to_datetime(d["time"], errors="coerce"))
    return s[s.index.notna()].dropna().sort_index()

def load_plant(src, freq="1h"):
    if os.path.isdir(src):
        cols = {}
        files = glob.glob(os.path.join(src, "*.xlsx"))
        for key, names in PI_TAGS.items():
            f = next((f for f in files for nm in names if nm in os.path.basename(f).upper().replace(" ", "")), None)
            if f:
                cols[key] = _read_pi_xlsx(f).resample(freq).mean()
        df = pd.DataFrame(cols)
    else:
        df = pd.read_csv(src, parse_dates=["time"]).set_index("time").resample(freq).mean()
    if "fan" in df and df["fan"].max() > 1.5:
        df["fan"] = df["fan"] / 100.0
    return df

def _read_openmeteo(path):
    rows = open(path, encoding="utf-8").read().splitlines()
    head = rows[1].split(",") if len(rows) > 1 else []
    k = next(i for i, r in enumerate(rows) if r.startswith("time"))
    w = pd.read_csv(path, skiprows=k)
    w["time"] = pd.to_datetime(w["time"]); w = w.set_index("time")
    # Open-Meteo writes either local time (timezone column) or GMT with utc_offset_seconds
    meta = dict(zip(rows[0].split(","), head))
    off = int(float(meta.get("utc_offset_seconds", "18000") or 18000))
    tz = meta.get("timezone", "")
    if tz in ("GMT", "UTC") or off == 0:
        w.index = w.index + pd.Timedelta(hours=5)        # to Asia/Almaty local
    ren = {}
    for c in w.columns:
        cl = c.lower()
        if cl.startswith("temperature"): ren[c] = "T_amb"
        elif cl.startswith("wind"): ren[c] = "wind"
        elif cl.startswith("precip") or cl.startswith("rain"): ren[c] = "rain"
        elif cl.startswith("relative_humidity"): ren[c] = "rh"
    return w.rename(columns=ren)

def load_weather(paths):
    parts = [_read_openmeteo(p) for p in paths if p and os.path.exists(p)]
    if not parts:
        raise FileNotFoundError("no weather file found")
    w = parts[0]
    for p in parts[1:]:
        w = w.combine_first(p)        # fill gaps and add columns/years from the other files
    return w.sort_index()

def find_weather(base):
    """All Open-Meteo CSVs for Atyrau (47.1 N 51.9 E) in the usual folders."""
    cands = []
    for d in [os.path.join(base, "weather"), os.path.join(base, "..", "weather"), os.path.expanduser("~/hackathonIndustry/weather")]:
        cands += glob.glob(os.path.join(d, "*.csv"))
    out = []
    for c in cands:
        try:
            meta = open(c, encoding="utf-8").read(300).splitlines()[1]
            lat, lon = (float(x) for x in meta.split(",")[:2])
            if abs(lat - 47.13) < 0.3 and abs(lon - 51.9) < 0.3:
                out.append(c)
        except Exception:
            pass
    return sorted(set(out))

def clean(df, flow_normal=20800):
    """Keep only hours where the physics can be trusted. Each rule is explained in the report."""
    flags = pd.DataFrame(index=df.index)
    flags["missing"] = df[["T_in", "T_out", "flow", "fan", "T_amb"]].isna().any(axis=1)
    flags["low_load"] = df["flow"] < 0.3 * flow_normal                     # start-up / shutdown
    flags["flaring"] = (df["pv0017"] > 1.0) if "pv0017" in df else False  # FI010 under-reads when gas is flared
    flags["unsteady"] = df["T_out"].diff().abs() > 5.0                     # large jumps: not steady state
    flags["inlet_below_outlet"] = df["T_in"] < df["T_out"] + 10
    df = df.copy(); df["ok"] = ~flags.any(axis=1)
    return df, flags.sum().to_dict()
