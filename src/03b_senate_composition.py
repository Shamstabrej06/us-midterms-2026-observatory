"""Step 3b — Senate composition gold table (added after Part 4).

Gap found while writing the Power BI pack: the gold layer had no Senate
SEAT COUNTS. fact_results holds Senate VOTES (state-level, per party)
but the composition of the chamber — the headline 2026 figure
(D 53 / R 45 / I 2) — lived only in data/silver/silver_senate_2026.csv.

This script builds fact_senate_composition from two sources that were
already in the repo:
  * silver_control.csv — Senate D/R seats per Congress, 103rd-119th
    (Wikipedia "Party divisions of United States Congresses").
  * silver_senate_2026.csv — the 2026 composition (D/R/I), preliminary.
seats_before for a Congress is the previous Congress's seats_after, so
net_change is computed, never typed.

Run:  python3 src/03b_senate_composition.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "outputs" / "midterms.db"

control = pd.read_csv(ROOT / "data" / "silver" / "silver_control.csv")
s26 = pd.read_csv(ROOT / "data" / "silver" / "silver_senate_2026.csv")

# Congress -> election cycle: the Congress seated after the election in
# year (first year of the "years" range) - 1.
rows = []
prev = {}  # party -> seats_after of the previous Congress
for _, r in control.sort_values("congress").iterrows():
    congress = int(r["congress"])
    cycle = int(str(r["years"]).split("–")[0]) - 1
    for party, col in (("Democratic", "senate_dem"), ("Republican", "senate_rep")):
        seats_after = r[col]
        if pd.isna(seats_after):
            continue
        seats_after = int(seats_after)
        seats_before = prev.get(party)
        rows.append({
            "cycle": cycle,
            "congress": congress,
            "party_name": party,
            "seats_before": seats_before,
            "seats_after": seats_after,
            "net_change": (seats_after - seats_before) if seats_before is not None else None,
            "status": "certified",
        })
        prev[party] = seats_after

# 2026 (120th Congress) from the composition table — includes Independents.
for _, r in s26.iterrows():
    rows.append({
        "cycle": 2026,
        "congress": 120,
        "party_name": r["party"],
        "seats_before": int(r["seats_before"]),
        "seats_after": int(r["seats_after"]),
        "net_change": int(r["net_change"]),
        "status": "preliminary",
    })

df = pd.DataFrame(rows).sort_values(["cycle", "party_name"]).reset_index(drop=True)
assert len(df) == 37, f"expected 37 rows, got {len(df)}"  # 17 Congresses x 2 parties + 3 for 2026 (incl. Independents)
assert int(df[(df["cycle"] == 2026) & (df["party_name"] == "Democratic")]["seats_after"].iloc[0]) == 53
assert int(df[(df["cycle"] == 2026)]["seats_after"].sum()) == 100

for dest in (ROOT / "outputs" / "gold" / "fact_senate_composition.csv",
             ROOT / "powerbi" / "gold" / "fact_senate_composition.csv"):
    df.to_csv(dest, index=False)
    print(f"  wrote {dest} ({len(df)} rows)")

con = sqlite3.connect(DB)
df.to_sql("fact_senate_composition", con, if_exists="replace", index=False)
con.close()
print("  appended fact_senate_composition to outputs/midterms.db")
print(df[df["cycle"].isin([2018, 2022, 2026])].to_string(index=False))
