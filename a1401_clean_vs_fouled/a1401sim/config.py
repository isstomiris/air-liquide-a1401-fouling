"""
Input register for the A-1401 rating model.

Every value carries a source tag:
  DS   = A-1401 datasheet / GA drawing table (values as transcribed in the project
         audit, AUDIT_report.md section 1; the original drawings were not available
         to this calculation and could not be re-checked here)
  PFD  = plant process flow diagram (as transcribed in the project diagnosis)
  LAB  = plant laboratory gas analyses (medians, as transcribed in the project audit)
  HIST = process historian export "Data (full history).xlsx"
  WX   = Open-Meteo ERA5 hourly reanalysis, Atyrau 47.14 N 51.89 E
  CORR = published engineering correlation
  ASM  = engineering assumption made in this calculation (tested in sensitivity)
All values SI unless the name says otherwise.
"""
import math

P_ATM = 101_700.0                        # Pa, site at -22 m elevation (WX metadata)  ASM

# ------------------------------------------------------------------ geometry
GEOMETRY = dict(
    Do=0.025,            # m, tube OD                                   DS
    t_wall=0.002,        # m, tube wall                                 DS
    n_tubes=276,         # main syngas tubes                            DS (bundle BOM item 31)
    rows=6,              # main tube rows                               DS
    passes=2,            # tube passes                                  DS (per project diagnosis)
    L=10.42,             # m, effective finned length: 226 m2 / (pi*0.025*276)   derived from DS areas
    Df=0.057,            # m, fin outer diameter                        ASM (A12, reproduces both DS areas)
    tf=0.0004,           # m, fin thickness                             ASM
    fins_per_m=423.0,    # fins per metre, solved so fin area = 5,288 m2  derived
    St=0.064,            # m, transverse pitch                          ASM (46 tubes in ~3 m bundle width)
    Sl=0.0554,           # m, longitudinal pitch (equilateral layout)   ASM
    k_fin=205.0,         # W/m/K aluminium fins                         ASM
    k_wall=16.0,         # W/m/K, S30403 stainless                      handbook value
    rows_pass1=(4, 5, 6),   # hot gas enters the TOP three rows        ASM (counter-crossflow)
    rows_pass2=(1, 2, 3),   # second pass in the bottom rows, met first by the air  ASM
)
DS_AREA_BARE = 226.0       # m2   DS
DS_AREA_EXT = 5288.4       # m2   DS

# ------------------------------------------------------------------ process stream
DRY_COMPOSITION = {        # mol fraction, dry basis                   LAB medians (normalised below)
    "Hydrogen": 0.744, "CarbonDioxide": 0.179, "Methane": 0.0496,
    "CarbonMonoxide": 0.0225, "Nitrogen": 0.006,
}
_s = sum(DRY_COMPOSITION.values())
DRY_COMPOSITION = {k: v / _s for k, v in DRY_COMPOSITION.items()}
BRIEF_COMPOSITION = {"Hydrogen": 0.743, "CarbonDioxide": 0.178, "Methane": 0.050,
                     "CarbonMonoxide": 0.022, "Nitrogen": 0.006}   # team brief, sums to 0.999

WATER_TO_DRY_BASE = 510.0 / 919.0   # 0.555 mol H2O per mol dry gas, PFD steam balance   PFD (unverified, carbon balance does not close)
WATER_TO_DRY_SCENARIOS = {
    "high (PFD steam balance)": 0.555,
    "saturated at 162 C inlet": None,  # filled at run time = just saturated at the inlet
    "low (carbon-balance case)": 0.24,
}
P_PROCESS = 2.65e6 + P_ATM   # Pa abs; DS inlet 2.69 MPa(g), D-1403 2.56 MPa(g)   DS/PFD, mid value
ENHANCEMENT_FACTOR = 1.0     # water vapour enhancement factor in H2 at 27 bar   ASM (tested 1.03)

# ------------------------------------------------------------------ fans
FAN = dict(
    n_fans=3,
    Q_rated_m3h=114_000.0,   # per fan                                  DS
    dP_rated_total=190.0,    # Pa, TOTAL pressure at rated flow         DS
    rpm=477.0, D=2.4, motor_kW=11.0,                                  # DS
    a=1.6, b=0.6,            # generic axial curve dP = dP_r (a n^2 - b q^2), a-b = 1   ASM (no vendor curve)
    eta_total=0.65,          # fan total efficiency, only used for power   ASM
)
SYSTEM_SHARE_OTHER = None    # share of rated dP outside the bundle; None = computed from Robinson-Briggs
RB_EXPONENT = 1.684          # bundle dP ~ velocity^(2-0.316)   CORR Robinson & Briggs (1966)

# ------------------------------------------------------------------ tube side
H_CONDENSATE_FILM = 8000.0   # W/m2K, thin condensate film             ASM (order of magnitude)
R_FOUL_INSIDE = 0.0002       # m2K/W, clean shift-gas allowance        ASM (TEMA-type)
H_AIR_MULT = 1.0             # multiplier on Briggs & Young            CORR (+/-20 % scatter)

# ------------------------------------------------------------------ numerics
N_SEGMENTS = 24              # segments along each tube
T_GRID_STEP = 0.05           # K, enthalpy table resolution
