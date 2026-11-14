"""Thermal impact diagnosis for A-1401. Writes results.json and charts/*.png"""
import json, math, os
import numpy as np
import a1401_model as m

out = {}
F_NOW, TIN_NOW, TOUT_SP = 20801, 166.8, 65.0
REC = 12200 / (0.744 * 20588)            # PSA H2 recovery from PFD = 0.796
out["psa_recovery"] = REC

# --- 1. design validation
out["design_check"] = {Ta: round(m.max_flow(135, Ta, 1.0, 0.0, T_limit=55)) for Ta in (30, 35, 38)}
out["design_flow_100pct_load"] = round(20588 / 0.58385)

# --- 2. clean-bundle numbers at design airflow
Qa = m.airflow_from_speed(1.0)
UAa, info = m.UA_air(Qa, 320)
out["clean_air_side"] = dict(airflow_m3s=Qa, V_face=info["V_face"], h_air=info["h"], Re=info["Re"],
                             fin_eff=info["eta_f"], surface_eff=info["eta_o"], UA_air_kWK=UAa / 1e3,
                             fan_kW_each=m.fan_power_kW(1.0) / 3)

# --- 3. anchor points
anchors = {"1 Jan 2026 (00-08h)": (144.7, 69.7, 22862, -2.0, 0.544),
           "14 Nov 2026 15:16": (166.8, 66.4, 20801, 6.5, 0.879)}
out["anchors"] = {}
for name, (Ti, To, F, Ta, sp) in anchors.items():
    Qa = m.airflow_from_speed(sp)
    fr, Q, inf = m.area_fraction_needed(Ti, To, F, Ta, Qa)
    b = m.duty_breakdown(Ti, To, F)
    phi = m.solve_phi(Ti, To, F, Ta, sp)
    out["anchors"][name] = dict(T_in=Ti, T_out=To, flow=F, T_amb=Ta, fan=sp, duty_MW=Q / 1e6,
                                breakdown={k: (v / 1e6 if k in ("total", "gas_sensible", "latent", "other_water_sensible") else v) for k, v in b.items()},
                                CF=fr, area_needed_vs_real=1 / fr, clean_T_out=m.solve_T_out(Ti, F, Ta, Qa), phi_equiv=phi,
                                airflow_pct_fouled=100 * m.fan_flow_ratio(sp, phi) / m.fan_flow_ratio(sp, 0))
phi_now = out["anchors"]["14 Nov 2026 15:16"]["phi_equiv"]

# R_d-only interpretation of 14 Nov
lo, hi = 0.0, 0.05
for _ in range(30):
    mid = (lo + hi) / 2
    if m.predict(166.8, 20801, 6.5, 0.879, 0.0, mid)[0] > 66.4: hi = mid
    else: lo = mid
out["Rd_only_equiv_m2KW"] = (lo + hi) / 2

# --- 4. sensitivity of phi_equiv (14 Nov)
sens = {}
def run(label, **kw):
    saved = {}
    for k, v in kw.items():
        if k == "speed": continue
        saved[k] = getattr(m, k); setattr(m, k, v)
    sp = kw.get("speed", 0.879)
    sens[label] = m.solve_phi(166.8, 66.4, 20801, 6.5, sp)
    for k, v in saved.items(): setattr(m, k, v)
run("base")
run("fan % maps to 25-50 Hz (speed 0.94)", speed=0.5 + 0.5 * 0.879)
run("tube-side film 4,000 W/m2K", H_COND_FILM=4000.0)
run("bundle = 85 % of fan pressure", SYS_OTHER=0.15)
run("bundle = 65 % of fan pressure", SYS_OTHER=0.35)
run("flow +10 % (flaring)", )
sens["flow +10 % (flaring)"] = m.solve_phi(166.8, 66.4, 20801 * 1.1, 6.5, 0.879)
sens["ambient +2 K"] = m.solve_phi(166.8, 66.4, 20801, 8.5, 0.879)
out["phi_sensitivity"] = sens

# --- 5. curves vs blockage, fans 100 %
phis = np.round(np.arange(0, 0.81, 0.05), 2)
curves = []
for p in phis:
    q = m.fan_flow_ratio(1.0, p)
    Qa = m.FAN["Q_design"] * q
    UAa, inf = m.UA_air(Qa, 320, p)
    To_s = m.solve_T_out(TIN_NOW, F_NOW, 38.0, Qa, p)
    curves.append(dict(phi=float(p), airflow_pct=100 * q, h_air=inf["h"], UA_air_pct=100 * UAa / out["clean_air_side"]["UA_air_kWK"] / 1e3,
                       fan_kW_each=m.fan_power_kW(1.0, p) / 3, T_out_summer38=To_s,
                       duty_summer38_MW=m.duty(TIN_NOW, To_s, F_NOW) / 1e6))
out["curves"] = curves

# --- 6. summer bottleneck
summer = {}
for Ta in (30.0, 35.0, 38.0, 41.0):
    row = {}
    for lab, p in (("clean", 0.0), ("now", phi_now)):
        for tin in (TIN_NOW, 144.7):
            To = m.predict(tin, F_NOW, Ta, 1.0, p)[0]
            mf = m.max_flow(tin, Ta, 1.0, p, T_limit=TOUT_SP)
            row[f"{lab}_Tin{int(tin)}"] = dict(T_out=To, max_flow=mf)
    summer[Ta] = row
out["summer"] = summer

# --- 7. hours per year and lost hydrogen (ERA5 Atyrau histograms, 1 K bins)
hist = {"2025": {35: 42, 36: 28, 37: 17, 38: 9, 39: 5, 34: 68, 33: 94, 32: 87, 31: 170, 30: 153, 29: 142, 28: 176, 27: 211, 26: 232, 25: 246, 24: 272, 23: 256, 22: 263, 21: 243, 20: 238},
        "2026": {40: 2, 39: 22, 38: 25, 37: 25, 36: 38, 35: 47, 34: 74, 33: 98, 32: 115, 31: 138, 30: 160, 29: 180, 28: 182, 27: 183, 26: 220, 25: 232, 24: 238, 23: 263, 22: 231, 21: 266, 20: 229}}
mf_cache = {}
def mflow(Ta, p, tin):
    k = (Ta, round(p, 3), tin)
    if k not in mf_cache: mf_cache[k] = m.max_flow(tin, Ta + 0.5, 1.0, p, T_limit=TOUT_SP)
    return mf_cache[k]
losses = {}
for yr, h in hist.items():
    for lab, p, tin in (("fouled_now_Tin167", phi_now, TIN_NOW), ("clean_Tin167", 0.0, TIN_NOW), ("fouled_now_Tin145", phi_now, 144.7)):
        lost_nm3 = 0.0; hours = 0
        for Ta, n in h.items():
            mf = mflow(Ta, p, tin)
            if mf < F_NOW:
                lost_nm3 += (F_NOW - mf) * n; hours += n
        h2_nm3 = lost_nm3 * 0.744 * REC
        losses[f"{yr}_{lab}"] = dict(hours_limited=hours, dry_syngas_lost_Nm3=lost_nm3, H2_lost_Nm3=h2_nm3, H2_lost_t=h2_nm3 * 0.08988 / 1000)
out["losses"] = losses
out["max_flow_table"] = {f"{k[0]}C_phi{k[1]}_Tin{k[2]}": v for k, v in mf_cache.items()}

json.dump(out, open("results.json", "w"), indent=1, default=float)
print(json.dumps({k: out[k] for k in ("design_check", "anchors", "Rd_only_equiv_m2KW", "phi_sensitivity", "summer", "losses")}, indent=1, default=lambda x: round(float(x), 3)))
