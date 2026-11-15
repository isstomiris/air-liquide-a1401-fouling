# A-1401 · 7-minute speech for four speakers

**Perovskite team · Air Liquide case · AIChE Student Hackathon 2026**

## Timing

| Speaker | Slides | Topic | Time |
|---|---|---|---|
| Speaker 1 | 1–5 | Object, problem, plant data | 1:40 |
| Speaker 2 | 6–11 | Thermal model, hybrid monitoring | 1:50 |
| Speaker 3 | 12–16 | Solutions and results | 1:30 |
| Speaker 4 | 17–24 | Economics, plan, safety | 2:00 |

Slides 25–27 are backup (repository, references, glossary). Don't present them; open them only for a question.

Speak at about 130 words a minute. If you run late, skip the lines marked *(optional)*.

---

## Speaker 1 · Problem (1:40)

**Slide 1 · Title (10 s)**
"Good morning. We are the Perovskite team. Our object is the air cooler A-1401 at Air Liquide's hydrogen unit UPOV-2 in Atyrau. The question: why it loses cooling every summer, and how to keep it clean."

**Slide 2 · Where A-1401 sits (25 s)**
"A-1401 cools wet syngas before the PSA. Atyrau air ranges from minus 20 to over 40 °C, and in May to July poplar fluff flies everywhere. 56 % of the cooler's duty is condensing water, so it is really a condenser."

**Slide 3 · How debris hurts (20 s)**
"Fluff sticks under the bottom tube row. Gaps close, the fans move less air, and the cooler moves less heat. On hot days the fans are already at 100 %, so the only control left is to cut gas flow."

**Slide 4 · Three years of data (25 s)**
"We turned three years of plant history into one number: equivalent blockage. Every summer it climbs 10 to 15 points, and every cleaning wins back 9 to 12. But a 50 to 60 % base never goes away."

**Slide 5 · Production impact (20 s)**
"Fans run at 100 % for about 40 % of the year. In hot weather the plant runs 25 to 35 % less gas, up to 800 tonnes of hydrogen in 2025. That is an upper bound, because demand may explain part of it."

> **Handover:** "To quantify this we built a model. [Speaker 2]."

---

## Speaker 2 · Model and monitoring (1:50)

**Slide 6 · How we model the cooler (20 s)**
"This is a physics model of the real bundle: 6 rows by 24 cells, with water condensation in every cell. The energy balance closes to 0.001 %, and the error on weeks the model never saw is 2.4 K."

**Slide 7 · Air side and fin efficiency (15 s)**
"On the air side we use the Briggs–Young correlation, which gives 49 W/m²K. Schmidt's method gives a fin efficiency of 0.86. By the end of summer, air-side conductance falls from 224 to 85 kW/K."

**Slide 8 · Fan and system curves (15 s)**
"Where the fan curve meets the system curve, 30 % blockage costs only 17 % of the airflow. At 68 % blockage, only 45 % of the air gets through."

**Slide 9 · Energy balance (10 s)** *(optional)*
"The heat the gas loses equals the heat the air gains: 4,242 kW clean, against 3,529 kW fouled."

**Slide 10 · Hybrid monitoring (25 s)**
"Before choosing a cleaning method, operators need to know how dirty the cooler is. Our hybrid model does two things. The physics part turns every hour of PI data into a health number. Then a gradient-boosting model forecasts it 7, 14 and 30 days ahead and raises an alarm. It needs no new instruments."

**Slide 11 · Prediction tested (25 s)**
"On a cycle it never saw, the alarm fired 17 days before the 40 % cliff, with no false alarms. On real plant data fouling moves slowly, so the forecast only ties with 'no change'. Its main value is the hourly health number."

> **Handover:** "Now, how do we clean? [Speaker 3]."

---

## Speaker 3 · Solutions and results (1:30)

**Slide 12 · Comparison (20 s)**
"We compared five methods. Compressed air leaves debris behind, water causes chloride cracking on hot 304L, and chemicals attack the aluminium fins. We picked two dry, online methods: sonic horns with a spray coating, and DECAMEX dry powder."

**Slide 13 · Clean vs fouled (20 s)**
"On a real hot day the outlet is 37 °C clean and 75 °C fouled, and the gas the cooler can handle at 65 °C halves."

**Slide 14 · Validation (15 s)**
"We checked the model against the plant's own 2026 cleaning. It predicted 59.5 °C, and the plant measured 56.9."

**Slide 15 · Duty recovered (20 s)**
"DECAMEX recovers 242 kW, which is plus 16 % gas capacity. Horns recover 166 kW, plus 10 %. Neither beats a full clean, but both run online, without a shutdown."

**Slide 16 · Whole season (15 s)**
"Replayed hour by hour over summer 2025, the outlet is above 65 °C for about 1,000 fewer hours."

> **Handover:** "What does it cost? [Speaker 4]."

---

## Speaker 4 · Economics, plan, safety (2:00)

**Slide 17 · Economics (30 s)**
"We built the cost line by line with Atyrau unit rates: the National Bank exchange rate, the local power tariff and local wages. Spray coating plus horns costs 93,500 dollars and pays back in 1.1 years. DECAMEX starts for 6,400, but each campaign costs 30,000 because the crew flies in. This is a Class 4 estimate, minus 30 to plus 50 %."

**Slide 18 · Turnaround compared (20 s)**
"A wash during a planned turnaround is cheapest, about 11,500 dollars. But if it needs its own 3-day stop, that loses 80 tonnes of hydrogen. Our methods run during the season."

**Slide 19 · Lead time (10 s)**
"A DECAMEX trial is possible in 4 to 8 weeks, and a spray-coated test bay in 6 to 10."

**Slide 20 · Recommendation (20 s)**
"Monitor all year and clean before the peak. Start with a half-square-metre pilot on real fluff before the 2027 season. Inspect a cleaned bundle to explain the 50 % base."

**Slide 21 · Safety verdict (20 s)**
"DECAMEX passes for a controlled trial. The coating and horn retrofit does not pass yet. The 120 Hz horn sits close to a tube vibration mode, and the original 200 °C cure was above the 170 °C design limit. Our spray cures below 170 °C."

**Slides 22–24 · Safety detail (15 s)** *(show quickly)*
"These slides hold the calculations: tube modes, a 15.6 MPa hoop stress, the fan-off check, and a pass, conditional or hold verdict for every step."

**Close (5 s)**
"Thank you. All data, code and calculations are behind the QR code."

---

## Hard terms: plain meaning to have ready

| Term | Say it like this |
|---|---|
| Equivalent blockage *b* | The share of air gaps the model must close to match the measured outlet. It includes debris and anything else the model misses. |
| UA | Heat moved per degree of temperature difference, in kW/K. |
| Duty | Heat removed, in kW. |
| Fin efficiency η<sub>f</sub> | How much of the fin is as good as the tube surface. 0.86 means 86 %. |
| Briggs–Young | A standard correlation for the air-side coefficient on finned tubes. |
| Fan / system curve | Where the fan's pressure equals the bundle's resistance. That point sets the airflow. |
| PSA | Pressure swing adsorption, the hydrogen purifier downstream. |
| Health indicator | The hourly blockage number from the physics model. |
| Gradient boosting | Many small decision trees added together. It works with little data. |
| Conformal band | An uncertainty band calibrated so 80 % of outcomes fall inside. |
| Backtest | Pretend it's a past date, forecast, then compare with what really happened. |
| NPV / IRR | Value of future cash today at 10 %; the interest rate at which the project breaks even. |
| Class 4 estimate | The industry standard (AACE) for feasibility-stage costs, accurate to −30 / +50 %. |
| Modal / natural frequency | The frequency at which a tube likes to vibrate. A horn near it can cause fatigue. |
| Hoop stress | Stress in the tube wall from internal pressure. |
| HAZOP / HAZID | Structured team reviews that find hazards before work starts. |
| Chloride stress cracking | Cracks in hot stainless steel where salty water evaporates. |

---

## Likely questions

### Axel Schmidt · Operations Director

1. **"Is the 25–35 % gas loss really the cooler, or just lower demand?"**
   We call it an upper bound. Fans are at 100 % in those hours and the outlet is at its limit, which points to cooling. Separating demand needs the production plan, and we'd welcome it.
2. **"Can we stop one fan while running at full load?"**
   Not proven yet. Our sensitivity puts the outlet between 70.9 and 86.6 °C. So we propose a verified load and weather window, or a trial with the cooler isolated.
3. **"Will horns damage the tubes?"**
   They might. Our screen shows a tube mode 7.2 % from 120 Hz, which is why horns are on hold until a strain test.
4. **"Why not just clean at the turnaround?"**
   It cleans best, but turnarounds are fixed and the goal is longer runs between them. An extra 3-day stop costs about 80 t of H₂.
5. **"How does the monitor fit our PI system?"**
   It uses 5 existing tags plus weather, runs hourly, and stays advisory, with no control action.
6. **"What is the 50–60 % base?"**
   It's unknown. It could be louvres, fan wear, damaged fins or model offset. Inspecting a cleaned bundle would tell.

### Ulvi Umiraliyeva · Director, Atyrau plant

1. **"Are these costs realistic for Atyrau?"**
   They are built from local rates: the NBK exchange rate, the Atyrau Energo tariff and Atyrau wage statistics. The two lines that need quotes are the horn price and the DECAMEX day rate.
2. **"Can local suppliers do it?"**
   The coating material, spray crew, scaffold and frames can all be local. The horns are imported, with a 10–16 week lead time. DECAMEX is a French service.
3. **"What do you need from the plant?"**
   Three things: cleaning dates and method, a D-1403 condensate measurement, and permission for a 0.5 m² patch trial.
4. **"When could this run?"**
   A DECAMEX trial in 4–8 weeks, before the 2027 fluff season.
5. **"Water is scarce here. Does this need water?"**
   No. Both methods are dry. That's one reason we rejected washing.
6. **"Which Kazakh regulations apply?"**
   We used international references such as HSE and OSHA. Kazakh law and Air Liquide standards govern, and the plant's HSE team would confirm them.

### Assel Yermekova · HR

1. **"How did you split the work?"**
   Each speaker owned a block: the problem, the model and monitoring, the solutions, and economics and safety. Give one concrete example of each person's role.
2. **"What was hardest?"**
   Messy plant data and a frozen export, plus learning wet condensation physics.
3. **"Did you use AI tools?"**
   Yes, as the case brief permits. We checked the results against plant data and hand calculations, and we can explain every number.
4. **"What did you learn?"**
   That the cheapest fix on paper (a turnaround wash) isn't the best for operations. Timing matters more than cleaning power.
5. **"Why Air Liquide?"**
   Give a personal answer: a real plant in Kazakhstan, and hydrogen.

---

## If you don't know, or don't remember

- **Don't guess a number.** Say: *"I don't want to give you a wrong figure. It's in our calculations file, and we can send it today."* Then point to the QR code or the backup slide.
- **Hand over.** Say: *"[Name] built that part. [Name], can you take it?"* Agree beforehand who covers what.
- **Bridge to what you do know.** Say: *"We didn't model that directly. What we can say is…"* and give the nearest result.
- **Name the limit, then the next step.** Say: *"That's outside the data we had. We'd answer it with [a strain test / the condensate measurement / a vendor quote]."* Judges value honesty about limits.
- **Clarify the question.** Say: *"Do you mean the cost per campaign or per year?"* This buys time and avoids answering the wrong question.
- **Look at the slide.** Most numbers are on it. Say: *"As on slide 17…"*
- **Never contradict a teammate on stage.** Add to the answer instead: *"To add to that…"*

### Numbers worth memorising

37 → 75 °C · 56 % condensing · 25–35 % less gas · 700–800 t H₂ · +242 kW / +166 kW · 1,000 fewer hours above 65 °C · alarm 17 days early · 93,500 USD and 1.1 years · 6,400 + 30,215 USD per campaign · 80 t H₂ per 3-day stop · 120 Hz vs 112 Hz · 170 °C design limit
