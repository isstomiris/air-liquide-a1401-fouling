"""
Geometry, air-side heat transfer, bundle pressure drop and fan operating point.

Blockage model (input b = fraction of the air passages that is closed by debris):
  * Air passes only through the open fraction (1-b): local velocity in the open passages = V/(1-b).
  * Only the open fraction of the finned surface exchanges heat:  A_active = (1-b) A.
    (The blocked surface carries no air.  This is NOT applied a second time to h: h is computed
     at the higher local velocity of the open passages, which partly compensates.)
  * Bundle pressure drop (Robinson & Briggs):  dP_bundle ~ (V/(1-b))^1.684 at a given total flow.
  * Fan: generic axial curve through the datasheet point; the airflow is where fan and
    system curves cross.  So 30 % blocked area does NOT mean 30 % less air.
"""
import math
import numpy as np
from scipy.optimize import brentq
from . import config as C

# ------------------------------------------------------------------ geometry
G = dict(C.GEOMETRY)
G["Di"] = G["Do"] - 2 * G["t_wall"]
G["tubes_per_row"] = G["n_tubes"] // G["rows"]
G["L_tot"] = G["n_tubes"] * G["L"]
_fin_area_each = 2 * math.pi / 4 * (G["Df"] ** 2 - G["Do"] ** 2) + math.pi * G["Df"] * G["tf"]
G["A_fin"] = G["fins_per_m"] * _fin_area_each * G["L_tot"]
G["A_root"] = math.pi * G["Do"] * (1 - G["fins_per_m"] * G["tf"]) * G["L_tot"]
G["A_ext"] = G["A_fin"] + G["A_root"]
G["A_bare"] = math.pi * G["Do"] * G["L_tot"]
G["A_in"] = math.pi * G["Di"] * G["L_tot"]
G["A_face"] = G["tubes_per_row"] * G["St"] * G["L"]
G["s_fin"] = 1 / G["fins_per_m"] - G["tf"]                     # clear gap between fins
G["l_fin"] = (G["Df"] - G["Do"]) / 2
G["A_min_per_face"] = (G["St"] - G["Do"] - 2 * G["l_fin"] * G["tf"] * G["fins_per_m"]) / G["St"]
G["Sd"] = math.hypot(G["St"] / 2, G["Sl"])


def air_props(T):
    """dry air at site pressure: density, viscosity (Sutherland), conductivity, cp"""
    rho = C.P_ATM / (287.05 * T)
    mu = 1.458e-6 * T ** 1.5 / (T + 110.4)
    k = 2.646e-3 * T ** 1.5 / (T + 245.4 * 10 ** (-12 / T))
    return rho, mu, k, 1006.0


# ------------------------------------------------------------------ heat transfer
def h_air(V_face, T, b=0.0, mult=None):
    """Briggs & Young (1963), staggered helically finned tubes. V_face in m/s over the whole face."""
    mult = C.H_AIR_MULT if mult is None else mult
    rho, mu, k, cp = air_props(T)
    V_max = V_face / G["A_min_per_face"] / (1 - b)
    Re = rho * V_max * G["Do"] / mu
    Pr = cp * mu / k
    Nu = 0.134 * Re ** 0.681 * Pr ** (1 / 3) * (G["s_fin"] / G["l_fin"]) ** 0.2 * (G["s_fin"] / G["tf"]) ** 0.1134
    return mult * Nu * k / G["Do"], Re, V_max


def fin_efficiency(h):
    """annular fin of constant thickness, Schmidt (1949) approximation"""
    ro, re = G["Do"] / 2, G["Df"] / 2
    m = math.sqrt(2 * h / (G["k_fin"] * G["tf"]))
    phi = (re / ro - 1) * (1 + 0.35 * math.log(re / ro))
    x = m * ro * phi
    return math.tanh(x) / x


def UA_air(Q_m3s, T_air_mean, b=0.0, mult=None):
    """air-side conductance of the whole bundle (W/K) and the intermediate values"""
    V_face = Q_m3s / G["A_face"]
    h, Re, Vmax = h_air(V_face, T_air_mean, b, mult)
    eta_f = fin_efficiency(h)
    eta_o = 1 - G["A_fin"] / G["A_ext"] * (1 - eta_f)
    UA = h * eta_o * G["A_ext"] * (1 - b)
    return UA, dict(V_face=V_face, V_max=Vmax, Re_air=Re, h_air=h, eta_fin=eta_f, eta_surface=eta_o,
                    A_active=G["A_ext"] * (1 - b))


# ------------------------------------------------------------------ pressure drop and fan
def dP_bundle_RB(Q_m3s, T=293.15, b=0.0):
    """Robinson & Briggs (1966) friction for staggered high-fin tubes, 6 rows (Pa)."""
    rho, mu, k, cp = air_props(T)
    V_max = Q_m3s / G["A_face"] / G["A_min_per_face"] / (1 - b)
    Gm = rho * V_max
    Re = Gm * G["Do"] / mu
    f = 18.93 * Re ** -0.316 * (G["St"] / G["Do"]) ** -0.927 * (G["St"] / G["Sd"]) ** 0.515
    return 2 * f * G["rows"] * Gm ** 2 / rho


Q_RATED = C.FAN["n_fans"] * C.FAN["Q_rated_m3h"] / 3600.0          # m3/s, all fans
DP_BUNDLE_RB_RATED = dP_bundle_RB(Q_RATED, 293.15)              # Pa, independent geometric estimate
# Share of the rated 190 Pa TOTAL pressure that is lost in the bundle:
#   190 Pa - fan velocity pressure (0.5 rho V^2 at the 2.4 m fan ring) - ~10 Pa inlet/plenum losses
_V_ring = C.FAN["Q_rated_m3h"] / 3600 / (math.pi / 4 * C.FAN["D"] ** 2)
FAN_VELOCITY_PRESSURE = 0.5 * 1.2 * _V_ring ** 2
BUNDLE_SHARE = (C.FAN["dP_rated_total"] - FAN_VELOCITY_PRESSURE - 10.0) / C.FAN["dP_rated_total"] \
    if C.SYSTEM_SHARE_OTHER is None else 1 - C.SYSTEM_SHARE_OTHER


def airflow(speed=1.0, b=0.0, bundle_share=None, a=None, bcoef=None):
    """Volumetric airflow (m3/s at fan conditions) from fan curve = system curve.
       fan:     dP/dP_r = a n^2 - c q^2              (a - c = 1, passes through rated point)
       system:  dP/dP_r = (1-s) q^2 + s [q/(1-b)]^1.684
    Air density scales both curves equally, so q does not depend on air temperature."""
    s = BUNDLE_SHARE if bundle_share is None else bundle_share
    a = C.FAN["a"] if a is None else a
    c = C.FAN["b"] if bcoef is None else bcoef
    e = C.RB_EXPONENT

    def res(q):
        return a * speed ** 2 - c * q ** 2 - ((1 - s) * q ** 2 + s * (q / (1 - b)) ** e)
    q = brentq(res, 1e-6, 3 * speed + 1e-3)
    dP = C.FAN["dP_rated_total"] * (a * speed ** 2 - c * q ** 2)
    return Q_RATED * q, dict(q_frac=q, fan_dP_Pa=dP,
                             fan_power_kW_each=Q_RATED * q * dP / C.FAN["eta_total"] / 1000 / C.FAN["n_fans"])
