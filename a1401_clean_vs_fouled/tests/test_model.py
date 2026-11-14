"""Numerical verification tests.  Run:  python -m pytest tests   (or  python tests/test_model.py)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
from a1401sim.thermo import WetSyngas, saturation_ratio
from a1401sim.airside import G, airflow
from a1401sim.exchanger import rate
from a1401sim import config as C

GAS = WetSyngas()


def test_geometry_matches_datasheet_areas():
    assert abs(G["A_ext"] - C.DS_AREA_EXT) / C.DS_AREA_EXT < 0.005
    assert abs(G["A_bare"] - C.DS_AREA_BARE) / C.DS_AREA_BARE < 0.005


def test_enthalpy_split_closes():
    bd = GAS.breakdown(433.15, 333.15, 250.0)
    parts = bd["dry_gas_sensible_W"] + bd["water_vapour_sensible_W"] + bd["condensate_sensible_W"] + bd["latent_W"]
    assert abs(parts - bd["total_W"]) / bd["total_W"] < 1e-6


def test_saturation_physics():
    assert saturation_ratio(433.15) > saturation_ratio(333.15) > 0      # hotter gas holds more water
    assert 170 < GAS.dew_point() - 273.15 < 190                         # 0.555 mol/mol at 27.5 bar


def test_fan_rated_point_and_blockage_response():
    q0, _ = airflow(1.0, 0.0); q3, _ = airflow(1.0, 0.3)
    assert abs(q0 - 95.0) < 1e-6                     # 3 x 114,000 m3/h
    assert 0.7 < q3 / q0 < 1.0                       # 30 % blocked area is NOT 30 % less air


def test_energy_and_water_balance_clean_and_fouled():
    for b in (0.0, 0.3, 0.65):
        r = rate(159.4, 17444, 31.8, 1.0, b, gas=GAS)
        assert abs(r["Q_total_kW"] - r["Q_air_side_kW"]) / r["Q_total_kW"] < 1e-3
        assert abs(r["water_in_kg_h"] - r["vapour_out_kg_h"] - r["liquid_out_kg_h"]) < 1e-6 * r["water_in_kg_h"]
        assert r["T_amb_C"] < r["T_out_C"] < r["T_in_C"] and r["T_air_out_C"] < r["T_in_C"]


def test_monotonic_with_blockage():
    T = [rate(159.4, 17444, 31.8, 1.0, b, gas=GAS)["T_out_C"] for b in np.arange(0, 0.71, 0.1)]
    assert np.all(np.diff(T) > 0)


def test_grid_converged():
    a = rate(159.4, 17444, 31.8, 1.0, 0.5, gas=GAS, N=24)["T_out_C"]
    b = rate(159.4, 17444, 31.8, 1.0, 0.5, gas=GAS, N=48)["T_out_C"]
    assert abs(a - b) < 0.1


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f(); print("PASS", k)
