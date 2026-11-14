# Conceptual PFD of the A-1401 syngas air-cooler section (UPOV-2, Atyrau)
# Built with the pfd-generator skill primitives (pid_lib.py).
from pid_lib import PID, esc
W, H = 1600, 940
d = PID(W, H)
G, B, C, R = d.GREEN, d.BLUE, d.CYAN, d.RUST
AIR = "#8a94a3"
d.title("A-1401 RAW HYDROGEN AIR COOLER - SECTION PFD",
        "UPOV-2 hydrogen unit, Atyrau  |  Syngas cooling and water removal before PSA  |  Fan-speed temperature control")
Y = 420  # main syngas band

# ---------- vessel D-1403 (body first)
d.vessel(1230, 330, 1350, 610, level=530, level_label="WATER")

# ---------- process pipes
d.pipe(f"M 60,{Y} L 218,{Y}", G)                 # from E-1407 to E-1408
d.pipe(f"M 282,{Y} L 440,{Y}", G)                # E-1408 -> A-1401
d.pipe(f"M 780,{Y} L 898,{Y}", G)                # A-1401 -> E-1409
d.pipe(f"M 962,{Y} L 1058,{Y}", G)               # E-1409 -> E-1410
d.pipe(f"M 1122,{Y} L 1230,{Y}", G, arrow=True)  # E-1410 -> D-1403
d.pipe("M 1290,330 L 1290,200 L 1570,200", G, arrow=True)   # gas to PSA
d.pipe("M 1340,200 L 1340,130 L 1570,130", G, arrow=True)   # flare branch
d.pipe("M 1320,610 L 1320,700 L 1570,700", B, arrow=True)   # condensate out
# utilities
d.pipe("M 250,540 L 250,452", B, arrow=True)     # condensate in to E-1408
d.pipe("M 250,388 L 250,300", B, arrow=True)     # to deaerator
d.pipe("M 930,540 L 930,452", B, arrow=True)     # demin water in E-1409
d.pipe("M 930,388 L 930,300", B, arrow=True)     # demin out
d.pipe("M 1090,540 L 1090,452", C, arrow=True)   # CWS
d.pipe("M 1090,388 L 1090,300", C, arrow=True)   # CWR
d.pipe("M 760,640 L 760,462", R, arrow=True)     # steam heating row (winter)

# ---------- A-1401 bundle + fans
d.add('<rect x="440" y="380" width="340" height="80" fill="#f7f8fa" stroke="#343a46" stroke-width="2.2"/>')
for x in range(452, 780, 12):
    d.add(f'<line x1="{x}" y1="384" x2="{x}" y2="456" stroke="#c9ced6" stroke-width="1"/>')
d.add('<rect x="455" y="398" width="290" height="44" fill="#ffffff" stroke="none" opacity="0.92"/>')
d.txt(600, 416, "A-1401  finned-tube bundle", size=12, weight="bold", anchor="middle")
d.txt(600, 433, "6 rows, 2 passes, 304L tubes, 5,288 m2 fins", size=9.5, fill=d.SUB, anchor="middle")
for i, fx in enumerate((500, 600, 700)):
    # air arrows up through bundle
    d.add(f'<path d="M {fx},{520} L {fx},{470}" stroke="{AIR}" stroke-width="2" fill="none" marker-end="url(#aSig)"/>')
    d.add(f'<path d="M {fx},{378} L {fx},{340}" stroke="{AIR}" stroke-width="2" fill="none" stroke-dasharray="3,4" marker-end="url(#aSig)"/>')
    d.add(f'<ellipse cx="{fx}" cy="532" rx="40" ry="9" fill="#ffffff" stroke="#343a46" stroke-width="1.6"/>')
    d.add(f'<rect x="{fx-12}" y="545" width="24" height="22" fill="#ffffff" stroke="#343a46" stroke-width="1.5"/>')
    d.txt(fx, 561, "M", size=11, weight="bold", anchor="middle")
    d.txt(fx - 46, 536, "ABC"[i], size=10, weight="bold", fill=d.SUB, anchor="end")
d.txt(600, 330, "hot air out (to atmosphere)", size=9.5, fill=d.SUB, anchor="middle")
d.txt(430, 590, "3 fans x 11 kW", size=9.5, fill=d.SUB, anchor="end")
d.txt(430, 604, "2.4 m, VFD speed", size=9.5, fill=d.SUB, anchor="end")
d.txt(560, 506, "ambient air", size=9.5, fill=d.SUB, anchor="middle")
d.txt(770, 660, "LP steam (winter", size=9, fill=R, anchor="middle")
d.txt(770, 672, "heating row)", size=9, fill=R, anchor="middle")

# ---------- exchangers (circles)
for cx, tag, svc in ((250, "E-1408", "condensate preheater"),
                     (930, "E-1409", "demin water heater"),
                     (1090, "E-1410", "cooling-water trim")):
    d.add(f'<circle cx="{cx}" cy="{Y}" r="32" fill="#ffffff" stroke="#343a46" stroke-width="2"/>')
    d.add(f'<path d="M {cx-32},{Y} L {cx-12},{Y} L {cx-4},{Y-14} L {cx+4},{Y+14} L {cx+12},{Y} L {cx+32},{Y}" fill="none" stroke="#343a46" stroke-width="1.4"/>')
    d.equip_tag(cx + (0 if cx != 250 else 0), 580, tag, svc)
d.equip_tag(1262, 650, "D-1403", "water separator")

# utility labels
d.txt(258, 296, "to D-1406 deaerator", size=9.5, fill=B)
d.txt(258, 552, "process condensate", size=9.5, fill=B)
d.txt(938, 296, "demin water out", size=9.5, fill=B)
d.txt(938, 552, "demin water in", size=9.5, fill=B)
d.txt(1098, 296, "CW return", size=9.5, fill=C)
d.txt(1098, 552, "CW supply", size=9.5, fill=C)

# line labels / destinations
d.txt(60, 450, "Wet syngas from", size=11, weight="bold", fill=G)
d.txt(60, 465, "E-1407 / MT shift", size=11, weight="bold", fill=G)
d.txt(1570, 188, "To PSA (H2 purification)", size=11, weight="bold", fill=G, anchor="end")
d.txt(1570, 118, "To flare", size=11, weight="bold", fill=d.RED, anchor="end")
d.txt(1570, 688, "Liquid water out", size=11, weight="bold", fill=B, anchor="end")

# ---------- instrument signals (before balloons)
d.lead(150, Y, 150, 372)
d.lead(370, Y, 370, 372)
d.lead(840, Y, 840, 478)
d.sig("M 840,522 L 840,616")                     # TT0055 -> TICA0055
d.sig("M 840,664 L 840,760 L 600,760 L 600,724") # TICA -> TY0055
d.sig("M 600,678 L 600,572")                     # TY -> fan B
d.sig("M 578,700 L 500,700 L 500,572")           # TY -> fan A
d.sig("M 622,700 L 700,700 L 700,572")           # TY -> fan C
d.lead(1010, Y, 1010, 372)
d.lead(1170, Y, 1170, 372)
d.lead(1350, 560, 1388, 560)
d.lead(1460, 200, 1460, 248)
d.sig("M 1438,270 L 1424,270")                   # PT -> PIC
d.sig("M 1400,246 L 1400,164")                   # PIC -> PV0017
d.lead(1530, 200, 1530, 248)

# ---------- control valve and balloons last
d.cvalve(1400, 130, "PV0017", fail="FO", actuator="below", tag_dy=-22)
d.bubble(150, 350, "TI", "026")
d.bubble(370, 350, "TI", "050")
d.bubble(840, 500, "TT", "0055")
d.bubble(840, 640, "TIC", "0055", shared=True)
d.bubble(600, 700, "TY", "0055")
d.bubble(1010, 350, "TI", "0059")
d.bubble(1170, 350, "TI", "0083")
d.bubble(1410, 560, "LI", "018")
d.bubble(1460, 270, "PT", "0017")
d.bubble(1400, 270, "PIC", "0017", shared=True)
d.bubble(1530, 270, "FI", "010")

# measured values next to tags (1 Jan 2026 -> 14 Nov 2026)
def val(x, y, s, anchor="middle"):
    d.txt(x, y, esc(s), size=9.5, fill="#7a3b00", weight="bold", anchor=anchor)
val(150, 310, "164 C")
val(370, 310, "143 -> 167 C")
val(868, 492, "70 -> 66 C", anchor="start")
val(868, 645, "SP 65 C", anchor="start")
val(628, 735, "fans 50% -> 88%", anchor="start")
val(1010, 310, "58 -> 56 C")
val(1170, 310, "38.8 C")
val(1432, 595, "water level", anchor="start")
val(1460, 314, "2.56 MPa(g)")
val(1530, 314, "~20,800 Nm3/h")
val(1555, 333, "(dry gas only;", anchor="end")
val(1555, 346, "misses flared gas)", anchor="end")
d.txt(860, 772, "temperature control: hotter outlet -> faster fans", size=9.5, fill=d.SUB)

d.notes(60, 800, "DESIGN BASIS (datasheet) AND PLANT DATA",
        ["Design: 135 -> 55 C, 2.69 MPa(g), design temp 170 C; 3 fans x 114,000 m3/h at 190 Pa; 226 m2 bare / 5,288 m2 fin area.",
         "Values in brown: plant data 1 Jan 2026 -> 14 Nov 2026 (PI). Water condenses from ~120-130 C down; D-1403 removes it.",
         "Conceptual drawing: relief valves, isolation/drain valves, UV0071 and line numbers omitted."], size=9.5)
d.legend([("Syngas (gas + condensing water)", G, False), ("Water / condensate", B, False),
          ("Cooling water", C, False), ("Steam", R, False), ("Control signal", d.SIG, True)],
         y=900, gap=250, size=11)
d.revision("Rev A  14-Nov-2026")
d.save("A-1401_section_PFD.svg")
import cairosvg
cairosvg.svg2png(url="A-1401_section_PFD.svg", write_to="A-1401_section_PFD.png", output_width=2400)
cairosvg.svg2png(url="A-1401_section_PFD.svg", write_to="/tmp/claude-0/-home-user/2cc34b7a-2b95-582d-8bec-1bb8972917b6/scratchpad/pfd_prev.png", output_width=1600)
print("ok")
