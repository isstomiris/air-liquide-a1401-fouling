"""Uncertainty analysis requested by the audit (H1-H4): phi as a range, tornado, re-tuned design ambient."""
import json, a1401_model as m
NOV = (166.8, 66.4, 20801, 6.5, 0.879)
JAN = (144.7, 69.7, 22862, -2.0, 0.544)
DESIGN_FLOW = 20588 / 0.58385
out = {}
def phi_of(pt, flow_mult=1.0, dTa=0.0, speed=None):
    Ti, To, F, Ta, sp = pt
    return m.solve_phi(Ti, To, F * flow_mult, Ta + dTa, sp if speed is None else speed)

# 1. design-ambient re-tuning: H_MULT that makes the clean model hit the design flow
cal = {}
for Ta in (30.0, 35.0, 38.0):
    lo, hi = 0.5, 1.6
    for _ in range(14):
        mid = (lo + hi) / 2; m.H_MULT = mid
        if m.max_flow(135, Ta, 1.0, 0.0, T_limit=55) > DESIGN_FLOW: hi = mid
        else: lo = mid
    cal[Ta] = (lo + hi) / 2
m.H_MULT = 1.0
out["design_ambient_Hmult"] = cal
out["uncalibrated_design_capacity"] = {Ta: m.max_flow(135, Ta, 1.0, 0.0, T_limit=55) for Ta in (30.0, 35.0, 38.0)}

def run(label, setup=None, undo=None, **kw):
    saved = {}
    if setup: saved = setup()
    r = {"nov": phi_of(NOV, **kw), "jan": phi_of(JAN, **kw)}
    if undo: undo(saved)
    tor[label] = r; print(label, {k: round(v, 3) for k, v in r.items()}, flush=True)

def setter(**vals):
    def s():
        saved = {k: getattr(m, k) for k in vals}
        for k, v in vals.items(): setattr(m, k, v)
        return saved
    def u(saved):
        for k, v in saved.items(): setattr(m, k, v)
    return s, u
def fan(a, b):
    def s():
        saved = dict(m.FAN); m.FAN["a"], m.FAN["b"] = a, b; return saved
    def u(saved): m.FAN.clear(); m.FAN.update(saved)
    return s, u

tor = {}
run("Base case")
run("Real gas flow +10 %", flow_mult=1.10)
run("Real gas flow +25 %", flow_mult=1.25)
run("Real gas flow +50 %", flow_mult=1.50)
s, u = setter(H_MULT=0.8); run("Air-side coefficient -20 %", s, u)
s, u = setter(H_MULT=1.2); run("Air-side coefficient +20 %", s, u)
s, u = setter(H_MULT=cal[30.0]); run("Design air temperature 30 C (model re-tuned)", s, u)
s, u = setter(H_MULT=cal[38.0]); run("Design air temperature 38 C (model re-tuned)", s, u)
s, u = fan(1.3, 0.3); run("Flatter fan curve", s, u)
s, u = fan(2.2, 1.2); run("Steeper fan curve", s, u)
s, u = setter(WATER_TO_DRY=0.36); run("Less water: just saturated at 167 C", s, u)
s, u = setter(WATER_TO_DRY=0.24); run("Much less water (if carbon balance is right)", s, u)
s, u = setter(SYS_OTHER=0.15); run("Bundle = 85 % of fan pressure", s, u)
s, u = setter(SYS_OTHER=0.35); run("Bundle = 65 % of fan pressure", s, u)
run("Fan % means 25-50 Hz", speed=None) if False else None
tor["Fan % means 25-50 Hz"] = {"nov": phi_of(NOV, speed=0.5 + 0.5 * 0.879), "jan": phi_of(JAN, speed=0.5 + 0.5 * 0.544)}
run("Air 2 K warmer", dTa=2.0)
out["tornado"] = tor

# 2. duty under the water-content alternatives (14 Nov)
dw = {}
for w in (0.555, 0.45, 0.36, 0.24):
    m.WATER_TO_DRY = w
    b = m.duty_breakdown(166.8, 66.4, 20801)
    dw[w] = dict(duty_MW=b["total"] / 1e6, latent_share=b["latent"] / b["total"], dew_point_C=b["dew_point_C"])
m.WATER_TO_DRY = 0.555
out["duty_vs_water"] = dw
# condensation share at the three anchor cases
out["latent_share"] = {k: (lambda b: b["latent"] / b["total"])(m.duty_breakdown(*v)) for k, v in
                       {"design": (135, 55, 20588), "jan": (144.7, 69.7, 22862), "nov": (166.8, 66.4, 20801)}.items()}
out["duty_inlet_145_vs_167"] = (m.duty(144.7, 66.4, 20801) / 1e6, m.duty(166.8, 66.4, 20801) / 1e6)
json.dump(out, open("uncertainty.json", "w"), indent=1, default=float)
print(json.dumps({k: out[k] for k in ("design_ambient_Hmult", "duty_vs_water", "latent_share", "duty_inlet_145_vs_167")}, indent=1, default=lambda x: round(float(x), 3)))
