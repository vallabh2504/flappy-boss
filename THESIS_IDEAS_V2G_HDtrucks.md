# Thesis Idea Map — V2G / Bidirectional Charging for Heavy-Duty Truck Depots
### TRATON / MAN R&D · "UnPlugged Energisers" · Efficient Transport
**Prepared:** 19 June 2026 · Author context: M.Sc. Automotive Engineering, RWTH Aachen · 7–8 month thesis window

> This document is written for *you* to imagine and choose. It is opinionated. Each idea has a flow diagram
> (Mermaid — renders in GitHub, VS Code "Markdown Preview Mermaid Support", Obsidian, Typora). At the end there is
> a single **recommended fused thesis** with a timeline, plus the questions we need to answer to lock the scope.

---

## 0. The one thing that changes everything: *your* unfair advantages

Most V2G theses are written by people who have **none** of the three assets you have. Your novelty should be built
on these, not on "a bigger model":

| Asset | Why it is rare | What it unlocks |
|---|---|---|
| **You sit inside the OEM that writes the battery warranty** | Academics model the *owner's* fear ("will V2G void my warranty?"). Nobody optimizes from the *OEM's* side, where the warranty is a **design variable**. | Warranty-budget-coupled dispatch + warranty *product* co-design (Idea 2). |
| **Real truck + charger + a few days of real V2G** | Almost every degradation model in V2G optimization is calibrated on **lab cells** (18650 / small pouch), then scaled. Nobody closes the loop on a real HD pack under *commanded* V2G. | Sim-to-real calibration / residual learning (Idea 1) — this is your credibility anchor. |
| **EU + China is in your job description** | Most comparisons are descriptive tables. | A reusable **policy compiler** (Idea 5) — an internal TRATON market-entry tool, not just a thesis chapter. |

**Hard truth on novelty (verified against current literature):** "Add a battery-aging layer," "build a digital twin,"
"do MPC instead of MILP," "compare NMC vs LFP," and "chance-constrained FCR bidding" are **all already published**.
A thesis that only does those is *good engineering, weak research*. The novelty has to live in a **new decision
function**, and the digital twin must be demoted to "the validation environment," not "the contribution."

---

## 1. The layered platform (your digital twin = the *lab*, not the *result*)

Build this once. Every idea below is a *function* that plugs into it. This framing lets you honestly say "the twin is
the apparatus; my contribution is function X tested in it."

```mermaid
flowchart TB
    subgraph L1["L1 · Mission / Duty Layer"]
        M1["Vehicle mass, payload<br/>route topography, road type"]
        M2["Ambient temp, HVAC/aux load"]
        M3["Arrival SoC, departure deadline<br/>charger compatibility (CCS/MCS)"]
        M4["Vehicle history:<br/>age, mileage, cumulative throughput, current SoH"]
    end
    subgraph L2["L2 · Electro-Thermal-Aging Layer"]
        A1["Pack model (NMC-811 / LFP)"]
        A2["Semi-empirical aging:<br/>calendar f(SoC,T,t) + cycle f(DoD,C-rate,T)"]
        A3["Thermal model (pack temp rise under C-rate)"]
    end
    subgraph L3["L3 · Market / Regulation Layer"]
        R1["SDAC 15-min day-ahead prices"]
        R2["Intraday + ancillary (FCR/aFRR/mFRR)"]
        R3["Grid fees, §14a, EnWG-2026 single-fee, taxes"]
        R4["Country profile: DE / NL / FR / CN"]
    end
    subgraph L4["L4 · Optimizer Layer (swappable)"]
        O1["MILP (perfect-foresight upper bound)"]
        O2["Rolling MPC (24h horizon)"]
        O3["Stochastic / chance-constrained"]
        O4["Rule-based fallback (firmware-realistic)"]
    end
    subgraph L5["L5 · Uncertainty / Forecast Layer"]
        U1["Price forecast error"]
        U2["Arrival/departure jitter"]
        U3["Route energy consumption variance"]
        U4["§14a curtailment events"]
    end
    subgraph L6["L6 · Validation Layer  ★ your edge"]
        V1["Real truck + charger V2G test"]
        V2["Measured: RT efficiency map, power taper,<br/>V2G response delay, thermal rise"]
        V3["Calibrate / correct L2 & L4 parameters"]
    end
    L1 --> L4
    L2 --> L4
    L3 --> L4
    L5 --> L4
    L4 --> OUT["Dispatch decision +<br/>per-asset value attribution (duals)"]
    L6 -. corrects .-> L2
    L6 -. corrects .-> L4
    OUT --> DASH["High-viz dashboard:<br/>€/truck, SoH trajectory, revenue by country/market"]
```

---

## 2. The ideas (ranked, each with a flow diagram)

Ordering = my recommendation for **novelty × feasibility × TRATON value**, given your assets.

---

### ⭐ Idea 1 — Sim-to-Real "Degradation Twin Calibration" (your credibility anchor)

**The gap:** V2G economics swing entirely on the degradation cost per kWh. Yet that number is almost always taken from
**lab cells** and assumed to transfer to a 400+ kWh truck pack. It does not — pack-level thermal gradients, BMS
balancing, contactor/inverter losses and real C-rate tapers differ. Nobody has published a **measured-stress →
degradation** calibration for a real *heavy-duty* pack under *commanded* bidirectional events.

**The new function:** A calibration layer that runs your few-day V2G test, extracts the *measured* stress signatures
(RT-efficiency map, power taper curve, V2G command→delivery delay, pack temperature rise per C-rate), and computes the
**residual** between your in-house lab aging model's prediction and the real pack behaviour. Output: a *corrected,
truck-specific* degradation cost surface that the optimizer then uses.

**Why TRATON cares:** Every euro of the V2G business case rests on this number. You turn an *assumed* parameter into a
*measured* one — de-risking the entire Energisers value proposition. This is the part of the thesis that *only you* can do.

```mermaid
flowchart LR
    LAB["In-house lab aging model<br/>(cell-level, NMC/LFP)"] --> PRED["Predicted stress→fade"]
    subgraph TEST["Few-day real truck + charger V2G test"]
        T1["Commanded charge/discharge profiles<br/>(vary C-rate, DoD, SoC window)"]
        T2["Measure: RT efficiency, taper,<br/>response delay, ΔT, dV/dQ"]
    end
    T1 --> T2 --> MEAS["Measured stress signatures"]
    PRED --> RES{"Residual =<br/>measured − predicted"}
    MEAS --> RES
    RES --> CORR["Truck-specific corrected<br/>degradation cost surface c(SoC,DoD,C,T)"]
    CORR --> OPT["Feeds Optimizer Layer L4"]
    RES --> INSIGHT["Insight: where lab models<br/>over/under-estimate pack life"]
```

**Feasibility:** HIGH for the *stress-signature* measurement (efficiency, taper, delay, thermal — measurable in days).
MEDIUM for *capacity-fade* measurement (true fade needs weeks/months — so you measure *stress proxies*, not fade itself,
and validate that the proxies match the model's inputs). Be honest about this in the thesis; it is still novel.

---

### ⭐⭐ Idea 2 — Warranty-Budget-Coupled V2G Dispatch (the OEM-only idea)

**The gap (verified):** Existing warranty+V2G work is **owner-side** — "performance guarantees," "will my capacity drop."
The **OEM-side** question is unaddressed: *MAN writes the warranty* (e.g., 80% SoH at N years **or** Y kWh throughput,
whichever first). V2G *spends* that warranty budget. How should the optimizer treat **remaining warranty throughput as a
depletable, shadow-priced resource** — and what **warranty product structure** makes V2G net-positive for *both* MAN and
the fleet operator? This couples **controller design to contract design**. That coupling, for HD trucks, from the OEM
seat, is genuinely open.

**The new function:** Add a warranty-state variable `W(t)` (remaining guaranteed throughput / equivalent full cycles).
Each V2G kWh draws down `W`. The MILP/MPC dual on the `W`-constraint is the **shadow price of warranty** — the true
marginal cost of cycling. Then run **contract co-design**: simulate warranty products (flat, throughput-metered,
"V2G-miles," reservation-only for NMC) and find which maximizes joint OEM+fleet surplus.

```mermaid
flowchart TB
    WARR["Warranty contract<br/>SoH≥80% at min(N years, Y kWh)"] --> BUDGET["Warranty budget W(t)<br/>= remaining guaranteed throughput"]
    BUDGET --> CONS["Constraint in optimizer:<br/>Σ V2G throughput ≤ W(t)"]
    PRICES["Market revenue (arb/FCR/V2B)"] --> OBJ["Objective:<br/>max revenue − degradation − warranty drawdown"]
    CONS --> OBJ
    OBJ --> SOLVE["Solve MILP / MPC"]
    SOLVE --> DUAL["Dual variable on W →<br/>SHADOW PRICE OF WARRANTY (€/kWh)"]
    DUAL --> DECIDE{"Is market revenue ><br/>warranty shadow price?"}
    DECIDE -- yes --> DO["Dispatch V2G"]
    DECIDE -- no --> HOLD["Preserve warranty / idle"]
    SOLVE --> COD["Contract co-design loop:<br/>test warranty product variants"]
    COD --> SURPLUS["Joint OEM+fleet surplus per product"]
    SURPLUS --> REC["Recommended warranty product for V2G fleets"]
```

**Why this is the headline:** It is publishable (it reframes V2G as a *contract-bounded* control problem), and it is
directly a **MAN sales + product-policy artifact**: "here is the warranty we should offer V2G fleets, and here is why it
makes money for everyone." Nobody outside an OEM can credibly write this chapter.

---

### ⭐⭐ Idea 3 — Manufacturing Firm Ancillary Capacity by Duty-Cycle Co-Scheduling

**The gap (verified):** FCR needs **firm** capacity over a product window; trucks leave the depot, so naive availability
is too random. Existing EV-FCR papers treat availability as **exogenous** and bid under it with chance constraints
(Nordic, light-duty). Nobody **shapes the logistics** to *create* firm capacity. A *depot* operator can stagger
departures / hold a rotating sub-fleet back to guarantee an always-plugged-in pool — turning availability from a
**constraint into a decision variable**, co-optimized with logistics feasibility, then **VPP-aggregated** across depots
for statistical smoothing.

**The new function:** Joint optimization of `{route/departure feasibility} × {firm FCR capacity commitment}`, with a
reliability target (e.g. P99 that committed MW is deliverable), aggregated over multiple depots.

```mermaid
flowchart TB
    subgraph DEPOTS["Multi-depot fleet (VPP)"]
        D1["Depot A trucks"]
        D2["Depot B trucks"]
        D3["Depot C trucks"]
    end
    DEPOTS --> AVAIL["Availability profiles<br/>(stochastic presence)"]
    LOG["Logistics constraints:<br/>routes, deadlines, driver hours"] --> JOINT
    AVAIL --> JOINT["JOINT optimizer:<br/>shape departures to guarantee<br/>a rotating always-plugged sub-fleet"]
    JOINT --> FIRM["Firm capacity C_firm with P99 reliability"]
    FIRM --> BID["FCR / aFRR capacity bid"]
    BID --> REV["Ancillary revenue (the 55–65% slice)"]
    JOINT --> FEAS{"Logistics still feasible?"}
    FEAS -- no --> RELAX["Reduce committed MW"]
    FEAS -- yes --> REV
    REV --> COMP["Compare: arbitrage-only vs<br/>arbitrage+firm-FCR economics"]
```

**Feasibility:** MEDIUM–HIGH (data-driven; no extra hardware). **TRATON value:** CRITICAL — ancillary services are the
majority of stationary-storage revenue in Germany; this is the literal product the Energisers team would sell.

---

### ⭐ Idea 4 — Value-of-Fidelity / Minimum-Viable-Twin Study

**The gap:** Everyone adds layers; *nobody asks which layers actually change the decision.* "How much model complexity is
needed before the **dispatch decision and the € outcome stop improving**?" is methodologically elegant and under-studied.

**The new function:** Systematic ablation — strip layers (hourly vs 15-min, linear vs nonlinear aging, deterministic vs
stochastic, calendar aging on/off, thermal on/off) and measure the **decision regret** and **€ error** each adds.

```mermaid
flowchart LR
    FULL["Full-fidelity twin<br/>(all layers ON)"] --> BASE["Baseline € + dispatch"]
    FULL --> ABL["Ablate one layer at a time"]
    ABL --> A1["− nonlinear aging"]
    ABL --> A2["− 15-min (use hourly)"]
    ABL --> A3["− stochastic (use deterministic)"]
    ABL --> A4["− thermal"]
    A1 & A2 & A3 & A4 --> REG["Measure decision regret<br/>and € error vs baseline"]
    REG --> RANK["Rank layers by decision value"]
    RANK --> SPEC["Output: minimum controller spec<br/>for MAN CMS firmware"]
```

**Why TRATON cares:** Directly answers "what must our on-board/CMS optimizer actually compute vs. academic decoration?"
This is a *firmware specification* deliverable. Excellent as a **supporting chapter** to Idea 1/2.

---

### ⭐⭐ Idea 5 — EU↔China "Policy Compiler" (required by your job, made novel)

**The gap:** Country comparisons are descriptive. Make it a **compiler**: input tariff structure + regulation + battery
mix → output an **optimizer configuration** (which strategy layers are profitable, in what order) + a single normalized
**Charging-Cost-Structure Index** ranking markets.

```mermaid
flowchart LR
    IN["Inputs per market:<br/>TOU tariff, capacity charge,<br/>grid-fee rule, V2G/ancillary access,<br/>battery chemistry mix"] --> COMP["Policy Compiler<br/>(rule engine)"]
    COMP --> CFG["Optimizer config:<br/>enable {TOU shift, peak-shave, V2G, FCR, PV}<br/>+ parameter set"]
    CFG --> RUN["Run twin per market"]
    RUN --> CCSI["Charging-Cost-Structure Index<br/>(normalized strategy ranking)"]
    CCSI --> DE["DE (post-EnWG-2026)"]
    CCSI --> NL["NL (V2G-mature)"]
    CCSI --> FR["FR (no double fee)"]
    CCSI --> CN["CN (different market design)"]
    DE & NL & FR & CN --> TOOL["Reusable TRATON market-entry tool<br/>(India/Brazil/US later)"]
```

**Why TRATON cares:** Becomes an **internal benchmarking tool**, reusable for any future market — far more than a thesis
table. Strong as the **breadth chapter** alongside a deep core idea.

---

### Idea 6 — Per-Truck Flexibility-Value Attribution ("shadow-price bill")

**The gap:** Fleet operators get one bill and cannot see *which truck* caused cost. MILP **dual variables** give the
marginal cost contribution of each truck/charger/chemistry **for free** in every solve — but no tool surfaces them as
operational intelligence.

```mermaid
flowchart LR
    SOLVE["Solved depot MILP"] --> DUALS["Extract dual variables<br/>(per constraint)"]
    DUALS --> ATTR["Attribute € to each truck/charger"]
    ATTR --> MSG["'Truck T07 cost €23 extra:<br/>arrived low-SoC, forced peak charging'"]
    MSG --> USE1["Driver incentives"]
    MSG --> USE2["Route replanning"]
    MSG --> USE3["Where to add chargers"]
```

**Verdict:** Lovely **product feature** and a clean "novel output" deliverable, but thin as a *standalone* thesis. Use it
as the **interpretable-output layer** of Idea 2 (the warranty shadow price is the same mathematics). This is your
"function developer" deliverable.

---

### Idea 7 — Future-Scenario Stress Layer (2030 / 2040 / 2050)

**The gap / correct framing:** Don't predict "free electricity in 50 years." The literature points to **lower average
wholesale prices but more frequent zero/negative-price hours and higher short-term volatility** under deep
renewables. A V2G controller's value then shifts from *price minimization* to *volatility & surplus-window timing*.

```mermaid
flowchart TB
    NOW["2026 baseline<br/>15-min SDAC, EnWG single fee, §14a"] --> S30["2030–35 scenario:<br/>more negative-price hours"]
    S30 --> S40["2040 scenario:<br/>high volatility, deep RES"]
    S40 --> S50["2050 scenario:<br/>low avg price, frequent zero-price windows"]
    S30 & S40 & S50 --> TEST["Run SAME optimizer on each"]
    TEST --> Q["Does V2G value survive?<br/>Does optimal strategy shift<br/>from arbitrage → flexibility timing?"]
    Q --> ROBUST["Robustness / future-proofing finding"]
```

**Verdict:** Great **discussion / future-work chapter** that makes the thesis feel forward-looking. Keep it as scenarios,
not predictions. Not a standalone thesis.

---

## 3. Novelty & priority matrix

| # | Idea | Novelty | Feasibility (7–8 mo) | TRATON value | Needs real truck? | Role |
|---|---|---|---|---|---|---|
| 1 | Sim-to-real degradation calibration | **High** | Med–High | **High** (de-risks business case) | **Yes** | Validation anchor |
| 2 | Warranty-budget-coupled dispatch | **Very High** | Medium | **Critical** (OEM product/policy) | Helpful | **Headline** |
| 3 | Firm ancillary via duty-cycle co-sched | **High** | Med–High | **Critical** (revenue) | No | Strong core/stretch |
| 4 | Value-of-fidelity / min-viable twin | High | High | High (firmware spec) | No | Supporting |
| 5 | EU↔China policy compiler | Medium–High | High | High (market entry) | No | Breadth chapter |
| 6 | Per-truck shadow-price attribution | Medium–High | High | High (product feature) | No | Output layer |
| 7 | Future-scenario stress | Medium | High | Medium | No | Discussion |

---

## 4. ⭐ Recommended fused thesis

> **"Warranty-Aware, Empirically-Calibrated V2G Dispatch for Heavy-Duty Truck Depots — with a Cross-Market (EU/China) Decision Compiler"**

This fuses **Idea 2 (headline novelty) + Idea 1 (your real-truck credibility anchor) + Idea 6 (interpretable output) +
Idea 5 (breadth, job requirement)**, with **Idea 4** as a tight supporting chapter and **Idea 3 / Idea 7** as clearly
labelled stretch / future work. It is sharp, OEM-unique, uses every one of your unfair advantages, and is defensible to
both RWTH and TRATON.

**The single research question:**
> *How should a heavy-duty truck depot dispatch V2G when the battery warranty is a depletable, shadow-priced contractual
> resource — and what warranty product makes V2G net-positive for both the OEM and the fleet — validated against measured
> behaviour of a real truck pack and generalized across EU and Chinese market structures?*

**Contribution stack:**
1. **Method:** warranty-budget state + shadow-price-of-warranty in the optimizer (new).
2. **Empirics:** real-truck stress calibration correcting the in-house aging model (new, your edge).
3. **Product/policy:** warranty-product co-design → recommended V2G warranty for MAN (new, OEM-only).
4. **Generalization:** EU/China policy compiler + per-truck value attribution (reusable tools).

```mermaid
flowchart TB
    START["Month 0: scope + data access locked"] --> P1
    subgraph PHASE1["Phase 1 · Platform + Baseline (M1–M2)"]
        P1["Reproduce baseline depot MILP<br/>+ 15-min SDAC + EnWG-2026 rules"]
    end
    subgraph PHASE2["Phase 2 · Real-Truck Test (M2–M3)  ★edge"]
        P2["Design + run few-day V2G test<br/>measure efficiency/taper/delay/thermal"]
        P2b["Calibrate aging model (Idea 1)"]
    end
    subgraph PHASE3["Phase 3 · Headline Method (M3–M5)"]
        P3["Add warranty budget + shadow price (Idea 2)"]
        P3b["Per-truck attribution via duals (Idea 6)"]
    end
    subgraph PHASE4["Phase 4 · Generalize (M5–M6)"]
        P4["EU/China policy compiler (Idea 5)"]
        P4b["Value-of-fidelity ablation (Idea 4)"]
    end
    subgraph PHASE5["Phase 5 · Synthesize (M6–M8)"]
        P5["Warranty product co-design + recommendation"]
        P5b["Future scenarios (Idea 7) + dashboard + write-up"]
    end
    P1 --> P2 --> P2b --> P3 --> P3b --> P4 --> P4b --> P5 --> P5b
    P5b --> END["Thesis + TRATON artifact:<br/>recommended V2G warranty + min controller spec"]
```

**8-month timeline (Gantt):**

```mermaid
gantt
    dateFormat  YYYY-MM
    axisFormat  %b
    title 8-Month Plan
    section Foundation
    Lit review + scope lock        :2026-09, 1M
    Platform + baseline MILP       :2026-09, 2M
    section Real-truck (edge)
    Test design + safety approval  :2026-10, 1M
    Run V2G test + calibrate       :2026-11, 1M
    section Headline method
    Warranty shadow-price model    :2026-12, 2M
    Per-truck attribution          :2027-01, 1M
    section Generalize
    EU/China compiler              :2027-02, 1M
    Value-of-fidelity ablation     :2027-02, 1M
    section Close
    Warranty co-design + scenarios :2027-03, 1M
    Dashboard + writing            :2027-03, 2M
```

---

## 5. EU ↔ China dimension (concrete, not a table of clichés)

Compile each market into an optimizer config; key axes that actually change the dispatch:

- **Grid-fee treatment of stored-then-returned energy** — DE just fixed this (single fee from Jan 2026, ⚠ initially tied
  to own-PV users); FR already favorable; CN differs by province.
- **Market time resolution** — EU SDAC is 15-min (since Oct 2025); China's spot pilots differ by province.
- **Ancillary access for aggregated EV fleets** — who can prequalify, minimum bid size, symmetric vs asymmetric.
- **Capacity/demand charge structure** — drives peak-shaving value (German *Leistungspreis* on peak 15-min).
- **Battery chemistry mix** — China fleets skew **LFP** (more V2G-tolerant); EU MAN packs skew **NMC** (calendar-aging
  sensitive). The *same* optimizer should behave differently → this is a clean result, not just description.

---

## 6. Real-truck test plan (keep it surgical — days, not fade)

You cannot measure capacity fade in a few days. Don't try. Measure the **inputs** your model assumes, and prove/correct them:

```mermaid
flowchart LR
    subgraph MEASURE["Measure in the test window"]
        E1["Round-trip efficiency map<br/>η(SoC, power)"]
        E2["Charge/discharge power taper vs SoC"]
        E3["V2G command → delivery delay + ramp"]
        E4["Pack ΔT vs C-rate (thermal)"]
        E5["dV/dQ / impedance snapshot (SoH proxy)"]
    end
    MEASURE --> CAL["Correct optimizer params<br/>(replace η=1.0 errors, real limits)"]
    CAL --> CRED["Credible economics<br/>(not lab-cell extrapolation)"]
```

**This single step kills the most common reviewer criticism** ("your efficiencies/limits are assumed"). It is the
cheapest, highest-credibility part of the whole thesis.

---

## 7. Questions I need answered to lock the final scope

These genuinely change the plan — please answer the ones you can:

1. **Warranty access:** Can you get MAN's *actual* eTruck battery warranty terms (SoH threshold, year/throughput limits)?
   Idea 2 (the headline) needs this. If not, can we use a representative anonymized version?
2. **Bidirectional test freedom:** Free to command arbitrary charge/discharge profiles, or only a tightly-scripted pilot?
   This decides how rich the calibration (Idea 1) can be.
3. **Telematics resolution:** Charger + truck logs at ≤1-min resolution? Needed for taper/delay/thermal capture.
4. **Pack history:** Do you have age, mileage, cumulative throughput, present SoH for the test truck? Enables the
   "history-aware" angle.
5. **In-house aging model:** Can you see/modify its equations (semi-empirical params), or is it a black box? Decides
   whether calibration is "correct the params" or "wrap a residual model around it."
6. **Deliverable type:** Should the final artifact lean **publishable method paper**, **TRATON internal prototype/tool**,
   or **future product concept**? (Affects how much weight goes to compiler/dashboard vs. the method.)

---

## 8. Honest bottom line

- **Don't** build "a giant Simulink twin" as the contribution — it's an apparatus, and reviewers know it.
- **Do** make the headline a *new decision function* only you can write: **warranty as a shadow-priced budget from the
  OEM seat (Idea 2)**, made credible by **real-truck calibration (Idea 1)**, generalized by the **EU/China compiler
  (Idea 5)**, and made tangible by **per-truck shadow-price attribution (Idea 6)**.
- **Stretch goal / second paper:** firm ancillary capacity via duty-cycle co-scheduling (Idea 3).

---

### Sources (state-of-the-art & regulatory verification)
- [Extra Throughput vs Days Lost in V2G (arXiv 2024)](https://arxiv.org/html/2408.02139v1) — your N04
- [Economic Viability of V2G Reassessed — degradation-cost LCA (MDPI Sustainability 2025)](https://www.mdpi.com/2071-1050/17/12/5626)
- [Assessing battery degradation in V2G optimization models (Energy Informatics)](https://energyinformatics.springeropen.com/articles/10.1186/s42162-023-00288-x)
- [Empirical capacity measurements of EVs under V2G degradation (ResearchGate)](https://www.researchgate.net/publication/352845601)
- [EV aggregator bidding in Nordic FCR-D: chance-constrained (arXiv 2024)](https://arxiv.org/html/2404.12818)
- [Multi-market V2G revenue incl. FCR (Applied Energy 2025)](https://www.sciencedirect.com/science/article/pii/S0306261925017787)
- [German Parliament removes V2G barrier — EnWG, 13 Nov 2025 (electrive)](https://www.electrive.com/2025/11/14/germany-clears-the-way-for-bidirectional-charging/)
- [Bundestag paves way for bidirectional charging (heise)](https://www.heise.de/en/news/E-mobility-Bundestag-paves-the-way-for-bidirectional-charging-11079628.html)
- [Scania demonstrates V2G through MCS (Charged EVs)](https://chargedevs.com/newswire/scania-demonstrates-vehicle-to-grid-through-megawatt-charging-system-for-heavy-electric-vehicles/)
- [chargebyte CCL MCS — ISO 15118-20 over Ethernet (Charged EVs)](https://chargedevs.com/newswire/chargebytes-ccl-mcs-brings-iso-15118-20-over-ethernet-to-megawatt-charging-for-heavy-duty-evs/)
