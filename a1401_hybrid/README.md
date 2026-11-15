# A-1401 hybrid cleaning strategies

Season replay (incl. combinations of sonic horns, DECAMEX and the turnaround clean; not used in the deck) on the same
wet model as `a1401_solutions_check/`, plus quick economics and the decision matrix used in the deck.

Run in order (needs the packages of `a1401_clean_vs_fouled/` and matplotlib):

    python simulate_hybrid.py     # results/hybrid_scenarios.csv, hybrid_traces.json, capacity_curve_65C.csv
    python economics.py           # results/economics.csv
    python decision_matrix.py     # results/decision_matrix.csv
    python figures.py             # figures/h1..h4

Key assumptions (all stated in the script headers):
* Three-pool debris model: horns reach 50 % of each new deposit, DECAMEX 90 %, 10 % is reached by neither.
* Turnaround clean on 27 Jun removes all seasonal debris; base falls to the measured 2026 level 0.574.
* Deep clean: share of the 0.594 base removed is a WHAT-IF (5-100 %), to be settled by inspection.
* Extra gas only in hours with no-action outlet > 65 C, capped at the cool-weather median flow 25,052 Nm3/h.
* Costs are team order-of-magnitude estimates (low / central / high), not vendor quotes.
