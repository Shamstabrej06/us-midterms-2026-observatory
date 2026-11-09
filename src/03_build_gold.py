"""Step 3 — silver -> gold: build the star schema.

Reads data/silver/ and writes the gold layer:
  outputs/gold/*.csv  (also copied to powerbi/gold/ for import)
  outputs/midterms.db (SQLite, same tables)

GRAIN NOTE (documented deviation from the brief): the brief specifies
fact_results at "one row per race-county-cycle". No public county-level
vote data could be obtained (MEDSL county files are guestbook-gated; see
data/SOURCES.md), so fact_results is built at race-STATE-cycle grain.
The grain is explicit in every row (geography_level) and in the data
dictionary. County population still appears in dim_geography.

Tables:
  fact_results        one row per race-geography-party (House/Senate/
                      President/Governor/Attorney General)
  fact_finance        one row per candidate-cycle (FEC)
  fact_turnout        national VEP turnout per midterm year + state 2022
  fact_texas_statewide Texas statewide races (Governor/Senate/President/AG)
  dim_geography       states (+DC + territories) with 2024 population
  dim_cycle           election cycles 1994-2026 with control context
  dim_party           Democratic / Republican / Other
  dim_office          race types (House, Senate, President, Governor, AG)

Run:  python3 src/03_build_gold.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SILVER = ROOT / "data" / "silver"
RAW = ROOT / "data" / "raw"
GOLD = ROOT / "outputs" / "gold"
PBIGOLD = ROOT / "powerbi" / "gold"
GOLD.mkdir(parents=True, exist_ok=True)
PBIGOLD.mkdir(parents=True, exist_ok=True)


def log(msg):
    print(msg)


def build_dims():
    # dim_geography: states + DC + territories, population from counties
    counties = pd.read_csv(SILVER / "silver_counties.csv")
    pop = counties.groupby(["state_name", "state_abbr"], dropna=False)[
        "population_2024"].sum().reset_index()
    # Census regions/divisions from the raw popest file (state-level rows
    # are SUMLEV 40)
    raw = pd.read_csv(RAW / "co-est2024-alldata.csv", encoding="latin-1",
                      usecols=["SUMLEV", "STATE", "STNAME", "REGION", "DIVISION"])
    states = raw[raw["SUMLEV"] == 40][["STNAME", "REGION", "DIVISION"]].drop_duplicates()
    region_map = {"1": "Northeast", "2": "Midwest", "3": "South", "4": "West"}
    division_map = {"1": "New England", "2": "Middle Atlantic",
                    "3": "East North Central", "4": "West North Central",
                    "5": "South Atlantic", "6": "East South Central",
                    "7": "West South Central", "8": "Mountain", "9": "Pacific"}
    states["region"] = states["REGION"].astype(str).map(region_map)
    states["division"] = states["DIVISION"].astype(str).map(division_map)
    geo = pop.merge(states, left_on="state_name", right_on="STNAME", how="left")
    geo = geo.drop(columns=["STNAME"])
    # state FIPS from the county FIPS values (county FIPS = state*1000 + county)
    fips_map = (counties.assign(state_fips=counties["fips"] // 1000)
                .groupby("state_abbr")["state_fips"].min().to_dict())
    geo["state_fips"] = geo["state_abbr"].map(fips_map)
    geo = geo[["state_fips", "state_abbr", "state_name", "region",
               "division", "population_2024"]].sort_values("state_fips")
    # Territories: not in the Census county estimates file, so they carry no
    # population here; added so FEC territory candidates join to the dimension.
    terr = pd.DataFrame([
        {"state_fips": 72, "state_abbr": "PR", "state_name": "Puerto Rico",
         "region": "Territory", "division": "Territory", "population_2024": None},
        {"state_fips": 66, "state_abbr": "GU", "state_name": "Guam",
         "region": "Territory", "division": "Territory", "population_2024": None},
        {"state_fips": 78, "state_abbr": "VI", "state_name": "U.S. Virgin Islands",
         "region": "Territory", "division": "Territory", "population_2024": None},
        {"state_fips": 60, "state_abbr": "AS", "state_name": "American Samoa",
         "region": "Territory", "division": "Territory", "population_2024": None},
        {"state_fips": 69, "state_abbr": "MP", "state_name": "Northern Mariana Islands",
         "region": "Territory", "division": "Territory", "population_2024": None},
    ])
    geo = pd.concat([geo, terr], ignore_index=True).sort_values("state_fips")
    geo.to_csv(GOLD / "dim_geography.csv", index=False)
    log(f"dim_geography.csv: {len(geo)} rows")

    # dim_party
    party = pd.DataFrame([
        {"party_key": "DEM", "party_name": "Democratic"},
        {"party_key": "REP", "party_name": "Republican"},
        {"party_key": "OTH", "party_name": "Other"},
        {"party_key": "IND", "party_name": "Independent"},
    ])
    party.to_csv(GOLD / "dim_party.csv", index=False)

    # dim_office
    office = pd.DataFrame([
        {"office_key": "HOU", "office_name": "House", "chamber": "House",
         "seats_total": 435},
        {"office_key": "SEN", "office_name": "Senate", "chamber": "Senate",
         "seats_total": 100},
        {"office_key": "PRE", "office_name": "President", "chamber": "Executive",
         "seats_total": 1},
        {"office_key": "GOV", "office_name": "Governor", "chamber": "State executive",
         "seats_total": 50},
        {"office_key": "ATG", "office_name": "Attorney General",
         "chamber": "State executive", "seats_total": 50},
    ])
    office.to_csv(GOLD / "dim_office.csv", index=False)

    # dim_cycle: 1994-2026 midterms + presidential years in range
    ct = pd.read_csv(SILVER / "silver_control.csv")
    hs = pd.read_csv(SILVER / "silver_house_summary.csv")
    rows = []
    for _, r in ct.iterrows():
        congress = int(r["congress"])
        # election year that seated this Congress = first year of the term - 1
        # (Congress years are e.g. '1993–1995' -> election 1992). Midterm
        # Congresses are the even ones; derive the election year from the
        # years string instead: 'YYYY–YYYY' -> election year = first YYYY - 1
        first_year = int(str(r["years"]).split("–")[0])
        election_year = first_year - 1
        rows.append({"cycle": election_year, "congress": congress,
                     "election_type": "midterm" if election_year % 4 == 2 else "presidential",
                     "president": r["president"],
                     "president_party": r["president_party"],
                     "senate_majority": r["senate_majority"],
                     "house_majority": r["house_majority"],
                     "trifecta": r["trifecta"]})
    cyc = pd.DataFrame(rows)
    # 2026 row: the 119th Congress was seated by the 2024 election; the
    # 2026 midterm seats the 120th Congress, which the control table does
    # not cover yet. Add it from the House/Senate results.
    cyc = cyc[cyc["cycle"] != 2026]
    cyc = pd.concat([cyc, pd.DataFrame([{
        "cycle": 2026, "congress": 120, "election_type": "midterm",
        "president": "Donald Trump", "president_party": "Republican",
        "senate_majority": "Democratic", "house_majority": "Democratic",
        "trifecta": False}])], ignore_index=True)
    cyc = cyc.sort_values("cycle")
    cyc.to_csv(GOLD / "dim_cycle.csv", index=False)
    log(f"dim_cycle.csv: {len(cyc)} rows")
    return geo, party, office, cyc


def build_fact_results():
    rows = []
    # House summary: national, per party per cycle
    hs = pd.read_csv(SILVER / "silver_house_summary.csv")
    for _, r in hs.iterrows():
        rows.append({"race_id": f"HOU-NAT-{int(r['cycle'])}",
                     "cycle": int(r["cycle"]), "office_key": "HOU",
                     "geography_level": "national", "state_fips": None,
                     "state_abbr": None, "party_key": "DEM" if r["party"] == "Democratic" else "REP",
                     "party_name": r["party"], "candidate": None,
                     "votes": r["popular_votes"], "vote_share_pct": r["popular_pct"],
                     "seats_before": r["seats_before"], "seats_after": r["seats_after"],
                     "net_change": r["net_change"], "margin_pts": None,
                     "winner_party": None, "status": r["status"]})
    # House seats by state
    st = pd.read_csv(SILVER / "silver_house_seats_by_state.csv")
    for _, r in st.iterrows():
        for party, seats, chg in (("Democratic", r["dem_seats"], r["dem_change"]),
                                  ("Republican", r["rep_seats"], r["rep_change"])):
            rows.append({"race_id": f"HOU-{r['state_abbr']}-{int(r['cycle'])}",
                         "cycle": int(r["cycle"]), "office_key": "HOU",
                         "geography_level": "state", "state_fips": r["state_fips"],
                         "state_abbr": r["state_abbr"],
                         "party_key": "DEM" if party == "Democratic" else "REP",
                         "party_name": party, "candidate": None,
                         "votes": None, "vote_share_pct": None,
                         "seats_before": None, "seats_after": seats,
                         "net_change": chg, "margin_pts": None,
                         "winner_party": None,
                         "status": "preliminary" if r["cycle"] == 2026 else "certified"})
    # Senate races (state-level, two-party)
    ss = pd.read_csv(SILVER / "silver_senate_state.csv")
    for _, r in ss.iterrows():
        rows.append({"race_id": f"SEN-{r['state_po']}-{int(r['year'])}"
                     + ("-SP" if r["special"] else ""),
                     "cycle": int(r["year"]), "office_key": "SEN",
                     "geography_level": "state",
                     "state_fips": None, "state_abbr": r["state_po"],
                     "party_key": "DEM", "party_name": "Democratic",
                     "candidate": None, "votes": r["Democratic"],
                     "vote_share_pct": r["dem_share_pct"],
                     "seats_before": None, "seats_after": None,
                     "net_change": None, "margin_pts": r["margin_pts"],
                     "winner_party": "Democratic" if r["margin_pts"] > 0 else "Republican",
                     "status": "certified"})
        rows.append({**rows[-1], "race_id": rows[-1]["race_id"],
                     "party_key": "REP", "party_name": "Republican",
                     "candidate": None, "votes": r["Republican"],
                     "vote_share_pct": round(100 - r["dem_share_pct"], 2),
                     "margin_pts": -r["margin_pts"] if pd.notna(r["margin_pts"]) else None})
    # President (state-level, two-party)
    ps = pd.read_csv(SILVER / "silver_president_state.csv")
    for _, r in ps.iterrows():
        rows.append({"race_id": f"PRE-{r['state_po']}-{int(r['year'])}",
                     "cycle": int(r["year"]), "office_key": "PRE",
                     "geography_level": "state", "state_fips": None,
                     "state_abbr": r["state_po"], "party_key": "DEM",
                     "party_name": "Democratic", "candidate": None,
                     "votes": r["Democratic"], "vote_share_pct": r["dem_share_pct"],
                     "seats_before": None, "seats_after": None, "net_change": None,
                     "margin_pts": r["margin_pts"],
                     "winner_party": "Democratic" if r["margin_pts"] > 0 else "Republican",
                     "status": "certified"})
        rows.append({**rows[-1], "party_key": "REP", "party_name": "Republican",
                     "votes": r["Republican"],
                     "vote_share_pct": round(100 - r["dem_share_pct"], 2),
                     "margin_pts": -r["margin_pts"] if pd.notna(r["margin_pts"]) else None})
    # Governors (state-level, winner + margin)
    gv = pd.read_csv(SILVER / "silver_governors.csv")
    for _, r in gv.iterrows():
        rows.append({"race_id": f"GOV-{r['state_abbr']}-{int(r['cycle'])}",
                     "cycle": int(r["cycle"]), "office_key": "GOV",
                     "geography_level": "state", "state_fips": r["state_fips"],
                     "state_abbr": r["state_abbr"],
                     "party_key": ("DEM" if r["winner_party"] == "Democratic"
                                   else "REP" if r["winner_party"] == "Republican" else None),
                     "party_name": r["winner_party"], "candidate": None,
                     "votes": None, "vote_share_pct": None,
                     "seats_before": None, "seats_after": None, "net_change": None,
                     "margin_pts": r["margin_pts"],
                     "winner_party": r["winner_party"], "status": r["status"]})
    # Texas AG 2026 (from the Texas statewide table)
    tx = pd.read_csv(SILVER / "silver_texas_statewide.csv")
    ag = tx[(tx["office"] == "Attorney General")]
    for _, r in ag.iterrows():
        for party, cand, votes, pct in (
                ("Democratic", r["dem_candidate"], r["dem_votes"], r["dem_pct"]),
                ("Republican", r["rep_candidate"], r["rep_votes"], r["rep_pct"])):
            rows.append({"race_id": "ATG-TX-2026", "cycle": 2026,
                         "office_key": "ATG", "geography_level": "state",
                         "state_fips": 48, "state_abbr": "TX",
                         "party_key": "DEM" if party == "Democratic" else "REP",
                         "party_name": party, "candidate": cand,
                         "votes": votes, "vote_share_pct": pct,
                         "seats_before": None, "seats_after": None,
                         "net_change": None,
                         "margin_pts": r["margin_pts"] if party == "Democratic" else -r["margin_pts"],
                         "winner_party": r["winner_party"], "status": "preliminary"})
    fr = pd.DataFrame(rows)
    fr.to_csv(GOLD / "fact_results.csv", index=False)
    log(f"fact_results.csv: {len(fr)} rows")
    return fr


def build_fact_finance():
    f = pd.read_csv(SILVER / "silver_finance.csv")
    ff = f[["cand_id", "cand_name", "cycle", "office", "office_name",
            "office_state", "state_name", "office_district", "cand_ici",
            "party", "party_std", "total_receipts", "total_disbursements",
            "cash_on_hand_bop", "cash_on_hand_end", "debts_owed_by",
            "individual_contributions", "other_committee_contributions",
            "party_committee_contributions", "coverage_end_date",
            "status"]].copy()
    ff = ff.rename(columns={"cand_id": "candidate_id", "cand_name": "candidate_name",
                            "cand_ici": "incumbent_status", "party": "party_raw",
                            "party_std": "party_name",
                            "office_state": "state_abbr",
                            "office_district": "district"})
    ff["party_key"] = ff["party_name"].map({"Democratic": "DEM",
                                            "Republican": "REP"}).fillna("OTH")
    ff.to_csv(GOLD / "fact_finance.csv", index=False)
    log(f"fact_finance.csv: {len(ff)} rows")
    return ff


def build_fact_turnout_texas():
    tn = pd.read_csv(SILVER / "silver_turnout_national.csv")
    tn = tn.rename(columns={"year": "cycle", "vep_turnout_rate_pct": "turnout_rate_pct"})
    tn["geography_level"] = "national"
    tn["state_abbr"] = None
    tn = tn[["cycle", "geography_level", "state_abbr", "turnout_rate_pct", "status"]]
    ts = pd.read_csv(SILVER / "silver_turnout_state_2022.csv")
    ts = ts.rename(columns={"vep_turnout_rate_pct": "turnout_rate_pct",
                            "state_abv": "state_abbr"})
    ts["cycle"] = 2022
    ts["geography_level"] = "state"
    ts["status"] = "final"
    ts = ts[["cycle", "geography_level", "state_abbr", "turnout_rate_pct", "status"]]
    ft = pd.concat([tn, ts], ignore_index=True)
    ft.to_csv(GOLD / "fact_turnout.csv", index=False)
    log(f"fact_turnout.csv: {len(ft)} rows")

    tx = pd.read_csv(SILVER / "silver_texas_statewide.csv")
    tx.to_csv(GOLD / "fact_texas_statewide.csv", index=False)
    log(f"fact_texas_statewide.csv: {len(tx)} rows")
    return ft, tx


def build_db(tables):
    db_path = ROOT / "outputs" / "midterms.db"
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    for name, df in tables.items():
        df.to_sql(name, con, index=False)
    con.execute("CREATE INDEX IF NOT EXISTS idx_results_cycle ON fact_results(cycle)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_results_state ON fact_results(state_abbr)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_finance_cycle ON fact_finance(cycle)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_finance_candidate ON fact_finance(candidate_id)")
    con.commit()
    con.close()
    log(f"midterms.db: {db_path.stat().st_size:,} bytes")


def main():
    geo, party, office, cyc = build_dims()
    fr = build_fact_results()
    ff = build_fact_finance()
    ft, tx = build_fact_turnout_texas()
    # copies for Power BI import
    for f in GOLD.glob("*.csv"):
        (PBIGOLD / f.name).write_bytes(f.read_bytes())
    log(f"powerbi/gold/: {len(list(PBIGOLD.glob('*.csv')))} CSVs copied")
    tables = {"dim_geography": geo, "dim_party": party, "dim_office": office,
              "dim_cycle": cyc, "fact_results": fr, "fact_finance": ff,
              "fact_turnout": ft, "fact_texas_statewide": tx}
    build_db(tables)
    print("\n--- 03_build_gold complete ---")


if __name__ == "__main__":
    main()