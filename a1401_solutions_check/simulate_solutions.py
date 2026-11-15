"""
A-1401: simulation of the two proposed air-side cleaning solutions on the wet (condensing) rating model.

  Solution 1  Aculon AL-B low-adhesion coating + 12 piezoelectric vibration modules (daily cycles)
  Solution 2  CTP DECAMEX dry chemical cleaning (periodic online campaigns, one fan stopped at a time)

Model used: a1401sim from ../a1401_clean_vs_fouled (segmented 6-row x 24-segment crossflow rating, wet syngas
with condensation, generic fan curve + Robinson-Briggs bundle resistance). Nothing in that model is changed here.

Run:   python simulate_solutions.py          (about 1-3 minutes; needs the same packages as a1401_clean_vs_fouled)

What is simulated
  A. Steady state at the summer reference window (18 Jul 2025 17-20 UTC; 159.4 C, 17,444 Nm3/h dry, air 31.8 C,
     fans 100 %) for each post-treatment equivalent blockage: airflow, UA, duty (sensible / latent), outlet,
     maximum dry-gas flow for a 65 C outlet.
  B. Season 2025 (1 Apr - 30 Sep), hour by hour, on the real historian hours with fans at 100 % and air >= 10 C.
     The "no action" path is the measured equivalent blockage (smoothed). Each solution modifies that path with
     a two-pool debris model (reachable / unreachable) and its cleaning schedule. The model outlet for each hour
     comes from the per-hour blockage grid already computed by a1401_clean_vs_fouled (results/_history_grid_cache.npz).
  C. Temporary state with one of three fans stopped (DECAMEX planning basis; vibration sector windows).
  D. The documents' original 30 % example re-run on the wet model, for reference only.

Clearance parameters c, d, e are the scenario values from A1401_Detailed_Engineering_Protocols.md (assumptions,
not measurements). They are applied only to the seasonal debris increment (see README), because the history
shows that the base of about 0.60 equivalent blockage is not removed by the existing cleaning.
"""
import json, os, sys, math
import numpy as np
import pandas as pd
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.normpath(os.path.join(HERE, "..", "a1401_clean_vs_fouled"))
sys.path.insert(0, MODEL_DIR)
from a1401sim.exchanger import rate, scalar          # noqa: E402
from a1401sim.thermo import WetSyngas, nm3h_to_mol_s  # noqa: E402
from a1401sim.airside import airflow                  # noqa: E402

OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)
FIG = os.path.join(HERE, "figures"); os.makedirs(FIG, exist_ok=True)
GAS = WetSyngas()

# ---------------------------------------------------------------- reference window (same as a1401_clean_vs_fouled)
REF = dict(T_in=159.4, flow=17444.0, T_amb=31.8)   # REPORT.md section 3, 18 Jul 2025 17:00-20:00 UTC
T_SET = 65.0

# ---------------------------------------------------------------- clearance scenarios (from the protocols file, all P)
# c = fraction of the debris the method reaches, d = fraction of reached debris detached per event,
# e = fraction of detached debris that leaves without re-blocking elsewhere.
S1 = {"conservative": (0.40, 0.25, 0.50), "central": (0.65, 0.50, 0.80), "optimistic": (0.80, 0.70, 0.90)}
S2 = {"conservative": (0.70, 0.60, 0.75), "central": (0.90, 0.85, 0.90), "optimistic": (1.00, 0.95, 0.98)}
S1_HARDWARE = 0.002          # permanent obstruction of open face by combs/brackets (protocols file, P)
S1_SEASON = ("2025-05-01", "2025-09-30")   # daily vibration sequence (protocols: daily over the fouling season)
S2_SCHEDULES = {             # DECAMEX campaign dates (P). Deposition in 2025 ran from late April to late June.
    "1 campaign (1 Jul)": ["2025-07-01"],
    "2 campaigns (1 Jun, 1 Jul)": ["2025-06-01", "2025-07-01"],
    "4 campaigns (15 May, 1 Jun, 15 Jun, 1 Jul)": ["2025-05-15", "2025-06-01", "2025-06-15", "2025-07-01"],
}
S2_CENTRAL_SCHEDULE = "2 campaigns (1 Jun, 1 Jul)"
EXISTING_DATE = "2025-07-01"  # existing-type cleaning moved to 1 Jul (as done at the 2026 turnaround)


def rate_ref(b, **kw):
    return scalar(rate(REF["T_in"], REF["flow"], REF["T_amb"], 1.0, b, gas=GAS, **kw))


def max_flow_65(b, Q_air_override=None):
    f = lambda fl: rate(REF["T_in"], fl, REF["T_amb"], 1.0, b, gas=GAS, Q_air_override=Q_air_override)["T_out_C"] - T_SET
    lo, hi = 3000.0, 80000.0
    return brentq(f, lo, hi, xtol=20.0) if f(lo) < 0 < f(hi) else float("nan")


def with_hardware(b, bh):
    return b + (1 - b) * bh


# ================================================================ B. season simulation
def load_history():
    h = pd.read_csv(os.path.join(MODEL_DIR, "results", "history_equivalent_blockage_hourly.csv"), parse_dates=["timestamp"])
    z = np.load(os.path.join(MODEL_DIR, "results", "_history_grid_cache.npz"))
    g, bgrid = z["g"], z["b"]
    assert len(g) == len(h), "grid cache and hourly file must have the same hours"
    h = h.set_index("timestamp")
    return h, g, bgrid


def t_at_b(grid_rows, bgrid, b):
    """model outlet for each hour at that hour's blockage (linear interpolation in the per-hour grid)"""
    b = np.asarray(b)
    out = np.empty(len(grid_rows))
    for i, (row, bb) in enumerate(zip(grid_rows, b)):
        out[i] = np.interp(bb, bgrid, row)
    return out


def no_action_path(h):
    """Smoothed measured path, 2025. Base = median 15 Mar - 20 Apr 2025. Increment made monotone (cumulative max of
    a 7-day rolling median) so that it can be read as deposited debris; decreases are treated as noise."""
    x = h.loc["2025-03-01":"2025-09-30", "b_eq"].dropna()
    base = float(x["2025-03-15":"2025-04-20"].median())
    hourly = pd.date_range("2025-04-01", "2025-09-30 23:00", freq="h")
    roll = x.rolling("7D", min_periods=24).median().reindex(hourly, method="nearest", tolerance=pd.Timedelta("10D"))
    roll = roll.interpolate().bfill().ffill()
    inc = np.maximum(0.0, np.maximum.accumulate(roll.values - base))
    return base, pd.Series(inc, index=hourly)


def pool_path(inc, c, d, e, event_times, s=1.0):
    """Two-pool deposit model. New deposit dM splits into reachable (c) and unreachable (1-c) pools.
    Each cleaning event removes the fraction d*e of the reachable pool. s = deposition multiplier (coating)."""
    dM = np.diff(np.concatenate([[0.0], inc.values])) * s
    ev = set(pd.DatetimeIndex(event_times))
    R = U = 0.0
    out = np.empty(len(dM))
    for i, (t, dm) in enumerate(zip(inc.index, dM)):
        R += c * dm; U += (1 - c) * dm
        if t in ev:
            R *= (1 - d * e)
        out[i] = R + U
    return pd.Series(out, index=inc.index)


def season(h, g, bgrid):
    base, inc = no_action_path(h)
    sel = h.loc["2025-04-01":"2025-09-30"]
    idx = [h.index.get_loc(t) for t in sel.index]
    grid_rows = g[idx]
    n_dry = np.array([nm3h_to_mol_s(f) for f in sel.flow])
    H_in = GAS.H_of_T(sel.T_in.values + 273.15)

    def evaluate(name, b_series, note):
        b_h = b_series.reindex(sel.index, method="nearest").values
        T = t_at_b(grid_rows, bgrid, b_h)
        Q = n_dry * (H_in - GAS.H_of_T(T + 273.15)) / 1000.0
        hot = sel.T_amb.values >= 30
        jas = (sel.index >= "2025-07-01")
        return dict(scenario=name, note=note,
                    mean_b_Jul_Sep=float(np.mean(b_h[jas])), max_b=float(np.max(b_h)),
                    mean_T_out_C=float(np.mean(T)), mean_T_out_air_ge_30C=float(np.mean(T[hot])),
                    hours_T_out_gt_65C=int(np.sum(T > 65)), hours_evaluated=int(len(T)),
                    mean_duty_kW=float(np.mean(Q))), T, b_h

    rows, traces = [], {}
    # measured outlet and the model at the smoothed no-action path (consistency check)
    T_meas = sel.T_out.values
    r0, T0, b0 = evaluate("0  No in-season action (2025 as measured)", base + inc, "smoothed measured path")
    r0["MAE_vs_measured_K"] = float(np.mean(np.abs(T0 - T_meas)))
    r0["bias_vs_measured_K"] = float(np.mean(T0 - T_meas))
    rows.append(r0); traces["No in-season action"] = (b0, T0)

    ex = pool_path(inc, 1.0, 1.0, 1.0, pd.date_range(EXISTING_DATE, periods=1))
    r, T, b = evaluate("E  Existing-type cleaning moved to 1 Jul", base + ex,
                       "removes the whole seasonal increment once (Oct 2025 cleaning removed at least that)")
    rows.append(r); traces["Existing-type cleaning, 1 Jul"] = (b, T)

    days = pd.date_range(S1_SEASON[0] + " 06:00", S1_SEASON[1] + " 06:00", freq="D")
    for k, (c, d, e) in S1.items():
        p = pool_path(inc, c, d, e, days)
        bs = with_hardware(base + p, S1_HARDWARE)
        r, T, b = evaluate(f"S1 {k}: coating + vibration, daily", bs, f"c={c}, d={d}, e={e}, hardware {S1_HARDWARE}")
        rows.append(r); traces[f"S1 {k}"] = (b, T)
    for s in (0.8, 0.6):
        c, d, e = S1["central"]
        p = pool_path(inc, c, d, e, days, s=s)
        r, T, b = evaluate(f"S1 central, coating deposition multiplier s={s}", with_hardware(base + p, S1_HARDWARE),
                           "sensitivity only; no evidence for any s < 1")
        rows.append(r)
    for k, (c, d, e) in S2.items():
        ev = [pd.Timestamp(x + " 06:00") for x in S2_SCHEDULES[S2_CENTRAL_SCHEDULE]]
        p = pool_path(inc, c, d, e, ev)
        r, T, b = evaluate(f"S2 {k}: DECAMEX, {S2_CENTRAL_SCHEDULE}", base + p, f"c={c}, d={d}, e={e}")
        rows.append(r); traces[f"S2 {k}"] = (b, T)
    for sch, dates in S2_SCHEDULES.items():
        if sch == S2_CENTRAL_SCHEDULE:
            continue
        c, d, e = S2["central"]
        p = pool_path(inc, c, d, e, [pd.Timestamp(x + " 06:00") for x in dates])
        r, T, b = evaluate(f"S2 central, {sch}", base + p, "schedule sensitivity")
        rows.append(r)
    rz, Tz, bz = evaluate("Z  Seasonal increment fully absent all season (limit)", base + 0 * inc,
                          "upper limit of any method that acts only on the seasonal debris")
    rows.append(rz); traces["Increment absent (limit)"] = (bz, Tz)
    df = pd.DataFrame(rows)
    q0 = df.loc[0, "mean_duty_kW"]
    df["mean_duty_gain_kW_vs_no_action"] = df.mean_duty_kW - q0
    return base, inc, sel, T_meas, df, traces


# ================================================================ main
def main():
    res = {}
    h, g, bgrid = load_history()
    base, inc, sel, T_meas, sdf, traces = season(h, g, bgrid)
    res["season_base_b"] = base
    res["season_peak_increment"] = float(inc.max())
    sdf.round(4).to_csv(os.path.join(OUT, "season_2025_scenarios.csv"), index=False)
    print(f"base b = {base:.3f}, peak seasonal increment = {inc.max():.3f}")
    print(sdf.drop(columns=["note"]).round(3).to_string())

    # measured anchor: existing cleaning, autumn 2025
    x = h["b_eq"]
    before = float(x["2025-08-01":"2025-09-30"].median()); after = float(x["2025-11-01":"2025-11-30"].median())
    res["anchor_existing_cleaning"] = dict(b_before_Aug_Sep_2025=before, b_after_Nov_2025=after,
                                           hours_after=int(x["2025-11-01":"2025-11-30"].count()),
                                           last_reading_b_ge_0p65=str(x["2025-09-01":"2025-11-30"][x >= 0.65].index.max()),
                                           first_reading_b_le_0p60=str(x["2025-09-01":"2025-11-30"][x <= 0.60].index.min()))
    print(res["anchor_existing_cleaning"])

    # ------------------------------------------------ A. reference-day steady states
    b_end = 0.685  # end of summer 2025, fitted (a1401_clean_vs_fouled REPORT 6.5)
    jas = lambda name: float(sdf.loc[sdf.scenario.str.startswith(name), "mean_b_Jul_Sep"].iloc[0])
    states = [("Clean bundle (model)", 0.0),
              ("Best measured after a cleaning (Nov 2025)", after),
              ("Spring base 2025 (no seasonal debris)", base),
              ("No action, end of summer 2025 (fitted)", b_end),
              ("Existing-type cleaning, 1 Jul (season mean Jul-Sep)", jas("E ")),
              ("S1 conservative (season mean Jul-Sep)", jas("S1 conservative")),
              ("S1 central (season mean Jul-Sep)", jas("S1 central:")),
              ("S1 optimistic (season mean Jul-Sep)", jas("S1 optimistic")),
              ("S2 conservative (season mean Jul-Sep)", jas("S2 conservative")),
              ("S2 central (season mean Jul-Sep)", jas("S2 central:")),
              ("S2 optimistic (season mean Jul-Sep)", jas("S2 optimistic"))]
    # single event applied to the end-of-summer state (eta on the seasonal increment only)
    for k, (c, d, e) in S1.items():
        states.append((f"S1 {k}, one event on end-of-summer state", with_hardware(base + (b_end - base) * (1 - c * d * e), S1_HARDWARE)))
    for k, (c, d, e) in S2.items():
        states.append((f"S2 {k}, one campaign on end-of-summer state", base + (b_end - base) * (1 - c * d * e)))
    # the documents' 30 % example on the wet model (illustration only)
    states += [("Doc example: 30 % initial (assumed)", 0.30),
               ("Doc example: S1 central from 30 %", with_hardware(0.30 * (1 - 0.65 * 0.5 * 0.8), S1_HARDWARE)),
               ("Doc example: S2 central from 30 %", 0.30 * (1 - 0.9 * 0.85 * 0.9))]
    rows = []
    for lab, b in states:
        r = rate_ref(b)
        rows.append(dict(state=lab, b=b, air_m3h=r["air_m3h"], UA_kW_K=r["UA_total_kW_K"], duty_kW=r["Q_total_kW"],
                         sensible_kW=r["Q_sensible_kW"], latent_kW=r["Q_latent_kW"], T_out_C=r["T_out_C"],
                         condensed_kg_h=r["condensed_kg_h"], max_flow_65C_Nm3h=max_flow_65(b),
                         energy_closure_pct=100 * abs(r["Q_total_kW"] - r["Q_air_side_kW"]) / r["Q_total_kW"]))
        print(f"{lab:55s} b={b:.3f} T={r['T_out_C']:.1f} Q={r['Q_total_kW']:.0f}")
    A = pd.DataFrame(rows)
    Qf = float(A.loc[A.state.str.startswith("No action"), "duty_kW"].iloc[0])
    Qb = float(A.loc[A.state.str.startswith("Spring base"), "duty_kW"].iloc[0])
    Qc = float(A.loc[A.state.str.startswith("Clean"), "duty_kW"].iloc[0])
    Ff = float(A.loc[A.state.str.startswith("No action"), "max_flow_65C_Nm3h"].iloc[0])
    A["duty_gain_vs_no_action_kW"] = A.duty_kW - Qf
    A["pct_of_seasonal_deficit_recovered"] = 100 * (A.duty_kW - Qf) / (Qb - Qf)
    A["pct_of_clean_deficit_recovered"] = 100 * (A.duty_kW - Qf) / (Qc - Qf)
    A["capacity_gain_vs_no_action_pct"] = 100 * (A.max_flow_65C_Nm3h / Ff - 1)
    A.round(3).to_csv(os.path.join(OUT, "reference_day_states.csv"), index=False)

    # ------------------------------------------------ C. one fan stopped (2 of 3 running)
    # Each running fan sees the same per-fan system curve as before (sectors treated as independent), so total air
    # = 2/3 of the three-fan value, and one third of the face carries no air: b' = 1 - (2/3)(1 - b).
    # Natural draft and leakage through the idle sector are neglected (conservative).
    fan_rows = []
    for T_amb in (20.0, REF["T_amb"]):
        for lab, b in (("end of summer", b_end), ("spring base", base)):
            Q3 = airflow(1.0, b)[0]
            bp = 1 - (2 / 3) * (1 - b)
            r3 = rate(REF["T_in"], REF["flow"], T_amb, 1.0, b, gas=GAS)
            r2 = rate(REF["T_in"], REF["flow"], T_amb, 1.0, bp, gas=GAS, Q_air_override=(2 / 3) * Q3)
            f3 = brentq(lambda fl: rate(REF["T_in"], fl, T_amb, 1.0, b, gas=GAS)["T_out_C"] - T_SET, 3000, 80000, xtol=20)
            f2 = brentq(lambda fl: rate(REF["T_in"], fl, T_amb, 1.0, bp, gas=GAS, Q_air_override=(2 / 3) * Q3)["T_out_C"] - T_SET,
                        1000, 80000, xtol=20)
            fan_rows.append(dict(air_C=T_amb, state=lab, b=b, T_out_3fans=r3["T_out_C"], T_out_2fans=r2["T_out_C"],
                                 duty_3fans_kW=r3["Q_total_kW"], duty_2fans_kW=r2["Q_total_kW"],
                                 max_flow_65C_3fans=f3, max_flow_65C_2fans=f2))
    F = pd.DataFrame(fan_rows); F.round(2).to_csv(os.path.join(OUT, "one_fan_stopped.csv"), index=False)
    print(F.round(1).to_string())

    # ------------------------------------------------ checks
    checks = dict(
        energy_closure_max_pct=float(A.energy_closure_pct.max()),
        season_no_action_MAE_K=float(sdf.loc[0, "MAE_vs_measured_K"]),
        season_no_action_bias_K=float(sdf.loc[0, "bias_vs_measured_K"]),
        outlet_monotonic_in_b=bool(np.all(np.diff(A.sort_values("b").T_out_C.values) >= -1e-6)),
        every_scenario_b_le_no_action=bool((sdf.mean_b_Jul_Sep.iloc[1:] <= sdf.mean_b_Jul_Sep.iloc[0] + S1_HARDWARE + 1e-9).all()),
    )
    res["checks"] = checks
    print(checks)
    res["reference_day"] = A.round(4).to_dict(orient="records")
    res["season"] = sdf.round(4).to_dict(orient="records")
    res["one_fan_stopped"] = F.round(3).to_dict(orient="records")
    with open(os.path.join(OUT, "results.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    # ------------------------------------------------ figures
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = sel.index
    fig, ax = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
    pick = ["No in-season action", "Existing-type cleaning, 1 Jul", "S1 central", "S2 central", "Increment absent (limit)"]
    cols = ["#444444", "#8c6d31", "#1f77b4", "#d62728", "#2ca02c"]
    for k, cl in zip(pick, cols):
        b_h, T_h = traces[k]
        if k == "No in-season action":
            ax[0].plot(t, b_h, "-", lw=2.2, color=cl, label=k, zorder=5, alpha=0.6)
        else:
            ax[0].plot(t, b_h, ".", ms=1.5, color=cl, label=k)
        ax[1].plot(t, pd.Series(T_h, index=t).rolling(24, min_periods=1).mean(), "-", lw=1, color=cl, label=k)
    ax[1].plot(t, pd.Series(T_meas, index=t).rolling(24, min_periods=1).mean(), ":", lw=1, color="k", label="Measured outlet")
    ax[1].axhline(65, color="grey", lw=0.8, ls="--")
    ax[0].set_ylabel("Equivalent blockage, -"); ax[1].set_ylabel("Syngas outlet, C (24-h mean of model hours)")
    ax[0].legend(fontsize=8, markerscale=6, loc="upper left"); ax[1].legend(fontsize=8, loc="upper left")
    ax[0].set_title("A-1401 season 2025: equivalent blockage and outlet under each solution (central clearance)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_season_2025.png"), dpi=150); plt.close(fig)

    sub = A[A.state.str.contains("season mean|No action|Spring base|Clean|Best measured")].copy()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(sub.state, sub.T_out_C, color="#888888")
    for y, (v, q) in enumerate(zip(sub.T_out_C, sub.duty_kW)):
        ax.text(v + 0.5, y, f"{v:.1f} C | {q:,.0f} kW", va="center", fontsize=8)
    ax.axvline(65, color="k", lw=0.8, ls="--")
    ax.set_xlabel("Syngas outlet at the reference window, C"); ax.invert_yaxis(); ax.set_xlim(0, 100)
    ax.set_title("Reference window 18 Jul 2025 (159.4 C, 17,444 Nm3/h, air 31.8 C, fans 100 %)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_reference_day.png"), dpi=150); plt.close(fig)
    print("done")


if __name__ == "__main__":
    main()
