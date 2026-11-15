"""Copy the team's Python figures into deck/img with warm colours (orange, gold, red) turned into navy blue,
so the deck uses one blue palette. Only hue/brightness of warm pixels change; data, axes and labels are untouched."""
import os, sys
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["pfd/A-1401_section_PFD.png", "model/charts/1_airflow_choking.png", "model/charts/2_duty_breakdown.png",
         "model/charts/3_bottleneck_vs_ambient.png", "model/charts/6_real_history.png",
         "a1401_clean_vs_fouled/figures/fig0_A1401_schematic.png", "a1401_clean_vs_fouled/figures/fig2_outlet_T.png",
         "a1401_clean_vs_fouled/figures/fig3_airflow.png", "a1401_clean_vs_fouled/figures/fig5_duty_vs_blockage.png",
         "a1401_clean_vs_fouled/figures/fig6_duty_split.png", "a1401_clean_vs_fouled/figures/fig8_history_comparison.png",
         "monitor/chart6_backtest.png", "monitor/chart7_forecast_error.png",
         "a1401_solutions_check/figures_v2/fig1_season_2025_v2.png", "a1401_solutions_check/figures_v2/fig2_reference_day_v2.png"]


def recolor(path, out):
    im = Image.open(path).convert("RGB")
    hsv = np.array(im.convert("HSV")).astype(float)
    H, S, V = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    warm = ((H <= 55) | (H >= 340)) & (S > 0.12) & (V > 0.25)
    strong = warm & (S > 0.45)
    H[warm] = 214
    V[strong] = V[strong] * 0.62
    S[strong] = np.maximum(S[strong], 0.85)
    hsv2 = np.stack([H * 255 / 360, S * 255, V * 255], -1).clip(0, 255).astype(np.uint8)
    Image.fromarray(hsv2, "HSV").convert("RGB").save(out)


for f in FILES:
    o = os.path.join(ROOT, "deck", "img", os.path.basename(f))
    recolor(os.path.join(ROOT, f), o)
    print("ok", o)
