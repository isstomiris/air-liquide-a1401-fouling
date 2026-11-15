import sys; sys.path.insert(0,'economics')
from estimate_class4 import *
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
wb=Workbook()
H=Font(bold=True,color="FFFFFF"); HF=PatternFill("solid",fgColor="0A3A75"); B=Font(bold=True)
IN=Font(color="0000FF"); thin=Side(style="thin",color="D6DCDF")
def hdr(ws,row,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(row,i,v); c.font=H; c.fill=HF; c.alignment=Alignment(wrap_text=True,vertical="center")
# Rates
r=wb.active; r.title="Rates"
r["A1"]="A-1401 cost estimate: unit-rate basis (AACE 18R-97 Class 4, accuracy -30 % / +50 %), Atyrau, Nov 2026"; r["A1"].font=Font(bold=True,size=12)
hdr(r,3,["Rate","Value","Unit","Source"])
rows=[("Exchange rate",444.3,"KZT/USD","National Bank of Kazakhstan, official rate 15 Nov 2026"),
("Electricity tariff",40.20,"KZT/kWh excl. VAT","Atyrau Energo, producers of goods/services, from 1 Dec 2024 (kept for 2026)"),
("Average wage, Atyrau industry",638696,"KZT/month","Bureau of National Statistics, 2025"),
("Average wage, Atyrau mining & quarrying",949524,"KZT/month","Bureau of National Statistics, 2025"),
("Working hours",166.5,"h/month","40-h week"),
("Employer taxes and contributions",1.25,"factor","team assumption (social tax, contributions, health insurance)"),
("Contractor overhead and margin",1.5,"factor","team assumption"),
("Engineering overhead and margin",1.6,"factor","team assumption"),
("Contingency",0.20,"fraction of direct","Class 4 practice"),
("Owner's costs",0.05,"fraction of direct","project management, procurement"),
("H2 benefit, illustrative",95.81,"t/yr","3,000 Nm3/h x 600 h x 0.0532 kg/Nm3"),
("H2 contribution margin",1.0,"USD/kg","team central case"),
("Discount rate",0.10,"","team assumption"),]
for i,(a,v,u,s) in enumerate(rows,4):
    r.cell(i,1,a); c=r.cell(i,2,v); c.font=IN; r.cell(i,3,u); r.cell(i,4,s)
r["A18"]="Derived"; r["A18"].font=B
der=[("Power, USD/kWh","=B5/B4"),("Plant staff, USD/h","=B6/B8/B4*B9"),("Contractor crew, USD/h","=B19*0+B6/B8/B4*B9*B10"),("Engineer, USD/h","=B7/B8/B4*B9*B11")]
for i,(a,f) in enumerate(der,19):
    r.cell(i,1,a); r.cell(i,2,f).number_format="0.00"
r["B21"]="=B6/B8/B4*B9*B10"
for col,w in zip("ABCD",(42,14,22,70)): r.column_dimensions[col].width=w
REF={ENG:"Rates!$B$22",LAB_CON:"Rates!$B$21",LAB_OWN:"Rates!$B$20"}
def sheet(name,lines,cont_rows=True):
    ws=wb.create_sheet(name); hdr(ws,1,["Section","Item","Qty","Unit","Unit rate, USD","Amount, USD","Basis"])
    for i,(sec,it,q,u,rate,bas) in enumerate(lines,2):
        ws.cell(i,1,sec); ws.cell(i,2,it); c=ws.cell(i,3,q); c.font=IN; ws.cell(i,4,u)
        rr=next((v for k,v in REF.items() if abs(k-rate)<1e-9),None)
        c=ws.cell(i,5,"="+rr if rr else rate); c.number_format="#,##0.00"
        if not rr: c.font=IN
        ws.cell(i,6,f"=C{i}*E{i}").number_format="#,##0"; ws.cell(i,7,bas)
    n=len(lines)+1; t=n+2
    ws.cell(t,2,"Direct cost").font=B; ws.cell(t,6,f"=SUM(F2:F{n})").number_format="#,##0"
    if cont_rows:
        ws.cell(t+1,2,"Contingency"); ws.cell(t+1,6,f"=F{t}*Rates!$B$12").number_format="#,##0"
        ws.cell(t+2,2,"Owner's costs"); ws.cell(t+2,6,f"=F{t}*Rates!$B$13").number_format="#,##0"
        ws.cell(t+3,2,"Total estimate").font=B; ws.cell(t+3,6,f"=SUM(F{t}:F{t+2})").number_format="#,##0"; ws.cell(t+3,6).font=B
        ws.cell(t+4,2,"Range -30 % / +50 %"); ws.cell(t+4,6,f'=TEXT(F{t+3}*0.7,"#,##0")&" - "&TEXT(F{t+3}*1.5,"#,##0")')
        tot=f"'{name}'!F{t+3}"
    else:
        ws.cell(t+1,2,"Contingency"); ws.cell(t+1,6,f"=F{t}*Rates!$B$12").number_format="#,##0"
        ws.cell(t+2,2,"Cost per campaign").font=B; ws.cell(t+2,6,f"=F{t}+F{t+1}").number_format="#,##0"
        tot=f"'{name}'!F{t+2}"
    for col,w in zip("ABCDEFG",(26,52,8,9,14,14,40)): ws.column_dimensions[col].width=w
    return tot
t1=sheet("S1 CAPEX",S1); t2=sheet("S2 readiness",S2); t3=sheet("S2 per campaign",S2_CAMP,False)
o=wb.create_sheet("S1 OPEX"); hdr(o,1,["Item","Qty / yr","Unit","Unit rate, USD","Amount, USD"])
b=build()
for i,(it,q,u,rate) in enumerate(b["s1_opex_lines"],2):
    o.cell(i,1,it); o.cell(i,2,q).font=IN; o.cell(i,3,u)
    rr={KWH:"Rates!$B$19",LAB_OWN:"Rates!$B$20"}
    ref=next((v for k,v in rr.items() if abs(k-rate)<1e-9),None)
    o.cell(i,4,"="+ref if ref else rate).number_format="#,##0.00"; o.cell(i,5,f"=B{i}*D{i}").number_format="#,##0"
n=len(b["s1_opex_lines"])+1; o.cell(n+2,1,"Annual OPEX").font=B; o.cell(n+2,5,f"=SUM(E2:E{n})").number_format="#,##0"
s1op=f"'S1 OPEX'!E{n+2}"
for col,w in zip("ABCDE",(48,10,8,14,14)): o.column_dimensions[col].width=w
# Summary
s=wb.create_sheet("Summary",0); s["A1"]="A-1401 economics summary (USD)"; s["A1"].font=Font(bold=True,size=12)
hdr(s,3,["","S1 spray coating + horns","S2 DECAMEX"])
lines=[("Initial cost",f"={t1}",f"={t2}"),("Annual OPEX",f"={s1op}",f"=2*{t3}"),
("Annual benefit (H2 x margin)","=Rates!$B$14*Rates!$B$15*1000","=Rates!$B$14*Rates!$B$15*1000"),
("Net annual cash","=B6-B5","=C6-C5"),("Simple payback, yr","=B4/B7","=C4/C7"),
("5-yr NPV","=-B4+NPV(Rates!$B$16,B7,B7,B7,B7,B7)","=-C4+NPV(Rates!$B$16,C7,C7,C7,C7,C7)"),
("H2 needed for 3-yr payback, t/yr","=(B5+B4/3)/1000/Rates!$B$15","=(C5+C4/3)/1000/Rates!$B$15")]
for i,(a,f1,f2) in enumerate(lines,4):
    s.cell(i,1,a); s.cell(i,2,f1).number_format="#,##0.00" if "payback" in a or "t/yr" in a else "#,##0"; s.cell(i,3,f2).number_format=s.cell(i,2).number_format
s["A13"]="IRR, 5 yr"; 
for col,c in (("B","B"),("C","C")):
    pass
s["A15"]="Cash flow for IRR"; 
for j in range(6):
    s.cell(16,j+2,"=-B4" if j==0 else "=B7"); s.cell(17,j+2,"=-C4" if j==0 else "=C7")
s["A16"]="S1, years 0-5"; s["A17"]="S2, years 0-5"
s["B13"]="=IRR(B16:G16)"; s["C13"]="=IRR(C17:H17,0.5)"; s["C13"]="=IRR(B17:G17,3)"
s["B13"].number_format=s["C13"].number_format="0%"
s["A19"]="Accuracy: AACE 18R-97 Class 4 (-30 % / +50 %). Team estimate from public unit rates; not vendor quotes."
s.column_dimensions["A"].width=40; s.column_dimensions["B"].width=26; s.column_dimensions["C"].width=20
wb.save("economics/A1401_cost_estimate_Class4.xlsx"); print("ok")
