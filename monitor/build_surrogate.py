"""Fast lookup table of the physics model: outlet T for any (inlet T, air T, fan speed, blockage).
The full model takes ~1 s per case; the synthetic-year backtest needs thousands of cases, so we
pre-compute a grid once (~10-25 min) and interpolate. Flow fixed at 20,800 Nm3/h (14 Nov)."""
import os, sys, json, itertools, numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import a1401_model as m
TIN = [140, 155, 170]; TAMB = [-25, -15, -5, 5, 15, 25, 35, 45]; SPEED = [0.3, 0.5, 0.7, 0.85, 1.0]
PHI = [0, .1, .2, .3, .4, .5, .6, .7, .8]; FLOW = 20800
def run(c):
    return float(m.predict(c[0], FLOW, c[1], c[2], c[3])[0])
if __name__ == "__main__":
    cases = list(itertools.product(TIN, TAMB, SPEED, PHI))
    with Pool(os.cpu_count()) as p:
        out = p.map(run, cases, chunksize=4)
    json.dump(dict(TIN=TIN, TAMB=TAMB, SPEED=SPEED, PHI=PHI, FLOW=FLOW, T_out=out),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "surrogate_Tout.json"), "w"))
    print("done", len(out))
