"""
A-1401 bottom-up cost estimate (AACE 18R-97 Class 4: accuracy -30 % / +50 %), Atyrau, Kazakhstan, Nov 2026.
Every line = quantity x unit rate. Unit-rate basis (checked 15 Nov 2026):
  FX            444.3 KZT/USD, National Bank of Kazakhstan official rate
  Power         40.20 KZT/kWh excl. VAT, Atyrau Energo tariff for producers of goods/services -> 0.0905 USD/kWh
  Labour        638,696 KZT/month, Atyrau industry average wage 2025 (Bureau of National Statistics);
                /166.5 h = 8.63 USD/h; x1.25 employer taxes and contributions = 10.8 USD/h (plant staff);
                x1.5 contractor overhead and margin = 16.2 USD/h (local contractor crew)
  Engineering   949,524 KZT/month, Atyrau mining & quarrying average 2025 -> 12.8 USD/h x1.25 x1.6 = 25.7 USD/h
  Horns         6,000 USD per PAS-120-class assembly (technoeconomic file budget basis; vendor quote required)
  Others        stated per line; all are team unit rates, not quotes.
"""
import json
FX = 444.3
KWH = 40.20 / FX
LAB_OWN = 638696 / 166.5 / FX * 1.25
LAB_CON = LAB_OWN * 1.5
ENG = 949524 / 166.5 / FX * 1.25 * 1.6
R = lambda x: round(x, 2)
RATES = {"FX KZT/USD": FX, "Power USD/kWh": R(KWH), "Plant staff USD/h": R(LAB_OWN),
         "Contractor USD/h": R(LAB_CON), "Engineer USD/h": R(ENG)}

# (section, item, qty, unit, unit_rate_usd, basis)
S1 = [
 ("Engineering & approvals", "Process / mechanical design and MOC", 160, "h", ENG, "local engineering rate"),
 ("Engineering & approvals", "Tube modal check and horn frame design (FEA)", 80, "h", ENG, "local engineering rate"),
 ("Engineering & approvals", "HAZID / HAZOP workshop, 5 people x 2 days", 80, "h", ENG, "local engineering rate"),
 ("Engineering & approvals", "OEM review of coating and horn loads", 1, "lot", 3000, "allowance"),
 ("Equipment", "Sonic horn assemblies, PAS-120 class", 3, "pc", 6000, "budget basis, quote needed"),
 ("Equipment", "Freight and customs to Atyrau (13 % of horns)", 1, "lot", 0.13 * 18000, "8 % freight + 5 % duty"),
 ("Equipment", "Ex-rated solenoids, regulators, air piping", 3, "set", 1200, "team rate"),
 ("Equipment", "Sequencer / PLC, cabling", 1, "lot", 2500, "team rate"),
 ("Equipment", "Horn support frames, local fabrication", 600, "kg", 2.5, "fabricated steel"),
 ("Equipment", "Collection hood, skirts, duct (local)", 1, "set", 4000, "team rate"),
 ("Equipment", "Dust collector 1 m3/s, cartridge type", 1, "pc", 6000, "team rate"),
 ("Coating (in situ)", "Water-based silica coating, local feedstock", 250, "L", 4.0, "0.06 L/m2 x 4,231 m2 incl. losses"),
 ("Coating (in situ)", "Pre-clean before spray, contractor crew", 80, "h", LAB_CON, "4 people x 2 days x 10 h"),
 ("Coating (in situ)", "Spray crew", 120, "h", LAB_CON, "4 people x 3 days x 10 h"),
 ("Coating (in situ)", "Airless spray unit rental", 5, "day", 60, "rental"),
 ("Coating (in situ)", "Scaffold / access, 3 bays, 2 weeks", 3, "bay", 1300, "rental incl. erect/strip"),
 ("Installation & commissioning", "Mechanical and electrical installation", 200, "h", LAB_CON, "4 people x 5 days x 10 h"),
 ("Installation & commissioning", "Acoustic survey and noise dosimetry", 2, "day", 1000, "specialist"),
 ("Installation & commissioning", "Strain-gauge response test, kit + engineer", 1, "lot", 4500, "specialist"),
 ("Safety", "Permits, gas test, fire watch / standby", 200, "h", LAB_OWN, "2 people x 10 days x 10 h"),
 ("Safety", "PPE: hearing protection, respirators", 1, "lot", 600, "team rate"),
 ("Qualification", "Feedstock analysis XRD + ICP (silica, heavy metals)", 4, "sample", 300, "university lab"),
 ("Qualification", "Adhesion and thermal-cycling tests 60-160 C", 1, "lot", 2000, "university lab"),
 ("Qualification", "Representative test cartridges", 1, "lot", 1500, "team rate"),
]
S2 = [
 ("Engineering & approvals", "Site survey, method statement, MOC", 80, "h", ENG, "local engineering rate"),
 ("Engineering & approvals", "HAZID workshop, 5 people x 2 days", 80, "h", ENG, "local engineering rate"),
 ("Engineering & approvals", "Fan-off window study (process)", 40, "h", ENG, "local engineering rate"),
]
S2_CAMP = [
 ("Vendor service", "Vendor technicians, 3 x 4 days (incl. travel)", 12, "man-day", 900, "international day rate"),
 ("Vendor service", "Flights to Atyrau, return", 3, "trip", 1400, "team rate"),
 ("Vendor service", "Hotel and per diem", 12, "man-day", 180, "Atyrau"),
 ("Vendor service", "Equipment freight, both ways", 1, "lot", 3500, "air/road freight"),
 ("Consumables", "DECAMEX powder", 95, "kg", 12, "94.69 kg per campaign"),
 ("Site support", "Local helpers", 40, "h", LAB_CON, "2 people x 2 days x 10 h"),
 ("Site support", "Scaffold / access", 1, "lot", 2000, "rental"),
 ("Safety", "Permits, gas test, standby", 40, "h", LAB_OWN, "2 people x 2 days x 10 h"),
 ("Safety", "Waste collection and disposal", 1, "lot", 300, "local"),
]
CONT = 0.20   # Class 4 contingency
OWNER = 0.05  # owner's costs (project management, procurement)

def total(lines):
    return sum(q * r for _, _, q, _, r, _ in lines)

def build():
    s1_direct = total(S1); s1 = s1_direct * (1 + CONT + OWNER)
    s2_direct = total(S2); s2 = s2_direct * (1 + CONT + OWNER)
    camp = total(S2_CAMP) * (1 + CONT)
    # S1 annual OPEX
    s1_opex_lines = [
        ("Compressed air + collector power", 343.06 + 80, "kWh", KWH),
        ("Operator time, 2 people x 1 h x 24 events", 48, "h", LAB_OWN),
        ("Horn diaphragms and seals", 6, "pc", 300),
        ("Collector filters", 1, "set", 400),
        ("Annual inspection, specialist", 1, "day", 500),
        ("Coating renewal (re-spray once a year)", 1, "lot",
         250 * 4 + 200 * LAB_CON + 300 + 3 * 1300),
    ]
    s1_opex = sum(q * r for _, q, _, r in s1_opex_lines)
    s2_opex = 2 * camp
    return dict(s1_direct=s1_direct, s1=s1, s2_direct=s2_direct, s2=s2, camp=camp,
                s1_opex=s1_opex, s2_opex=s2_opex, s1_opex_lines=s1_opex_lines)

def econ(c0, opex, h2_t=95.81, margin=1.0, rate=0.10, years=5):
    cash = [-c0] + [h2_t * margin * 1000 - opex] * years
    npv = sum(c / (1 + rate) ** t for t, c in enumerate(cash))
    lo, hi = -0.99, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        v = sum(c / (1 + mid) ** t for t, c in enumerate(cash))
        lo, hi = (mid, hi) if v > 0 else (lo, mid)
    net = cash[1]
    disc, cum, dpb = 0, -c0, None
    for t in range(1, years + 1):
        prev = cum; cum += net / (1 + rate) ** t
        if cum >= 0 and dpb is None: dpb = t - 1 + (-prev) / (net / (1 + rate) ** t)
    hurdle = (opex + c0 / 3) / 1000 / margin
    return dict(npv=npv, irr=lo, payback=c0 / net, disc_payback=dpb, hurdle_t=hurdle)

if __name__ == "__main__":
    b = build()
    print("Rates:", {k: v for k, v in RATES.items()})
    for k in ("s1_direct", "s1", "s2_direct", "s2", "camp", "s1_opex", "s2_opex"):
        print(f"{k:10s} {b[k]:>10,.0f} USD")
    for nm, c0, op in (("S1", b["s1"], b["s1_opex"]), ("S2", b["s2"], b["s2_opex"])):
        e = econ(c0, op)
        print(nm, f"range {c0*0.7:,.0f}-{c0*1.5:,.0f}", {k: (round(v, 3) if v is not None else None) for k, v in e.items()})
    for m in (0.5, 1.0, 2.0):
        print("margin", m, "S1 payback", round(econ(b['s1'], b['s1_opex'], margin=m)['payback'], 2),
              "S2", round(econ(b['s2'], b['s2_opex'], margin=m)['payback'], 2))
