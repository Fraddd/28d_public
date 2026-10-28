"""
28DIGITAL demo - "Programme Cockpit" synthetic data generator.
ALL DATA IS FICTIONAL. Nothing here is real programme, recipient or employer data.

Run:  python gen_28digital_demo_data.py
Out:  bronze_files/ref/*.csv        editable reference tables
      bronze_files/src/*.csv        source files (-> Lakehouse Files/Bronze)
      _answer_key/seed_log.csv      every injected issue (NOT uploaded to Fabric)
Deterministic: same SEED = same files.
"""
import calendar
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

SEED = 28
random.seed(SEED)
OUT = Path("bronze_files")
KEY = Path("_answer_key")
for p in (OUT / "ref", OUT / "src", KEY):
    p.mkdir(parents=True, exist_ok=True)

AS_OF = date(2026, 12, 31)
QUARTERS = {1: (date(2026, 1, 1), date(2026, 3, 31)), 2: (date(2026, 4, 1), date(2026, 6, 30)),
            3: (date(2026, 7, 1), date(2026, 9, 30)), 4: (date(2026, 10, 1), date(2026, 12, 31))}
QL = {q: f"2026Q{q}" for q in QUARTERS}
INDIRECT_RATE = 0.25
SEEDS = []


def seed(issue, file, key, detail=""):
    SEEDS.append(dict(issue_type=issue, file=file, record_key=key, detail=detail))


def add_months(d, m):
    y, mo = d.year + (d.month - 1 + m) // 12, (d.month - 1 + m) % 12 + 1
    return date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))


def ts(d, h=6):
    return datetime(d.year, d.month, d.day, h, 0, 0)


def overlap(a1, a2, b1, b2):
    return max((min(a2, b2) - max(a1, b1)).days + 1, 0)


def save(df, sub, name):
    df.to_csv(OUT / sub / f"{name}.csv", index=False)
    print(f"{sub}/{name}.csv: {len(df)} rows")


# ------------------------------------------------------------------ 1. REFERENCE TABLES
ref_programme = pd.DataFrame([
    dict(programme_id="COCREATE", name="Co-Creation Accelerator", funder="EIT", max_funding_eur=250000,
         funding_rate_pct=100, min_cofunding_pct=0, prefinancing_pct=0, duration_months=4,
         payment_model="eligible costs, 100%", per_org_cap_eur=None),
    dict(programme_id="VIP_PARTNER", name="VIP delivery partners", funder="EIT", max_funding_eur=35000,
         funding_rate_pct=50, min_cofunding_pct=50, prefinancing_pct=25, duration_months=10,
         payment_model="reimbursement of actual costs", per_org_cap_eur=None),
    dict(programme_id="UNITE", name="UNITE-style consortium call", funder="EC", max_funding_eur=1000000,
         funding_rate_pct=100, min_cofunding_pct=0, prefinancing_pct=0, duration_months=18,
         payment_model="milestone reimbursement", per_org_cap_eur=600000),
    dict(programme_id="SUMMER_SCHOOL", name="Summer Schools (spare row)", funder="EIT", max_funding_eur=None,
         funding_rate_pct=None, min_cofunding_pct=30, prefinancing_pct=None, duration_months=None,
         payment_model="reimbursement of actual costs", per_org_cap_eur=None),
])
ref_programme["updated_at"] = ts(date(2026, 1, 1))

K = ["kpi_code", "name", "kpi_type", "formula_text", "unit", "target_cocreate", "target_vip", "target_unite",
     "green_pct", "amber_pct", "evidence_required", "version", "effective_from"]
kpis = [
    ("EITHE03.1", "Supported start-ups", "reported", "distinct recipients Active/Graduated at period end", "count", 13, 10, None, 100, 80, False, 1, "2026-01-01"),
    ("EITHE06.1", "Investment raised", "reported", "sum EUR verified funding raised, excl. 28DIGITAL support", "EUR", 6000000, None, None, 100, 80, True, 1, "2026-01-01"),
    ("JOBS", "Jobs created", "derived", "FTE_NOW minus FTE_BASELINE", "FTE", 40, None, None, 100, 80, False, 1, "2026-01-01"),
    ("PILOTS", "Corporate pilots / signed LOIs", "reported", "count of pilots or signed LOIs", "count", 8, None, None, 100, 80, True, 1, "2026-01-01"),
    ("DELIV", "On-time deliverables", "derived", "on-time / due; tiers: on time, late <=30d, later", "pct", 100, 100, 100, 100, 80, False, 1, "2026-01-01"),
    ("ABSORB", "Absorption rate", "derived", "actual eligible costs / planned budget vs linear plan (green within +-10%)", "pct", 100, 100, 100, 100, 80, False, 1, "2026-01-01"),
    ("COFUND", "Co-funding share", "derived", "partner co-funding / total eligible budget vs required minimum", "pct", None, 50, None, 100, 80, False, 1, "2026-01-01"),
    ("REPORT", "Reports on time", "derived", "reports received on time / expected", "pct", 100, 100, 100, 100, 80, False, 1, "2026-01-01"),
    ("DQSCORE", "Data quality score", "derived", "quality checks passed / run, per source", "pct", 95, 95, 95, 100, 80, False, 1, "2026-01-01"),
    ("ROLLUP_STARTUPS", "Roll-up: start-ups vs 2030", "rollup", "supported start-ups / scaled 2030 target", "count", None, None, None, 100, 80, False, 1, "2026-01-01"),
    ("ROLLUP_MOBILISED", "Roll-up: EUR mobilised vs 2030", "rollup", "investment raised / scaled 2030 target", "EUR", None, None, None, 100, 80, False, 1, "2026-01-01"),
    ("ROLLUP_VENTURES", "Roll-up: new ventures vs 2030", "rollup", "sum NEW_VENTURES / scaled 2030 target", "count", None, None, None, 100, 80, False, 1, "2026-01-01"),
    # version 2 of DQSCORE: green threshold relaxed from 100% to 95% (shows the SCD2 on definitions)
    ("DQSCORE", "Data quality score", "derived", "quality checks passed / run, per source", "pct", 95, 95, 95, 95, 80, False, 2, "2026-07-01"),
]
ref_kpi = pd.DataFrame(kpis, columns=K)
ref_kpi["updated_at"] = ref_kpi["effective_from"].map(lambda s: ts(date.fromisoformat(s)))

ref_cost = pd.DataFrame([
    ("A", "Personnel", True, None, None), ("B", "Subcontracting", False, 30, None),
    ("C1", "Purchase - travel", True, None, None), ("C2", "Purchase - equipment depreciation", True, None, None),
    ("C3", "Purchase - other goods and services", True, None, None),
    ("D1", "Financial support to third parties", False, None, None),
    ("E", "Indirect costs (flat rate)", False, None, 25),
], columns=["category_code", "name", "in_indirect_base", "max_share_pct", "indirect_rate_pct"])

ref_t2030 = pd.DataFrame([
    ("ROLLUP_STARTUPS", 1000, 0.02), ("ROLLUP_VENTURES", 500, 0.02), ("ROLLUP_MOBILISED", 2_000_000_000, 0.02),
], columns=["kpi_code", "target_2030", "demo_scale_factor"])

for df, n in ((ref_programme, "ref_programme"), (ref_kpi, "ref_kpi_definition"),
              (ref_cost, "ref_cost_category"), (ref_t2030, "ref_target_2030")):
    save(df, "ref", n)

# ------------------------------------------------------------------ 2. RECIPIENTS + EVENTS
HUBS = [("Brussels", "BE"), ("Budapest", "HU"), ("Stockholm", "SE"), ("Helsinki", "FI"),
        ("Cagliari", "IT"), ("Berlin", "DE"), ("Paris", "FR"), ("Lisbon", "PT")]
NAMES = {
    "COCREATE": ["Aurelia Quantum", "Nimbus Edge", "VoltaMesh", "Cryptara", "Lumio Health", "TerraSense",
                 "Sentinel Mesh", "Polaris Robotics"],
    "VIP_PARTNER": ["Nordic Incubator Hub", "Mediterranean Venture Lab", "Danube Start Studio",
                    "Iberia Launchpad", "Baltic Builders", "Alpine Scale Partners"],
    "UNITE": ["UNITE Consortium Alpha", "UNITE Consortium Beta", "UNITE Consortium Gamma", "UNITE Consortium Delta"],
}
STARTS = {
    "COCREATE": [date(2026, 1, 15), date(2026, 2, 2), date(2026, 3, 2), date(2026, 4, 1), date(2026, 5, 4),
                 date(2026, 6, 1), date(2026, 7, 1), date(2026, 8, 3)],
    "VIP_PARTNER": [date(2026, 1, 12), date(2026, 2, 2), date(2026, 2, 16), date(2026, 3, 2), date(2026, 3, 16),
                    date(2026, 4, 1)],
    "UNITE": [date(2026, 2, 1), date(2026, 3, 2), date(2026, 4, 1), date(2026, 5, 4)],
}
DUR = {"COCREATE": 4, "VIP_PARTNER": 10, "UNITE": 18}
PREFIX = {"COCREATE": "CC", "VIP_PARTNER": "VIP", "UNITE": "UN"}
RTYPE = {"COCREATE": "Start-up", "VIP_PARTNER": "Delivery partner", "UNITE": "Consortium"}

recs = []
for prog in NAMES:
    for i, (nm, st) in enumerate(zip(NAMES[prog], STARTS[prog]), 1):
        rid = f"{PREFIX[prog]}{i:02d}"
        end = add_months(st, DUR[prog]) - timedelta(days=1)
        eq = round(random.uniform(3.5, 7.0), 1) if prog == "COCREATE" else None
        ev = [(st - timedelta(days=45), "Selected", eq), (st, "Active", eq)]
        if prog != "UNITE" and end + timedelta(days=1) <= AS_OF:
            ev.append((end + timedelta(days=1), "Graduated", eq))
        recs.append(dict(rid=rid, name=nm, rtype=RTYPE[prog], prog=prog, start=st, end=end, eff_end=end,
                         withdrawn=False, hub=HUBS[(i + len(recs)) % len(HUBS)], events=ev, eq=eq))
R = {r["rid"]: r for r in recs}

# scripted history: withdrawal, equity revision, status going backwards (seeded)
w = R["CC06"]
w["events"] = [e for e in w["events"] if e[1] != "Graduated"] + [(date(2026, 8, 20), "Withdrawn", w["eq"])]
w["withdrawn"], w["eff_end"] = True, date(2026, 8, 20)
e3 = R["CC03"]
e3["events"].append((date(2026, 8, 10), "Graduated", round(e3["eq"] + 0.5, 1)))   # equity revision, same status
R["CC01"]["events"].append((date(2026, 11, 3), "Active", R["CC01"]["eq"]))          # Graduated -> Active
seed("status_backwards", "src_recipient_snapshot_2026Q4", "CC01", "Graduated (May) then Active (3 Nov)")
for r in recs:
    r["events"].sort(key=lambda e: e[0])


def snapshot(q, extra=None):
    qe = QUARTERS[q][1]
    rows = []
    for r in recs:
        past = [e for e in r["events"] if e[0] <= qe]
        if not past:
            continue
        d, st, eq = past[-1]
        rows.append(dict(recipient_id=r["rid"], recipient_name=r["name"], recipient_type=r["rtype"],
                         programme_id=r["prog"], status=st, equity_pct=eq, hub=r["hub"][0], country=r["hub"][1],
                         project_start=r["start"], project_end=r["end"], updated_at=ts(d)))
    return pd.DataFrame(rows)


snaps = {q: snapshot(q) for q in QUARTERS}
dup = snaps[2][snaps[2].recipient_id == "CC02"]
snaps[2] = pd.concat([snaps[2], dup], ignore_index=True)
seed("duplicate", "src_recipient_snapshot_2026Q2", "CC02", "identical row appears twice")
for q, df in snaps.items():
    save(df, "src", f"src_recipient_snapshot_{QL[q]}")
# SCD2 test file: Q4 clean copy with exactly ONE status change (VIP05 Active -> Graduated)
t = snaps[4].copy()
m = t.recipient_id == "VIP05"
t.loc[m, ["status", "updated_at"]] = ["Graduated", ts(date(2026, 12, 28), 9)]
save(t, "src", "src_recipient_snapshot_2026Q4_onechange")

# ------------------------------------------------------------------ 3. AWARDS
aw = []
for r in recs:
    if r["prog"] == "COCREATE":
        f, c, mo = random.randrange(120, 251, 5) * 1000, 0, None
    elif r["prog"] == "VIP_PARTNER":
        f = random.randrange(25, 36) * 1000
        c = round(f * random.uniform(1.0, 1.4), -2)
        mo = None
    else:
        f = random.randrange(600, 1001, 50) * 1000
        c = round(f * 0.10, -3)
        mo = round(f * random.uniform(0.45, 0.58), -3)
    aw.append(dict(recipient_id=r["rid"], programme_id=r["prog"], funding_awarded_eur=f, cofunding_eur=c,
                   max_org_funding_eur=mo, updated_at=ts(r["events"][0][0])))
awd = pd.DataFrame(aw).set_index("recipient_id")
awd.loc["VIP03", "funding_awarded_eur"] = 38500
seed("funding_over_cap", "src_award", "VIP03", "38,500 awarded vs 35,000 cap")
awd.loc["VIP05", "cofunding_eur"] = round(awd.loc["VIP05", "funding_awarded_eur"] * 0.61, -2)
seed("cofunding_below_min", "src_award", "VIP05", "co-funding about 38% of total vs 50% minimum")
awd.loc["UN02", "max_org_funding_eur"] = 640000
seed("funding_over_cap", "src_award", "UN02", "640,000 for one organisation vs 600,000 cap")
awd["total_eligible_budget_eur"] = awd.funding_awarded_eur + awd.cofunding_eur
awd = awd.reset_index()
save(awd[["recipient_id", "programme_id", "funding_awarded_eur", "cofunding_eur", "total_eligible_budget_eur",
          "max_org_funding_eur", "updated_at"]], "src", "src_award")
TOTAL = dict(zip(awd.recipient_id, awd.total_eligible_budget_eur))
FUND = dict(zip(awd.recipient_id, awd.funding_awarded_eur))

# ------------------------------------------------------------------ 4. BUDGET PLAN + COST LINES
WEIGHTS = {"COCREATE": dict(A=.62, B=.08, C1=.03, C2=.04, C3=.12, D1=0),
           "VIP_PARTNER": dict(A=.70, B=.06, C1=.04, C2=.00, C3=.12, D1=.05),
           "UNITE": dict(A=.55, B=.10, C1=.04, C2=.05, C3=.08, D1=0)}
plan, costs, base_q, b_q = [], [], {}, {}
for r in recs:
    wt = WEIGHTS[r["prog"]]
    wsum = sum(wt.values())
    wt = {c: v / wsum for c, v in wt.items()}
    base_share = sum(wt[c] for c in ("A", "C1", "C2", "C3"))
    days_q = {q: overlap(r["start"], r["end"], *QUARTERS[q]) for q in QUARTERS}
    d2026 = sum(days_q.values())
    plan_total = TOTAL[r["rid"]] * d2026 / ((r["end"] - r["start"]).days + 1)
    direct_total = plan_total / (1 + INDIRECT_RATE * base_share)
    absorb = random.uniform(0.65, 1.05)
    for q in QUARTERS:
        if days_q[q] == 0:
            continue
        qs, qe = QUARTERS[q]
        share = days_q[q] / d2026
        pl, cm = {}, {}
        for c, wc in wt.items():
            if wc == 0:
                continue
            pl[c] = direct_total * wc * share
            cm[c] = pl[c] * random.uniform(0.85, 1.0)
        pl["E"] = INDIRECT_RATE * sum(pl.get(c, 0) for c in ("A", "C1", "C2", "C3"))
        cm["E"] = INDIRECT_RATE * sum(cm.get(c, 0) for c in ("A", "C1", "C2", "C3"))
        for c in pl:
            plan.append(dict(recipient_id=r["rid"], quarter=QL[q], category_code=c, planned_eur=round(pl[c], 2),
                             committed_eur=round(cm[c], 2), updated_at=ts(qs - timedelta(days=15))))
        # actual costs inside [start, min(end, eff_end)] only
        a_s, a_e = max(qs, r["start"]), min(qe, r["end"], r["eff_end"], AS_OF)
        if a_e < a_s:
            continue
        ratio = ((a_e - a_s).days + 1) / days_q[q]
        base = 0.0
        for c, amount in pl.items():
            if c == "E":
                continue
            tot = amount * absorb * random.uniform(0.9, 1.1) * min(ratio, 1)
            n = {"A": 3, "C1": random.randint(1, 2), "C3": random.randint(1, 2)}.get(c, 1)
            parts = [random.random() + 0.3 for _ in range(n)]
            for i, p in enumerate(parts, 1):
                amt = round(tot * p / sum(parts), 2)
                d = a_s + timedelta(days=random.randint(0, (a_e - a_s).days))
                ev = (f"TS-{r['rid']}-{QL[q]}-{i}" if c == "A" else
                      f"GRANT-{random.randint(1000, 9999)}" if c == "D1" else f"INV-{random.randint(100000, 999999)}")
                costs.append(dict(recipient_id=r["rid"], category_code=c, cost_date=d, actual_eur=amt,
                                  evidence_ref=ev, updated_at=ts(min(d + timedelta(days=5), AS_OF), 8)))
                if c in ("A", "C1", "C2", "C3"):
                    base += amt
                if c == "B":
                    b_q[(r["rid"], q)] = b_q.get((r["rid"], q), 0) + amt
        if base > 0:
            costs.append(dict(recipient_id=r["rid"], category_code="E", cost_date=a_e,
                              actual_eur=round(INDIRECT_RATE * base, 2), evidence_ref="FLATRATE-25",
                              updated_at=ts(min(a_e + timedelta(days=5), AS_OF), 8)))
            base_q[(r["rid"], q)] = base

# high subcontracting: UN03 subcontracting x6
for c in costs:
    if c["recipient_id"] == "UN03" and c["category_code"] == "B":
        c["actual_eur"] = round(c["actual_eur"] * 6, 2)
seed("high_subcontracting", "src_cost_lines", "UN03", "subcontracting about 40% of direct costs vs 30% threshold")

cdf = pd.DataFrame(costs).sort_values(["cost_date", "recipient_id"]).reset_index(drop=True)
cdf.insert(0, "cost_id", [f"CL{i:05d}" for i in range(1, len(cdf) + 1)])
qof = lambda d: (d.month - 1) // 3 + 1  # noqa: E731

# wrong indirect (2 lines)
e_lines = cdf[(cdf.category_code == "E") & (cdf.recipient_id.str.startswith("CC"))].index.tolist()
i1 = random.choice(e_lines)
cdf.loc[i1, "actual_eur"] = round(cdf.loc[i1, "actual_eur"] * 1.2, 2)
seed("wrong_indirect", "src_cost_lines", cdf.loc[i1, "cost_id"], "rate 30% instead of 25%")
cand = [i for i in cdf[cdf.category_code == "E"].index
        if b_q.get((cdf.loc[i, "recipient_id"], qof(cdf.loc[i, "cost_date"])), 0) > 0 and i != i1]
i2 = random.choice(cand)
bq = b_q[(cdf.loc[i2, "recipient_id"], qof(cdf.loc[i2, "cost_date"]))]
cdf.loc[i2, "actual_eur"] = round(cdf.loc[i2, "actual_eur"] + INDIRECT_RATE * bq, 2)
seed("wrong_indirect", "src_cost_lines", cdf.loc[i2, "cost_id"], "base wrongly includes subcontracting")

# B-lines used for the other seeds (B is outside the indirect base, so E stays consistent)
b_idx = [i for i in cdf[(cdf.category_code == "B") & (cdf.recipient_id != "UN03")].index]
random.shuffle(b_idx)
for i in b_idx[:3]:
    seed("missing_category", "src_cost_lines", cdf.loc[i, "cost_id"], "category blank (was B)")
    cdf.loc[i, "category_code"] = ""
for i in b_idx[3:6]:
    r = R[cdf.loc[i, "recipient_id"]]
    new = r["end"] + timedelta(days=random.randint(20, 40)) if i % 2 else r["start"] - timedelta(days=random.randint(10, 20))
    seed("cost_outside_dates", "src_cost_lines", cdf.loc[i, "cost_id"], f"{cdf.loc[i, 'cost_date']} -> {new}")
    cdf.loc[i, "cost_date"] = new
# missing evidence on 4 other lines (non-E, not touched above)
ev_c = [i for i in cdf[~cdf.category_code.isin(["E", ""])].index if i not in b_idx[:6]]
for i in random.sample(ev_c, 4):
    seed("missing_evidence_ref", "src_cost_lines", cdf.loc[i, "cost_id"], "evidence_ref blank")
    cdf.loc[i, "evidence_ref"] = ""
# duplicates: one B line and one D1 line copied under a new cost_id
dsrc = [b_idx[6]] + cdf[cdf.category_code == "D1"].index[:1].tolist()
extra = []
for n, i in enumerate(dsrc, 1):
    row = cdf.loc[i].copy()
    row["cost_id"] = f"CL9{n:04d}"
    row["updated_at"] = row["updated_at"] + timedelta(days=1)
    extra.append(row)
    seed("duplicate", "src_cost_lines", f"{cdf.loc[i, 'cost_id']} = CL9{n:04d}", "same recipient, date, amount, category")
cdf = pd.concat([cdf, pd.DataFrame(extra)], ignore_index=True)
save(pd.DataFrame(plan).pipe(lambda d: d.insert(0, "plan_id", [f"BP{i:04d}" for i in range(1, len(d) + 1)]) or d),
     "src", "src_budget_plan")
save(cdf, "src", "src_cost_lines")

# ------------------------------------------------------------------ 5. MILESTONES / DELIVERABLES / PAYMENTS
TPL = {"COCREATE": [("M1", "milestone", "Challenge validated", .25), ("M2", "milestone", "Prototype integrated at partner", .60),
                    ("D1", "deliverable", "Pilot results", .90), ("R1", "report", "Mid-term report", .50),
                    ("R2", "report", "Final report", 1.0)],
       "VIP_PARTNER": [("M1", "milestone", "Bootcamp delivered", .10), ("D1", "deliverable", "Curriculum delivered", .45),
                       ("R1", "report", "Mid-term cost report", .50), ("D2", "deliverable", "Demo Day held", .85),
                       ("R2", "report", "Final evaluation report", 1.0)],
       "UNITE": [("M1", "milestone", "Kick-off and workplan", .15), ("M2", "milestone", "Solution prototype", .45),
                 ("R1", "report", "Interim report", .50), ("M3", "milestone", "Pilot deployed", .75),
                 ("R2", "report", "Final report", 1.0)]}
items, due_of = [], {}
for r in recs:
    span = (r["end"] - r["start"]).days
    for code, typ, title, frac in TPL[r["prog"]]:
        due = r["start"] + timedelta(days=int(frac * span)) + (timedelta(days=15) if code == "R2" else timedelta(0))
        due_of[(r["rid"], code)] = due
        sub, status = None, "Not due"
        if due <= AS_OF:
            x = random.random()
            delay = (-random.randint(0, 10) if x < .70 else random.randint(1, 30) if x < .90 else random.randint(31, 75))
            if r["withdrawn"] and due > r["eff_end"]:
                status = "Cancelled"
            elif due + timedelta(days=delay) > AS_OF:
                status = "Overdue"
                seed("late_deliverable", "src_milestone_deliverable", f"{r['rid']}-{code}", "not submitted, past due")
            else:
                sub, status = due + timedelta(days=delay), "Accepted"
                if delay > 0:
                    seed("late_deliverable", "src_milestone_deliverable", f"{r['rid']}-{code}",
                         f"{delay} days late ({'<=30' if delay <= 30 else '>30'})")
        items.append(dict(item_id=f"{r['rid']}-{code}", recipient_id=r["rid"], item_type=typ, title=title,
                          due_date=due, submitted_date=sub, status=status,
                          updated_at=ts(sub or min(due, AS_OF), 10)))
save(pd.DataFrame(items), "src", "src_milestone_deliverable")

PAY = {"COCREATE": [("PRE", .5, "start", 0), ("FINAL", .5, "R2", 30)],
       "VIP_PARTNER": [("PRE", .25, "start", 0), ("FINAL", .75, "R2", 30)],
       "UNITE": [("INTERIM1", .3, "M1", 20), ("INTERIM2", .4, "R1", 30), ("FINAL", .3, "R2", 45)]}
pays = []
for r in recs:
    for tr, pct, anchor, lag in PAY[r["prog"]]:
        planned = (r["start"] if anchor == "start" else due_of[(r["rid"], anchor)]) + timedelta(days=lag)
        if r["withdrawn"] and planned > r["eff_end"]:
            continue
        paid = planned + timedelta(days=random.randint(0, 15))
        paid = paid if paid <= AS_OF else None
        pays.append(dict(recipient_id=r["rid"], tranche=tr, amount_eur=round(pct * FUND[r["rid"]], 2),
                         planned_date=planned, paid_date=paid, updated_at=ts(paid or min(planned, AS_OF), 11)))
pdf = pd.DataFrame(pays)
pdf.insert(0, "payment_id", [f"PAY{i:03d}" for i in range(1, len(pdf) + 1)])
save(pdf, "src", "src_payments")

# ------------------------------------------------------------------ 6. KPI ACTUALS (reported inputs only)
kr = []
for r in recs:
    fq = next(q for q in QUARTERS if QUARTERS[q][1] >= r["start"])
    fte = random.randint(3, 15)
    for q in range(fq, 5):
        qs, qe = QUARTERS[q]
        if r["withdrawn"] and qs > r["eff_end"]:
            continue
        upd = ts(min(qe + timedelta(days=10), AS_OF), 9)
        add = lambda code, val, ev="": kr.append(dict(recipient_id=r["rid"], kpi_code=code, quarter=QL[q],  # noqa: E731
                                                     value=val, evidence_ref=ev, updated_at=upd))
        if r["prog"] == "COCREATE":
            if q == fq:
                add("FTE_BASELINE", fte)
            else:
                fte += random.choice([0, 0, 1, 2, 3])
            add("FTE_NOW", fte)
            inv = round(random.uniform(0.2, 1.5) * 1e6, -3) if (q > fq and random.random() < .6) else 0
            add("EITHE06.1", inv, f"EV-INV-{r['rid']}-{QL[q]}" if inv else "")
            pil = random.choice([0, 1, 1, 2])
            add("PILOTS", pil, f"EV-LOI-{r['rid']}-{QL[q]}" if pil else "")
        elif r["prog"] == "VIP_PARTNER":
            add("NEW_VENTURES", random.choice([0, 1, 1, 2, 3]))
kdf = pd.DataFrame(kr)
for i in random.sample(kdf[(kdf.kpi_code.isin(["EITHE06.1", "PILOTS"])) & (kdf.value > 0)].index.tolist(), 2):
    seed("missing_evidence_ref", "src_kpi_actuals", f"{kdf.loc[i, 'recipient_id']}|{kdf.loc[i, 'kpi_code']}|{kdf.loc[i, 'quarter']}",
         "evidence required but blank")
    kdf.loc[i, "evidence_ref"] = ""
save(kdf, "src", "src_kpi_actuals")

# ------------------------------------------------------------------ 7. ANSWER KEY
sl = pd.DataFrame(SEEDS)
sl.insert(0, "seed_id", [f"S{i:03d}" for i in range(1, len(sl) + 1)])
sl.to_csv(KEY / "seed_log.csv", index=False)
print("\nSeeded issues by type:\n", sl.issue_type.value_counts().to_string())
print("\nDone. Upload bronze_files/ref and bronze_files/src to the Lakehouse (Files/bronze). Keep _answer_key local.")