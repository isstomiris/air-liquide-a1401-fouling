import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = json.load(open("results.json"))
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False})
def finish(fig, ax, title, sub, path):
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color=INK, pad=26)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10, color=INK2)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)

# 1. airflow choking
cv = R["curves"]; phi = [c["phi"] * 100 for c in cv]
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(phi, [c["airflow_pct"] for c in cv], color=C1, lw=2)
ax.plot(phi, [c["UA_air_pct"] for c in cv], color=C2, lw=2)
ax.text(phi[-1] + 1, cv[-1]["airflow_pct"], "Airflow", color=INK, va="center", fontsize=10.5)
ax.text(phi[-1] + 1, cv[-1]["UA_air_pct"], "Air-side heat\ntransfer (hA)", color=INK, va="center", fontsize=10.5)
pn = R["anchors"]["14 Nov 2026 15:16"]["phi_equiv"] * 100
ax.axvspan(31, 78, color=C4, alpha=0.10, lw=0); ax.axvspan(55, 70, color=C4, alpha=0.22, lw=0)
ax.text(56, 12, "14 Nov estimate:\nlikely 55-70%\n(possible 31-78%)", fontsize=10, color=INK2)
ax.set_xlabel("Fin gaps blocked by debris (%)"); ax.set_ylabel("% of clean value (fans at 100%)")
ax.set_xlim(0, 92); ax.set_ylim(0, 105)
finish(fig, ax, "Airflow choking: debris cuts air and heat transfer", "A-1401 model, 3 fans at full speed. Lines are % of the clean bundle.", "charts/1_airflow_choking.png")

# 2. duty breakdown
cases = [("Datasheet\n135 -> 55 C", None), ("1 Jan 2026\n145 -> 70 C", "1 Jan 2026 (00-08h)"), ("14 Nov 2026\n167 -> 66 C", "14 Nov 2026 15:16")]
import a1401_model as m
vals = []
for lab, key in cases:
    b = m.duty_breakdown(135, 55, 20588) if key is None else {k: v * 1e6 if k in ("total", "gas_sensible", "latent", "other_water_sensible") else v for k, v in R["anchors"][key]["breakdown"].items()}
    vals.append((b["gas_sensible"] / 1e6, b["latent"] / 1e6, b["other_water_sensible"] / 1e6))
fig, ax = plt.subplots(figsize=(9, 5.2))
x = range(len(cases)); bottoms = [0] * 3
names = ["Gas cooling", "Water condensing (latent heat)", "Water cooling (liquid + vapour)"]
cols = [C1, C2, C3]
for j in range(3):
    hs = [v[j] for v in vals]
    ax.bar(x, hs, bottom=bottoms, color=cols[j], width=0.55, edgecolor=SURF, linewidth=2, label=names[j])
    bottoms = [b + h for b, h in zip(bottoms, hs)]
for i, t in enumerate(bottoms):
    ax.text(i, t + 0.08, f"{t:.1f} MW", ha="center", fontsize=11, fontweight="bold", color=INK)
ax.set_xticks(list(x)); ax.set_xticklabels([c[0] for c in cases])
ax.set_ylabel("Heat removed by A-1401 (MW)"); ax.set_ylim(0, 6.2); ax.grid(axis="x", visible=False)
ax.legend(frameon=False, loc="upper left", fontsize=10)
finish(fig, ax, "Most of the cooler's work is condensing water", "Same ~20,600-22,900 Nm3/h dry gas. A hotter inlet means more water vapour to condense.", "charts/2_duty_breakdown.png")

# 3. max flow vs ambient (scenario curves, audit M3)
mfv = R["loss_scenarios"]["max_flow_vs_Tamb"]
fig, ax = plt.subplots(figsize=(9, 5.2))
spec = [("phi0_Tin167", "Clean", C1, "-"), ("phi35_Tin167", "35% blocked", C3, "-"),
        ("phi50_Tin167", "50% blocked", C4, "-"), ("phi65_Tin167", "65% blocked", C2, "-"),
        ("phi65_Tin145", "65% blocked, inlet 145 C", C2, "--")]
for key, lab, col, ls in spec:
    pts = sorted((float(k), v) for k, v in mfv[key].items())
    xs = [p[0] + 0.5 for p in pts]; ys = [min(p[1], 60000) / 1000 for p in pts]
    ax.plot(xs, ys, color=col, lw=2, ls=ls)
    ly = {"phi35_Tin167": ys[-1] + 1.2, "phi65_Tin145": ys[-1] + 0.1, "phi50_Tin167": ys[-1] - 1.0}.get(key, ys[-1])
    ax.text(xs[-1] + 0.6, ly, lab, color=INK, va="center", fontsize=9.5)
ax.hlines(20.801, 0, 45.5, color=INK2, lw=1.2, ls=":")
ax.text(1, 17.6, "Current dry-gas flow 20,800 Nm3/h", color=INK2, fontsize=10)
ax.set_xlabel("Outside air temperature (C)"); ax.set_ylabel("Max dry syngas flow held at 65 C (1,000 Nm3/h)")
ax.set_xlim(0, 58); ax.set_ylim(0, 50)
finish(fig, ax, "When does the cooler limit production?", "Solid lines: inlet 167 C (14 Nov). Below the dotted line the plant must cut load. Fans at 100%.", "charts/3_bottleneck_vs_ambient.png")

# 4. outlet temp at 38 C vs blockage
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(phi, [c["T_out_summer38"] for c in cv], color=C2, lw=2)
ax.axhline(65, color=INK2, lw=1.2, ls="--"); ax.text(1, 67, "Set point 65 C", color=INK2, fontsize=10)
ax.axvspan(31, 78, color=C4, alpha=0.10, lw=0); ax.axvspan(55, 70, color=C4, alpha=0.22, lw=0)
ax.text(56, 125, "14 Nov:\nlikely 55-70%", color=INK2, fontsize=10)
ax.set_xlabel("Fin gaps blocked by debris (%)"); ax.set_ylabel("Gas outlet temperature (C)")
ax.set_xlim(0, 82); ax.set_ylim(20, 140)
finish(fig, ax, "The 'cliff': outlet temperature on a 38 C day", "Fans 100%, inlet 167 C, 20,800 Nm3/h. Little effect up to ~40% blockage, then it rises fast.", "charts/4_outlet_vs_blockage_38C.png")

# 5. tornado of the blockage estimate (audit H1)
U = json.load(open("uncertainty.json"))["tornado"]
base = U["Base case"]
groups = [("Real gas flow higher than meter (+10/+25/+50%)", ["Real gas flow +10 %", "Real gas flow +25 %", "Real gas flow +50 %"]),
          ("Water content (steam balance vs carbon balance)", ["Less water: just saturated at 167 C", "Much less water (if carbon balance is right)"]),
          ("Design air temperature 30-38 C", ["Design air temperature 30 C (model re-tuned)", "Design air temperature 38 C (model re-tuned)"]),
          ("Air-side heat transfer -20/+20%", ["Air-side coefficient -20 %", "Air-side coefficient +20 %"]),
          ("Fan % = 25-50 Hz instead of 0-50 Hz", ["Fan % means 25-50 Hz"]),
          ("Fan curve flatter/steeper", ["Flatter fan curve", "Steeper fan curve"]),
          ("Bundle share of fan pressure 65-85%", ["Bundle = 85 % of fan pressure", "Bundle = 65 % of fan pressure"]),
          ("Air 2 K warmer than weather data", ["Air 2 K warmer"])]
rows = []
for lab, keys in groups:
    for mon in ("nov", "jan"):
        v = [U[k][mon] * 100 for k in keys] + [base[mon] * 100]
        rows.append((lab, mon, min(v), max(v)))
order = sorted(groups, key=lambda g: -max(r[3] - r[2] for r in rows if r[0] == g[0]))
fig, ax = plt.subplots(figsize=(9.5, 6.2))
for i, (lab, _) in enumerate(order):
    y = len(order) - 1 - i
    for mon, col, dy in (("nov", C2, 0.17), ("jan", C1, -0.17)):
        r = next(r for r in rows if r[0] == lab and r[1] == mon)
        ax.barh(y + dy, r[3] - r[2], left=r[2], height=0.3, color=col)
    ax.text(29, y, lab, ha="right", va="center", fontsize=9.5, color=INK)
ax.axvline(base["nov"] * 100, color=C2, lw=1, ls="--"); ax.axvline(base["jan"] * 100, color=C1, lw=1, ls="--")
ax.text(base["nov"] * 100 - 0.5, len(order) - 0.35, f"14 Nov base {base['nov']*100:.0f}%", color=C2, fontsize=9.5, ha="right")
ax.text(base["jan"] * 100 + 0.5, len(order) - 0.35, f"1 Jan base {base['jan']*100:.0f}%", color=C1, fontsize=9.5)
ax.set_yticks([]); ax.set_xlim(0, 85); ax.set_ylim(-0.6, len(order) + 0.1); ax.grid(axis="y", visible=False)
ax.set_xticks(range(30, 90, 10))
ax.set_xlabel("Estimated blockage of fin gaps (%)")
finish(fig, ax, "How sure are we about the blockage? Not very", "Each bar: how far the estimate moves if one assumption changes. Orange = 14 Nov, blue = 1 Jan.", "charts/5_blockage_uncertainty_tornado.png")
print("ok")
