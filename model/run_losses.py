"""H2-loss scenarios for A-1401 using real Atyrau weather.

Weather source (audit M1): ERA5 reanalysis via Open-Meteo, point 47.12 N 51.92 E, hourly 2-m air
temperature, 1 Jan 2025 - 13 Nov 2026. If the CSV file
  atyrau_open-meteo_47.12N_51.92E_2025-01-01_2026-11-13.csv
is found in ../weather/, the hackathonIndustry folder or the catalyst folder, the hour counts are
built from it. Otherwise the script falls back to the 1-degree hour counts below, which were made
from exactly the same ERA5 download (so the answer is the same; the CSV just lets anyone check it).

Scenarios (audit M3): blockage 35 / 50 / 65 % x inlet gas 145 / 167 C, plus clean.
"""
import json, glob, os, csv, collections
import a1401_model as m

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "atyrau_open-meteo_47.12N_51.92E_2025-01-01_2026-11-13.csv"
SEARCH = [os.path.join(HERE, "..", "weather", NAME),
          os.path.expanduser("~/hackathonIndustry/" + NAME),
          os.path.expanduser("~/hackathonIndustry/weather/" + NAME)] + \
         glob.glob(os.path.expanduser("~/catalyst/**/" + NAME), recursive=True) + \
         glob.glob("/mnt/user-data/uploads/**/" + NAME, recursive=True)

H25 = {"0":284,"1":218,"2":164,"3":157,"4":134,"5":193,"6":198,"7":187,"8":207,"9":214,"10":194,"11":188,"12":241,"13":165,"14":191,"15":194,"16":196,"17":224,"18":243,"19":219,"20":238,"21":243,"22":263,"23":256,"24":272,"25":246,"26":232,"27":211,"28":176,"29":142,"30":153,"31":170,"32":87,"33":94,"34":68,"35":42,"36":28,"37":17,"38":9,"39":5,"-1":332,"-2":233,"-3":210,"-4":196,"-5":131,"-6":108,"-7":109,"-8":131,"-9":115,"-10":69,"-11":59,"-12":45,"-13":31,"-14":11,"-15":7,"-16":2,"-17":4,"-18":2,"-21":1,"-19":1}
H26 = {"0":134,"1":135,"2":132,"3":104,"4":102,"5":91,"6":105,"7":128,"8":121,"9":158,"10":161,"11":172,"12":193,"13":212,"14":222,"15":223,"16":222,"17":220,"18":214,"19":255,"20":229,"21":266,"22":231,"23":263,"24":238,"25":232,"26":220,"27":183,"28":182,"29":180,"30":160,"31":138,"32":115,"33":98,"34":74,"35":47,"36":38,"37":25,"38":25,"39":22,"40":2,"-1":152,"-2":131,"-3":122,"-4":103,"-6":84,"-5":96,"-7":98,"-8":89,"-9":58,"-10":68,"-11":42,"-12":52,"-13":62,"-15":25,"-17":29,"-16":30,"-14":29,"-18":24,"-19":9,"-20":9}

def histograms_from_csv(path):
    """1-degree bins (floor) of hourly temperature, per year."""
    import math
    H = {"2025": collections.Counter(), "2026_Jan-Nov": collections.Counter()}
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    start = next(i for i, r in enumerate(rows) if r and r[0] == "time")
    for r in rows[start + 1:]:
        if len(r) < 2 or r[1] == "":
            continue
        yr = "2025" if r[0].startswith("2025") else "2026_Jan-Nov"
        H[yr][str(math.floor(float(r[1])))] += 1
    return {k: dict(v) for k, v in H.items()}

src = next((p for p in SEARCH if os.path.exists(p)), None)
if src:
    HIST = histograms_from_csv(src); SOURCE = "csv: " + os.path.basename(src)
else:
    HIST = {"2025": H25, "2026_Jan-Nov": H26}; SOURCE = "embedded hour counts from the same ERA5 download"

R = json.load(open(os.path.join(HERE, "results.json")))
REC = R["psa_recovery"]
F_NOW = 20801          # Nm3/h dry syngas on 14 Nov (FI010, no flaring) [A2]
T_LIMIT = 65.0         # C, D-1403 gas outlet limit [A1]
PHIS = [0.0, 0.35, 0.50, 0.65]
TINS = [144.7, 166.8]  # 145 = 1 Jan style inlet, 167 = 14 Nov inlet (PV0017)

cache = {}
def mf(Ta, p, tin):
    k = (Ta, p, tin)
    if k not in cache:
        cache[k] = m.max_flow(tin, Ta + 0.5, 1.0, p, T_limit=T_LIMIT)   # bin centre
    return cache[k]

scen = {}
for p in PHIS:
    for tin in TINS:
        if p == 0.0 and tin < 150:
            continue          # clean + cool inlet obviously never limits
        lab = f"phi{int(p*100)}_Tin{round(tin)}"
        # threshold: first 1-degree bin (from warm side scan) where max flow < current flow
        temps = sorted({int(k) for h in HIST.values() for k in h})
        thr = None
        out = {}
        for Ta in range(0, 46):
            if mf(Ta, p, tin) < F_NOW and thr is None:
                thr = Ta
        for yr, h in HIST.items():
            lost = hrs = 0
            for k, n in h.items():
                Ta = int(k)
                if Ta < 0:
                    continue
                x = mf(Ta, p, tin)
                if x < F_NOW:
                    lost += (F_NOW - x) * n; hrs += n
            h2 = lost * 0.744 * REC
            out[yr] = dict(hours_limited=hrs, H2_lost_t=round(h2 * 0.08988 / 1000, 1))
        scen[lab] = dict(phi=p, T_in=tin, limit_starts_at_Tamb_C=thr, **out)
        print(lab, thr, out, flush=True)

R["loss_scenarios"] = dict(weather_source=SOURCE, F_now_Nm3h=F_NOW, T_limit_C=T_LIMIT,
                           note="Upper-bound style: assumes the plant would otherwise run at 20,801 Nm3/h every hour of the year.",
                           scenarios=scen,
                           max_flow_vs_Tamb={f"phi{int(p*100)}_Tin{round(t)}": {str(Ta): v for (Ta, pp, tt), v in sorted(cache.items()) if pp == p and tt == t}
                                             for p in PHIS for t in TINS if not (p == 0.0 and t < 150)})
json.dump(R, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
