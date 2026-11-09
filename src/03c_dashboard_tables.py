"""Step 3c — promote two dashboard tables from silver to gold.

Gap found while writing the Power BI pack: two tables the dashboard
needs existed only in silver —
  * silver_senate_flips_2026.csv (6 rows) — the flipped 2026 Senate
    seats for the "What Changes Now" page.
  * silver_house_closest_races.csv (163 rows) — the closest House
    races of 2018/2022 for the competitiveness visuals.
No values are changed; the files are copied verbatim into the gold
layer (outputs/gold/, powerbi/gold/, outputs/midterms.db) under fact_
names so the build guide can reference them as gold tables.

Run:  python3 src/03c_dashboard_tables.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

TABLES = {
    "silver_senate_flips_2026": "fact_senate_flips_2026",
    "silver_house_closest_races": "fact_house_closest_races",
}

con = sqlite3.connect(ROOT / "outputs" / "midterms.db")
for silver_name, gold_name in TABLES.items():
    df = pd.read_csv(ROOT / "data" / "silver" / f"{silver_name}.csv")
    for dest in (ROOT / "outputs" / "gold" / f"{gold_name}.csv",
                 ROOT / "powerbi" / "gold" / f"{gold_name}.csv"):
        df.to_csv(dest, index=False)
    df.to_sql(gold_name, con, if_exists="replace", index=False)
    print(f"  {gold_name}: {len(df)} rows")
con.close()
print("  added to outputs/midterms.db")
