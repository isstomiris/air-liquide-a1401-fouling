"""
Numerical verification of the A-1401 model (energy, material, physical limits, grid, property cross-check).
Called by run_all.py; can also be run on its own:  python verify.py
"""
import math
import numpy as np
from a1401sim import config as C
from a1401sim.thermo import WetSyngas, MW, nm3h_to_mol_s
from a1401sim.exchanger import rate


def pr_cross_check(T_in_C, T_out_C, W):
    """Independent property package: Peng-Robinson EOS flash (Caleb Bell 'thermo' library, ChemSep kij).
    Returns water vapour per mol dry gas at inlet/outlet and the enthalpy change per mol dry gas."""
    try:
        from thermo import ChemicalConstantsPackage, PRMIX, CEOSGas, CEOSLiquid, FlashVLN
        from thermo.interaction_parameters import IPDB
    except Exception as e:                                   # optional dependency
        return dict(available=False, reason=str(e))
    names = ['hydrogen', 'carbon dioxide', 'methane', 'carbon monoxide', 'nitrogen', 'water']
    const, corr = ChemicalConstantsPackage.from_IDs(names)
    kij = IPDB.get_ip_asymmetric_matrix('ChemSep PR', const.CASs, 'kij')
    kw = dict(Tcs=const.Tcs, Pcs=const.Pcs, omegas=const.omegas, kijs=kij)
    fl = FlashVLN(const, corr, liquids=[CEOSLiquid(PRMIX, kw, HeatCapacityGases=corr.HeatCapacityGases)],
                  gas=CEOSGas(PRMIX, kw, HeatCapacityGases=corr.HeatCapacityGases))
    dry = [C.DRY_COMPOSITION[k] for k in ("Hydrogen", "CarbonDioxide", "Methane", "CarbonMonoxide", "Nitrogen")]
    z = [x / (1 + W) for x in dry] + [W / (1 + W)]
    res = {}
    for tag, T in (("in", T_in_C), ("out", T_out_C)):
        r = fl.flash(T=T + 273.15, P=C.P_PROCESS, zs=z)
        yw = r.gas.zs[-1] if r.gas is not None else 0.0
        ng = r.VF * (1 + W)                                  # mol gas per mol dry gas (dry gas ~ all in vapour)
        res[f"vapour_{tag}_mol_per_mol_dry"] = yw * ng
        res[f"H_{tag}_J_per_mol_dry"] = r.H() * (1 + W)
    res["dH_J_per_mol_dry"] = res["H_in_J_per_mol_dry"] - res["H_out_J_per_mol_dry"]
    res["available"] = True
    return res


def run_checks(gas, REF, cmp_):
    out = {}
    # ---------------- A. energy balance, every case
    eb = {}
    for case, r in cmp_.iterrows():
        n = r.n_dry_mol_s
        Q_table = n * (gas.H_of_T(r.T_in_C + 273.15) - gas.H_of_T(r.T_out_C + 273.15)) / 1000
        parts = r.Q_dry_gas_sensible_kW + r.Q_vapour_sensible_kW + r.Q_condensate_sensible_kW + r.Q_latent_kW
        eb[case] = dict(process_kW=round(r.Q_total_kW, 2), sum_of_cells_kW=round(r.Q_cells_kW, 2), air_gain_kW=round(r.Q_air_side_kW, 2),
                        process_from_T_out_kW=round(Q_table, 2), sum_of_duty_parts_kW=round(parts, 2),
                        max_rel_error_pct=round(100 * max(abs(r.Q_total_kW - r.Q_air_side_kW), abs(r.Q_total_kW - r.Q_cells_kW),
                                                         abs(r.Q_total_kW - Q_table), abs(r.Q_total_kW - parts)) / r.Q_total_kW, 4))
    out["A_energy_balance"] = eb
    out["A_pass"] = all(v["max_rel_error_pct"] < 0.5 for v in eb.values())
    # ---------------- B. material balance
    mb = {}
    for case, r in cmp_.iterrows():
        w_in = r.water_in_kg_h
        w_out = r.vapour_out_kg_h + r.liquid_out_kg_h
        cond = r.vapour_in_kg_h - r.vapour_out_kg_h
        mb[case] = dict(water_in_kg_h=round(w_in, 2), vapour_plus_liquid_out_kg_h=round(w_out, 2),
                        vapour_in=round(r.vapour_in_kg_h, 1), liquid_in=round(r.liquid_in_kg_h, 1),
                        vapour_out=round(r.vapour_out_kg_h, 1), liquid_out=round(r.liquid_out_kg_h, 1),
                        condensed_check=round(cond - r.condensed_kg_h, 3),
                        rel_error_pct=round(100 * abs(w_in - w_out) / w_in, 6))
    out["B_material_balance"] = mb
    out["B_dry_gas"] = "dry components carried unchanged per mole (no reaction, gas solubility in condensate neglected)"
    out["B_pass"] = all(v["rel_error_pct"] < 0.01 and abs(v["condensed_check"]) < 1 for v in mb.values())
    # ---------------- C. physical limits
    lim = {}
    for case, r in cmp_.iterrows():
        lim[case] = dict(T_out_above_air_in=bool(r.T_out_C > r.T_amb_C), air_out_below_gas_in=bool(r.T_air_out_C < r.T_in_C),
                         duty_below_max_possible=bool(r.Q_total_kW < r.n_dry_mol_s * (gas.H_of_T(r.T_in_C + 273.15) - gas.H_of_T(r.T_amb_C + 273.15)) / 1000),
                         converged=bool(r.converged))
    out["C_physical_limits"] = lim
    out["C_pass"] = all(all(v.values()) for v in lim.values())
    # ---------------- D. grid convergence
    gc = {}
    for N in (6, 12, 24, 48):
        r = rate(REF["T_in_C"], REF["flow_dry_Nm3h"], REF["T_amb_C"], 1.0, 0.5, gas=gas, N=N)
        gc[N] = round(r["T_out_C"], 3)
    out["D_grid_T_out_at_b50"] = gc
    out["D_pass"] = abs(gc[24] - gc[48]) < 0.1
    # ---------------- E. property cross-check (Peng-Robinson flash)
    clean = cmp_.iloc[0]
    pr = pr_cross_check(REF["T_in_C"], clean.T_out_C, gas.W)
    if pr.get("available"):
        ours_dH = gas.H_of_T(REF["T_in_C"] + 273.15) - gas.H_of_T(clean.T_out_C + 273.15)
        pr.update(ours_vapour_in=float(gas.vapour(REF["T_in_C"] + 273.15)), ours_vapour_out=float(gas.vapour(clean.T_out_C + 273.15)),
                  ours_dH_J_per_mol_dry=float(ours_dH), dH_difference_pct=100 * (pr["dH_J_per_mol_dry"] - ours_dH) / ours_dH)
    out["E_property_cross_check_PR"] = pr
    return out


if __name__ == "__main__":
    import json
    g = WetSyngas()
    print(json.dumps(pr_cross_check(160, 60, g.W), indent=1))
    print("ours vapour in/out", g.vapour(433.15), g.vapour(333.15), "dH", g.H_of_T(433.15) - g.H_of_T(333.15))
