"""Step 1 of the monitoring model: turn plant readings into ONE health number.

Health indicator (HI) = cleanliness factor CF = UA_actual / UA_clean.
  - 1.0  = cooler as good as new
  - 0.5  = cooler does half the heat transfer it should (what we found on 14 Nov)
For each time step we take inlet T (TIA050), outlet T (TICA0055), dry-gas flow (FI010), fan speed (TY0055)
and outside air T, and ask the physics model: "how much of the clean cooler's heat-transfer ability
is needed to explain this outlet temperature?" That removes the effect of weather, load and fan speed,
so what's left is (mostly) fouling.

We also convert CF to the "equivalent blocked fraction" phi with a lookup table (CF -> phi depends a
little on fan speed), so operators see a % that matches the 3D model and the slides.
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import a1401_model as m

HERE = os.path.dirname(os.path.abspath(__file__))

def cf_from_readings(T_in, T_out, flow, T_amb, speed):
    """Cleanliness factor from one set of readings (about 0.2 s per call)."""
    fr, Q, _ = m.area_fraction_needed(T_in, T_out, flow, T_amb, m.airflow_from_speed(speed))
    return fr, Q

def build_lookup(path=os.path.join(HERE, "cf_to_phi_table.json")):
    """CF as a function of phi and fan speed, at 14-Nov-like conditions. Built once (about 2 min)."""
    if os.path.exists(path):
        return json.load(open(path))
    phis = [round(x, 2) for x in np.arange(0, 0.81, 0.05)]
    speeds = [0.5, 0.7, 0.88, 1.0]
    tab = {}
    for sp in speeds:
        row = []
        for p in phis:
            T_out = m.predict(166.8, 20801, 6.5, sp, p)[0]
            cf, _ = cf_from_readings(166.8, T_out, 20801, 6.5, sp)
            row.append(cf)
        tab[str(sp)] = row
        print("speed", sp, [round(c, 3) for c in row], flush=True)
    out = dict(phi=phis, cf=tab)
    json.dump(out, open(path, "w"), indent=1)
    return out

def phi_from_cf(cf, speed, tab):
    sps = sorted(float(s) for s in tab["cf"])
    s = min(sps, key=lambda x: abs(x - speed))
    cfs = np.array(tab["cf"][str(s)]); ph = np.array(tab["phi"])
    order = np.argsort(cfs)                       # cf falls as phi rises
    return float(np.interp(cf, cfs[order], ph[order]))

DATA = "/mnt/user-data/uploads/catalyst/drive-download-20261114T094529Z-1-001/"
TAGS = {"T_in": "DATA - TIA050, 01_01_2026-13_11_2026.xlsx", "T_out": "DATA - TICA0055 - 01_01_2026 - 13_11_2026.xlsx",
        "flow": "DATA - FI010, 01_01_2026 - 13_11_2026.xlsx", "fan": "DATA TY0055A_B_C - 01_01_2026 - 13_11_2026.xlsx"}

def load_pi(freq="2min"):
    cols = {}
    for k, f in TAGS.items():
        d = pd.read_excel(DATA + f, sheet_name=0, skiprows=2)
        d.columns = ["src", "time", "value"]
        s = pd.Series(pd.to_numeric(d["value"], errors="coerce").values, index=pd.to_datetime(d["time"])).dropna()
        cols[k] = s.resample(freq).mean()
    df = pd.DataFrame(cols).dropna()           # keep only times where every tag exists
    df["fan"] = df["fan"] / 100.0
    return df

if __name__ == "__main__":
    tab = build_lookup()
    df = load_pi()
    df["T_amb"] = -2.0   # ERA5 hourly mean for 1 Jan 00-03 h (A9); replace with the hourly CSV when it is in weather/
    out = []
    for t, r in df.iterrows():
        cf, Q = cf_from_readings(r.T_in, r.T_out, r.flow, r.T_amb, r.fan)
        out.append(dict(time=str(t), cf=cf, phi=phi_from_cf(cf, r.fan, tab), duty_MW=Q / 1e6))
    res = pd.DataFrame(out)
    nov_cf, _ = cf_from_readings(166.8, 66.4, 20801, 6.5, 0.879)
    summary = dict(jan_points=len(res), jan_window=[res.time.iloc[0], res.time.iloc[-1]],
                   jan_cf_mean=res.cf.mean(), jan_cf_std=res.cf.std(), jan_phi_mean=res.phi.mean(), jan_phi_std=res.phi.std(),
                   nov_cf=nov_cf, nov_phi=phi_from_cf(nov_cf, 0.879, tab))
    res.to_csv(os.path.join(HERE, "hi_january.csv"), index=False)
    json.dump(summary, open(os.path.join(HERE, "hi_summary.json"), "w"), indent=1, default=float)
    print(json.dumps(summary, indent=1, default=float))
