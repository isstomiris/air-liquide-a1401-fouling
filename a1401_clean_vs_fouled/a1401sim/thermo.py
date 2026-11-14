"""
Wet-syngas thermodynamics on a per-mole-of-dry-gas basis.

Model (stated simply):
  * The dry gas (H2, CO2, CH4, CO, N2) is an ideal-gas mixture: h_dry(T) = sum y_i h_i0(T).
    Ideal-gas enthalpies from CoolProp (CP0MOLAR integrated).  The real-gas departure of the
    dry gas at 27.5 bar is checked separately in verify.py and is < 1 % of the duty.
  * Water is the only condensable component.  If the total water exceeds what the gas can hold,
    the vapour is saturated:  y_w = f * p_sat(T) / P      (Raoult/Dalton, f = enhancement factor)
    n_vap = min(W, y_w/(1-y_w)) per mol dry gas,   n_liq = W - n_vap
  * Water vapour enthalpy = saturated vapour enthalpy at T; liquid = saturated liquid at T
    (IAPWS-95 via CoolProp).  Latent heat therefore = h_v(T) - h_l(T), counted exactly once.
  * Dissolution of CO2/H2 in the condensate is neglected (heat of solution << latent heat).
Total stream enthalpy H(T) per mol dry gas is tabulated on a fine grid so the exchanger model can
convert enthalpy <-> temperature by interpolation.
"""
import numpy as np
from CoolProp.CoolProp import PropsSI
from . import config as C

MW = {"Hydrogen": 2.016, "CarbonDioxide": 44.01, "Methane": 16.043, "CarbonMonoxide": 28.01,
      "Nitrogen": 28.014, "Water": 18.015}
T_REF = 273.15


def mw_dry(comp=None):
    comp = comp or C.DRY_COMPOSITION
    return sum(x * MW[k] for k, x in comp.items())


def nm3h_to_mol_s(nm3h):
    """dry-gas normal flow (0 C, 1.01325 bar) to mol/s"""
    return nm3h / 22.414 / 3.6


def psat(T):
    return PropsSI("P", "T", T, "Q", 0, "Water")


def saturation_ratio(T, P=C.P_PROCESS, f=C.ENHANCEMENT_FACTOR):
    """mol water vapour per mol dry gas in saturated gas at T"""
    y = min(f * psat(T) / P, 0.999)
    return y / (1 - y)


def dew_point(W, P=C.P_PROCESS, f=C.ENHANCEMENT_FACTOR):
    """temperature (K) at which a gas with W mol water / mol dry gas starts to condense"""
    y = W / (1 + W)
    return PropsSI("T", "P", y * P / f, "Q", 1, "Water")


class WetSyngas:
    """Enthalpy table and phase split for one water loading W (mol H2O / mol dry gas)."""

    def __init__(self, W=C.WATER_TO_DRY_BASE, comp=None, P=C.P_PROCESS, f=C.ENHANCEMENT_FACTOR,
                 T_lo=273.16, T_hi=500.0, dT=C.T_GRID_STEP):
        self.W, self.P, self.f = W, P, f
        self.comp = comp or C.DRY_COMPOSITION
        self.T = np.arange(T_lo, T_hi, dT)
        # dry-gas ideal-gas Cp on a coarse grid, then integrated on the fine grid
        Tc = np.linspace(T_lo, T_hi, 60)
        cpc = np.array([sum(x * PropsSI("CP0MOLAR", "T", t, "P", 1e5, k) for k, x in self.comp.items()) for t in Tc])
        self.cp_dry = np.interp(self.T, Tc, cpc)                       # J/mol/K
        h_dry = np.concatenate([[0.0], np.cumsum(0.5 * (self.cp_dry[1:] + self.cp_dry[:-1]) * np.diff(self.T))])
        self.h_dry = h_dry - np.interp(T_REF, self.T, h_dry)            # J/mol dry, ref 0 C
        # water: saturation and saturated-phase enthalpies (coarse grid, interpolated)
        Tw = np.linspace(T_lo, min(T_hi, 640.0), 300)
        ps = np.array([psat(t) for t in Tw])
        hv = np.array([PropsSI("H", "T", t, "Q", 1, "Water") for t in Tw]) * MW["Water"] / 1000
        hl = np.array([PropsSI("H", "T", t, "Q", 0, "Water") for t in Tw]) * MW["Water"] / 1000
        self.hv = np.interp(self.T, Tw, hv)                            # J/mol water
        self.hl = np.interp(self.T, Tw, hl)
        y = np.minimum(f * np.interp(self.T, Tw, ps) / P, 0.999)
        self.n_v = np.minimum(W, y / (1 - y))                          # mol vapour / mol dry
        self.n_l = W - self.n_v
        self.H = self.h_dry + self.n_v * self.hv + self.n_l * self.hl  # J/mol dry gas
        assert np.all(np.diff(self.H) > 0), "enthalpy must increase with T"
        self._tr = None

    def transport(self, T):
        """gas-phase viscosity and conductivity at T (tabulated once per water loading)"""
        if self._tr is None:
            Tt = np.linspace(274.0, 480.0, 22)
            vals = []
            for t in Tt:
                nv = float(self.vapour(t)); yw = nv / (1 + nv)
                vals.append(gas_transport(t, 1 - yw, yw, self.comp))
            self._tr = (Tt, np.array(vals))
        Tt, v = self._tr
        return float(np.interp(T, Tt, v[:, 0])), float(np.interp(T, Tt, v[:, 1]))

    # conversions -------------------------------------------------------------
    def H_of_T(self, T):
        return np.interp(T, self.T, self.H)

    def T_of_H(self, H):
        return np.interp(H, self.H, self.T)

    def vapour(self, T):
        return np.interp(T, self.T, self.n_v)

    def liquid(self, T):
        return np.interp(T, self.T, self.n_l)

    def dew_point(self):
        return dew_point(self.W, self.P, self.f)

    def gas_fraction_of_dH(self, T):
        """Z = (sensible heat of the gas phase) / (total dH) for a small cooling step at T.
        Used by the Silver-Bell-Ghaly tube-side method."""
        cp_eff = np.gradient(self.H, self.T)
        cp_gas = self.cp_dry + self.n_v * np.gradient(self.hv, self.T)
        return np.interp(T, self.T, np.clip(cp_gas / cp_eff, 0.02, 1.0))

    # duty decomposition --------------------------------------------------------
    def breakdown(self, T_in, T_out, n_dry, steps=400):
        """Exact split of the duty (W) between T_in and T_out (K) for n_dry mol/s.
        Each small step dH = d(dry) + vapour sensible + liquid sensible + latent, with the
        latent part = moles condensed in the step x [h_v - h_l] at the step's upper temperature."""
        Ts = np.linspace(T_in, T_out, steps + 1)
        hd, hv, hl = (np.interp(Ts, self.T, a) for a in (self.h_dry, self.hv, self.hl))
        nv, nl = self.vapour(Ts), self.liquid(Ts)
        dry = hd[0] - hd[-1]
        vap_s = np.sum(nv[1:] * (hv[:-1] - hv[1:]))
        liq_s = np.sum(nl[:-1] * (hl[:-1] - hl[1:]))
        dn = nv[:-1] - nv[1:]
        lat = np.sum(dn * (hv[:-1] - hl[:-1]))
        liq_s += np.sum(dn * (hl[:-1] - hl[1:]))      # condensate formed in-step, cooled to step end
        total = self.H_of_T(T_in) - self.H_of_T(T_out)
        f = n_dry
        return dict(total_W=f * total, dry_gas_sensible_W=f * dry, water_vapour_sensible_W=f * vap_s,
                    condensate_sensible_W=f * liq_s, latent_W=f * lat,
                    closure_W=f * (total - dry - vap_s - liq_s - lat),
                    vapour_in_kg_h=f * nv[0] * MW["Water"] * 3.6, vapour_out_kg_h=f * nv[-1] * MW["Water"] * 3.6,
                    liquid_in_kg_h=f * nl[0] * MW["Water"] * 3.6, liquid_out_kg_h=f * nl[-1] * MW["Water"] * 3.6,
                    condensed_kg_h=f * (nv[0] - nv[-1]) * MW["Water"] * 3.6)


# ----------------------------------------------------------------- transport properties
def gas_transport(T, y_dry_frac, y_w, comp=None):
    """viscosity (Pa s) and conductivity (W/m/K) of the gas phase, Wilke / Mason-Saxena mixing
    of pure-component low-pressure values from CoolProp."""
    comp = comp or C.DRY_COMPOSITION
    names = list(comp) + ["Water"]
    y = np.array([comp[k] * y_dry_frac for k in comp] + [y_w])
    y = y / y.sum()
    mu, k, M = [], [], []
    for nm in names:
        p = 1e5 if nm != "Water" else min(0.9 * psat(T), 1e5) if T < 373.15 else 1e5
        src = "Nitrogen" if nm == "CarbonMonoxide" else nm      # CoolProp has no CO transport model; CO ~ N2 (same M, similar sigma)
        mu.append(PropsSI("V", "T", T, "P", p, src)); k.append(PropsSI("L", "T", T, "P", p, src)); M.append(MW[nm])
    mu, k, M = map(np.array, (mu, k, M))
    phi = np.array([[(1 + (mu[i] / mu[j]) ** 0.5 * (M[j] / M[i]) ** 0.25) ** 2 / (8 * (1 + M[i] / M[j])) ** 0.5
                     for j in range(len(M))] for i in range(len(M))])
    den = phi @ y
    return float(np.sum(y * mu / den)), float(np.sum(y * k / den))
