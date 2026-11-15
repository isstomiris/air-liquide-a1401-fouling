"""Figures for the hybrid strategies (blue palette). Run after simulate_hybrid.py and economics.py."""
import os, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, "figures"); os.makedirs(FIG, exist_ok=True)
R = pd.read_csv(os.path.join(HERE, "results", "hybrid_scenarios.csv")).set_index("strategy")
E = pd.read_csv(os.path.join(HERE, "results", "economics.csv"))
NAVY, BLUE, SKY, PALE, GREY, INK = "#0a3a75", "#0b80dc", "#6cbcf5", "#cfe8fb", "#9aa4ab", "#0b0b0c"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#888", "axes.labelcolor": INK, "xtick.color": "#444", "ytick.color": "#444"})

# H1 outlet on the hot reference day
pick = [("No in-season action (2025)", "No action (2025)", GREY),
        ("Horns only (24 events)", "Sonic horns", SKY), ("DECAMEX only (2 campaigns)", "DECAMEX x2", SKY),
        ("Full turnaround clean only (27 Jun)", "Turnaround clean (plant 2026)", SKY),
        ("Full clean + horns", "Turnaround + horns", BLUE), ("DECAMEX 1 Jun + full clean + DECAMEX 1 Aug", "Turnaround + DECAMEX x2", BLUE),
        ("Full clean + horns + DECAMEX 1 Jun, 1 Aug", "Turnaround + horns + DECAMEX", BLUE),
        ("Deep clean (base -10 %) + horns", "Deep turnaround (-10 % base) + horns", NAVY),
        ("Deep clean (base -25 %) + horns", "Deep turnaround (-25 % base) + horns", NAVY),
        ("Deep clean (base -100 %) + DECAMEX 1 Jun, 1 Aug", "Deep turnaround, base fully removed", NAVY),
        ("Limit: clean bundle all season", "Clean bundle (model)", PALE)]
fig, ax = plt.subplots(figsize=(12, 6.6))
for i, (k, lab, c) in enumerate(pick):
    v = R.loc[k, "ref_T_out_C"]; h = R.loc[k, "hours_gt_65C"]
    ax.barh(i, v, color=c, height=0.66)
    ax.text(v + 0.8, i, f"{v:.1f} °C   ·   {h:,} h > 65 °C", va="center", fontsize=12, color=INK)
ax.set_yticks(range(len(pick))); ax.set_yticklabels([p[1] for p in pick]); ax.invert_yaxis()
ax.axvline(65, color=BLUE, ls="--", lw=1.3); ax.text(65.5, -0.75, "65 °C target", color=BLUE, fontsize=12)
ax.set_xlim(0, 105); ax.set_xlabel("Syngas outlet on the hot day (18 Jul 2025, air 31.8 °C), °C")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.text(0.01, 0.012, "Hours > 65 °C: season 2025 replayed hour by hour. Cleaning at the 27 Jun stop; before it the plant runs as in 2025. Horn hardware costs ~0.4 K on the hot day.", fontsize=10.5, color="#555"); fig.savefig(os.path.join(FIG, "h1_hybrid_outlet.png"), dpi=170); plt.close(fig)

# H2 base removal: outlet and extra H2
ks = [0, 5, 7.5, 10, 25]
keys = ["Full turnaround clean only (27 Jun)"] + [f"Deep clean (base -{k:g} %) only" for k in ks[1:]]
T = [R.loc[k, "ref_T_out_C"] for k in keys]; H = [R.loc[k, "extra_H2_t"] for k in keys]
ks2 = [25, 50, 75, 100]; T2 = [R.loc[f"Deep clean (base -{k} %) + DECAMEX 1 Jun, 1 Aug", "ref_T_out_C"] for k in ks2]
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
ax[0].plot(ks + ks2[1:], T + T2[1:], "o-", color=NAVY, lw=2.2)
ax[0].axhline(36.7, color=SKY, ls=":", lw=1.5); ax[0].text(30, 32.2, "clean bundle 36.7 °C", color=BLUE)
ax[0].axhline(65, color=BLUE, ls="--", lw=1); ax[0].text(60, 62.2, "65 °C target", color=BLUE)
ax[0].set_xlabel("Share of the 50-60 % base removed at the turnaround, %"); ax[0].set_ylabel("Outlet on the hot day, °C")
ax[0].set_ylim(30, 70); ax[0].set_title("Outlet falls toward the clean bundle", loc="left", fontsize=14)
cost = 60 / 1.5   # 60 kUSD deep-clean add-on at 1.5 USD/kg -> tonnes needed
inc = np.array(H) - H[0]
ax[1].bar([str(k) for k in ks], inc, color=[GREY] + [NAVY] * 4, width=0.6)
ax[1].axhline(cost, color=BLUE, ls="--", lw=1.3); ax[1].text(-0.35, cost + 6, "pays for itself (60 k USD at 1.5 USD/kg = 40 t)", color=BLUE, fontsize=11)
for i, v in enumerate(inc):
    ax[1].text(i, v + 5, f"+{v:.0f} t", ha="center", fontsize=12)
ax[1].set_xlabel("Share of base removed, %"); ax[1].set_ylabel("Extra H₂ vs current practice, t per season")
ax[1].set_title("Extra hydrogen vs today's turnaround clean", loc="left", fontsize=14)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "h2_base_removal.png"), dpi=170); plt.close(fig)

# H3 economics: net per year vs no action with low-high whiskers
plans = ["Horns", "DECAMEX x2", "Turnaround clean (current practice)", "Turnaround + horns", "Turnaround + DECAMEX x2",
         "Turnaround + horns + DECAMEX x2", "Deep turnaround (-10 % base) + horns", "Deep turnaround (-25 % base) + horns"]
cols = [SKY, SKY, GREY, BLUE, BLUE, BLUE, NAVY, NAVY]
fig, ax = plt.subplots(figsize=(12, 6))
for i, p in enumerate(plans):
    s = E[E.plan == p].set_index("case")["net_vs_no_action_kUSD_yr"]
    ax.barh(i, s["central"], color=cols[i], height=0.62)
    ax.plot([s["low"], s["high"]], [i, i], color=INK, lw=1.3); ax.plot([s["low"]] * 2, [i - .15, i + .15], color=INK, lw=1.3); ax.plot([s["high"]] * 2, [i - .15, i + .15], color=INK, lw=1.3)
    ax.text(s["high"] + 15, i, f"{s['central']:,.0f} k USD/yr", va="center", fontsize=12)
ax.set_yticks(range(len(plans))); ax.set_yticklabels([p.replace(" (current practice)", "\n(plant practice 2026)") for p in plans]); ax.invert_yaxis()
ax.set_xlabel("Net value per year vs no action, k USD (bar: central; line: low-high)"); ax.set_xlim(0, 1350)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "h3_economics.png"), dpi=170); plt.close(fig)

# H4 season blockage trace
tr = json.load(open(os.path.join(HERE, "results", "hybrid_traces.json"))); d = pd.to_datetime(tr["days"])
fig, ax = plt.subplots(figsize=(12, 5))
for k, lab, c, ls in [("No in-season action (2025)", "No action (2025)", GREY, "-"),
                      ("Full turnaround clean only (27 Jun)", "Turnaround clean (plant 2026)", SKY, "-"),
                      ("Full clean + horns", "Turnaround + horns", BLUE, "-"),
                      ("Deep clean (base -25 %) + horns", "Deep turnaround (-25 % base) + horns", NAVY, "-")]:
    ax.plot(d, np.array(tr["traces"][k]) * 100, ls, color=c, lw=2.4, label=lab)
ax.set_ylabel("Equivalent blockage, %"); ax.legend(frameon=False, loc="lower left", fontsize=12); ax.set_ylim(40, 72)
ax.annotate("27 Jun stop", xy=(pd.Timestamp("2025-06-27"), 58), xytext=(pd.Timestamp("2025-07-12"), 66), arrowprops=dict(arrowstyle="->", color="#555"), color="#555")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "h4_season_blockage.png"), dpi=170); plt.close(fig)
print("ok")
