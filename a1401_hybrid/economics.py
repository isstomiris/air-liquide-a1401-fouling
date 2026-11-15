"""
Quick economics for the hybrid strategies (reads results/hybrid_scenarios.csv from simulate_hybrid.py).

ALL COSTS ARE TEAM ORDER-OF-MAGNITUDE ESTIMATES (low / central / high), NOT VENDOR QUOTES. They are written
here so anyone can change them; the payback answer is shown for the whole range.
  H2 margin, USD/kg      1.0 / 1.5 / 2.0   (team assumption A13: H2 value 1.5-2.5 USD/kg, minus feed gas)
  Turnaround full clean  already in the plant's turnaround budget (the plant did it in Jun-Jul 2026): 0 extra
  Deep-clean add-on      30k / 60k / 120k per turnaround (DECAMEX through all 6 rows + borescope + fin combing)
  DECAMEX online campaign 15k / 30k / 60k each (vendor service, one fan stopped ~4.8 h)
  Sonic horns            CAPEX 50k / 90k / 150k (3 horns, vacuum hood, air piping, install);
                         OPEX 15k/yr (5k upkeep + ~24 h/yr with one fan off, about 6.7 t H2 at 1.5 USD/kg)
  Fan-off loss DECAMEX   one fan off -> about 30 % less gas for 4.8 h per campaign = 1.3 t H2 per campaign
Benefit: extra H2 from simulate_hybrid.py (season 2025 replay, capped at the cool-weather flow; upper estimate).
"""
import os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(os.path.join(HERE, "results", "hybrid_scenarios.csv")).set_index("strategy")
MARGIN = dict(low=1.0, central=1.5, high=2.0)              # USD/kg = kUSD/t
DEC = dict(low=15, central=30, high=60)                     # kUSD per campaign
DEEP = dict(low=30, central=60, high=120)                   # kUSD per turnaround
HCAP = dict(low=50, central=90, high=150)                   # kUSD once
HOPEX_UPKEEP, FANOFF_H2_HORNS_t, FANOFF_H2_DEC_t = 5, 6.7, 1.3
LEAD = {"horns": "8-12 weeks (order + mounting design + hot-work permit)",
        "decamex": "4-8 weeks to book the service crew",
        "deep": "next planned turnaround (planned now, done at the stop)",
        "full": "next planned turnaround"}
PLANS = [  # name in csv, short label, horns?, online DECAMEX campaigns, full?, deep?
    ("Horns only (24 events)", "Horns", True, 0, False, False),
    ("DECAMEX only (2 campaigns)", "DECAMEX x2", False, 2, False, False),
    ("Full turnaround clean only (27 Jun)", "Turnaround clean (current practice)", False, 0, True, False),
    ("Full clean + horns", "Turnaround + horns", True, 0, True, False),
    ("DECAMEX 1 Jun + full clean + DECAMEX 1 Aug", "Turnaround + DECAMEX x2", False, 2, True, False),
    ("Full clean + horns + DECAMEX 1 Jun, 1 Aug", "Turnaround + horns + DECAMEX x2", True, 2, True, False),
    ("Deep clean (base -5 %) + DECAMEX 1 Jun, 1 Aug", "Deep turnaround (-5 % base) + DECAMEX x2", False, 2, True, True),
    ("Deep clean (base -10 %) + DECAMEX 1 Jun, 1 Aug", "Deep turnaround (-10 % base) + DECAMEX x2", False, 2, True, True),
    ("Deep clean (base -25 %) + DECAMEX 1 Jun, 1 Aug", "Deep turnaround (-25 % base) + DECAMEX x2", False, 2, True, True),
    ("Deep clean (base -10 %) only", "Deep turnaround (-10 % base)", False, 0, True, True),
    ("Deep clean (base -25 %) only", "Deep turnaround (-25 % base)", False, 0, True, True),
    ("Deep clean (base -10 %) + horns", "Deep turnaround (-10 % base) + horns", True, 0, True, True),
    ("Deep clean (base -25 %) + horns", "Deep turnaround (-25 % base) + horns", True, 0, True, True),
]
ref_cur = R.loc["Full turnaround clean only (27 Jun)", "extra_H2_t"]
rows = []
for key, lab, horns, ndec, full, deep in PLANS:
    r = R.loc[key]
    for case in ("low", "central", "high"):
        m = MARGIN[case]
        # pessimistic pairing: low margin with high cost, and the reverse
        cc = {"low": "high", "central": "central", "high": "low"}[case]
        capex = HCAP[cc] if horns else 0
        fan_t = (FANOFF_H2_HORNS_t if horns else 0) + FANOFF_H2_DEC_t * ndec
        opex = (HOPEX_UPKEEP if horns else 0) + DEC[cc] * ndec + (DEEP[cc] if deep else 0) + fan_t * m
        gain = r.extra_H2_t * m
        net = gain - opex
        inc_gain = (r.extra_H2_t - ref_cur) * m
        inc_net = inc_gain - opex
        rows.append(dict(plan=lab, case=case, extra_H2_t=r.extra_H2_t, ref_T_out_C=r.ref_T_out_C,
                         hours_gt_65C=r.hours_gt_65C, capex_kUSD=capex, opex_kUSD_yr=round(opex, 1),
                         gain_vs_no_action_kUSD_yr=round(gain), net_vs_no_action_kUSD_yr=round(net),
                         payback_vs_no_action_months=round(12 * capex / net, 1) if capex and net > 0 else (0 if net > 0 else None),
                         extra_vs_current_practice_t=round(r.extra_H2_t - ref_cur, 1) if full else None,
                         net_vs_current_practice_kUSD_yr=round(inc_net) if full else None,
                         payback_vs_current_months=(round(12 * capex / inc_net, 1) if capex and inc_net > 0 else
                                                    (0 if inc_net > 0 else None)) if full else None,
                         lead_time="; ".join(v for k, v in LEAD.items() if (k == "horns" and horns) or (k == "decamex" and ndec)
                                             or (k == "deep" and deep) or (k == "full" and full and not deep))))
E = pd.DataFrame(rows)
E.to_csv(os.path.join(HERE, "results", "economics.csv"), index=False)
pd.set_option("display.width", 250)
print(E[E.case == "central"].drop(columns=["case", "lead_time"]).to_string(index=False))
print(E[E.case != "central"][["plan", "case", "net_vs_no_action_kUSD_yr", "net_vs_current_practice_kUSD_yr", "payback_vs_current_months"]].to_string(index=False))
