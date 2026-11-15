"""Weighted decision matrix for the final recommendation.
Cooling and economics scores are computed from the simulation (linear 1-5 scale); safety, certainty and
feasibility are team judgement (1-5) with the reason written next to each. Deep-clean options use the
conservative -10 % base case. 'After inspection' = the turnaround inspection confirms the base comes off."""
import os, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
E = pd.read_csv(os.path.join(HERE, "results", "economics.csv")); E = E[E.case == "central"].set_index("plan")
W = dict(cooling=0.30, economics=0.25, safety=0.15, certainty=0.15, feasibility=0.15)
O = [  # label, economics plan, safety, certainty, feasibility, reasons
    ("Sonic horns", "Horns", 3, 2, 3, "148 dB, fan stops; untested on poplar fluff; 8-12 wk order"),
    ("DECAMEX x2 online", "DECAMEX x2", 4, 3, 4, "dry powder, 1 fan off 4.8 h; used in industry, not on fluff; 4-8 wk"),
    ("Turnaround clean (plant 2026)", "Turnaround clean (current practice)", 4, 5, 3, "done at a stop; proven 57 °C in 2026; needs a June stop"),
    ("Turnaround + horns", "Turnaround + horns", 3, 4, 3, "as above plus horn risks"),
    ("Deep turnaround", "Deep turnaround (-10 % base)", 4, 3, 3, "DECAMEX through all rows at the stop; base removal unproven"),
    ("Deep turnaround + horns", "Deep turnaround (-10 % base) + horns", 3, 3, 3, "best cooling and money; two uncertainties"),
]
h0, hmin = 2651, min(E.loc[p, "hours_gt_65C"] for _, p, *_ in O)
nmax = max(E.loc[p, "net_vs_no_action_kUSD_yr"] for _, p, *_ in O)
rows = []
for lab, p, sa, ce, fe, why in O:
    co = 1 + 4 * (h0 - E.loc[p, "hours_gt_65C"]) / (h0 - hmin)
    ec = 1 + 4 * E.loc[p, "net_vs_no_action_kUSD_yr"] / nmax
    tot = W["cooling"] * co + W["economics"] * ec + W["safety"] * sa + W["certainty"] * ce + W["feasibility"] * fe
    ce2 = 5 if "Deep" in lab else ce
    tot2 = tot + W["certainty"] * (ce2 - ce)
    rows.append(dict(option=lab, cooling=round(co, 1), economics=round(ec, 1), safety=sa, certainty=ce, feasibility=fe,
                     score_today=round(tot, 2), score_after_inspection=round(tot2, 2), reasons=why))
D = pd.DataFrame(rows); D.to_csv(os.path.join(HERE, "results", "decision_matrix.csv"), index=False)
print(D.drop(columns="reasons").to_string(index=False))
