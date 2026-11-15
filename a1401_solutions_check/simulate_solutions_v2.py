"""
A-1401: simulation of the REVISED solution protocols (revision 2 of the team documents, 15 Nov 2026).

  Solution 1 (new)  O2T8 octyl-silica coating + three Primasonics PAS-120 acoustic horns + traversing vacuum hood
                    (replaces the Aculon AL-B coating + 12 piezoelectric modules of revision 1)
  Solution 2        CTP DECAMEX, new scenario values (net clearance 24.5 / 64.8 / 93.1 % per campaign)

Same wet model, same 2025 season basis and same method as simulate_solutions.py (revision-1 simulation, kept unchanged
in results/ and figures/). This script imports its helper functions and writes to results_v2/ and figures_v2/.
The revision-1 central cases are re-run here so the old and new Solution 1 can be compared side by side.

Run:   python simulate_solutions_v2.py      (about 30 s)

Inputs taken from A1401_Detailed_Engineering_Protocols 2.md (all assumptions of the document authors, label P):
  S1 c,d,e  low (0.20, 0.40, 0.50)  base (0.50, 0.60, 0.70)  high (0.80, 0.80, 0.90)           section 9.2
  S1 installed UA multiplier g1 = 0.99 (sensitivity 0.97-1.00)                                  section 5.2
  S1 events per year 24 (sensitivity 12 / 52)                                                   S1-10
  S2 c,d,e  low (0.70, 0.50, 0.70)  base (0.90, 0.80, 0.90)  high (1.00, 0.95, 0.98)           section 9.2
  S2 campaigns per year 2 (sensitivity 1 / 4)                                                   S2-08
How they are applied here (choices of this simulation, stated in SIMULATION_REPORT_v2.md):
  * clearance acts on the seasonal debris increment only (base 0.594 not credited), two-pool model;
  * S1 events are spread evenly over the debris season 1 May - 30 Sep (24 events = every 6.6 days);
  * g1 is applied to the air-side coefficient (h_mult = g1), because the coating and horn hardware sit on the
    air side; for the hour-by-hour season it is converted to an equivalent blockage shift at the reference window.
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import simulate_solutions as v1                        # noqa: E402  (revision-1 simulation, helper functions)
from a1401sim.exchanger import rate, scalar            # noqa: E402

OUT = os.path.join(HERE, "results_v2"); os.makedirs(OUT, exist_ok=True)
FIG = os.path.join(HERE, "figures_v2"); os.makedirs(FIG, exist_ok=True)
GAS, REF = v1.GAS, v1.REF

S1_NEW = {"low": (0.20, 0.40, 0.50), "base": (0.50, 0.60, 0.70), "high": (0.80, 0.80, 0.90)}
S2_NEW = {"low": (0.70, 0.50, 0.70), "base": (0.90, 0.80, 0.90), "high": (1.00, 0.95, 0.98)}
G1 = 0.99
S1_EVENTS = {"12 events/yr": 12, "24 events/yr": 24, "52 events/yr": 52}
S1_BASE_EVENTS = "24 events/yr"
SEASON = ("2025-05-01 06:00", "2025-09-30 06:00")
S2_SCHEDULES = v1.S2_SCHEDULES
S2_CENTRAL = v1.S2_CENTRAL_SCHEDULE
B_2026_AFTER_TURNAROUND = 0.574   # measured median 8 Jul - 30 Sep 2026 after the 27 Jun - 7 Jul 2026 cleaning (SIMULATION_REPORT.md §5)
SETPOINTS = (60.0, 65.0, 70.0)    # outlet targets used by the plant in 2026 (diagnosis Part 0)


def rate_at(b, h_mult=None, T_amb=None, flow=None):
    return scalar(rate(REF["T_in"], flow or REF["flow"], REF["T_amb"] if T_amb is None else T_amb, 1.0, b,
                       gas=GAS, h_mult=h_mult))


def max_flow(b, T_set, h_mult=None):
    f = lambda fl: rate(REF["T_in"], fl, REF["T_amb"], 1.0, b, gas=GAS, h_mult=h_mult)["T_out_C"] - T_set
    return brentq(f, 3000.0, 80000.0, xtol=20.0) if f(3000.0) < 0 < f(80000.0) else float("nan")


def equivalent_b_shift(b_ref, h_mult):
    """blockage increase that has the same effect on the reference-window outlet as h_mult on the air side"""
    T_target = rate_at(b_ref, h_mult=h_mult)["T_out_C"]
    return brentq(lambda bb: rate_at(bb)["T_out_C"] - T_target, b_ref, min(0.9, b_ref + 0.1), xtol=1e-5) - b_ref


def event_times(n):
    return list(pd.date_range(*SEASON, periods=n).round("h"))


def main():
    res = {}
    h, g, bgrid = v1.load_history()
    base, inc = v1.no_action_path(h)
    sel = h.loc["2025-04-01":"2025-09-30"]
    idx = [h.index.get_loc(t) for t in sel.index]
    grid_rows = g[idx]
    n_dry = np.array([v1.nm3h_to_mol_s(f) for f in sel.flow])
    H_in = GAS.H_of_T(sel.T_in.values + 273.15)
    jas = sel.index >= "2025-07-01"; hot = sel.T_amb.values >= 30

    db_g1 = equivalent_b_shift(0.62, G1)
    db_g097 = equivalent_b_shift(0.62, 0.97)
    res["g1_equivalent_blockage_shift"] = {"0.99": db_g1, "0.97": db_g097}
    print(f"base {base:.3f}  peak increment {inc.max():.3f}  g1=0.99 -> +{db_g1:.4f} b, g1=0.97 -> +{db_g097:.4f} b")

    rows, traces = [], {}

    def evaluate(name, group, b_series, note, hm=None):
        b_h = b_series.reindex(sel.index, method="nearest").values
        T = v1.t_at_b(grid_rows, bgrid, b_h)
        Q = n_dry * (H_in - GAS.H_of_T(T + 273.15)) / 1000.0
        r = dict(scenario=name, group=group, note=note, mean_b_Jul_Sep=float(np.mean(b_h[jas])),
                 mean_T_out_C=float(np.mean(T)), mean_T_out_air_ge_30C=float(np.mean(T[hot])),
                 hours_gt_60C=int(np.sum(T > 60)), hours_gt_65C=int(np.sum(T > 65)), hours_gt_70C=int(np.sum(T > 70)),
                 hours_evaluated=int(len(T)), mean_duty_kW=float(np.mean(Q)))
        rows.append(r); traces[name] = (b_h, T)
        return r

    evaluate("No in-season action (2025 as measured)", "reference", base + inc, "smoothed measured path")
    evaluate("Existing-type cleaning moved to 1 Jul", "reference",
             base + v1.pool_path(inc, 1, 1, 1, [pd.Timestamp("2025-07-01 06:00")]), "full increment removed once")
    # --- new Solution 1
    for k, (c, d, e) in S1_NEW.items():
        p = v1.pool_path(inc, c, d, e, event_times(S1_EVENTS[S1_BASE_EVENTS]))
        evaluate(f"S1 new {k}: O2T8 + horns, 24 events", "S1 new", base + p + db_g1, f"c={c}, d={d}, e={e}, g1=0.99")
    c, d, e = S1_NEW["base"]
    for lab, n in S1_EVENTS.items():
        if lab != S1_BASE_EVENTS:
            evaluate(f"S1 new base, {lab}", "S1 new sensitivity", base + v1.pool_path(inc, c, d, e, event_times(n)) + db_g1,
                     "event-count sensitivity")
    evaluate("S1 new base, g1 = 0.97", "S1 new sensitivity",
             base + v1.pool_path(inc, c, d, e, event_times(24)) + db_g097, "installed-penalty sensitivity")
    evaluate("S1 new base, g1 = 1.00", "S1 new sensitivity",
             base + v1.pool_path(inc, c, d, e, event_times(24)), "installed-penalty sensitivity")
    evaluate("S1 new fails (no clearance), g1 = 0.99", "S1 new sensitivity", base + inc + db_g1, "failure case")
    # --- old Solution 1 (revision 1: Aculon AL-B + piezo, daily), central, for comparison
    c, d, e = v1.S1["central"]
    days = pd.date_range(v1.S1_SEASON[0] + " 06:00", v1.S1_SEASON[1] + " 06:00", freq="D")
    evaluate("S1 old central: Aculon + piezo, daily", "S1 old",
             v1.with_hardware(base + v1.pool_path(inc, c, d, e, days), v1.S1_HARDWARE), "revision-1 inputs")
    # --- new Solution 2
    for k, (c, d, e) in S2_NEW.items():
        ev = [pd.Timestamp(x + " 06:00") for x in S2_SCHEDULES[S2_CENTRAL]]
        evaluate(f"S2 new {k}: DECAMEX, {S2_CENTRAL}", "S2 new", base + v1.pool_path(inc, c, d, e, ev), f"c={c}, d={d}, e={e}")
    c, d, e = S2_NEW["base"]
    for sch, dates in S2_SCHEDULES.items():
        if sch != S2_CENTRAL:
            evaluate(f"S2 new base, {sch}", "S2 new sensitivity",
                     base + v1.pool_path(inc, c, d, e, [pd.Timestamp(x + " 06:00") for x in dates]), "schedule sensitivity")
    c, d, e = v1.S2["central"]
    evaluate("S2 old central: DECAMEX, revision-1 values", "S2 old",
             base + v1.pool_path(inc, c, d, e, [pd.Timestamp(x + " 06:00") for x in S2_SCHEDULES[S2_CENTRAL]]), "revision-1 inputs")
    evaluate("Limit: no seasonal debris at all", "reference", base + 0 * inc, "upper limit for seasonal-only methods")
    S = pd.DataFrame(rows)
    S["mean_duty_gain_kW_vs_no_action"] = S.mean_duty_kW - S.mean_duty_kW.iloc[0]
    S.round(4).to_csv(os.path.join(OUT, "season_2025_scenarios_v2.csv"), index=False)
    print(S.drop(columns=["note", "group"]).round(2).to_string())

    # ------------------------------------------------ reference-window states
    jb = lambda name: float(S.loc[S.scenario == name, "mean_b_Jul_Sep"].iloc[0])
    b_end = 0.685
    states = [("Clean bundle (model)", 0.0, None),
              ("Measured after the 2026 turnaround cleaning (Jul-Sep 2026)", B_2026_AFTER_TURNAROUND, None),
              ("Spring base 2025", base, None),
              ("No action, end of summer 2025 (fitted)", b_end, None),
              ("Existing-type cleaning moved to 1 Jul", jb("Existing-type cleaning moved to 1 Jul"), None)]
    for k in S1_NEW:   # held state without the g1 shift; g1 applied as h_mult
        states.append((f"S1 new {k} (O2T8 + horns, held Jul-Sep)", jb(f"S1 new {k}: O2T8 + horns, 24 events") - db_g1, G1))
    states.append(("S1 old central (Aculon + piezo, held Jul-Sep)", jb("S1 old central: Aculon + piezo, daily"), None))
    for k in S2_NEW:
        states.append((f"S2 new {k} (DECAMEX x2, held Jul-Sep)", jb(f"S2 new {k}: DECAMEX, {S2_CENTRAL}"), None))
    states.append(("S2 old central (DECAMEX x2, revision-1 values)", jb("S2 old central: DECAMEX, revision-1 values"), None))
    for k, (c, d, e) in S1_NEW.items():
        states.append((f"S1 new {k}, one event on end-of-summer state", base + (b_end - base) * (1 - c * d * e), G1))
    for k, (c, d, e) in S2_NEW.items():
        states.append((f"S2 new {k}, one campaign on end-of-summer state", base + (b_end - base) * (1 - c * d * e), None))
    states.append(("S1 new fails, g1 = 0.99", b_end, G1))
    states += [("Doc example: 30 % initial (assumed)", 0.30, None),
               ("Doc example: S1 new base from 30 %", 0.30 * (1 - 0.5 * 0.6 * 0.7), G1),
               ("Doc example: S2 new base from 30 %", 0.30 * (1 - 0.9 * 0.8 * 0.9), None)]
    A = []
    for lab, b, hm in states:
        r = rate_at(b, h_mult=hm)
        row = dict(state=lab, b=b, air_h_mult=hm or 1.0, air_m3h=r["air_m3h"], UA_kW_K=r["UA_total_kW_K"],
                   duty_kW=r["Q_total_kW"], sensible_kW=r["Q_sensible_kW"], latent_kW=r["Q_latent_kW"], T_out_C=r["T_out_C"],
                   energy_closure_pct=100 * abs(r["Q_total_kW"] - r["Q_air_side_kW"]) / r["Q_total_kW"])
        for ts in SETPOINTS:
            row[f"max_flow_{int(ts)}C_Nm3h"] = max_flow(b, ts, hm)
        A.append(row)
        print(f"{lab:58s} b={b:.3f} T={r['T_out_C']:.1f} Q={r['Q_total_kW']:.0f}")
    A = pd.DataFrame(A)
    f = lambda s: A.loc[A.state.str.startswith(s)].iloc[0]
    Qf, Qb, Qc = f("No action").duty_kW, f("Spring base").duty_kW, f("Clean").duty_kW
    A["duty_gain_vs_no_action_kW"] = A.duty_kW - Qf
    A["duty_gain_pct"] = 100 * (A.duty_kW / Qf - 1)
    A["pct_of_seasonal_deficit_recovered"] = 100 * (A.duty_kW - Qf) / (Qb - Qf)
    A["pct_of_clean_deficit_recovered"] = 100 * (A.duty_kW - Qf) / (Qc - Qf)
    for ts in SETPOINTS:
        A[f"capacity_gain_{int(ts)}C_pct"] = 100 * (A[f"max_flow_{int(ts)}C_Nm3h"] / f("No action")[f"max_flow_{int(ts)}C_Nm3h"] - 1)
    A.round(3).to_csv(os.path.join(OUT, "reference_day_states_v2.csv"), index=False)

    checks = dict(energy_closure_max_pct=float(A.energy_closure_pct.max()),
                  outlet_monotonic_in_b_for_h_mult_1=bool(np.all(np.diff(A[A.air_h_mult == 1].sort_values("b").T_out_C.values) >= -1e-6)),
                  s1_failure_worse_than_no_action=bool(f("S1 new fails").T_out_C > f("No action").T_out_C))
    res.update(checks=checks, season_base_b=base, season_peak_increment=float(inc.max()),
               reference_day=A.round(4).to_dict(orient="records"), season=S.round(4).to_dict(orient="records"))
    with open(os.path.join(OUT, "results_v2.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    print(checks)

    # ------------------------------------------------ figures
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = sel.index
    fig, ax = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
    pick = [("No in-season action (2025 as measured)", "#444444"),
            ("Existing-type cleaning moved to 1 Jul", "#8c6d31"),
            ("S1 old central: Aculon + piezo, daily", "#9ecae1"),
            ("S1 new base: O2T8 + horns, 24 events", "#1f77b4"),
            ("S2 new base: DECAMEX, " + S2_CENTRAL, "#d62728"),
            ("Limit: no seasonal debris at all", "#2ca02c")]
    for k, cl in pick:
        b_h, T_h = traces[k]
        if k.startswith("No in-season"):
            ax[0].plot(t, b_h, "-", lw=2.2, color=cl, label=k, zorder=5, alpha=0.6)
        else:
            ax[0].plot(t, b_h, ".", ms=1.5, color=cl, label=k)
        ax[1].plot(t, pd.Series(T_h, index=t).rolling(24, min_periods=1).mean(), "-", lw=1, color=cl, label=k)
    ax[1].plot(t, pd.Series(sel.T_out.values, index=t).rolling(24, min_periods=1).mean(), ":", lw=1, color="k", label="Measured outlet")
    for ts in SETPOINTS:
        ax[1].axhline(ts, color="grey", lw=0.6, ls="--")
    ax[0].set_ylabel("Equivalent blockage, -"); ax[1].set_ylabel("Syngas outlet, C (24-h mean of model hours)")
    ax[0].legend(fontsize=7, markerscale=6, loc="upper left"); ax[1].legend(fontsize=7, loc="upper left")
    ax[0].set_title("A-1401 season 2025 under the revised solutions (base clearance)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_season_2025_v2.png"), dpi=150); plt.close(fig)

    sub = A[A.state.str.contains("held Jul-Sep|revision-1|No action|Spring base|Clean|Measured after|Existing-type")]
    fig, ax = plt.subplots(figsize=(10.5, 6))
    cols = ["#1f77b4" if "S1 new" in s else "#9ecae1" if "S1 old" in s else "#d62728" if "S2 new" in s
            else "#f4a6a6" if "S2 old" in s else "#888888" for s in sub.state]
    ax.barh(sub.state, sub.T_out_C, color=cols)
    for y, (v, q) in enumerate(zip(sub.T_out_C, sub.duty_kW)):
        ax.text(v + 0.5, y, f"{v:.1f} C | {q:,.0f} kW", va="center", fontsize=8)
    for ts in SETPOINTS:
        ax.axvline(ts, color="k", lw=0.6, ls="--")
    ax.set_xlim(0, 100); ax.invert_yaxis()
    ax.set_xlabel("Syngas outlet at the reference window, C")
    ax.set_title("Reference window 18 Jul 2025 (159.4 C, 17,444 Nm3/h, air 31.8 C, fans 100 %)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_reference_day_v2.png"), dpi=150); plt.close(fig)
    print("done")


if __name__ == "__main__":
    main()
