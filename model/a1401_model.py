"""
A-1401 raw-hydrogen air cooler: thermal + air-side model (clean vs debris-fouled).

Plain-language map of the code:
  1. GEOMETRY      - tube and fin dimensions back-calculated from the datasheet areas
  2. PROCESS SIDE  - how much heat the wet syngas releases between two temperatures
                     (gas cooling + water condensing + liquid water cooling)
  3. AIR SIDE      - fan + pressure-drop balance -> how much air flows;
                     Briggs & Young correlation -> air heat-transfer coefficient;
                     annular-fin efficiency (Schmidt approximation)
  4. TUBE SIDE     - gas-film coefficient (Gnielinski) corrected for condensation
                     in the presence of non-condensable gas (Silver-Bell-Ghaly)
  5. RATING        - incremental (zone) method: march along the cooling curve,
                     add up the exchanger area each slice needs
  6. FOULING       - blocked fin-gap fraction phi (less air, less active surface)
                     + debris thermal resistance R_d
All units SI unless stated. Every assumption is tagged [A#] = section 8 of the plan.
"""
import math
import numpy as np
from CoolProp.CoolProp import PropsSI

R_GAS = 8.314
P_ATM = 101_700.0          # Pa, Atyrau is ~20 m below sea level

# ---------------------------------------------------------------- 1. GEOMETRY
GEO = dict(
    Do=0.025, Di=0.021,     # tube OD/ID (datasheet: 25 x 2.0, 304L)
    Df=0.057, tf=0.0004,    # fin OD, fin thickness [A12]
    nf=423.0,               # fins per metre, solved so fin area = 5,288 m2 (datasheet)
    St=0.064, Sl=0.0554,    # transverse / longitudinal pitch, equilateral triangle [A12]
    rows=6, tubes_per_row=46, L=10.42, passes=2,
    k_fin=205.0,            # aluminium fins
    k_wall=16.0,            # 304L stainless
)
g = GEO
g["Nt"] = g["rows"] * g["tubes_per_row"]                       # 276 tubes
g["Ltot"] = g["Nt"] * g["L"]                                   # m of tube
_fin_area_per_fin = 2 * math.pi / 4 * (g["Df"]**2 - g["Do"]**2) + math.pi * g["Df"] * g["tf"]
_base_exposed = math.pi * g["Do"] * (1 - g["nf"] * g["tf"])
g["A_fin"] = g["nf"] * _fin_area_per_fin * g["Ltot"]
g["A_tot"] = g["A_fin"] + _base_exposed * g["Ltot"]            # ~5,290 m2 (datasheet 5,288)
g["A_bare"] = math.pi * g["Do"] * g["Ltot"]                    # ~226 m2 (datasheet 226)
g["A_in"] = math.pi * g["Di"] * g["Ltot"]
g["A_face"] = g["tubes_per_row"] * g["St"] * g["L"]
g["s_gap"] = 1 / g["nf"] - g["tf"]                             # clear gap between fins (~2 mm)
g["l_fin"] = (g["Df"] - g["Do"]) / 2
# free-flow fraction at the minimum cross-section of one row
g["sigma"] = (g["St"] - g["Do"] - (g["Df"] - g["Do"]) * g["tf"] * g["nf"]) / g["St"]

# ---------------------------------------------------------------- 2. PROCESS SIDE
DRY = {"Hydrogen": 0.744, "CarbonDioxide": 0.179, "Methane": 0.0496, "CarbonMonoxide": 0.0225, "Nitrogen": 0.006}  # [A5] lab medians (CH4 median 4.96, audit L2)
_s = sum(DRY.values()); DRY = {k: v / _s for k, v in DRY.items()}
MW = {"Hydrogen": 2.016, "CarbonDioxide": 44.01, "Methane": 16.04, "CarbonMonoxide": 28.01, "Nitrogen": 28.01, "Water": 18.015}
MW_DRY = sum(DRY[k] * MW[k] for k in DRY)
WATER_TO_DRY = 510.0 / 919.0     # total water (vapour + liquid) per mol dry gas, steam balance [A6]
P_PROC = 2.65e6 + P_ATM          # Pa abs, between 2.69 (inlet) and 2.56 (D-1403) MPa(g)


def nm3h_to_mols(nm3h):
    return nm3h / 22.414 / 3.6   # mol/s (Nm3 at 0 C, 1 atm)


_cp_cache = {}
def cp_dry_molar(T):
    """ideal-gas molar Cp of the dry syngas, J/mol/K"""
    key = round(T, 0)
    if key not in _cp_cache:
        _cp_cache[key] = sum(x * PropsSI("CP0MOLAR", "T", key, "P", 1e5, f) for f, x in DRY.items())
    return _cp_cache[key]


def psat(T):
    return PropsSI("P", "T", T, "Q", 0, "Water")


def water_split(T, n_dry, P=P_PROC):
    """mol/s of water vapour and liquid at T (gas saturated, liquid present)"""
    n_wt = WATER_TO_DRY * n_dry
    y = min(psat(T) / P, 0.999)
    n_v = min(n_wt, n_dry * y / (1 - y))
    return n_v, n_wt - n_v


def H_process(T, n_dry, Tref=273.15):
    """enthalpy flow (W) of the wet syngas at temperature T (K), relative to Tref"""
    # dry gas sensible
    Ts = np.linspace(Tref, T, 12)
    h_dry = n_dry * np.trapezoid([cp_dry_molar(t) for t in Ts], Ts)
    n_v, n_l = water_split(T, n_dry)
    hv = PropsSI("H", "T", T, "Q", 1, "Water") * MW["Water"] / 1000   # J/mol
    hl = PropsSI("H", "T", T, "Q", 0, "Water") * MW["Water"] / 1000
    return h_dry + n_v * hv + n_l * hl


def duty(T_in_C, T_out_C, flow_nm3h):
    n = nm3h_to_mols(flow_nm3h)
    return H_process(T_in_C + 273.15, n) - H_process(T_out_C + 273.15, n)


def duty_breakdown(T_in_C, T_out_C, flow_nm3h):
    n = nm3h_to_mols(flow_nm3h)
    Ti, To = T_in_C + 273.15, T_out_C + 273.15
    Ts = np.linspace(To, Ti, 12)
    q_gas = n * np.trapezoid([cp_dry_molar(t) for t in Ts], Ts)
    nv_i, nl_i = water_split(Ti, n); nv_o, nl_o = water_split(To, n)
    cond = nv_i - nv_o
    q_lat = cond * np.mean([PropsSI("H", "T", t, "Q", 1, "Water") - PropsSI("H", "T", t, "Q", 0, "Water") for t in (Ti, To)]) * MW["Water"] / 1000
    q_tot = duty(T_in_C, T_out_C, flow_nm3h)
    return dict(total=q_tot, gas_sensible=q_gas, latent=q_lat, other_water_sensible=q_tot - q_gas - q_lat,
                condensed_kg_h=cond * MW["Water"] * 3.6, vapour_in_kg_h=nv_i * MW["Water"] * 3.6,
                vapour_out_kg_h=nv_o * MW["Water"] * 3.6, dew_point_C=dew_point_C(n))


def dew_point_C(n_dry):
    """temperature at which ALL water would be vapour (above it the gas is dry)"""
    n_wt = WATER_TO_DRY * n_dry
    y = n_wt / (n_wt + n_dry)
    return PropsSI("T", "P", y * P_PROC, "Q", 1, "Water") - 273.15


# ---------------------------------------------------------------- 3. AIR SIDE
FAN = dict(Q_design=3 * 114_000 / 3600, dP_design=190.0, a=1.6, b=0.6, eta=0.65)   # [A3]
H_MULT = 1.0      # multiplier on the air-side correlation (Briggs & Young is good to about +/-20 %)
SYS_OTHER = 0.25   # share of the 190 Pa that is NOT the bundle (inlet, plenum, fan ring) [A3]


def air_props(T):
    rho = P_ATM / (287.05 * T)
    mu = 1.458e-6 * T**1.5 / (T + 110.4)
    k = 2.646e-3 * T**1.5 / (T + 245.4 * 10**(-12 / T))
    cp = 1006.0
    return rho, mu, k, cp


def fan_flow_ratio(speed, phi=0.0, k_extra=0.0):
    """
    Volumetric airflow as a fraction of design, from fan curve = system curve.
      fan:    dP = Pd (a n^2 - b q^2)              (generic axial curve, fan laws)
      system: dP = Pd (s_other + s_bundle * kb) q^2
      fouled bundle: open area x (1 - phi) -> local velocity / (1 - phi)
                     -> bundle dP x (1 - phi)^-1.684  (Robinson-Briggs velocity exponent)
      k_extra: extra resistance (e.g. a screen) as a fraction of design dP
    Air density cancels (both curves scale with rho), so q does not depend on T_amb.
    """
    kb = (1 - phi) ** -1.684
    s = SYS_OTHER + (1 - SYS_OTHER) * kb + k_extra
    return speed * math.sqrt(FAN["a"] / (s + FAN["b"])) * math.sqrt((1 + FAN["b"]) / FAN["a"]) if FAN.get("normalise") else speed * math.sqrt(FAN["a"] / (s + FAN["b"]))


def fan_power_kW(speed, phi=0.0, k_extra=0.0, rho=1.15):
    q = fan_flow_ratio(speed, phi, k_extra)
    dP = FAN["dP_design"] * (FAN["a"] * speed**2 - FAN["b"] * q**2) * rho / 1.15
    return FAN["Q_design"] * q * dP / FAN["eta"] / 1000


def h_air(V_face, T_air, phi=0.0):
    """Briggs & Young (1963) for helically finned tubes, staggered. Returns h (W/m2K), Re."""
    rho, mu, k, cp = air_props(T_air)
    Vmax = V_face / g["sigma"] / (1 - phi)       # air squeezes through the open gaps
    Re = rho * Vmax * g["Do"] / mu
    Pr = cp * mu / k
    Nu = 0.134 * Re**0.681 * Pr**(1 / 3) * (g["s_gap"] / g["l_fin"])**0.2 * (g["s_gap"] / g["tf"])**0.1134
    return H_MULT * Nu * k / g["Do"], Re


def fin_efficiency(h):
    """annular fin, Schmidt approximation"""
    ro, re = g["Do"] / 2, g["Df"] / 2
    m = math.sqrt(2 * h / (g["k_fin"] * g["tf"]))
    ratio = re / ro
    Lc = ro * (ratio - 1) * (1 + 0.35 * math.log(ratio))
    return math.tanh(m * Lc) / (m * Lc)


def UA_air(airflow_m3s, T_air, phi=0.0, R_d=0.0):
    """air-side conductance (W/K) of the whole bundle"""
    V_face = airflow_m3s / g["A_face"]
    h, Re = h_air(V_face, T_air, phi)
    h_eff = 1 / (1 / h + R_d)                  # debris mat in series with the air film
    eta_f = fin_efficiency(h_eff)
    eta_o = 1 - g["A_fin"] / g["A_tot"] * (1 - eta_f)
    return h_eff * eta_o * g["A_tot"] * (1 - phi), dict(h=h, h_eff=h_eff, Re=Re, eta_f=eta_f, eta_o=eta_o, V_face=V_face)


# ---------------------------------------------------------------- 4. TUBE SIDE
R_FOUL_IN = 0.0002   # m2K/W, clean shift gas (TEMA-type allowance)
H_COND_FILM = 8000.0 # W/m2K, thin condensate film inside the tube


def h_tube(T, n_dry, dQgas_frac):
    """effective tube-side coefficient (W/m2K) for condensing H2-rich gas"""
    n_v, n_l = water_split(T, n_dry)
    n_g = n_dry + n_v
    MWg = (n_dry * MW_DRY + n_v * MW["Water"]) / n_g
    m_g = n_g * MWg / 1000                                    # kg/s gas
    rho = P_PROC * MWg / 1000 / (R_GAS * T)
    A_flow = g["Nt"] / g["passes"] * math.pi / 4 * g["Di"]**2
    V = m_g / rho / A_flow
    # mixture transport properties: H2-rich gas, simple mole-fraction weighting
    yH2 = DRY["Hydrogen"] * n_dry / n_g
    mu = 1.0e-5 * yH2 + 1.7e-5 * (1 - yH2)
    k = (0.20 * yH2 + 0.028 * (1 - yH2)) * (T / 400) ** 0.7
    cp = (cp_dry_molar(T) * n_dry + 34.0 * n_v) / n_g / MWg * 1000
    Re = rho * V * g["Di"] / mu
    Pr = cp * mu / k
    f = (0.79 * math.log(Re) - 1.64) ** -2
    Nu = (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f / 8) * (Pr**(2 / 3) - 1))   # Gnielinski
    hg = Nu * k / g["Di"]
    Z = max(dQgas_frac, 0.05)                                 # Silver-Bell-Ghaly
    return 1 / (1 / H_COND_FILM + Z / hg), hg


R_WALL = math.log(g["Do"] / g["Di"]) / (2 * math.pi * g["k_wall"] * g["Ltot"])   # K/W


# ---------------------------------------------------------------- 5. RATING
def area_fraction_needed(T_in_C, T_out_C, flow_nm3h, T_amb_C, airflow_m3s, phi=0.0, R_d=0.0, F=0.95, dT=0.5):
    """
    March from the cold end (T_out) to the hot end (T_in) in small temperature steps.
    For each step: heat released dQ, local temperature difference to the air, local U.
    Returns the fraction of the exchanger that this duty needs (1.0 = exactly fits).
    Air is heated counter-currently (2-pass counter-cross-flow, F-factor 0.95).
    """
    n = nm3h_to_mols(flow_nm3h)
    rho_in = air_props(T_amb_C + 273.15)[0]
    C_air = rho_in * airflow_m3s * 1006.0
    Ts = np.arange(T_out_C, T_in_C + 1e-9, dT) + 273.15
    if Ts[-1] < T_in_C + 273.15 - 1e-6:
        Ts = np.append(Ts, T_in_C + 273.15)
    Hs = np.array([H_process(t, n) for t in Ts])
    Q_total = Hs[-1] - Hs[0]
    T_air_out = T_amb_C + Q_total / C_air
    UAa, info = UA_air(airflow_m3s, 0.5 * (T_amb_C + T_air_out) + 273.15, phi, R_d)
    frac = 0.0
    for i in range(len(Ts) - 1):
        dQ = Hs[i + 1] - Hs[i]
        Tp = 0.5 * (Ts[i] + Ts[i + 1])
        Ta = T_amb_C + 273.15 + 0.5 * (Hs[i] + Hs[i + 1] - 2 * Hs[0]) / C_air
        dTloc = Tp - Ta
        if dTloc <= 0.2:
            return float("inf"), Q_total, info
        dQgas = n * cp_dry_molar(Tp) * (Ts[i + 1] - Ts[i])
        hi, _ = h_tube(Tp, n, dQgas / dQ)
        UA_in = 1 / (1 / (hi * g["A_in"]) + R_FOUL_IN / g["A_in"])
        UA = 1 / (1 / UAa + 1 / UA_in + R_WALL)
        frac += dQ / (F * UA * dTloc)
    return frac, Q_total, info


def solve_T_out(T_in_C, flow_nm3h, T_amb_C, airflow_m3s, phi=0.0, R_d=0.0):
    """outlet temperature at which the duty exactly fills the exchanger"""
    lo, hi = T_amb_C + 1.0, T_in_C - 0.3
    if area_fraction_needed(T_in_C, hi, flow_nm3h, T_amb_C, airflow_m3s, phi, R_d)[0] > 1:
        return T_in_C
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        f = area_fraction_needed(T_in_C, mid, flow_nm3h, T_amb_C, airflow_m3s, phi, R_d)[0]
        if f > 1:
            lo = mid
        else:
            hi = mid
        if hi - lo < 0.05:
            break
    return 0.5 * (lo + hi)


def airflow_from_speed(speed, phi=0.0, k_extra=0.0):
    return FAN["Q_design"] * fan_flow_ratio(speed, phi, k_extra)


def predict(T_in_C, flow_nm3h, T_amb_C, speed, phi=0.0, R_d=0.0, k_extra=0.0):
    Qa = airflow_from_speed(speed, phi, k_extra)
    To = solve_T_out(T_in_C, flow_nm3h, T_amb_C, Qa, phi, R_d)
    return To, duty(T_in_C, To, flow_nm3h), Qa


def solve_phi(T_in_C, T_out_C, flow_nm3h, T_amb_C, speed, R_d=0.0):
    """equivalent blocked fraction that reproduces a measured outlet temperature"""
    lo, hi = 0.0, 0.95
    if predict(T_in_C, flow_nm3h, T_amb_C, speed, 0.0, R_d)[0] >= T_out_C:
        return 0.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        To = predict(T_in_C, flow_nm3h, T_amb_C, speed, mid, R_d)[0]
        if To > T_out_C:
            hi = mid
        else:
            lo = mid
        if hi - lo < 0.002:
            break
    return 0.5 * (lo + hi)


def max_flow(T_in_C, T_amb_C, speed, phi, T_limit=65.0, R_d=0.0, lo=5000, hi=60000):
    """largest dry-gas flow (Nm3/h) the cooler can bring down to T_limit"""
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        Qa = airflow_from_speed(speed, phi)
        f = area_fraction_needed(T_in_C, T_limit, mid, T_amb_C, Qa, phi, R_d)[0]
        if f > 1:
            hi = mid
        else:
            lo = mid
        if hi - lo < 50:
            break
    return 0.5 * (lo + hi)
