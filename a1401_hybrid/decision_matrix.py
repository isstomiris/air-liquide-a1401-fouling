"""Weighted decision matrix for the final recommendation.
Cooling and economics scores are computed from the simulation (linear 1-5 scale); safety, certainty and
feasibility are team judgement (1-5) with the reason written next to each. Deep-clean options use the
the two proposed solutions are scored. Cooling: 1 = no action (2,651 h > 65 C), 5 = no seasonal debris (1,032 h)."""
import os, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
E = pd.read_csv(os.path.join(HERE, "results", "economics.csv")); E = E[E.case == "central"].set_index("plan")
W = dict(cooling=0.30, economics=0.25, safety=0.15, certainty=0.15, feasibility=0.15)
O = [  # label, economics plan, safety, certainty, feasibility, reasons
    ("Sonic horns + vacuum hood", "Horns", 3, 2, 3, "148 dB and 24 h/yr fan stops; untested on poplar fluff; 8-12 wk order"),
    ("DECAMEX dry cleaning", "DECAMEX x2", 4, 3, 4, "dry powder, 1 fan off 4.8 h per campaign; used in industry, not on fluff; 4-8 wk"),
]
h0, hmin = 2651, 1032   # no action; limit with no seasonal debris at all (solutions_check v2)
nmax = 600.0  # scale: 600 k USD/yr = 5
rows = []
for lab, p, sa, ce, fe, why in O:
    co = 1 + 4 * (h0 - E.loc[p, "hours_gt_65C"]) / (h0 - hmin)
    ec = 1 + 4 * E.loc[p, "net_vs_no_action_kUSD_yr"] / nmax
    tot = W["cooling"] * co + W["economics"] * ec + W["safety"] * sa + W["certainty"] * ce + W["feasibility"] * fe
    tot2 = tot + W["certainty"] * 1   # after a successful pilot on real fluff, certainty +1
    rows.append(dict(option=lab, cooling=round(co, 1), economics=round(ec, 1), safety=sa, certainty=ce, feasibility=fe,
                     score_today=round(tot, 2), score_after_pilot=round(tot2, 2), reasons=why))
D = pd.DataFrame(rows); D.to_csv(os.path.join(HERE, "results", "decision_matrix.csv"), index=False)
print(D.drop(columns="reasons").to_string(index=False))
