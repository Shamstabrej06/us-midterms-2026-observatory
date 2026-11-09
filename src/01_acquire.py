"""Step 1 — acquisition + inventory extracts.

Reads the raw files downloaded on 2026-11-09 (see data/SOURCES.md) from
data/raw/ and writes small, committed extracts to data/sample/.

Every extract is derived, never hand-typed: numbers in the findings must
trace to these files. Run:  python3 src/01_acquire.py

Outputs (data/sample/):
  house_summary.csv       House seats + popular vote by cycle (2014/2018/2022/2026)
  house_seats_by_state.csv Seats by party per state per cycle
  house_closest_races.csv  Closest House races, 2018 + 2022 (Wikipedia tables)
  senate_2026_composition.csv  2026 Senate before/after + flips
  control_table.csv        Party control of House/Senate/Presidency, 1994-2026
  turnout_national.csv     VEP midterm turnout rate, 1994-2022 (+ 2026 status)
  turnout_state_2022.csv   State VEP turnout rates, 2022
  fec_2018.csv / fec_2022.csv / fec_2026.csv  FEC candidate summaries
  president_state.csv      MEDSL state presidential results, 2016/2020/2024
  senate_state.csv         MEDSL statewide Senate results, 2014-2024
  counties_population.csv  Census county population estimates, 2024
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SAMPLE = ROOT / "data" / "sample"
SAMPLE.mkdir(parents=True, exist_ok=True)

LOG = []


def log(msg):
    LOG.append(msg)
    print(msg)


def num(x):
    """Parse a number with commas / % / dashes into float or None."""
    if x is None:
        return None
    s = str(x).strip().replace(",", "").replace("%", "").replace("\u2212", "-")
    s = re.sub(r"\[.*?\]", "", s).strip()
    if s in ("", "-", "—", "–", "NaN", "nan", "None"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def clean_party(s):
    s = str(s).strip()
    s = re.sub(r"\[.*?\]", "", s).strip()
    return s


# ---------------------------------------------------------------- House
def parse_house_summary():
    """Seats + popular vote per cycle from the Wikipedia results tables.

    Layouts differ by cycle (verified against each page's printed table):
      A (1994, 1998):  before, after, +/-, strength, vote%, votes
      B (2002-2018):   before, after, +/-, strength, votes, vote%, change
      C (2022):        votes, vote%, change, before, after, +/-, strength
      2026: seats + popular vote from the infobox (the results table's seat
      columns are still blank; its vote totals exclude 98 districts).
    Net change is always computed as after - before: the +/- column in the
    source tables is unsigned.
    """
    rows = []
    specs = [
        (1994, "wiki1994house.html", 6, "A"),
        (1998, "wiki1998house.html", 4, "A"),
        (2002, "wiki2002house.html", 4, "B"),
        (2006, "wiki2006house.html", 4, "B"),
        (2010, "wiki2010house.html", 4, "B"),
        (2014, "wiki14house.html", 4, "B"),
        (2018, "wiki18house.html", 4, "B"),
        (2022, "wiki22house.html", 4, "C"),
        (2026, "wiki26.html", 4, "2026"),
    ]
    for cycle, fname, idx, layout in specs:
        tabs = pd.read_html(RAW / fname)
        t = tabs[idx]
        t.columns = [" | ".join(str(c) for c in col).strip() for col in t.columns]
        party_col = t.columns[1]
        for _, r in t.iterrows():
            party = clean_party(r[party_col])
            if party not in ("Democratic Party", "Republican Party",
                             "Democratic", "Republican"):
                continue
            d = {"cycle": cycle, "party": party.replace(" Party", "")}
            if layout == "A":
                d["seats_before"] = num(r[t.columns[2]])
                d["seats_after"] = num(r[t.columns[3]])
                d["popular_pct"] = num(r[t.columns[6]])
                d["popular_votes"] = num(r[t.columns[7]])
            elif layout == "B":
                d["seats_before"] = num(r[t.columns[2]])
                d["seats_after"] = num(r[t.columns[3]])
                d["popular_votes"] = num(r[t.columns[6]])
                d["popular_pct"] = num(r[t.columns[7]])
            elif layout == "C":
                d["popular_votes"] = num(r[t.columns[2]])
                d["popular_pct"] = num(r[t.columns[3]])
                d["seats_before"] = num(r[t.columns[5]])
                d["seats_after"] = num(r[t.columns[6]])
            else:  # 2026: seats + votes from infobox (see below)
                d["seats_before"] = None
                d["seats_after"] = None
                d["popular_votes"] = None
                d["popular_pct"] = None
            d["net_change"] = (d["seats_after"] - d["seats_before"]
                               if d["seats_before"] is not None and d["seats_after"] is not None
                               else None)
            rows.append(d)
    # 2026 seats + popular vote from the infobox (table[1]); the infobox is the
    # most current snapshot on the page (declared 95.6% as of Nov 6, 2026).
    tabs26 = pd.read_html(RAW / "wiki26.html")
    info = tabs26[1]
    info = info.astype(str)
    for _, r in info.iterrows():
        label = str(r.iloc[0]).replace("\xa0", " ").strip()
        if label == "Seats before":
            dem_before, rep_before = num(r.iloc[1]), num(r.iloc[2])
        elif label == "Seats won":
            dem_won, rep_won = num(r.iloc[1]), num(r.iloc[2])
        elif label == "Popular vote":
            dem_votes, rep_votes = num(r.iloc[1]), num(r.iloc[2])
        elif label == "Percentage":
            dem_pct, rep_pct = num(r.iloc[1]), num(r.iloc[2])
    for d in rows:
        if d["cycle"] == 2026:
            if d["party"] == "Democratic":
                d["seats_before"], d["seats_after"] = dem_before, dem_won
                d["popular_votes"], d["popular_pct"] = dem_votes, dem_pct
            else:
                d["seats_before"], d["seats_after"] = rep_before, rep_won
                d["popular_votes"], d["popular_pct"] = rep_votes, rep_pct
            d["net_change"] = d["seats_after"] - d["seats_before"]
            d["seats_uncalled"] = 435 - int(dem_won + rep_won)
    out = pd.DataFrame(rows)
    out.to_csv(SAMPLE / "house_summary.csv", index=False)
    log(f"house_summary.csv: {len(out)} rows")
    return out


def parse_house_seats_by_state():
    rows = []
    for cycle, fname in [(2014, "wiki14house.html"), (2018, "wiki18house.html"),
                         (2022, "wiki22house.html"), (2026, "wiki26.html")]:
        t = pd.read_html(RAW / fname)[5]
        t.columns = [" | ".join(str(c) for c in col).strip() for col in t.columns]
        cols = list(t.columns)
        for _, r in t.iterrows():
            state = str(r[cols[0]]).strip()
            if state in ("State", "Total", "Totals", "nan"):
                continue
            dem_seats = dem_chg = rep_seats = rep_chg = None
            for c in cols[1:]:
                low = c.lower()
                if "democratic" in low and "seats" in low and "change" not in low:
                    dem_seats = num(r[c])
                elif "democratic" in low and "change" in low:
                    dem_chg = num(r[c])
                elif "republican" in low and "seats" in low and "change" not in low:
                    rep_seats = num(r[c])
                elif "republican" in low and "change" in low:
                    rep_chg = num(r[c])
            rows.append({"cycle": cycle, "state": state,
                         "total_seats": num(r[cols[1]]),
                         "dem_seats": dem_seats, "dem_change": dem_chg,
                         "rep_seats": rep_seats, "rep_change": rep_chg})
    out = pd.DataFrame(rows)
    out.to_csv(SAMPLE / "house_seats_by_state.csv", index=False)
    log(f"house_seats_by_state.csv: {len(out)} rows")
    return out


def parse_house_closest():
    rows = []
    for cycle, fname, idx in [(2018, "wiki18house.html", 9),
                              (2022, "wiki22house.html", 13)]:
        t = pd.read_html(RAW / fname)[idx]
        t.columns = [str(c).strip() for c in t.columns]
        for _, r in t.iterrows():
            margin = num(str(r["Margin"]).replace("pp", "").replace("%", ""))
            rows.append({"cycle": cycle, "district": str(r["District"]).strip(),
                         "winner": str(r["Winner"]).strip(), "margin_pts": margin})
    out = pd.DataFrame(rows)
    out.to_csv(SAMPLE / "house_closest_races.csv", index=False)
    log(f"house_closest_races.csv: {len(out)} rows "
        f"(2018: {(out.cycle == 2018).sum()}, 2022: {(out.cycle == 2022).sum()})")
    return out


# ---------------------------------------------------------------- Senate 2026
def parse_senate_2026():
    """2026 Senate composition, parsed from the Wikipedia composition table.

    The table's own rows give: seats before, seats not up, seats up, and
    seats won (general + special). Seats after = not up + won. Flips are
    counted from the rows whose text says "replaced by ... Democrats".
    """
    t = pd.read_html(RAW / "wiki26sen.html")[3]
    # columns: 0,1 = row labels (sub-row labels live in col 1 when col 0 is
    # blank); 2 = Democratic; 3 = Independent; 4 = Republican; 5 = Total
    before = not_up = up = None
    result_rows = []  # (total, D, I, R) for every "Result" row, in order
    flips = 0
    for _, r in t.iterrows():
        text = " ".join(str(x) for x in r.values if str(x) != "nan")
        label0 = str(r.iloc[0]).strip()
        label1 = str(r.iloc[1]).strip()
        label = label0 if label0 != "nan" else label1
        if label.startswith("Before these elections"):
            before = (num(r.iloc[2]), num(r.iloc[3]), num(r.iloc[4]))
        elif label == "Not up":
            not_up = (num(r.iloc[2]), num(r.iloc[3]), num(r.iloc[4]))
        elif label == "Up":
            up = (num(r.iloc[2]), num(r.iloc[3]), num(r.iloc[4]))
        elif label == "Result":
            result_rows.append((num(r.iloc[5]), num(r.iloc[2]),
                                num(r.iloc[3]), num(r.iloc[4])))
        if "replaced by" in text and "Democrat" in text:
            flips += int(num(r.iloc[5]) or 0)
    # Result rows in order: retiring (11), running (20), special (2),
    # overall general (33). General = the largest-total row; special = the
    # row with total 2. NOTE: retiring+running sub-rows sum to 31, not 33 —
    # two races' outcomes appear only in the overall row (footnote [f][g]
    # on the running row); the composition arithmetic uses the overall row.
    gen = max(result_rows, key=lambda x: x[0])
    spec = [x for x in result_rows if x[0] == 2][0]
    gen_result = (gen[1], gen[2], gen[3])
    spec_result = (spec[1], spec[2], spec[3])
    assert before and not_up and up and gen_result and spec_result, \
        f"Senate table parse failed: {before} {not_up} {up} {gen_result} {spec_result}"
    won = tuple((gen_result[i] or 0) + (spec_result[i] or 0) for i in range(3))
    parties = ["Democratic", "Republican", "Independent"]
    idx = {"Democratic": 0, "Republican": 2, "Independent": 1}
    recs = []
    for p in parties:
        i = idx[p]
        after = (not_up[i] or 0) + (won[i] or 0)
        recs.append({"cycle": 2026, "chamber": "Senate", "party": p,
                     "seats_before": before[i], "seats_not_up": not_up[i],
                     "seats_up": up[i], "seats_won_up": won[i],
                     "seats_after": after,
                     "net_change": after - (before[i] or 0)})
    out = pd.DataFrame(recs)
    out.to_csv(SAMPLE / "senate_2026_composition.csv", index=False)
    log(f"senate_2026_composition.csv: {len(out)} rows "
        f"(D {before[0]:.0f}->{out.loc[0,'seats_after']:.0f}, "
        f"R {before[2]:.0f}->{out.loc[1,'seats_after']:.0f}; "
        f"flips to Democrats: {flips})")
    return out, flips


# ---------------------------------------------------------------- Control table
def parse_control_table():
    """Party control per Congress, 1994-2026, from Wikipedia's Party divisions
    table. The table re-headers when the party system changes; for the modern
    era the columns are Democratic / Republican directly. The President cell
    uses rowspan, so its value is carried forward across rows that omit it.
    Counts like '46/45' (changed mid-Congress) take the first value, which
    is the composition at the start of the Congress."""
    from lxml import html as lh
    tree = lh.parse(str(RAW / "wiki_control.html"))
    table = tree.xpath('//table[contains(@class,"wikitable")]')[0]
    rows = table.xpath('.//tr')
    pres_party_by_name = {
        "Washington": None, "Adams": None, "Jefferson": None, "Madison": None,
        "Monroe": None, "Quincy Adams": None, "Jackson": None,
        "Van Buren": None, "Harrison": None, "Tyler": None, "Polk": None,
        "Taylor": None, "Fillmore": None, "Pierce": None, "Buchanan": None,
        "Lincoln": "Republican", "Johnson": "Democratic", "Grant": "Republican",
        "Hayes": "Republican", "Garfield": "Republican", "Arthur": "Republican",
        "Cleveland": "Democratic", "Harrison": "Republican",
        "McKinley": "Republican", "Roosevelt": "Republican", "Taft": "Republican",
        "Wilson": "Democratic", "Harding": "Republican", "Coolidge": "Republican",
        "Hoover": "Republican", "Roosevelt": "Democratic", "Truman": "Democratic",
        "Eisenhower": "Republican", "Kennedy": "Democratic",
        "Nixon": "Republican", "Ford": "Republican", "Carter": "Democratic",
        "Reagan": "Republican", "Bush": "Republican", "Clinton": "Democratic",
        "Obama": "Democratic", "Trump": "Republican", "Biden": "Democratic",
    }

    def first_count(s):
        if s is None:
            return None
        s = str(s)
        for sep in ("/", "–", "—", "-"):
            s = s.split(sep)[0]
        return num(s.strip())

    def party_of_president(name):
        name = re.sub(r"\[.*?\]", "", str(name)).strip()
        for key, party in pres_party_by_name.items():
            if key in name:
                return party, name
        return None, name

    recs = []
    header = None
    current_pres = None
    for tr in rows:
        cells = [c.text_content().strip() for c in tr.xpath('.//th|.//td')]
        if not cells:
            continue
        if cells[0] == "Congress":
            header = cells  # sub-column names for Senate/House
            continue
        if len(cells) < 13 or not re.match(r"^\d+(st|nd|rd|th)$", cells[0]):
            continue
        congress = int(re.match(r"^(\d+)", cells[0]).group(1))
        years = cells[1]
        # President: 14-cell rows carry it in cells[12]; 13-cell rows omit it
        if len(cells) == 14:
            current_pres = cells[12]
        pres_party, pres_name = party_of_president(current_pres or "")
        sen_c1, sen_c2 = first_count(cells[3]), first_count(cells[4])
        hou_c1, hou_c2 = first_count(cells[8]), first_count(cells[9])
        # Header tells us what columns 3/4 and 8/9 are.
        sen_mode = header[3] if header and len(header) > 3 else ""
        if sen_mode in ("Democrats", "Democratic"):
            sen_dem, sen_rep, hou_dem, hou_rep = sen_c1, sen_c2, hou_c1, hou_c2
        elif "Anti" in sen_mode:
            if pres_party == "Democratic":
                sen_dem, sen_rep = sen_c2, sen_c1
                hou_dem, hou_rep = hou_c2, hou_c1
            else:
                sen_dem, sen_rep = sen_c1, sen_c2
                hou_dem, hou_rep = hou_c1, hou_c2
        else:
            sen_dem = sen_rep = hou_dem = hou_rep = None
        recs.append({"congress": congress, "years": years,
                     "president": pres_name, "president_party": pres_party,
                     "senate_dem": sen_dem, "senate_rep": sen_rep,
                     "house_dem": hou_dem, "house_rep": hou_rep})
    out = pd.DataFrame(recs)
    # Keep Congresses whose term covers 1994-2026 (103rd, 1993-95, to 119th, 2025-27)
    out = out[(out["congress"] >= 103) & (out["congress"] <= 119)].copy()
    out.to_csv(SAMPLE / "control_table.csv", index=False)
    log(f"control_table.csv: {len(out)} rows (Congresses 103-119)")
    return out


# ---------------------------------------------------------------- Turnout
def parse_turnout():
    v14 = pd.read_csv(RAW / "vep14b.csv")
    v14 = v14.rename(columns={"TURNOUT_RATE_MIDTERM": "vep_turnout_rate"})
    v14["vep_turnout_rate"] = pd.to_numeric(v14["vep_turnout_rate"], errors="coerce")
    nat = v14[(v14["YEAR"] >= 1994) & (v14["YEAR"] <= 2022) & (v14["YEAR"] % 2 == 0)]
    rows = [{"year": int(r["YEAR"]), "vep_turnout_rate_pct": round(r["vep_turnout_rate"] * 100, 2),
             "status": "final", "source": "UF Election Lab US_VEP_Turnout_Rates_v1.4"}
            for _, r in nat.iterrows() if pd.notna(r["vep_turnout_rate"])]
    rows.append({"year": 2026, "vep_turnout_rate_pct": None,
                 "status": "not yet published",
                 "source": "UF Election Lab has not published a 2026 VEP rate; "
                           "Wikipedia infobox reports an estimated 125 million total "
                           "ballots (preliminary, no VEP denominator published)"})
    out = pd.DataFrame(rows)
    out.to_csv(SAMPLE / "turnout_national.csv", index=False)
    log(f"turnout_national.csv: {len(out)} rows (1994-2022 final, 2026 not yet published)")
    v12 = pd.read_csv(RAW / "Turnout_1980_2022_v1.2.csv")
    st22 = v12[(v12["YEAR"] == 2022) & (v12["STATE"] != "United States")][
        ["STATE", "STATE_ABV", "VEP_TURNOUT_RATE", "TOTAL_BALLOTS_COUNTED"]].copy()
    st22.columns = ["state", "state_abv", "vep_turnout_rate", "total_ballots_counted"]
    st22.to_csv(SAMPLE / "turnout_state_2022.csv", index=False)
    log(f"turnout_state_2022.csv: {len(st22)} rows")
    return out


# ---------------------------------------------------------------- FEC
FEC_COLS = ["cand_id", "cand_name", "cand_ici", "party_code", "party",
            "total_receipts", "transfers_from_auth", "total_disbursements",
            "reserved_09", "cash_on_hand_bop", "cash_on_hand_end",
            "reserved_12", "reserved_13", "reserved_14", "loan_repayments",
            "reserved_16", "debts_owed_by", "individual_contributions",
            "office_state", "office_district",
            "addr_1", "addr_2", "addr_3", "addr_4", "addr_5",
            "other_committee_contributions", "party_committee_contributions",
            "coverage_end_date", "refunded_individual",
            "refunded_other_committee"]
MONEY = ["total_receipts", "transfers_from_auth", "total_disbursements",
         "cash_on_hand_bop", "cash_on_hand_end", "loan_repayments",
         "debts_owed_by", "individual_contributions",
         "other_committee_contributions", "party_committee_contributions",
         "refunded_individual", "refunded_other_committee"]


def parse_fec():
    import zipfile
    for cycle, fname in [(2018, "weball18.zip"), (2022, "weball22.zip"),
                         (2026, "weball26.zip")]:
        with zipfile.ZipFile(RAW / fname) as z:
            name = z.namelist()[0]
            raw = z.read(name).decode("utf-8", errors="replace")
        rows = [ln.split("|") for ln in raw.splitlines() if ln.strip()]
        bad = [r for r in rows if len(r) != 30]
        log(f"fec {cycle}: {len(rows)} rows, {len(bad)} with !=30 fields (quarantined in silver)")
        df = pd.DataFrame([r for r in rows if len(r) == 30], columns=FEC_COLS)
        for c in MONEY:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["cycle"] = cycle
        df["office"] = df["cand_id"].str[0]
        df.to_csv(SAMPLE / f"fec_{cycle}.csv", index=False)
        log(f"fec_{cycle}.csv: {len(df)} rows")


# ---------------------------------------------------------------- MEDSL + Census
def parse_medsl_census():
    pres = pd.read_csv(RAW / "1976-2024-president.csv")
    pres = pres[pres["year"].isin([2016, 2020, 2024])].copy()
    pres.to_csv(SAMPLE / "president_state.csv", index=False)
    log(f"president_state.csv: {len(pres)} rows (2016/2020/2024, state-level)")
    sen = pd.read_csv(RAW / "1976-2024-senate-state.tab")
    # stage is 'gen' in older years and 'GEN' in 2022/2024; runoffs excluded
    sen = sen[(sen["year"] >= 2014) & (sen["stage"].str.upper() == "GEN")].copy()
    sen.to_csv(SAMPLE / "senate_state.csv", index=False)
    log(f"senate_state.csv: {len(sen)} rows (2014-2024 general elections)")
    pop = pd.read_csv(RAW / "co-est2024-alldata.csv", encoding="latin-1", usecols=[
        "SUMLEV", "STATE", "COUNTY", "STNAME", "CTYNAME", "POPESTIMATE2024"])
    pop = pop[pop["SUMLEV"] == 50].copy()
    pop["fips"] = pop["STATE"] * 1000 + pop["COUNTY"]
    pop = pop[["fips", "STNAME", "CTYNAME", "POPESTIMATE2024"]].rename(columns={
        "STNAME": "state_name", "CTYNAME": "county_name",
        "POPESTIMATE2024": "population_2024"})
    pop.to_csv(SAMPLE / "counties_population.csv", index=False)
    log(f"counties_population.csv: {len(pop)} counties")


def main():
    hs = parse_house_summary()
    parse_house_seats_by_state()
    parse_house_closest()
    parse_senate_2026()
    parse_control_table()
    parse_turnout()
    parse_fec()
    parse_medsl_census()
    print("\n--- 01_acquire complete ---")
    print(hs.to_string(index=False))


if __name__ == "__main__":
    main()
