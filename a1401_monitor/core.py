"""Physics core of the A-1401 monitor (fast).

All heavy physics (Briggs & Young air side, fan/system curve, condensing tube side, zone rating) lives in
../model/a1401_model.py. Here we only interpolate a pre-computed grid of that model, so one year of hourly
data takes well under a second.

    T_out(T_in, T_amb, speed, phi, flow)  -> gas outlet temperature [C]
    invert_phi(...)                       -> equivalent blocked fraction that explains a measured outlet T
    max_flow(...)                         -> largest dry-gas flow the cooler can hold at the set point
"""
import os, json
import numpy as np
from scipy.interpolate import RegularGridInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
H2_FRAC, PSA_REC, RHO_H2 = 0.744, 0.796, 0.08988      # lab median, PFD back-calculation, kg/Nm3

class Physics:
    def __init__(self):
        p5 = os.path.join(HERE, "surrogate5d.json")
        p4 = os.path.join(HERE, "..", "monitor", "surrogate_Tout.json")
        if os.path.exists(p5):
            S = json.load(open(p5))
            g = np.array(S["T_out"]).reshape(len(S["TIN"]), len(S["TAMB"]), len(S["SPEED"]), len(S["PHI"]), len(S["FLOW"]))
            self.f = RegularGridInterpolator((S["TIN"], S["TAMB"], S["SPEED"], S["PHI"], S["FLOW"]), g, bounds_error=False, fill_value=None)
            self.has_flow = True; self.flow_range = (min(S["FLOW"]), max(S["FLOW"]))
        else:   # fallback grid without the flow dimension (flow fixed at 20,800 Nm3/h)
            S = json.load(open(p4))
            g = np.array(S["T_out"]).reshape(len(S["TIN"]), len(S["TAMB"]), len(S["SPEED"]), len(S["PHI"]))
            self.f = RegularGridInterpolator((S["TIN"], S["TAMB"], S["SPEED"], S["PHI"]), g, bounds_error=False, fill_value=None)
            self.has_flow = False; self.flow_range = (20800, 20800)
        self.phi_max = max(S["PHI"])

    def T_out(self, tin, tamb, sp, phi, flow):
        n = max(np.size(a) for a in (tin, tamb, sp, phi, flow))
        b = [np.broadcast_to(np.asarray(a, float), (n,)) for a in (tin, tamb, sp, phi, flow)]
        if self.has_flow:
            return self.f(np.column_stack(b))
        return self.f(np.column_stack(b[:4]))

    @staticmethod
    def _bisect(fun, lo, hi, n, it=32):
        lo = np.full(n, lo, float); hi = np.full(n, hi, float)
        for _ in range(it):
            mid = 0.5 * (lo + hi); up = fun(mid) > 0
            lo = np.where(up, lo, mid); hi = np.where(up, mid, hi)
        return 0.5 * (lo + hi)

    def invert_phi(self, tin, tamb, sp, tout, flow):
        """Health indicator: blockage that makes the model reproduce the measured outlet temperature."""
        n = len(np.atleast_1d(tout))
        return self._bisect(lambda p: self.T_out(tin, tamb, sp, p, flow) - tout, 0.0, self.phi_max, n)

    def controller_speed(self, tin, tamb, phi, flow, setpoint=65.0, smin=0.3):
        """Slowest fan speed that holds the set point (what TIC0055 / TY0055 does)."""
        n = max(np.size(a) for a in (tin, tamb, phi, flow))
        return self._bisect(lambda s: setpoint - self.T_out(tin, tamb, s, phi, flow), smin, 1.0, n)

    def max_flow(self, tin, tamb, phi, setpoint=65.0):
        """Largest dry-gas flow held at the set point with fans at 100 % (needs the 5-D grid)."""
        n = max(np.size(a) for a in (tin, tamb, phi))
        lo, hi = self.flow_range
        return self._bisect(lambda q: self.T_out(tin, tamb, 1.0, phi, q) - setpoint, lo, hi, n)

def h2_t_per_h(lost_flow_nm3h):
    return np.asarray(lost_flow_nm3h) * H2_FRAC * PSA_REC * RHO_H2 / 1000.0
