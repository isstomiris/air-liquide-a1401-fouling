"""
A-1401 economics re-run for Atyrau, Kazakhstan, with S1 changed to an IN-SITU SPRAY coating made from low-cost
local feedstock (bio-based or mine-tailing silica). No bundle removal, no workshop oven, cure at ambient /
low temperature (must stay below the 170 C design wall temperature).

ALL VALUES ARE TEAM PLANNING ALLOWANCES (USD thousand, low / base / high), not quotes. Local rates used:
  loaded labour, Atyrau technician      8 / 12 / 18 USD per person-hour   (assumption; check with plant HR)
  industrial electricity, Kazakhstan    0.05 / 0.07 / 0.09 USD/kWh       (assumption, ~25-45 KZT/kWh at ~500 KZT/USD)
  H2 contribution margin                0.5 / 1.0 / 2.0 USD/kg           (unchanged from the technoeconomic file)
Benefit basis: the technoeconomic file's illustrative central case, 3,000 Nm3/h x 600 h x 0.053229 kg/Nm3 = 95.81 t/yr.
"""
K = 0.744 * 0.796 * 0.08988
H2_T = 3000 * 600 * K / 1000           # 95.81 t/yr illustrative
CASES = ("low", "base", "high")
S1_CAPEX = {  # k USD
    "Engineering, design, MOC (local institute)": (5, 10, 20),
    "3 sonic horns + regulators/valves (imported)": (12, 18, 30),
    "Collector, hood, skirts (local fabrication)": (5, 10, 20),
    "Controls and electrical (local)": (3, 6, 12),
    "First spray coating in situ: material, access, labour": (3, 6, 12),
    "Installation and commissioning (local crew)": (4, 8, 16),
}
S1_QUAL = (5, 10, 20)                    # bench tests with a local university lab: adhesion, 60-170 C ageing, fluff
CONT = 0.25
LAB = (8, 12, 18); KWH = (0.05, 0.07, 0.09); EVENTS = (12, 24, 52)
RESPRAY = (2, 5, 10); RESPRAY_EVERY = (2, 1, 0.5)       # k USD per in-situ re-spray, years between
HORN_MAINT = (1.5, 3, 6)
S2_READY = (3, 6, 12)
S2_CAMP = {"Vendor service, powder, crew": (4, 9, 18), "Mobilisation to Atyrau": (2, 4, 10),
           "Local access, collection, waste": (0.5, 1, 2.5), "Local site liaison, contingency": (0.5, 1, 2.5)}
CAMPS = (1, 2, 4)


def run():
    out = {}
    for i, c in enumerate(CASES):
        sub = sum(v[i] for v in S1_CAPEX.values())
        s1_c0 = sub * (1 + CONT) + S1_QUAL[i]
        s1_opex = (2 * EVENTS[i] * LAB[i] / 1000 + HORN_MAINT[i] + RESPRAY[i] / RESPRAY_EVERY[i]
                   + 343.06 * KWH[i] / 1000)
        camp = sum(v[i] for v in S2_CAMP.values())
        s2_c0, s2_opex = S2_READY[i], camp * CAMPS[i]
        out[c] = dict(s1_sub=sub, s1_c0=s1_c0, s1_opex=s1_opex, s2_c0=s2_c0, s2_camp=camp, s2_opex=s2_opex)
    b = out["base"]
    print("case  S1 initial  S1 OPEX/yr   S2 readiness  S2 per campaign  S2 OPEX/yr   (k USD)")
    for c, v in out.items():
        print(f"{c:5s} {v['s1_c0']:9.1f} {v['s1_opex']:10.1f} {v['s2_c0']:12.1f} {v['s2_camp']:14.1f} {v['s2_opex']:11.1f}")
    print(f"\nIllustrative benefit {H2_T:.2f} t H2/yr (base costs)")
    for m in (0.5, 1.0, 2.0):
        g = H2_T * m
        n1, n2 = g - b["s1_opex"], g - b["s2_opex"]
        print(f"margin {m}: S1 net {n1:6.1f} payback {b['s1_c0']/n1:5.2f} yr | S2 net {n2:6.1f} payback {b['s2_c0']/n2:5.2f} yr")
    for lab, c0, op in (("S1", b["s1_c0"], b["s1_opex"]), ("S2", b["s2_c0"], b["s2_opex"])):
        print(f"{lab}: H2 needed for 3-yr payback at 1 USD/kg = {op + c0/3:.1f} t/yr")
    af = sum(1 / 1.1 ** y for y in range(1, 6))
    for lab, c0, op in (("S1", b["s1_c0"], b["s1_opex"]), ("S2", b["s2_c0"], b["s2_opex"])):
        print(f"{lab}: 5-yr NPV at 10 %, 1 USD/kg = {-c0 + (H2_T - op) * af:.0f} k USD")
    return out


if __name__ == "__main__":
    run()
