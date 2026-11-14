"""
Segmented steady-state rating model of A-1401 (6 rows x N segments, 2 tube passes).

Arrangement (forced draft, counter-crossflow):
      warm air out (top)
   row 6  ->->->->->->   pass 1   (hot wet syngas enters here, header mixes rows 4-6)
   row 5  ->->->->->->   pass 1
   row 4  ->->->->->->   pass 1
   row 3  <-<-<-<-<-<-   pass 2   (return pass, cooled syngas + condensate leave)
   row 2  <-<-<-<-<-<-   pass 2
   row 1  <-<-<-<-<-<-   pass 2
      ambient air in (bottom, three fans)

Each cell (row r, segment j) exchanges heat with the air column j crossing it:
   Q_cell = C_air,cell * [1 - exp(-UA_cell / C_air,cell)] * (T_process - T_air,in)
   (air side unmixed through the cell; process temperature taken at the cell midpoint by a
    predictor-corrector step).  UA_cell = 1 / (1/UA_air + R_wall + 1/UA_inside), all per cell.
The process enthalpy (wet gas, with condensation) is carried along each tube; the two
headers mix the rows of a pass by enthalpy.  Air temperatures are updated row by row and the
whole field is iterated to convergence.
"""
import math
import numpy as np
from . import config as C
from .airside import G, UA_air, airflow, air_props
from .thermo import WetSyngas, nm3h_to_mol_s, gas_transport, MW, mw_dry


class TubeSide:
    """Tube-side coefficient table for one process flow: Gnielinski gas film + Silver-Bell-Ghaly."""

    def __init__(self, gas: WetSyngas, n_dry, T_lo, T_hi, h_film=None, R_foul=None, npts=30):
        self.h_film = C.H_CONDENSATE_FILM if h_film is None else h_film
        self.R_foul = C.R_FOUL_INSIDE if R_foul is None else R_foul
        tubes_per_pass = G["n_tubes"] / G["passes"]
        A_flow = tubes_per_pass * math.pi / 4 * G["Di"] ** 2
        Ts = np.linspace(T_lo, T_hi, npts)
        hs, hg_list, Re_list = [], [], []
        Mdry = mw_dry(gas.comp)
        for T in Ts:
            nv = float(gas.vapour(T))
            n_g = n_dry * (1 + nv)
            MWg = (Mdry + nv * MW["Water"]) / (1 + nv)
            m_g = n_g * MWg / 1000
            rho = gas.P * MWg / 1000 / (8.314 * T)
            V = m_g / rho / A_flow
            y_w = nv / (1 + nv)
            mu, k = gas.transport(T)
            cp_mol = (np.interp(T, gas.T, gas.cp_dry) + nv * 36.0) / (1 + nv)   # J/mol/K, vapour cp ~36
            cp = cp_mol / MWg * 1000
            Re = rho * V * G["Di"] / mu
            Pr = cp * mu / k
            f = (0.790 * math.log(Re) - 1.64) ** -2
            Nu = (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f / 8) * (Pr ** (2 / 3) - 1))
            hg = Nu * k / G["Di"]
            Z = float(gas.gas_fraction_of_dH(T))
            condensing = float(gas.liquid(T)) > 0 and T < gas.dew_point() + 1e-6
            h = 1 / (1 / self.h_film + Z / hg) if condensing else hg
            hs.append(h); hg_list.append(hg); Re_list.append(Re)
        self.Ts, self.h, self.hg, self.Re = Ts, np.array(hs), np.array(hg_list), np.array(Re_list)

    def __call__(self, T):
        return np.interp(T, self.Ts, self.h)


def rate(T_in_C, flow_nm3h, T_amb_C, speed=1.0, b=0.0, gas=None, N=None, h_mult=None, h_film=None,
         bundle_share=None, fan_a=None, fan_b=None, Q_air_override=None, tol=1e-3, max_iter=200):
    """Rate the exchanger for given inlet conditions.  Returns a dict of results (SI + readable units)."""
    gas = gas or WetSyngas()
    N = N or C.N_SEGMENTS
    n_dry = nm3h_to_mol_s(flow_nm3h)
    rows, tpr = G["rows"], G["tubes_per_row"]
    # ---- air
    if Q_air_override is None:
        Q_air, fan = airflow(speed, b, bundle_share, fan_a, fan_b)
    else:
        Q_air, fan = Q_air_override, dict(q_frac=Q_air_override / (3 * 114000 / 3600), fan_dP_Pa=float("nan"), fan_power_kW_each=float("nan"))
    T_amb = T_amb_C + 273.15
    rho_air = air_props(T_amb)[0]
    m_air = rho_air * Q_air
    C_cell = m_air * 1006.0 / N
    # ---- per-cell constants
    n_row = n_dry * tpr / (G["n_tubes"] / G["passes"])          # mol dry / s in one row of a pass
    A_in_cell = G["A_in"] / (rows * N)
    R_wall_cell = math.log(G["Do"] / G["Di"]) / (2 * math.pi * G["k_wall"] * G["L_tot"] / (rows * N))
    T_in = T_in_C + 273.15
    tube = TubeSide(gas, n_dry, T_amb - 1, T_in + 1, h_film=h_film)
    H_in = float(gas.H_of_T(T_in))
    p1 = [r - 1 for r in C.GEOMETRY["rows_pass1"]]
    p2 = [r - 1 for r in C.GEOMETRY["rows_pass2"]]
    Q = np.zeros((rows, N))
    Ta = np.full((rows, N), T_amb)
    T_air_mean = T_amb + 5
    T_out_prev = None

    def march(row_idx, H_start, order, UAa_cell):
        H = np.full(len(row_idx), H_start)
        Ta_rows = Ta[row_idx]
        for j in order:
            Tp0 = gas.T_of_H(H)
            for _ in range(2):                                   # predictor-corrector on cell midpoint
                UAi = 1 / (1 / (tube(Tp0) * A_in_cell) + tube.R_foul / A_in_cell)
                UA = 1 / (1 / UAa_cell + R_wall_cell + 1 / UAi)
                eps = 1 - np.exp(-UA / C_cell)
                q = eps * C_cell * (Tp0 - Ta_rows[:, j])
                q = np.maximum(q, 0.0)
                Tp1 = gas.T_of_H(H - q / n_row)
                Tp0 = 0.5 * (gas.T_of_H(H) + Tp1)
            Q[row_idx, j] = q
            H = H - q / n_row
        return H

    for it in range(max_iter):
        UAa_tot, ainfo = UA_air(Q_air, T_air_mean, b, h_mult)
        UAa_cell = UAa_tot / (rows * N)
        H1 = march(p1, H_in, range(N), UAa_cell)
        H_mid = H1.mean()                                        # header between passes (equal row flows)
        H2 = march(p2, H_mid, range(N - 1, -1, -1), UAa_cell)
        H_out = H2.mean()
        # update air temperatures row by row (air rises from row 1 to row 6)
        Ta_new = np.empty_like(Ta)
        Ta_new[0] = T_amb
        for r in range(1, rows):
            Ta_new[r] = Ta_new[r - 1] + Q[r - 1] / C_cell
        Ta[:] = 0.5 * Ta + 0.5 * Ta_new                          # under-relaxation for robustness
        T_air_out_cols = Ta_new[-1] + Q[-1] / C_cell
        T_air_out = float(T_air_out_cols.mean())
        T_air_mean = 0.5 * (T_amb + T_air_out)
        T_out = float(gas.T_of_H(H_out))
        if T_out_prev is not None and abs(T_out - T_out_prev) < tol and np.max(np.abs(Ta - Ta_new)) < 10 * tol:
            break
        T_out_prev = T_out
    converged = it < max_iter - 1
    Ta[:] = Ta_new
    # ---- results
    Q_proc = n_dry * (H_in - H_out)
    Q_cells = float(Q.sum())
    Q_air_side = m_air * 1006.0 * (T_air_out - T_amb)
    bd = gas.breakdown(T_in, T_out, n_dry)
    # physical conductances (bundle totals) evaluated at the mean tube-side state
    T_mid = 0.5 * (T_in + T_out)
    UA_in = 1 / (1 / (tube(T_mid) * G["A_in"]) + tube.R_foul / G["A_in"])
    R_wall = math.log(G["Do"] / G["Di"]) / (2 * math.pi * G["k_wall"] * G["L_tot"])
    UA_tot = 1 / (1 / UAa_tot + R_wall + 1 / UA_in)
    # apparent UA from the counterflow LMTD (for comparison with simple hand methods)
    dT1, dT2 = T_in - (T_air_out), T_out - T_amb
    lmtd = (dT1 - dT2) / math.log(dT1 / dT2) if dT1 > 0 and dT2 > 0 and abs(dT1 - dT2) > 1e-6 else max(dT1, 1e-6)
    W = gas.W
    water_in = n_dry * W * MW["Water"] * 3.6
    vap_out = n_dry * float(gas.vapour(T_out)) * MW["Water"] * 3.6
    liq_out = n_dry * float(gas.liquid(T_out)) * MW["Water"] * 3.6
    return dict(
        T_in_C=T_in_C, T_out_C=T_out - 273.15, T_amb_C=T_amb_C, T_air_out_C=T_air_out - 273.15,
        flow_dry_Nm3h=flow_nm3h, n_dry_mol_s=n_dry, water_to_dry=W, fan_speed=speed, blockage=b,
        air_m3h=Q_air * 3600, air_kg_s=m_air, air_frac_of_rated=fan["q_frac"], fan_dP_Pa=fan["fan_dP_Pa"],
        fan_power_kW_each=fan["fan_power_kW_each"],
        Q_total_kW=Q_proc / 1000, Q_cells_kW=Q_cells / 1000, Q_air_side_kW=Q_air_side / 1000,
        Q_dry_gas_sensible_kW=bd["dry_gas_sensible_W"] / 1000, Q_vapour_sensible_kW=bd["water_vapour_sensible_W"] / 1000,
        Q_condensate_sensible_kW=bd["condensate_sensible_W"] / 1000, Q_latent_kW=bd["latent_W"] / 1000,
        Q_sensible_kW=(bd["dry_gas_sensible_W"] + bd["water_vapour_sensible_W"] + bd["condensate_sensible_W"]) / 1000,
        condensed_kg_h=bd["condensed_kg_h"], vapour_in_kg_h=bd["vapour_in_kg_h"], liquid_in_kg_h=bd["liquid_in_kg_h"],
        vapour_out_kg_h=vap_out, liquid_out_kg_h=liq_out, water_in_kg_h=water_in,
        dew_point_C=gas.dew_point() - 273.15,
        UA_air_kW_K=UAa_tot / 1000, UA_inside_kW_K=UA_in / 1000, R_wall_K_kW=R_wall * 1000,
        UA_total_kW_K=UA_tot / 1000, UA_apparent_LMTD_kW_K=Q_proc / lmtd / 1000, LMTD_K=lmtd,
        h_air_W_m2K=ainfo["h_air"], Re_air=ainfo["Re_air"], eta_fin=ainfo["eta_fin"], eta_surface=ainfo["eta_surface"],
        V_face_m_s=ainfo["V_face"], V_max_open_m_s=ainfo["V_max"], A_active_m2=ainfo["A_active"],
        h_inside_mid_W_m2K=float(tube(T_mid)), h_gas_film_mid_W_m2K=float(np.interp(T_mid, tube.Ts, tube.hg)),
        Re_tube_mid=float(np.interp(T_mid, tube.Ts, tube.Re)),
        share_R_air=(1 / UAa_tot) / (1 / UA_tot), share_R_wall=R_wall / (1 / UA_tot), share_R_inside=(1 / UA_in) / (1 / UA_tot),
        iterations=it + 1, converged=bool(converged), Q_field=Q.copy(), Ta_field=Ta.copy(),
    )


def scalar(res):
    """drop the array fields so a result can be written to CSV/JSON"""
    return {k: (float(v) if isinstance(v, (np.floating,)) else v) for k, v in res.items() if not isinstance(v, np.ndarray)}
