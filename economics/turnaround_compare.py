"""Turnaround (shutdown) wash vs S1/S2, bottom-up at the same Atyrau unit rates as estimate_class4.py."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from estimate_class4 import LAB_CON, LAB_OWN, ENG, build
TAR = [("Wash crew 4 x 3 days x 10 h", 120, LAB_CON), ("Scaffold / access, 3 bays", 3, 1300),
       ("HP water unit rental", 3, 250), ("Water, m3", 60, 1.5), ("Effluent disposal", 1, 800),
       ("Inspection, engineer h", 16, ENG), ("Fin combing / repair", 1, 1000), ("Permits, standby h", 60, LAB_OWN)]
H2_RATE, MARGIN, YEARS = 1107, 1.0, 5
wash = sum(q * r for _, q, r in TAR) * 1.20
lost3 = H2_RATE * 24 * 3 * MARGIN
b = build()
cases = {"Turnaround wash": wash * YEARS, "S1 spray + horns": b["s1"] + YEARS * b["s1_opex"],
         "S2 DECAMEX": b["s2"] + YEARS * b["s2_opex"], "Wash + extra 3-day stop": (wash + lost3) * YEARS}
if __name__ == "__main__":
    for n, q, r in TAR: print(f"{n:32s} {q*r:8,.0f}")
    print(f"Wash per event incl. 20 % contingency: {wash:,.0f}; lost H2 per 3-day stop: {lost3:,.0f} USD ({H2_RATE*72/1000:.1f} t)")
    for k, v in cases.items(): print(f"{k:26s} 5-yr {v:10,.0f}  range {v*0.7:,.0f}-{v*1.5:,.0f}")
