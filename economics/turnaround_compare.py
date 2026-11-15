"""Turnaround (shutdown) cleaning vs S1/S2, team estimates at Atyrau rates (USD thousand, low/base/high).
The case files give no cleaning prices; all values are planning allowances, not quotes."""
H2_RATE = 1107  # kg H2/h, plant rate used in the technoeconomic file (5-day stop = 133 t)
MARGIN = 1.0    # USD/kg contribution margin (central case)
YEARS = 5
# direct cost of one shutdown wash: crew 4-6 people x 2-4 days at 8-18 USD/h, scaffold/access,
# high-pressure water unit, water + effluent, fan isolation, inspection, fin straightening
TAR_DIRECT = {"Crew (4-6 people, 2-4 days)": (1, 2.5, 6), "Scaffold and access": (2, 4, 8),
              "HP water unit, water, effluent": (1.5, 3, 6), "Isolation, inspection, fin repair": (1.5, 2.5, 5)}
DAYS = (1, 3, 5)  # extra outage days if the wash needs its own shutdown
direct = [round(sum(v[i] for v in TAR_DIRECT.values()), 1) for i in range(3)]
lost = [round(H2_RATE * 24 * d * MARGIN / 1000, 1) for d in DAYS]
print("TAR wash direct cost per event:", direct)
print("Lost H2 value for an extra stop (k USD):", lost, " t H2:", [round(H2_RATE*24*d/1000) for d in DAYS])
cases = {
    "Wash in a planned turnaround": [direct[i] * YEARS for i in range(3)],
    "Wash in an extra shutdown": [(direct[i] + lost[i]) * YEARS for i in range(3)],
    "S2 DECAMEX, online": [c0 + op * YEARS for c0, op in zip((3, 6, 12), (7, 30, 132))],
    "S1 spray coating + horns": [c0 + op * YEARS for c0, op in zip((45, 82.5, 157.5), (2.7, 8.6, 27.9))],
}
for k, v in cases.items():
    print(f"{k:32s} 5-yr cost, k USD: " + " / ".join(f"{x:.0f}" for x in v))
