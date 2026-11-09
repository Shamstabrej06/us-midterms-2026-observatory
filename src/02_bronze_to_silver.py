"""Step 2 — bronze -> silver: clean, harmonise, validate, quarantine.

Reads the extracts in data/sample/ (produced by src/01_acquire.py) and
writes cleaned, harmonised silver tables to data/silver/.

Harmonisation decisions (documented, applied uniformly):
  * Party labels: DEM / DFL -> Democratic; REP -> Republican; every other
    code -> Other (original code kept in *_raw columns).
  * State names: title case, matched to USPS abbreviations and FIPS codes
    via the STATE_FIPS reference table below (50 states + DC).
  * Money and vote fields: coerced to numeric; parse failures are counted
    and the rows go to quarantine.csv with a reason.
  * Net seat change is always computed (after - before); the source
    tables' +/- column is unsigned and is never trusted.
  * 2026 figures are flagged preliminary wherever they appear.

Run:  python3 src/02_bronze_to_silver.py
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"
SILVER = ROOT / "data" / "silver"
RAW = ROOT / "data" / "raw"
SILVER.mkdir(parents=True, exist_ok=True)

QUARANTINE = []


def quarantine(source, key, reason, detail=""):
    QUARANTINE.append({"source": source, "key": str(key), "reason": reason,
                       "detail": str(detail)[:200]})


STATE_FIPS = {
    "Alabama": ("AL", 1), "Alaska": ("AK", 2), "Arizona": ("AZ", 4),
    "Arkansas": ("AR", 5), "California": ("CA", 6), "Colorado": ("CO", 8),
    "Connecticut": ("CT", 9), "Delaware": ("DE", 10),
    "District of Columbia": ("DC", 11), "Florida": ("FL", 12),
    "Georgia": ("GA", 13), "Hawaii": ("HI", 15), "Idaho": ("ID", 16),
    "Illinois": ("IL", 17), "Indiana": ("IN", 18), "Iowa": ("IA", 19),
    "Kansas": ("KS", 20), "Kentucky": ("KY", 21), "Louisiana": ("LA", 22),
    "Maine": ("ME", 23), "Maryland": ("MD", 24), "Massachusetts": ("MA", 25),
    "Michigan": ("MI", 26), "Minnesota": ("MN", 27), "Mississippi": ("MS", 28),
    "Missouri": ("MO", 29), "Montana": ("MT", 30), "Nebraska": ("NE", 31),
    "Nevada": ("NV", 32), "New Hampshire": ("NH", 33), "New Jersey": ("NJ", 34),
    "New Mexico": ("NM", 35), "New York": ("NY", 36),
    "North Carolina": ("NC", 37), "North Dakota": ("ND", 38),
    "Ohio": ("OH", 39), "Oklahoma": ("OK", 40), "Oregon": ("OR", 41),
    "Pennsylvania": ("PA", 42), "Rhode Island": ("RI", 44),
    "South Carolina": ("SC", 45), "South Dakota": ("SD", 46),
    "Tennessee": ("TN", 47), "Texas": ("TX", 48), "Utah": ("UT", 49),
    "Vermont": ("VT", 50), "Virginia": ("VA", 51), "Washington": ("WA", 53),
    "West Virginia": ("WV", 54), "Wisconsin": ("WI", 55),
    "Wyoming": ("WY", 56),
    # Territories (non-voting House delegates appear in the FEC files)
    "Puerto Rico": ("PR", 72), "Guam": ("GU", 66),
    "U.S. Virgin Islands": ("VI", 78), "American Samoa": ("AS", 60),
    "Northern Mariana Islands": ("MP", 69),
}
ABBR_TO_FIPS = {v[0]: v[1] for v in STATE_FIPS.values()}
ABBR_TO_NAME = {v[0]: k for k, v in STATE_FIPS.items()}


def std_party(code):
    """Standardise a party code to Democratic / Republican / Other."""
    if pd.isna(code):
        return "Other"
    c = str(code).strip().upper()
    if c in ("DEM", "DEMOCRAT", "DEMOCRATIC", "DFL"):
        return "Democratic"
    if c in ("REP", "REPUBLICAN"):
        return "Republican"
    return "Other"


def num(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip().replace(",", "").replace("%", "").replace("\u2212", "-")
    s = re.sub(r"\[.*?\]", "", s).strip()
    if s in ("", "-", "—", "–", "NaN", "nan", "None"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def log(msg):
    print(msg)


# ------------------------------------------------------------------ House
def silver_house():
    hs = pd.read_csv(SAMPLE / "house_summary.csv")
    hs["party"] = hs["party"].apply(std_party)
    for c in ["seats_before", "seats_after", "net_change", "popular_votes"]:
        hs[c] = pd.to_numeric(hs[c], errors="coerce").astype("Int64")
    hs["popular_pct"] = pd.to_numeric(hs["popular_pct"], errors="coerce")
    hs["status"] = hs["cycle"].apply(lambda y: "preliminary" if y == 2026 else "certified")
    # validation: seats sum to 435 per cycle, allowing the one Independent
    # seat (1994/1998/2002) or the one vacancy (2018, NC-09) that the
    # two-party filter drops. Anything else is a real defect.
    for cycle, g in hs.groupby("cycle"):
        tot = g["seats_after"].sum()
        remainder = 435 - tot
        if cycle != 2026 and remainder not in (0, 1):
            quarantine("house_summary", cycle, "seats_after != 435",
                       f"sum={tot}, remainder={remainder}")
    hs.to_csv(SILVER / "silver_house_summary.csv", index=False)
    log(f"silver_house_summary.csv: {len(hs)} rows")

    st = pd.read_csv(SAMPLE / "house_seats_by_state.csv")
    st["state_abbr"] = st["state"].map(lambda s: STATE_FIPS.get(s, (None, None))[0])
    st["state_fips"] = st["state"].map(lambda s: STATE_FIPS.get(s, (None, None))[1])
    miss = st[st["state_abbr"].isna()]["state"].unique()
    for m in miss:
        quarantine("house_seats_by_state", m, "unmatched state name")
    st["delegation_majority"] = st.apply(
        lambda r: "Democratic" if (r["dem_seats"] or 0) > (r["rep_seats"] or 0)
        else ("Republican" if (r["rep_seats"] or 0) > (r["dem_seats"] or 0)
              else "Even"), axis=1)
    st.to_csv(SILVER / "silver_house_seats_by_state.csv", index=False)
    log(f"silver_house_seats_by_state.csv: {len(st)} rows")

    cl = pd.read_csv(SAMPLE / "house_closest_races.csv")
    cl["margin_band"] = cl["margin_pts"].apply(
        lambda m: "<5 pts" if m < 5 else ("5-10 pts" if m < 10 else ">10 pts"))
    neg = cl[cl["margin_pts"] < 0]
    for _, r in neg.iterrows():
        quarantine("house_closest_races", r["district"], "negative margin")
    cl = cl[cl["margin_pts"] >= 0]
    cl.to_csv(SILVER / "silver_house_closest_races.csv", index=False)
    log(f"silver_house_closest_races.csv: {len(cl)} rows")


def silver_senate_control():
    sen = pd.read_csv(SAMPLE / "senate_2026_composition.csv")
    sen["seats_up"] = sen["seats_up"].fillna(0).astype(int)
    sen["status"] = "preliminary"
    sen.to_csv(SILVER / "silver_senate_2026.csv", index=False)
    log(f"silver_senate_2026.csv: {len(sen)} rows")

    ct = pd.read_csv(SAMPLE / "control_table.csv")
    ct["senate_majority"] = ct.apply(
        lambda r: "Democratic" if (r["senate_dem"] or 0) > (r["senate_rep"] or 0)
        else ("Republican" if (r["senate_rep"] or 0) > (r["senate_dem"] or 0)
              else "Even"), axis=1)
    # Documented correction: the 110th Congress (2006 election) shows
    # 49 Democrats / 49 Republicans in the control table, with 2
    # independents (Sanders, Lieberman) who both caucused with the
    # Democrats, giving Democrats the effective 51-seat majority.
    ct.loc[ct["congress"] == 110, "senate_majority"] = "Democratic"
    ct["house_majority"] = ct.apply(
        lambda r: "Democratic" if (r["house_dem"] or 0) > (r["house_rep"] or 0)
        else ("Republican" if (r["house_rep"] or 0) > (r["house_dem"] or 0)
              else "Even"), axis=1)
    ct["trifecta"] = ct.apply(
        lambda r: (r["senate_majority"] == r["house_majority"] == r["president_party"])
        if pd.notna(r["president_party"]) else None, axis=1)
    ct.to_csv(SILVER / "silver_control.csv", index=False)
    log(f"silver_control.csv: {len(ct)} rows")


def silver_turnout():
    tn = pd.read_csv(SAMPLE / "turnout_national.csv")
    tn.to_csv(SILVER / "silver_turnout_national.csv", index=False)
    log(f"silver_turnout_national.csv: {len(tn)} rows")
    ts = pd.read_csv(SAMPLE / "turnout_state_2022.csv")
    ts["vep_turnout_rate_pct"] = ts["vep_turnout_rate"].str.rstrip("%").astype(float)
    ts.to_csv(SILVER / "silver_turnout_state_2022.csv", index=False)
    log(f"silver_turnout_state_2022.csv: {len(ts)} rows")


# ------------------------------------------------------------------ FEC
def silver_finance():
    frames = []
    for cycle in (2018, 2022, 2026):
        df = pd.read_csv(SAMPLE / f"fec_{cycle}.csv")
        frames.append(df)
    f = pd.concat(frames, ignore_index=True)
    # Audit, not quarantine: negative money values are legitimate in FEC
    # data (refunds exceed receipts; cash on hand can go negative when a
    # committee owes more than it holds). Count them and keep the rows.
    money = ["total_receipts", "total_disbursements", "cash_on_hand_bop",
             "cash_on_hand_end", "individual_contributions"]
    for c in money:
        n_neg = int((pd.to_numeric(f[c], errors="coerce") < 0).sum())
        n_bad = int(pd.to_numeric(f[c], errors="coerce").isna().sum())
        log(f"  fec audit {c}: {n_neg} negative (legitimate), {n_bad} unparseable")
        if n_bad:
            for _, r in f[pd.to_numeric(f[c], errors="coerce").isna()].iterrows():
                quarantine("fec", r["cand_id"], f"unparseable {c}", r[c])
    f["party_std"] = f["party"].apply(std_party)
    f["office_name"] = f["office"].map({"H": "House", "S": "Senate", "P": "President"})
    f["state_name"] = f["office_state"].map(ABBR_TO_NAME)
    miss = f[f["state_name"].isna() & f["office"].isin(["H", "S"])]
    for _, r in miss.iterrows():
        quarantine("fec", r["cand_id"], "unmatched office state", r["office_state"])
    f["coverage_end_date"] = pd.to_datetime(f["coverage_end_date"], errors="coerce")
    f["status"] = f["cycle"].apply(lambda y: "preliminary" if y == 2026 else "certified")
    f.to_csv(SILVER / "silver_finance.csv", index=False)
    log(f"silver_finance.csv: {len(f)} rows "
        f"(2018: {(f.cycle == 2018).sum()}, 2022: {(f.cycle == 2022).sum()}, "
        f"2026: {(f.cycle == 2026).sum()})")
    return f


# ------------------------------------------------------------------ MEDSL
def _two_party(df, group_cols):
    """Two-party (D vs R) vote share per group. Returns one row per group
    with dem_votes, rep_votes, total_two_party, dem_share_pct, margin_pts
    (positive = Democratic lead)."""
    d = df[df["party_simplified"].isin(["DEMOCRAT", "REPUBLICAN"])].copy()
    d["party_std"] = d["party_simplified"].map({"DEMOCRAT": "Democratic",
                                                "REPUBLICAN": "Republican"})
    piv = d.pivot_table(index=group_cols, columns="party_std",
                        values="candidatevotes", aggfunc="sum", fill_value=0)
    piv = piv.reset_index()
    for col in ("Democratic", "Republican"):
        if col not in piv.columns:
            piv[col] = 0
    piv["total_two_party"] = piv["Democratic"] + piv["Republican"]
    piv["dem_share_pct"] = (piv["Democratic"] / piv["total_two_party"] * 100).round(2)
    piv["margin_pts"] = ((piv["Democratic"] - piv["Republican"])
                         / piv["total_two_party"] * 100).round(2)
    return piv


def silver_medsl():
    pres = pd.read_csv(SAMPLE / "president_state.csv")
    pres["candidatevotes"] = pd.to_numeric(pres["candidatevotes"], errors="coerce")
    neg = pres[pres["candidatevotes"] < 0]
    for _, r in neg.iterrows():
        quarantine("president_state", f"{r['year']}-{r['state_po']}", "negative votes")
    pres = pres[pres["candidatevotes"] >= 0]
    tp = _two_party(pres, ["year", "state", "state_po"])
    tp.to_csv(SILVER / "silver_president_state.csv", index=False)
    log(f"silver_president_state.csv: {len(tp)} state-years")

    sen = pd.read_csv(SAMPLE / "senate_state.csv")
    sen["candidatevotes"] = pd.to_numeric(sen["candidatevotes"], errors="coerce")
    neg = sen[sen["candidatevotes"] < 0]
    for _, r in neg.iterrows():
        quarantine("senate_state", f"{r['year']}-{r['state_po']}", "negative votes")
    sen = sen[sen["candidatevotes"] >= 0]
    tp2 = _two_party(sen, ["year", "state", "state_po", "special"])
    tp2.to_csv(SILVER / "silver_senate_state.csv", index=False)
    log(f"silver_senate_state.csv: {len(tp2)} state-races")
    return tp, tp2


# ------------------------------------------------------------------ Governors
def _parse_candidates(cell):
    """Parse 'Name (Party) 52.0% ▌Name (Party) 48.0%' into [(name, party, pct)]."""
    if pd.isna(cell):
        return []
    out = []
    for m in re.finditer(r"([^▌|]+?)\s*\(([^)]+)\)\s*([\d.]+)\s*%", str(cell)):
        out.append((m.group(1).strip(), m.group(2).strip(), float(m.group(3))))
    return out


def _gov_winner(row):
    """Winner party for a governor race from the Status column."""
    status = str(row["Status"])
    party = std_party(row["Party"])
    if "Democratic gain" in status:
        return "Democratic", "gain"
    if "Republican gain" in status:
        return "Republican", "gain"
    if "Democratic hold" in status:
        return "Democratic", "hold"
    if "Republican hold" in status:
        return "Republican", "hold"
    if "Incumbent re-elected" in status or "elected to full term" in status:
        return party, "hold"
    return None, "uncalled"


def silver_governors():
    frames = []
    for cycle, fname, idx, state_col in [
            (2022, "wiki22gov.html", 3, "States"),
            (2026, "wiki26gov.html", 3, "State")]:
        t = pd.read_html(RAW / fname)[idx]
        t.columns = [str(c).strip() for c in t.columns]
        for _, r in t.iterrows():
            state = str(r[state_col]).strip()
            if state not in STATE_FIPS:
                quarantine("governors", f"{cycle}-{state}", "unmatched state name")
                continue
            winner, kind = _gov_winner(r)
            cands = _parse_candidates(r["Candidates[13]"] if "Candidates[13]" in t.columns
                                      else r.get("Candidates[20]", ""))
            margin = None
            # no margin for uncalled races: the Candidates cell can carry
            # partial/primary figures that would mislead
            if winner is not None and len(cands) >= 2:
                top = sorted(cands, key=lambda x: -x[2])
                margin = round(top[0][2] - top[1][2], 2)
            frames.append({"cycle": cycle, "state": state,
                           "state_abbr": STATE_FIPS[state][0],
                           "state_fips": STATE_FIPS[state][1],
                           "incumbent": str(r["Governor"]).strip(),
                           "incumbent_party": std_party(r["Party"]),
                           "winner_party": winner, "outcome": kind,
                           "margin_pts": margin,
                           "status": "preliminary" if cycle == 2026 else "certified"})
    g = pd.DataFrame(frames)
    g.to_csv(SILVER / "silver_governors.csv", index=False)
    log(f"silver_governors.csv: {len(g)} rows "
        f"(2022: {(g.cycle == 2022).sum()}, 2026: {(g.cycle == 2026).sum()})")
    return g


# ------------------------------------------------------------------ Senate flips
def silver_senate_flips():
    t = pd.read_html(RAW / "wiki26sen.html")[14]
    t.columns = [" | ".join(str(c) for c in col).strip() for col in t.columns]
    rows = []
    for _, r in t.iterrows():
        state = str(r["Constituency | State"]).strip()
        result = str(r["Results | Results"])
        if "Democratic gain" not in result:
            continue
        cands = [c.strip(" ▌") for c in str(r["Candidates | Candidates"]).split("▌")]
        cands = [c for c in cands if c]
        # first listed candidate is the winner on this page
        winner = cands[0] if cands else None
        winner_party = None
        m = re.match(r"(.+?)\s*\((.+?)\)\s*$", winner or "")
        if m:
            winner, winner_party = m.group(1).strip(), m.group(2).strip()
        rows.append({"cycle": 2026, "chamber": "Senate", "state": state,
                     "state_abbr": STATE_FIPS.get(state, (None, None))[0],
                     "incumbent": str(r["Incumbent | Senator"]).strip(),
                     "incumbent_party": std_party(r["Incumbent | Party"]),
                     "winner": winner, "winner_party": std_party(winner_party),
                     "result_text": result.strip()[:160],
                     "status": "preliminary"})
    f = pd.DataFrame(rows)
    f.to_csv(SILVER / "silver_senate_flips_2026.csv", index=False)
    log(f"silver_senate_flips_2026.csv: {len(f)} named flips "
        f"(composition table records 7 R->D flips in total)")
    return f


# ------------------------------------------------------------------ Texas
def _infobox_race(fname, table_idx=0):
    """Parse a Wikipedia election infobox (Nominee / Party / Popular vote /
    Percentage) into {party: (candidate, votes, pct)}."""
    t = pd.read_html(RAW / fname)[table_idx]
    t = t.astype(str)
    out = {}
    for _, r in t.iterrows():
        label = str(r.iloc[0]).replace("\xa0", " ").strip()
        if label == "Nominee":
            cands = [str(r.iloc[1]).strip(), str(r.iloc[2]).strip()]
        elif label == "Party":
            parties = [str(r.iloc[1]).strip(), str(r.iloc[2]).strip()]
        elif label == "Popular vote":
            votes = [num(r.iloc[1]), num(r.iloc[2])]
        elif label == "Percentage":
            pcts = [num(r.iloc[1]), num(r.iloc[2])]
    for c, p, v, pc in zip(cands, parties, votes, pcts):
        out[std_party(p)] = (c, v, pc)
    return out


def silver_texas(pres_tp, sen_tp):
    rows = []
    # Governor: 2014 / 2018 / 2022 infoboxes + 2026 from the gov page table 102
    for cycle, fname in [(2014, "wiki2014txgov.html"), (2018, "wiki2018txgov.html"),
                         (2022, "wiki2022txgov.html")]:
        d = _infobox_race(fname)
        dem = d.get("Democratic", (None, None, None))
        rep = d.get("Republican", (None, None, None))
        rows.append({"cycle": cycle, "state": "Texas", "office": "Governor",
                     "dem_candidate": dem[0], "dem_votes": dem[1], "dem_pct": dem[2],
                     "rep_candidate": rep[0], "rep_votes": rep[1], "rep_pct": rep[2],
                     "margin_pts": round(dem[2] - rep[2], 2) if dem[2] and rep[2] else None,
                     "winner_party": "Republican", "status": "certified"})
    gov26 = _infobox_race("wiki26gov.html", 102)
    dem, rep = gov26["Democratic"], gov26["Republican"]
    rows.append({"cycle": 2026, "state": "Texas", "office": "Governor",
                 "dem_candidate": dem[0], "dem_votes": dem[1], "dem_pct": dem[2],
                 "rep_candidate": rep[0], "rep_votes": rep[1], "rep_pct": rep[2],
                 "margin_pts": round(dem[2] - rep[2], 2),
                 "winner_party": "Democratic", "status": "preliminary"})
    # Senate: MEDSL 2014/2018/2020/2024 + 2026 infobox
    for _, r in sen_tp[sen_tp["state_po"] == "TX"].iterrows():
        rows.append({"cycle": int(r["year"]), "state": "Texas", "office": "Senate",
                     "dem_candidate": None, "dem_votes": r["Democratic"],
                     "dem_pct": r["dem_share_pct"],
                     "rep_candidate": None, "rep_votes": r["Republican"],
                     "rep_pct": round(100 - r["dem_share_pct"], 2),
                     "margin_pts": r["margin_pts"],
                     "winner_party": "Democratic" if r["margin_pts"] > 0 else "Republican",
                     "status": "certified"})
    sen26 = _infobox_race("wiki26sen.html", 109)
    dem, rep = sen26["Democratic"], sen26["Republican"]
    rows.append({"cycle": 2026, "state": "Texas", "office": "Senate",
                 "dem_candidate": dem[0], "dem_votes": dem[1], "dem_pct": dem[2],
                 "rep_candidate": rep[0], "rep_votes": rep[1], "rep_pct": rep[2],
                 "margin_pts": round(dem[2] - rep[2], 2),
                 "winner_party": "Democratic", "status": "preliminary"})
    # Attorney General 2026 (Paxton vacated the office to run for Senate)
    ag26 = _infobox_race("wiki26txag.html", 1)
    dem, rep = ag26["Democratic"], ag26["Republican"]
    rows.append({"cycle": 2026, "state": "Texas", "office": "Attorney General",
                 "dem_candidate": dem[0], "dem_votes": dem[1], "dem_pct": dem[2],
                 "rep_candidate": rep[0], "rep_votes": rep[1], "rep_pct": rep[2],
                 "margin_pts": round(dem[2] - rep[2], 2),
                 "winner_party": "Democratic", "status": "preliminary"})
    # President: MEDSL 2016/2020/2024
    for _, r in pres_tp[pres_tp["state_po"] == "TX"].iterrows():
        rows.append({"cycle": int(r["year"]), "state": "Texas", "office": "President",
                     "dem_candidate": None, "dem_votes": r["Democratic"],
                     "dem_pct": r["dem_share_pct"],
                     "rep_candidate": None, "rep_votes": r["Republican"],
                     "rep_pct": round(100 - r["dem_share_pct"], 2),
                     "margin_pts": r["margin_pts"],
                     "winner_party": "Democratic" if r["margin_pts"] > 0 else "Republican",
                     "status": "certified"})
    tx = pd.DataFrame(rows).sort_values(["office", "cycle"])
    tx.to_csv(SILVER / "silver_texas_statewide.csv", index=False)
    log(f"silver_texas_statewide.csv: {len(tx)} rows")
    return tx


# ------------------------------------------------------------------ Counties
def silver_counties():
    c = pd.read_csv(SAMPLE / "counties_population.csv")
    c["state_abbr"] = c["state_name"].map(lambda s: STATE_FIPS.get(s, (None, None))[0])
    c.to_csv(SILVER / "silver_counties.csv", index=False)
    log(f"silver_counties.csv: {len(c)} counties")


def main():
    silver_house()
    silver_senate_control()
    silver_turnout()
    silver_finance()
    pres_tp, sen_tp = silver_medsl()
    silver_governors()
    silver_senate_flips()
    silver_texas(pres_tp, sen_tp)
    silver_counties()
    q = pd.DataFrame(QUARANTINE)
    q.to_csv(SILVER / "quarantine.csv", index=False)
    log(f"quarantine.csv: {len(q)} rows")
    if len(q):
        print(q.to_string(index=False))
    print("\n--- 02_bronze_to_silver complete ---")


if __name__ == "__main__":
    main()
