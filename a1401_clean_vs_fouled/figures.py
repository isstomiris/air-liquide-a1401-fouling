"""Figures for the A-1401 clean vs fouled calculation note.  Every plotted number comes from run_all.py."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
INK, INK2, GRID = "#222222", "#555555", "#d9d9d9"
COL = ["#2a78d6", "#eb6834", "#1baf7a", "#c98500"]          # fixed order: A, B, C, D
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100, "savefig.dpi": 200,
                     "axes.titlesize": 10.5, "axes.titleweight": "bold", "legend.frameon": False})
SHORT = ["A Clean\n0 %", "B Assumed\n30 % (brief)", "C Spring 2025\n(fitted)", "D End of summer\n2025 (fitted)"]


def _note(fig, txt):
    fig.text(0.01, 0.01, txt, fontsize=7.3, color=INK2, ha="left", va="bottom")


def _bars(cmp_, key, ylabel, title, fname, fmt="{:,.0f}", note="", REF=None):
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    vals = cmp_[key].values
    labels = [f"{s}\nb = {100*b:.0f} %" if i > 1 else s for i, (s, b) in enumerate(zip(SHORT, cmp_.blockage))]
    ax.bar(range(len(vals)), vals, color=COL, width=0.6, edgecolor="white", linewidth=1.5)
    for i, v in enumerate(vals):
        ax.text(i, v, fmt.format(v), ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel(ylabel); ax.set_title(title, loc="left"); ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(vals) * 1.15)
    _note(fig, note); fig.tight_layout(rect=(0, 0.11, 1, 1)); fig.savefig(os.path.join(FIG, fname)); plt.close(fig)


def schematic():
    fig, ax = plt.subplots(figsize=(8.2, 5.2)); ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
    ax.add_patch(Rectangle((2.0, 2.6), 6.0, 2.2, fill=False, ec=INK, lw=1.4))
    for i in range(6):
        y = 2.8 + i * 0.33
        ax.plot([2.2, 7.8], [y, y], color="#7a7a7a", lw=2.2)
        ax.text(8.1, y, f"row {i+1}" + ("  pass 2" if i < 3 else "  pass 1"), fontsize=7.5, va="center", color=INK2)
    ax.plot([2.0, 8.0], [3.68, 3.68], color=INK2, lw=0.6, ls="--")
    ax.text(5.0, 5.0, "A-1401 finned-tube bundle: 276 tubes, 25 x 2 mm, S30403, 6 rows, 2 passes\n"
            "Al fins, 5,288 m2 extended / 226 m2 bare (datasheet)", ha="center", fontsize=8, color=INK)
    # headers
    ax.add_patch(Rectangle((1.4, 2.6), 0.6, 2.2, fc="#efefef", ec=INK, lw=1.0)); ax.add_patch(Rectangle((8.0, 2.6), 0.0, 2.2, ec=INK))
    ax.text(1.7, 3.7, "inlet / outlet header", ha="center", va="center", rotation=90, fontsize=7, color=INK2)
    # process in / out
    ax.annotate("", xy=(1.4, 4.35), xytext=(0.1, 4.35), arrowprops=dict(arrowstyle="-|>", color="#1b7f3b", lw=2))
    ax.text(0.1, 4.55, "Wet syngas IN (tube side)\nH2-rich gas + water vapour\n(+ entrained condensate)\n~160 C, 2.75 MPa abs", fontsize=7.3, color="#1b7f3b", va="bottom")
    ax.annotate("", xy=(0.1, 3.0), xytext=(1.4, 3.0), arrowprops=dict(arrowstyle="-|>", color="#1b7f3b", lw=2))
    ax.text(0.1, 2.85, "Cooled syngas +\nprocess CONDENSATE OUT\nto E-1409 / E-1410 / D-1403", fontsize=7.3, color="#1b7f3b", va="top")
    # fans
    for x in (3.0, 5.0, 7.0):
        ax.add_patch(Circle((x, 1.55), 0.55, fill=False, ec=INK, lw=1.1))
        ax.plot([x - 0.5, x + 0.5], [1.55, 1.55], color=INK, lw=1.1); ax.plot([x, x], [1.05, 2.05], color=INK, lw=1.1)
        ax.annotate("", xy=(x, 2.55), xytext=(x, 0.3), arrowprops=dict(arrowstyle="-|>", color=COL[0], lw=1.6))
    ax.text(5.0, 0.05, "Ambient AIR IN from below: 3 forced-draft fans, 2.4 m, 11 kW, 114,000 m3/h each (rated, 190 Pa total)",
            ha="center", fontsize=7.6, color=COL[0])
    for x in (3.0, 5.0, 7.0):
        ax.annotate("", xy=(x, 6.3), xytext=(x, 5.45), arrowprops=dict(arrowstyle="-|>", color="#b5462a", lw=1.6))
    ax.text(5.0, 6.45, "Warmed AIR OUT to atmosphere (top)", ha="center", fontsize=8, color="#b5462a")
    ax.text(9.95, 1.0, "Separate LP-steam heating row\n(winter only) not part of the\nmain cooling area; not modelled",
            fontsize=6.8, color=INK2, ha="right")
    ax.text(9.95, 2.0, "Debris collects on the\nunderside of row 1\n(air entry face)", fontsize=6.8, color=INK2, ha="right")
    ax.set_title("Figure 0. A-1401 air-cooled syngas exchanger, stream arrangement used in the model", loc="left", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig0_A1401_schematic.png")); plt.close(fig)


def make_all(cmp_, sweep, sens, sel, vals, per, REF, b_spring, b_summer):
    src = (f"Conditions: real historian window {REF['start_utc'][:16]}-{REF['end_utc'][11:16]} UTC; inlet {REF['T_in_C']:.1f} C, "
           f"{REF['flow_dry_Nm3h']:,.0f} Nm3/h dry gas,\nair {REF['T_amb_C']:.1f} C (ERA5), fans 100 %, water/dry gas 0.555. "
           "\nC and D: equivalent blockage fitted to plant outlet temperatures (includes any model offset). Source: run_all.py")
    schematic()
    _bars(cmp_, "Q_total_kW", "Total heat duty, kW", "Figure 1. Total cooling duty, clean vs fouled", "fig1_duty.png", note=src)
    _bars(cmp_, "T_out_C", "Syngas outlet temperature, C", "Figure 2. Syngas outlet temperature, clean vs fouled", "fig2_outlet_T.png", "{:.1f}", note=src)
    cm = cmp_.copy(); cm["air_kh"] = cm.air_m3h / 1000
    _bars(cm, "air_kh", "Airflow, 1000 m3/h (at ambient)", "Figure 3. Cooling airflow at 100 % fan speed", "fig3_airflow.png", "{:.0f}", note=src)
    _bars(cmp_, "UA_total_kW_K", "Overall conductance UA, kW/K", "Figure 4. Effective overall conductance UA", "fig4_UA.png", "{:.1f}", note=src)

    # ---- fig 5: sweep (two panels, shared x, one quantity per axis)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 6.0), sharex=True)
    x = 100 * sweep.blockage
    a1.plot(x, sweep.Q_total_kW, color=COL[0], lw=2, marker="o", ms=4, label="Total duty")
    a1.plot(x, sweep.Q_latent_kW, color=COL[0], lw=1.3, ls="--", label="of which condensation (latent)")
    a1.set_ylabel("Heat duty, kW"); a1.set_title("Figure 5. Duty and outlet temperature vs blockage", loc="left")
    a2.plot(x, sweep.T_out_C, color=INK, lw=2, marker="o", ms=4, label="Syngas outlet temperature")
    a2.set_ylabel("Syngas outlet, C"); a2.set_xlabel("Blocked fraction of air passages b, %")
    for lab, bb, c in (("B 30 % brief", 0.30, COL[1]), ("C spring 2025", b_spring, COL[2]), ("D end of summer 2025", b_summer, COL[3])):
        for ax in (a1, a2):
            ax.axvline(100 * bb, color=c, lw=1.2, ls=":")
        a2.text(100 * bb + 0.6, a2.get_ylim()[0] + 2, lab, rotation=90, fontsize=7.5, color=INK2, va="bottom")
    a2.axhline(REF["T_out_C"], color=INK2, lw=0.8, ls="--"); a2.text(1, REF["T_out_C"] + 0.8, f"measured {REF['T_out_C']:.1f} C", fontsize=7.5, color=INK2)
    a1.legend(loc="lower left", fontsize=8)
    _note(fig, src); fig.tight_layout(rect=(0, 0.09, 1, 1)); fig.savefig(os.path.join(FIG, "fig5_duty_vs_blockage.png")); plt.close(fig)

    # ---- fig 6: duty decomposition (stacked, 2 px gaps via white edges)
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    parts = [("Q_dry_gas_sensible_kW", "Dry gas, sensible", "#9ec5f4"), ("Q_vapour_sensible_kW", "Water vapour, sensible", "#6da7ec"),
             ("Q_condensate_sensible_kW", "Liquid water, sensible", "#256abf"), ("Q_latent_kW", "Condensation (latent)", "#0d366b")]
    bottom = np.zeros(len(cmp_))
    for k, lab, c in parts:
        v = cmp_[k].values
        ax.bar(range(len(v)), v, bottom=bottom, color=c, width=0.6, edgecolor="white", linewidth=1.5, label=lab)
        bottom += v
    for i, t in enumerate(bottom):
        ax.text(i, t, f"{t:,.0f} kW\nlatent {100*cmp_.Q_latent_kW.iloc[i]/t:.0f} %", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(cmp_))); ax.set_xticklabels(SHORT, fontsize=8.5); ax.grid(axis="x", visible=False)
    ax.set_ylabel("Heat duty, kW"); ax.set_ylim(0, bottom.max() * 1.22)
    ax.set_title("Figure 6. Duty split: sensible cooling vs water condensation", loc="left")
    ax.legend(loc="upper center", ncol=2, fontsize=7.8, bbox_to_anchor=(0.5, -0.17))
    _note(fig, src); fig.tight_layout(rect=(0, 0.1, 1, 1)); fig.savefig(os.path.join(FIG, "fig6_duty_split.png")); plt.close(fig)

    # ---- fig 7: sensitivity (two panels)
    base = sens.iloc[0]; s = sens.iloc[1:].copy()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 5.4), sharey=True)
    y = np.arange(len(s))[::-1]
    d1 = s.clean_T_out_C - base.clean_T_out_C
    d2 = 100 * (s.b_eq_fitted - base.b_eq_fitted)
    a1.barh(y, d1, color=[COL[0] if v >= 0 else "#86b6ef" for v in d1], height=0.6)
    a2.barh(y, d2, color=[COL[3] if v >= 0 else "#f0c060" for v in d2], height=0.6)
    a1.set_yticks(y); a1.set_yticklabels(s.scenario, fontsize=8)
    a1.set_xlabel(f"Change in CLEAN outlet temperature, K\n(base {base.clean_T_out_C:.1f} C)")
    a2.set_xlabel(f"Change in fitted equivalent blockage, percentage points\n(base {100*base.b_eq_fitted:.0f} %, refitted to the same measurement)")
    for ax in (a1, a2):
        ax.axvline(0, color=INK, lw=0.8); ax.grid(axis="y", visible=False); lo_, hi_ = ax.get_xlim(); ax.set_xlim(lo_ - 0.12 * (hi_ - lo_), hi_ + 0.08 * (hi_ - lo_))
    for yy, v in zip(y, d1): a1.text(v, yy, f" {v:+.1f}", va="center", ha="left" if v >= 0 else "right", fontsize=7.5)
    for yy, v in zip(y, d2): a2.text(v, yy, f" {v:+.1f}", va="center", ha="left" if v >= 0 else "right", fontsize=7.5)
    fig.suptitle("Figure 7. Sensitivity to the main uncertain assumptions (one at a time, summer reference window)", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    _note(fig, "Left: how much a clean exchanger's predicted outlet moves. Right: how much the blockage needed to explain the measured outlet moves. Source: results/sensitivity.csv")
    fig.tight_layout(rect=(0, 0.05, 1, 0.95)); fig.savefig(os.path.join(FIG, "fig7_sensitivity.png")); plt.close(fig)

    # ---- fig 8: history (a) equivalent blockage over time, (b) withheld prediction check
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw=dict(width_ratios=[1.6, 1]))
    daily = sel.b_eq.resample("1D").median()
    a1.plot(daily.index, 100 * daily, color=INK2, lw=0, marker="o", ms=1.8, alpha=0.7, label="daily median (fans 100 %, air >= 10 C)")
    a1.plot(daily.index, 100 * daily.rolling(14, min_periods=5).median(), color=INK, lw=1.6, label="14-day rolling median")
    for (_, r), c in zip(per.iterrows(), [COL[2], COL[3], COL[2], COL[3]]):
        nm = r.period
        a, b = {"Spring 2024": ("2024-04-01", "2024-05-15"), "End of summer 2024": ("2024-08-01", "2024-09-15"),
                "Spring 2025": ("2025-04-01", "2025-05-15"), "End of summer 2025": ("2025-08-01", "2025-09-15")}[nm.split(" (")[0]]
        a1.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=c, alpha=0.15, lw=0)
        a1.hlines(100 * r.b_fitted_on_calibration, pd.Timestamp(a), pd.Timestamp(b), color=c, lw=2.5)
    a1.set_ylabel("Equivalent blockage b_eq, %"); a1.set_ylim(0, 90)
    a1.set_title("Figure 8a. Blockage the model needs to match the plant", loc="left")
    a1.legend(loc="lower left", fontsize=7.5)
    for nm, c in zip(per.period, [COL[2], COL[3], COL[2], COL[3]]):
        v = vals[vals.period == nm]
        a2.scatter(v.T_out_meas, v.T_out_pred, s=6, color=c, alpha=0.55, lw=0)
    v = vals
    a2.scatter(v.T_out_meas, v.T_out_clean_pred, s=5, color="#aaaaaa", alpha=0.5, lw=0, label="clean model (b = 0)")
    a2.scatter([], [], s=12, color=COL[2], label="spring periods, b fitted on other weeks")
    a2.scatter([], [], s=12, color=COL[3], label="end-of-summer periods, b fitted on other weeks")
    lo, hi = 20, max(v.T_out_meas.max(), v.T_out_pred.max()) + 3
    a2.plot([lo, hi], [lo, hi], color=INK, lw=0.8); a2.set_xlim(lo, hi); a2.set_ylim(lo, hi)
    a2.set_xlabel("Measured outlet TICA0055, C (withheld weeks)"); a2.set_ylabel("Predicted outlet, C")
    a2.set_title("Figure 8b. Hold-out check", loc="left"); a2.legend(fontsize=7.2, loc="upper left")
    _note(fig, "Historian 1400TIA050 / TICA0055 / FI010 / TICA0055 output, hourly, Nov 2023 - 11 Mar 2026 (later values frozen, excluded). "
               "Air: ERA5 2 m temperature. Calibration = even ISO weeks, comparison = odd ISO weeks.")
    fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(os.path.join(FIG, "fig8_history_comparison.png")); plt.close(fig)
