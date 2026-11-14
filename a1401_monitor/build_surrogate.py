"""One-off: pre-compute the physics model on a 5-D grid (inlet T, air T, fan speed, blockage, gas flow)
so the monitor can evaluate thousands of hours in seconds. ~3,200 cases, ~30 min on 4 cores."""
import os, sys, json, itertools
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model"))
import a1401_model as m
TIN = [135, 150, 165, 175]; TAMB = [-25, -15, -5, 5, 15, 25, 35, 45]; SPEED = [0.3, 0.5, 0.7, 0.85, 1.0]
PHI = [0, .1, .2, .3, .4, .5, .6, .7, .8]; FLOW = [15000, 21000, 27000]
def run(c):
    return float(m.predict(c[0], c[4], c[1], c[2], c[3])[0])
if __name__ == "__main__":
    cases = list(itertools.product(TIN, TAMB, SPEED, PHI, FLOW))
    with Pool(os.cpu_count()) as p:
        out = p.map(run, cases, chunksize=8)
    json.dump(dict(TIN=TIN, TAMB=TAMB, SPEED=SPEED, PHI=PHI, FLOW=FLOW, T_out=out), open(os.path.join(HERE, "surrogate5d.json"), "w"))
    print("done", len(out))
