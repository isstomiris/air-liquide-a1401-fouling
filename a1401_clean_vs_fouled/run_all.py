"""
A-1401 clean vs fouled rating study - runs every calculation, writes every result and figure.

    python run_all.py            (about 5-10 minutes on a laptop, 4 cores)

Outputs go to ./results (CSV/JSON) and ./figures (PNG).
"""
import json, os, sys, time, math
from multiprocessing import Pool
import numpy as np
import pandas as pd
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from a1401sim import config as C
from a1401sim.thermo import WetSyngas, saturation_ratio, nm3h_to_mol_s
from a1401sim.exchanger import rate, scalar
from a1401sim.airside import G, BUNDLE_SHARE, DP_BUNDLE_RB_RATED, FAN_VELOCITY_PRESSURE, airflow
from a1401sim import history as H

RES = os.path.join(HERE, "results"); FIG = os.path.join(HERE, "figures")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
HIST = os.path.join(HERE, "data", "historian_full.xlsx")
WX = os.path.join(HERE, "data", "atyrau_precip_temp_2023-01-01_2026-11-14.csv")
B_GRID = np.array([0, .1, .2, .3, .4, .5, .55, .6, .65, .7, .75, .8, .85])
GAS = None


def _gas():
    global GAS
    if GAS is None:
        GAS = WetSyngas()
    return GAS


def _grid_row(args):
    T_in, flow, T_amb, speed = args
    return [rate(T_in, flow, T_amb, speed, b, gas=_gas())["T_out_C"] for b in B_GRID]


def b_from_grid(Tgrid, T_meas):
    """equivalent blockage at which the model reproduces the measured outlet (linear interpolation)"""
    if T_meas <= Tgrid[0]:
        return 0.0
    if T_meas >= Tgrid[-1]:
        return float("nan")
    return float(np.interp(T_meas, Tgrid, B_GRID))


def T_at_b(Tgrid, b):
    return float(np.interp(b, B_GRID, Tgrid))


def fit_b(T_in, flow, T_amb, speed, T_out, gas, **kw):
    f = lambda b: rate(T_in, flow, T_amb, speed, b, gas=gas, **kw)["T_out_C"] - T_out
    if f(0.0) >= 0:
        return 0.0
    if f(0.9) < 0:
        return float("nan")
    return brentq(f, 0.0, 0.9, xtol=1e-4)


def main():
    t0 = time.time()
    out = {}
    gas = _gas()
    # ============================================================ 1. historian audit
    d, audit = H.prepare(HIST, WX)
    out["historian_audit"] = audit
    print("audit", audit)

    # ============================================================ 2. operating intervals
    summer = H.steady_window(d, "2025-07-01", "2025-09-01", hours=4, fans100=True, T_amb_range=(28, 32),
                             prefer={"T_in": (160.0, 3.0), "flow": (17500.0, 1000.0)})
    jan = d["2026-01-01 00:00":"2026-01-01 02:00"]
    def summarise(w, label):
        return dict(label=label, start_utc=str(w.index[0]), end_utc=str(w.index[-1]), hours=len(w),
                    T_in_C=round(w.T_in.mean(), 2), T_out_C=round(w.T_out.mean(), 2),
                    flow_dry_Nm3h=round(w.flow.mean(), 0), ctrl_out_pct=round(100 * w.speed.mean(), 2),
                    pv0017_pct=round(w.pv0017.mean(), 2), T_amb_C=round(w.T_amb.mean(), 2),
                    T_in_std=round(w.T_in.std(), 2), flow_std=round(w.flow.std(), 0))
    REF = summarise(summer, "Summer reference, fans 100 %")
    JAN = summarise(jan, "1 Jan 2026 00-02 UTC (team brief interval)")
    out["intervals"] = [REF, JAN]
    print(REF); print(JAN)

    # ============================================================ 3. equivalent blockage on history
    # usable hours with fans at 100 % (no ambiguity in the fan-speed mapping) and air >= 10 C
    # (louvres assumed open; winter louvre position is not recorded)
    sel = d[d.ok & (d.speed >= 0.995) & (d.T_amb >= 10.0)].copy()
    args = list(zip(sel.T_in, sel.flow, sel.T_amb, np.ones(len(sel))))
    print("history hours to rate:", len(sel))
    cache = os.path.join(RES, "_history_grid_cache.npz")
    if os.path.exists(cache) and len(np.load(cache)["g"]) == len(args) and "--fresh" not in sys.argv:
        grids = np.load(cache)["g"]                      # delete this file (or use --fresh) to recompute
    else:
        with Pool(max(1, os.cpu_count())) as p:
            grids = np.array(p.map(_grid_row, args, chunksize=20))
        np.savez_compressed(cache, g=grids, b=B_GRID)
    sel["b_eq"] = [b_from_grid(g, t) for g, t in zip(grids, sel.T_out)]
    sel["T_clean_pred"] = grids[:, 0]
    for i, bb in enumerate(B_GRID):
        sel[f"T_b{int(round(100*bb))}"] = grids[:, i]
    sel.drop(columns=[c for c in sel.columns if c.startswith("T_b")]).to_csv(os.path.join(RES, "history_equivalent_blockage_hourly.csv"))

    periods = {
        "Spring 2024 (1 Apr-15 May)": ("2024-04-01", "2024-05-16"),
        "End of summer 2024 (1 Aug-15 Sep)": ("2024-08-01", "2024-09-16"),
        "Spring 2025 (1 Apr-15 May)": ("2025-04-01", "2025-05-16"),
        "End of summer 2025 (1 Aug-15 Sep)": ("2025-08-01", "2025-09-16"),
    }
    per_rows, val_rows = [], []
    for name, (a, b_) in periods.items():
        x = sel[a:b_]
        wk = x.index.isocalendar().week.values
        cal, val = x[wk % 2 == 0], x[wk % 2 == 1]
        gcal = grids[[sel.index.get_loc(i) for i in cal.index]]
        gval = grids[[sel.index.get_loc(i) for i in val.index]]
        # calibration: one b for the whole period, least squares on calibration hours
        sse = lambda bb: np.nansum([(T_at_b(g, bb) - t) ** 2 for g, t in zip(gcal, cal.T_out)])
        bs = np.linspace(0, 0.85, 171); b_fit = float(bs[np.argmin([sse(bb) for bb in bs])])
        pred = np.array([T_at_b(g, b_fit) for g in gval])
        err = pred - val.T_out.values
        naive = val.T_out.values - cal.T_out.mean()
        r = dict(period=name, hours_total=len(x), hours_calibration=len(cal), hours_withheld=len(val),
                 b_fitted_on_calibration=round(b_fit, 3), b_eq_median_all=round(float(x.b_eq.median()), 3),
                 b_eq_p10=round(float(x.b_eq.quantile(.1)), 3), b_eq_p90=round(float(x.b_eq.quantile(.9)), 3),
                 withheld_MAE_K=round(float(np.mean(np.abs(err))), 2), withheld_bias_K=round(float(np.mean(err)), 2),
                 withheld_RMSE_K=round(float(np.sqrt(np.mean(err ** 2))), 2),
                 naive_constant_MAE_K=round(float(np.mean(np.abs(naive))), 2),
                 clean_model_MAE_K=round(float(np.mean(np.abs(gval[:, 0] - val.T_out.values))), 2),
                 T_amb_mean=round(float(x.T_amb.mean()), 1), T_out_meas_mean=round(float(x.T_out.mean()), 1),
                 flow_mean=round(float(x.flow.mean()), 0), T_in_mean=round(float(x.T_in.mean()), 1))
        per_rows.append(r)
        val_rows.append(pd.DataFrame(dict(period=name, T_out_meas=val.T_out.values, T_out_pred=pred,
                                          T_out_clean_pred=gval[:, 0]), index=val.index))
    per = pd.DataFrame(per_rows); per.to_csv(os.path.join(RES, "history_periods_calibration_validation.csv"), index=False)
    vals = pd.concat(val_rows); vals.to_csv(os.path.join(RES, "history_withheld_predictions.csv"))
    out["history_periods"] = per_rows
    print(per.to_string())

    b_spring = float(per.loc[per.period.str.startswith("Spring 2025"), "b_fitted_on_calibration"].iloc[0])
    b_summer = float(per.loc[per.period.str.startswith("End of summer 2025"), "b_fitted_on_calibration"].iloc[0])
    b_window = fit_b(REF["T_in_C"], REF["flow_dry_Nm3h"], REF["T_amb_C"], 1.0, REF["T_out_C"], gas)

    # ============================================================ 4. clean vs fouled at the summer reference
    cases = [("A  Clean (0 %)", 0.0),
             ("B  Assumed 30 % (team brief input)", 0.30),
             ("C  Plant state, spring 2025 (fitted)", b_spring),
             ("D  Plant state, end of summer 2025 (fitted)", b_summer)]
    rows = []
    for lab, bb in cases:
        r = scalar(rate(REF["T_in_C"], REF["flow_dry_Nm3h"], REF["T_amb_C"], 1.0, bb, gas=gas))
        r["case"] = lab; rows.append(r)
    cmp_ = pd.DataFrame(rows).set_index("case")
    clean = cmp_.iloc[0]
    cmp_["duty_loss_vs_clean_pct"] = 100 * (clean.Q_total_kW - cmp_.Q_total_kW) / clean.Q_total_kW
    cmp_["UA_loss_vs_clean_pct"] = 100 * (clean.UA_total_kW_K - cmp_.UA_total_kW_K) / clean.UA_total_kW_K
    # capacity at the outlet set point: largest dry-gas flow that still leaves at <= 65 C (same inlet/air)
    def max_flow(bb, T_set=65.0):
        f = lambda fl: rate(REF["T_in_C"], fl, REF["T_amb_C"], 1.0, bb, gas=gas)["T_out_C"] - T_set
        return brentq(f, 3000.0, 80000.0, xtol=20.0) if f(3000.0) < 0 < f(80000.0) else float("nan")
    cmp_["max_flow_at_65C_Nm3h"] = [max_flow(bb) for _, bb in cases]
    cmp_["capacity_loss_vs_clean_pct"] = 100 * (cmp_.max_flow_at_65C_Nm3h.iloc[0] - cmp_.max_flow_at_65C_Nm3h) / cmp_.max_flow_at_65C_Nm3h.iloc[0]
    cmp_.T.to_csv(os.path.join(RES, "clean_vs_fouled_full.csv"))
    out["reference_window_b_fit_check"] = round(b_window, 3)
    out["cases"] = {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in cmp_.T.to_dict().items()}

    # brief's table layout, with explicit differences vs clean
    metrics = [("Air volumetric flow, m3/h (at fan, ambient)", "air_m3h", 0), ("Air mass flow, kg/s", "air_kg_s", 1),
               ("Effective UA (physical), kW/K", "UA_total_kW_K", 1), ("Apparent UA = Q/LMTD, kW/K", "UA_apparent_LMTD_kW_K", 1),
               ("Total heat duty, kW", "Q_total_kW", 0), ("Sensible heat duty, kW", "Q_sensible_kW", 0),
               ("Condensation (latent) duty, kW", "Q_latent_kW", 0), ("Syngas inlet temperature, C", "T_in_C", 1),
               ("Syngas outlet temperature, C", "T_out_C", 1), ("Air inlet temperature, C", "T_amb_C", 1),
               ("Air outlet temperature (mixed), C", "T_air_out_C", 1), ("Water condensed in A-1401, kg/h", "condensed_kg_h", 0),
               ("Air-side h, W/m2K", "h_air_W_m2K", 1), ("Active finned area, m2", "A_active_m2", 0),
               ("Fan pressure rise (total), Pa", "fan_dP_Pa", 0),
               ("Thermal performance loss vs clean (duty), %", "duty_loss_vs_clean_pct", 1),
               ("UA loss vs clean, %", "UA_loss_vs_clean_pct", 1),
               ("Max dry-gas flow for outlet <= 65 C, Nm3/h", "max_flow_at_65C_Nm3h", 0),
               ("Capacity loss vs clean at 65 C outlet, %", "capacity_loss_vs_clean_pct", 1)]
    tbl = []
    for lab, key, nd in metrics:
        row = {"Parameter": lab}
        for c in cmp_.index:
            row[c] = round(float(cmp_.loc[c, key]), nd)
        for c in cmp_.index[1:]:
            row["Diff " + c[:1] + "-A"] = round(float(cmp_.loc[c, key] - cmp_.loc[cmp_.index[0], key]), nd)
        tbl.append(row)
    tbl = pd.DataFrame(tbl); tbl.to_csv(os.path.join(RES, "clean_vs_fouled_table.csv"), index=False)
    print(tbl.to_string())

    # same comparison for the 1 Jan interval (winter, fans 54 %; louvre position unknown)
    jrows = []
    for lab, bb in cases:
        r = scalar(rate(JAN["T_in_C"], JAN["flow_dry_Nm3h"], JAN["T_amb_C"], JAN["ctrl_out_pct"] / 100, bb, gas=gas)); r["case"] = lab; jrows.append(r)
    pd.DataFrame(jrows).set_index("case").T.to_csv(os.path.join(RES, "clean_vs_fouled_1jan2026.csv"))
    out["jan_case"] = {r["case"]: dict(T_out_C=round(r["T_out_C"], 1), Q_kW=round(r["Q_total_kW"]), air_m3h=round(r["air_m3h"])) for r in jrows}
    out["jan_b_equivalent"] = round(fit_b(JAN["T_in_C"], JAN["flow_dry_Nm3h"], JAN["T_amb_C"], JAN["ctrl_out_pct"] / 100, JAN["T_out_C"], gas), 3)

    # ============================================================ 5. blockage sweep 0-70 %
    sw = []
    for bb in np.round(np.arange(0, 0.701, 0.05), 3):
        r = scalar(rate(REF["T_in_C"], REF["flow_dry_Nm3h"], REF["T_amb_C"], 1.0, bb, gas=gas)); sw.append(r)
    sweep = pd.DataFrame(sw)
    sweep["duty_loss_pct"] = 100 * (sweep.Q_total_kW.iloc[0] - sweep.Q_total_kW) / sweep.Q_total_kW.iloc[0]
    keep = ["blockage", "air_m3h", "air_frac_of_rated", "air_kg_s", "fan_dP_Pa", "h_air_W_m2K", "UA_air_kW_K", "UA_total_kW_K",
            "Q_total_kW", "Q_sensible_kW", "Q_latent_kW", "T_out_C", "T_air_out_C", "condensed_kg_h", "duty_loss_pct", "fan_power_kW_each"]
    sweep[keep].round(3).to_csv(os.path.join(RES, "blockage_sweep.csv"), index=False)
    # monotonicity check
    out["sweep_monotonic"] = dict(T_out_increasing=bool(np.all(np.diff(sweep.T_out_C) > 0)),
                                  duty_decreasing=bool(np.all(np.diff(sweep.Q_total_kW) < 0)),
                                  airflow_decreasing=bool(np.all(np.diff(sweep.air_m3h) < 0)),
                                  UA_decreasing=bool(np.all(np.diff(sweep.UA_total_kW_K) < 0)))
    # simple reference approximation from the brief: m_air,f = (1-b) m_air,clean, area unchanged
    simple = []
    for bb in (0.0, 0.3):
        r = rate(REF["T_in_C"], REF["flow_dry_Nm3h"], REF["T_amb_C"], 1.0, 0.0, gas=gas, Q_air_override=(1 - bb) * 95.0)
        simple.append(dict(b=bb, air_m3h=r["air_m3h"], T_out_C=r["T_out_C"], Q_kW=r["Q_total_kW"], UA_kW_K=r["UA_total_kW_K"]))
    out["brief_simple_approximation"] = simple

    # ============================================================ 6. sensitivity (one at a time)
    def scen(name, gas_=None, refit=True, T_amb_shift=0.0, flow_mult=1.0, **kw):
        g_ = gas_ or gas
        Ta = REF["T_amb_C"] + T_amb_shift; fl = REF["flow_dry_Nm3h"] * flow_mult
        rc = rate(REF["T_in_C"], fl, Ta, 1.0, 0.0, gas=g_, **kw)
        bb = fit_b(REF["T_in_C"], fl, Ta, 1.0, REF["T_out_C"], g_, **kw)
        rf = rate(REF["T_in_C"], fl, Ta, 1.0, bb, gas=g_, **kw) if not math.isnan(bb) else None
        r30 = rate(REF["T_in_C"], fl, Ta, 1.0, 0.30, gas=g_, **kw)
        return dict(scenario=name, clean_T_out_C=rc["T_out_C"], clean_Q_kW=rc["Q_total_kW"], clean_UA_kW_K=rc["UA_total_kW_K"],
                    b30_T_out_C=r30["T_out_C"], b30_duty_loss_pct=100 * (rc["Q_total_kW"] - r30["Q_total_kW"]) / rc["Q_total_kW"],
                    b_eq_fitted=bb, actual_Q_kW=rf["Q_total_kW"] if rf else float("nan"),
                    actual_duty_loss_pct=100 * (rc["Q_total_kW"] - rf["Q_total_kW"]) / rc["Q_total_kW"] if rf else float("nan"),
                    actual_air_frac=rf["air_frac_of_rated"] if rf else float("nan"))
    W_sat = saturation_ratio(REF["T_in_C"] + 273.15)
    sens = [scen("Base case")]
    sens += [scen("Water/dry gas 0.24 (carbon-balance case)", WetSyngas(W=0.24)),
             scen(f"Water/dry gas {W_sat:.3f} (just saturated at inlet)", WetSyngas(W=W_sat)),
             scen("Water enhancement factor 1.03", WetSyngas(f=1.03)),
             scen("Air-side h -20 % (correlation scatter)", h_mult=0.8), scen("Air-side h +20 %", h_mult=1.2),
             scen("Condensate film h 4,000 W/m2K", h_film=4000.0), scen("Condensate film h 16,000 W/m2K", h_film=16000.0),
             scen("Air inlet +2 K (recirculation / ERA5 bias)", T_amb_shift=2.0), scen("Air inlet -2 K", T_amb_shift=-2.0),
             scen("Gas flow +10 % (FI010 reads low)", flow_mult=1.10), scen("Gas flow +25 %", flow_mult=1.25),
             scen("Bundle share of fan dP 0.65", bundle_share=0.65), scen("Bundle share of fan dP 0.95", bundle_share=0.95),
             scen("Fan curve flatter (a=1.3, c=0.3)", fan_a=1.3, fan_b=0.3), scen("Fan curve steeper (a=2.0, c=1.0)", fan_a=2.0, fan_b=1.0)]
    sens = pd.DataFrame(sens); sens.round(3).to_csv(os.path.join(RES, "sensitivity.csv"), index=False)
    print(sens.round(2).to_string())

    # ============================================================ 7. design consistency
    design_flow_100 = 20588 / 0.58385
    def design_resid(Ta, flow):
        return rate(135.0, flow, Ta, 1.0, 0.0, gas=gas)["T_out_C"] - 55.0
    try:
        Ta_design = brentq(lambda t: design_resid(t, design_flow_100), 0.0, 54.0, xtol=0.05)
    except ValueError:
        Ta_design = float("nan")
    dsg = rate(135.0, design_flow_100, 35.0, 1.0, 0.0, gas=gas)
    pfd = rate(135.0, 20588, 35.0, 1.0, 0.0, gas=gas)
    # what UA does the DESIGN duty imply?  and what would a dry-gas-only (m cp dT) duty imply?
    n_d = nm3h_to_mol_s(design_flow_100)
    bd = gas.breakdown(135 + 273.15, 55 + 273.15, n_d)
    Q_wet = bd["total_W"]; Q_dry = bd["dry_gas_sensible_W"]
    out["design_consistency"] = dict(
        design_flow_100pct_Nm3h=round(design_flow_100), design_air_T_that_gives_55C_clean=round(Ta_design, 1),
        clean_T_out_at_35C_air=round(dsg["T_out_C"], 1), clean_Q_at_35C_kW=round(dsg["Q_total_kW"]),
        design_wet_duty_kW=round(Q_wet / 1000), design_dry_gas_only_duty_kW=round(Q_dry / 1000),
        PFD_58pct_load_clean_T_out_at_35C=round(pfd["T_out_C"], 1),
        fan_rated_point=dict(Q_m3h=342000, dP_total_Pa=190, velocity_pressure_Pa=round(FAN_VELOCITY_PRESSURE, 1),
                             bundle_share_used=round(BUNDLE_SHARE, 3), bundle_dP_used_Pa=round(BUNDLE_SHARE * 190, 1),
                             bundle_dP_Robinson_Briggs_Pa=round(DP_BUNDLE_RB_RATED, 1),
                             fan_power_each_kW_at_eta065=round(dsg["fan_power_kW_each"], 2), motor_kW=11.0),
        geometry=dict(A_ext_model=round(G["A_ext"], 1), A_ext_datasheet=C.DS_AREA_EXT, A_bare_model=round(G["A_bare"], 1),
                      A_bare_datasheet=C.DS_AREA_BARE, fin_gap_mm=round(1000 * G["s_fin"], 2), face_area_m2=round(G["A_face"], 2)),
    )
    # UA reconciliation (13.95 vs 119 kW/K)
    T_air_in = 35.0
    m_air = 342000 / 3600 * 1.146
    def ua_lmtd(Q):
        Tao = T_air_in + Q / (m_air * 1006)
        d1, d2 = 135 - Tao, 55 - T_air_in
        return Q / ((d1 - d2) / math.log(d1 / d2)) / 1000
    out["UA_reconciliation"] = dict(
        note="UA implied by the design duty with 35 C air at rated airflow, counterflow LMTD",
        UA_from_dry_gas_only_duty_kW_K=round(ua_lmtd(Q_dry), 1),
        UA_from_dry_gas_only_duty_PFD_flow_kW_K=round(ua_lmtd(Q_dry * 20588 / design_flow_100), 1),
        dry_gas_only_duty_PFD_flow_kW=round(Q_dry * 20588 / design_flow_100 / 1000), UA_from_wet_duty_kW_K=round(ua_lmtd(Q_wet), 1),
        UA_from_geometry_clean_kW_K=round(dsg["UA_total_kW_K"], 1), UA_air_side_only_kW_K=round(dsg["UA_air_kW_K"], 1),
        previous_python_model_kW_K=13.95, previous_diagnosis_kW_K=119.0)

    # ============================================================ 8. verification
    from verify import run_checks
    out["verification"] = run_checks(gas, REF, cmp_)
    out["runtime_s"] = round(time.time() - t0, 1)
    out["model_settings"] = dict(N_segments=C.N_SEGMENTS, P_process_Pa=C.P_PROCESS, water_to_dry=C.WATER_TO_DRY_BASE,
                                 dry_composition=C.DRY_COMPOSITION, bundle_share=BUNDLE_SHARE)
    json.dump(out, open(os.path.join(RES, "results.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    # ============================================================ 9. figures
    import figures
    figures.make_all(cmp_, sweep, sens, sel, vals, per, REF, b_spring, b_summer)
    print("done in", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
