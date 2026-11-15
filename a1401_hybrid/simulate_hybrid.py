"""
A-1401 hybrid cleaning strategies: combinations of sonic horns (S1), DECAMEX (S2) and a full turnaround clean.

Same wet model, same 2025 season basis and same two-pool debris model as ../a1401_solutions_check
(simulate_solutions.py and simulate_solutions_v2.py). Nothing in the rating model is changed.

Events
  horns    : S1 revision 2 base c,d,e = 0.50, 0.60, 0.70; 24 events 1 May-30 Sep; installed penalty g1 = 0.99
  decamex  : S2 revision 2 base c,d,e = 0.90, 0.80, 0.90; campaign dates per strategy
  full     : turnaround clean (existing type), 27 Jun. Removes all seasonal debris; base falls to the measured
             2026 post-turnaround level 0.574 (i.e. 0.020 of the base is removed, as measured in 2026)
  deep     : full clean + DECAMEX through all six rows at the same turnaround. HYPOTHESIS: a share k of the
             base (0.594) is old compacted debris that a deep clean can reach. k = 0.25 / 0.50 / 0.75 / 1.0 are
             what-if cases, not measurements; an inspection at the turnaround decides which is true.
Production: in hours where the no-action model outlet is above 65 C (cooler limits gas), extra dry gas =
  flow x (Fmax65(b_new)/Fmax65(b_no_action) - 1), Fmax65 from the reference-window rating; H2 = gas x 0.744 x
  0.796 x 0.0899 kg/Nm3 (same factors as the production-gap estimate). New flow is capped at the median flow the
  plant runs with air 0-10 C (cooler not limiting). Upper estimate: assumes the extra hydrogen can be sold.
Run: python simulate_hybrid.py   (about 1 min)
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.normpath(os.path.join(HERE, "..", "a1401_solutions_check"))
sys.path.insert(0, SC)
import simulate_solutions as v1                                     # noqa: E402
import simulate_solutions_v2 as v2                                  # noqa: E402
from a1401sim.thermo import nm3h_to_mol_s                           # noqa: E402

OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)
GAS = v1.GAS
H2_KG_PER_NM3_GAS = 0.744 * 0.796 * 0.0899
S1c, S2c = v2.S1_NEW["base"], v2.S2_NEW["base"]
TURN = pd.Timestamp("2025-06-27 06:00")
HORNS = v2.event_times(24)
DEC2 = [pd.Timestamp("2025-06-01 06:00"), pd.Timestamp("2025-07-01 06:00")]
DEC_AUG = [pd.Timestamp("2025-08-01 06:00")]
B_TURN = 0.574


def path(inc, base, horns=False, dec=(), full=None, base_after=None, db_horn=0.0):
    """Three-pool debris model. Each new deposit splits into pool A (reached by horns AND DECAMEX, share 0.50),
    pool B (reached by DECAMEX only, 0.90-0.50 = 0.40) and pool C (reached by neither, 0.10). Horns are assumed to
    reach a subset of what DECAMEX reaches (both act from the air side; DECAMEX lances reach deeper rows).
    Horn event: A *= 1 - d1 e1.  DECAMEX campaign: A, B *= 1 - d2 e2.  Full clean: A = B = C = 0, base -> base_after.
    Reduces exactly to the two-pool model of simulate_solutions.py when only one method is used."""
    cA, cB = S1c[0], S2c[0] - S1c[0]
    kH, kD = S1c[1] * S1c[2], S2c[1] * S2c[2]
    dM = np.diff(np.concatenate([[0.0], inc.values]))
    hs, ds = set(HORNS) if horns else set(), set(dec)
    A = B = C = 0.0; bb = base
    out = np.empty(len(dM))
    for i, (t, dm) in enumerate(zip(inc.index, dM)):
        A += cA * dm; B += cB * dm; C += (1 - cA - cB) * dm
        if full is not None and t == full:
            A = B = C = 0.0; bb = base_after
        if t in hs:
            A *= 1 - kH
        if t in ds:
            A *= 1 - kD; B *= 1 - kD
        out[i] = bb + A + B + C + (db_horn if horns else 0.0)
    return pd.Series(out, index=inc.index)


def main():
    h, g, bgrid = v1.load_history()
    base, inc = v1.no_action_path(h)
    sel = h.loc["2025-04-01":"2025-09-30"]
    idx = [h.index.get_loc(t) for t in sel.index]
    G = g[idx]
    n_dry = np.array([nm3h_to_mol_s(f) for f in sel.flow])
    H_in = GAS.H_of_T(sel.T_in.values + 273.15)
    flow = sel.flow.values
    # plant cannot run more gas than it runs in cool weather: cap = median dry-gas flow with air 0-10 C (slide data)
    FLOW_CAP = 25052.0   # median dry-gas flow with air 0-10 C, Nov 2023-Oct 2026 (a1401_monitor/out, deck slide 5)
    print(f"flow cap (median flow, air 0-10 C): {FLOW_CAP:.0f} Nm3/h")
    db_h = v2.equivalent_b_shift(0.62, v2.G1)
    print(f"base {base:.3f}, peak inc {inc.max():.3f}, bgrid {bgrid.min():.2f}-{bgrid.max():.2f}, horn shift {db_h:.4f}")
    # capacity curve at the reference window
    bc = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75])
    Fc = np.array([v2.max_flow(b, 65.0) for b in bc])
    F = lambda b: np.interp(b, bc, Fc)
    S = {}
    S["No in-season action (2025)"] = dict(g="ref", b=base + inc)
    S["Horns only (24 events)"] = dict(g="single", b=path(inc, base, horns=True, db_horn=db_h))
    S["DECAMEX only (2 campaigns)"] = dict(g="single", b=path(inc, base, dec=DEC2))
    S["Full turnaround clean only (27 Jun)"] = dict(g="single", b=path(inc, base, full=TURN, base_after=B_TURN))
    S["Horns + DECAMEX x2"] = dict(g="hybrid", b=path(inc, base, horns=True, dec=DEC2, db_horn=db_h))
    S["Full clean + horns"] = dict(g="hybrid", b=path(inc, base, horns=True, full=TURN, base_after=B_TURN, db_horn=db_h))
    S["DECAMEX 1 Jun + full clean + DECAMEX 1 Aug"] = dict(g="hybrid", b=path(inc, base, dec=[DEC2[0]] + DEC_AUG, full=TURN, base_after=B_TURN))
    S["Full clean + horns + DECAMEX 1 Jun, 1 Aug"] = dict(g="hybrid", b=path(inc, base, horns=True, dec=[DEC2[0]] + DEC_AUG, full=TURN, base_after=B_TURN, db_horn=db_h))
    for k in (0.05, 0.10, 0.25, 0.50, 0.75, 1.0):
        S[f"Deep clean (base -{int(k*100)} %) + DECAMEX 1 Jun, 1 Aug"] = dict(
            g="deep", b=path(inc, base, dec=[DEC2[0]] + DEC_AUG, full=TURN, base_after=base * (1 - k)))
    for k in (0.05, 0.075, 0.10, 0.25):
        S[f"Deep clean (base -{k*100:g} %) only"] = dict(g="deep", b=path(inc, base, full=TURN, base_after=base * (1 - k)))
        S[f"Deep clean (base -{k*100:g} %) + horns"] = dict(g="deep", b=path(inc, base, horns=True, full=TURN, base_after=base * (1 - k), db_horn=db_h))
    S["Limit: clean bundle all season"] = dict(g="ref", b=pd.Series(0.0, index=inc.index))
    rows = []
    jas = sel.index >= "2025-07-01"; hot = sel.T_amb.values >= 30
    b_na = None
    for name, d in S.items():
        b_h = d["b"].reindex(sel.index, method="nearest").values
        T = v1.t_at_b(G, bgrid, b_h)
        Q = n_dry * (H_in - GAS.H_of_T(T + 273.15)) / 1000.0
        if b_na is None:
            b_na, T_na = b_h, T
        lim = T_na > 65.0
        new = np.minimum(flow * F(b_h) / F(b_na), np.maximum(flow, FLOW_CAP))
        gain = np.where(lim, new - flow, 0.0)
        b_jas = float(np.mean(b_h[jas]))
        r_ref = v2.rate_at(b_jas, h_mult=v2.G1 if "orns" in name else None)
        rows.append(dict(strategy=name, group=d["g"], mean_b_Jul_Sep=b_jas, ref_T_out_C=r_ref["T_out_C"],
                         ref_duty_kW=r_ref["Q_total_kW"], ref_Fmax65_Nm3h=float(F(b_jas)),
                         season_mean_T_out_C=float(np.mean(T)), hot_mean_T_out_C=float(np.mean(T[hot])),
                         hours_gt_65C=int(np.sum(T > 65)), season_mean_duty_kW=float(np.mean(Q)),
                         extra_gas_Mm3=float(np.nansum(gain) / 1e6), extra_H2_t=float(np.nansum(gain) * H2_KG_PER_NM3_GAS / 1000)))
        print(f"{name:52s} bJAS={b_jas:.3f} Tref={r_ref['T_out_C']:5.1f} h>65={rows[-1]['hours_gt_65C']:5d} H2={rows[-1]['extra_H2_t']:6.0f} t")
    R = pd.DataFrame(rows)
    Q0, Qc = R.ref_duty_kW.iloc[0], R.ref_duty_kW.iloc[-1]
    R["ref_duty_gain_kW"] = R.ref_duty_kW - Q0
    R["pct_of_clean_bundle_gap_closed"] = 100 * (R.ref_duty_kW - Q0) / (Qc - Q0)
    R["ref_capacity_gain_pct"] = 100 * (R.ref_Fmax65_Nm3h / R.ref_Fmax65_Nm3h.iloc[0] - 1)
    R.round(3).to_csv(os.path.join(OUT, "hybrid_scenarios.csv"), index=False)
    pd.DataFrame(dict(b=bc, Fmax65_Nm3h=Fc)).to_csv(os.path.join(OUT, "capacity_curve_65C.csv"), index=False)
    json.dump(dict(base=base, horn_shift=db_h, H2_kg_per_Nm3=H2_KG_PER_NM3_GAS,
                   traces={k: list(np.round(v["b"].resample("D").mean().values, 4)) for k, v in S.items()},
                   days=[str(x.date()) for x in S["Horns only (24 events)"]["b"].resample("D").mean().index]),
              open(os.path.join(OUT, "hybrid_traces.json"), "w"))
    print(R[["strategy", "ref_T_out_C", "ref_duty_gain_kW", "pct_of_clean_bundle_gap_closed", "ref_capacity_gain_pct", "hours_gt_65C", "extra_H2_t"]].round(1).to_string())


if __name__ == "__main__":
    main()
