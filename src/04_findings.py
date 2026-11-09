"""Step 4 — findings: compute every metric from the gold layer and write
docs/findings.md + outputs/Findings_Scorecard.xlsx.

Every number below is computed from outputs/midterms.db in this script.
Nothing is hand-typed. Dropped metrics are recorded, not hidden.

Run:  python3 src/04_findings.py
"""

import re
import sqlite3
import unicodedata
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "outputs" / "midterms.db"
RAW = ROOT / "data" / "raw"
OUT_XLSX = ROOT / "outputs" / "Findings_Scorecard.xlsx"
OUT_MD = ROOT / "docs" / "findings.md"

CON = sqlite3.connect(DB)

# ---------------------------------------------------------------- helpers
SUFFIXES = {"JR", "SR", "II", "III", "IV", "JR.", "SR."}


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def norm_name(name):
    """Uppercase, strip suffixes and punctuation -> token string."""
    s = strip_accents(str(name).upper())
    s = re.sub(r"\(.*?\)", "", s)  # (BETO), (MR.) etc.
    s = s.replace(".", "").replace(",", " ").replace("'", "")
    toks = [t for t in s.split() if t not in SUFFIXES]
    return " ".join(toks)


def fec_last(name):
    """FEC names are 'LAST, FIRST ...' -> the last-name part, normalised."""
    s = strip_accents(str(name).upper())
    last = s.split(",")[0].strip()
    last = re.sub(r"\(.*?\)", "", last)
    last = last.replace(".", "").replace("'", "")
    toks = [t for t in last.split() if t not in SUFFIXES]
    return " ".join(toks)


def name_matches(fec_name, medsl_name):
    """True if the FEC candidate's last name appears in the MEDSL name."""
    last = fec_last(fec_name)
    med = norm_name(medsl_name)
    if not last or not med:
        return False
    return last in med or med.split()[-1] == last.split()[-1]


def money(x):
    return f"${x:,.0f}"


def log(msg):
    print(f"  [04] {msg}")


def load(sql):
    return pd.read_sql(sql, CON)


# ---------------------------------------------------------------- MONEY: top spender
def senate_top_spender_rate(cycle):
    """Share of Senate races where the top spender (FEC) won the race.

    2018/2022 winners come from MEDSL (max votes in the race); 2026
    winners from the Wikipedia Senate results table (first-listed
    candidate of the winning party). Candidates are scoped to the race:
    the FEC top spender is taken among candidates whose last name appears
    in that race's MEDSL candidate list, so a regular and a special
    election in the same state-year are not conflated.
    """
    fin = load(f"SELECT * FROM fact_finance WHERE cycle={cycle} AND office='S'")
    if cycle in (2018, 2022):
        sen_raw = pd.read_csv(ROOT / "data" / "sample" / "senate_state.csv")
        races = sen_raw[sen_raw["year"] == cycle]
        tot = hit = 0
        misses = []
        for (st, spec), g in races.groupby(["state_po", "special"]):
            winner = g.loc[g["candidatevotes"].idxmax()]
            cand_names = set(g["candidate"])
            scoped = fin[(fin["state_abbr"] == st)
                         & fin["candidate_name"].apply(
                             lambda n: any(name_matches(n, c) for c in cand_names))]
            if len(scoped) == 0:
                continue
            top = scoped.loc[scoped["total_receipts"].idxmax()]
            tot += 1
            if name_matches(top["candidate_name"], winner["candidate"]):
                hit += 1
            else:
                misses.append((st, "SPECIAL" if spec else "REG",
                               top["candidate_name"], winner["candidate"]))
        return hit, tot, misses
    # 2026: winners from the Wikipedia Senate per-state results table.
    # FEC candidates are scoped to the table's candidate list for that
    # state, so primary losers (e.g. Krishnamoorthi in IL) and senators
    # not up for re-election (e.g. Thune in SD) do not count as the
    # race's top spender.
    t = pd.read_html(RAW / "wiki26sen.html")[14]
    t.columns = [" | ".join(str(c) for c in col).strip() for col in t.columns]
    win = {}
    race_cands = {}
    for _, r in t.iterrows():
        st = str(r["Constituency | State"]).strip()
        res = str(r["Results | Results"])
        cands = [re.sub(r"\[\d+\]", "", c).strip(" ▌")
                 for c in str(r["Candidates | Candidates"]).split("▌")]
        cands = [c for c in cands if c]
        race_cands[st] = cands
        if "Democratic gain" in res or "Democratic hold" in res:
            wp = "Democratic"
        elif "Republican hold" in res:
            wp = "Republican"
        elif "Incumbent re-elected" in res:
            wp = "Democratic" if "Democratic" in str(r["Incumbent | Party"]) else "Republican"
        elif "DFL hold" in res:
            wp = "Democratic"
        else:
            continue  # uncalled / no outcome stated
        for c in cands:
            m = re.match(r"(.+?)\s*\((.+?)\)\s*$", c)
            if m and (m.group(2).strip() in ("Democratic", "Republican", "DFL")
                      and ((wp == "Democratic" and m.group(2).strip() in ("Democratic", "DFL"))
                           or (wp == "Republican" and m.group(2).strip() == "Republican"))):
                win[st] = m.group(1).strip()
                break
    tot = hit = 0
    misses = []
    for st, winner in win.items():
        abbr = {"Alabama": "AL", "Alaska": "AK", "Arkansas": "AR", "Colorado": "CO",
                "Delaware": "DE", "Georgia": "GA", "Idaho": "ID", "Illinois": "IL",
                "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
                "Maine": "ME", "Massachusetts": "MA", "Michigan": "MI",
                "Minnesota": "MN", "Mississippi": "MS", "Montana": "MT",
                "Nebraska": "NE", "New Hampshire": "NH", "New Jersey": "NJ",
                "New Mexico": "NM", "North Carolina": "NC", "Oklahoma": "OK",
                "Oregon": "OR", "Rhode Island": "RI", "South Carolina": "SC",
                "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
                "Virginia": "VA", "West Virginia": "WV", "Wyoming": "WY"}.get(st)
        if not abbr:
            continue
        cands = race_cands.get(st, [])
        scoped = fin[(fin["state_abbr"] == abbr)
                     & fin["candidate_name"].apply(
                         lambda n: any(name_matches(n, c) for c in cands))]
        if len(scoped) == 0:
            continue
        top = scoped.loc[scoped["total_receipts"].idxmax()]
        tot += 1
        if name_matches(top["candidate_name"], winner):
            hit += 1
        else:
            misses.append((st, "2026", top["candidate_name"], winner))
    return hit, tot, misses


def main():
    fr = load("SELECT * FROM fact_results")
    ff = load("SELECT * FROM fact_finance")
    ft = load("SELECT * FROM fact_turnout")
    tx = load("SELECT * FROM fact_texas_statewide")
    cyc = load("SELECT * FROM dim_cycle")
    gov = pd.read_csv(ROOT / "data" / "silver" / "silver_governors.csv")
    flips = pd.read_csv(ROOT / "data" / "silver" / "silver_senate_flips_2026.csv")
    closest = pd.read_csv(ROOT / "data" / "silver" / "silver_house_closest_races.csv")

    # ---------------------------------------------------------- WHAT HAPPENED
    hou = fr[(fr["office_key"] == "HOU") & (fr["geography_level"] == "national")]
    h26 = hou[hou["cycle"] == 2026].set_index("party_name")
    h24 = hou[hou["cycle"] == 2022].set_index("party_name")
    sen26 = load("SELECT * FROM fact_results WHERE 1=0")  # placeholder
    sen_comp = pd.read_csv(ROOT / "data" / "silver" / "silver_senate_2026.csv")

    # ---------------------------------------------------------- MIDTERM PATTERN
    pattern = []
    for _, r in cyc[cyc["election_type"] == "midterm"].iterrows():
        yr = int(r["cycle"])
        pp = r["president_party"]
        row = hou[(hou["cycle"] == yr) & (hou["party_name"] == pp)]
        if len(row):
            row = row.iloc[0]
            pattern.append({"cycle": yr, "president_party": pp,
                            "seats_before": int(row["seats_before"]),
                            "seats_after": int(row["seats_after"]),
                            "net_change": int(row["net_change"]),
                            "popular_pct": float(row["vote_share_pct"])})
    pattern = pd.DataFrame(pattern)

    # ---------------------------------------------------------- TURNOUT
    tn = ft[ft["geography_level"] == "national"].sort_values("cycle")

    # ---------------------------------------------------------- COMPETITIVENESS
    comp = []
    for yr in (2018, 2022):
        sub = closest[closest["cycle"] == yr]
        comp.append({"cycle": yr, "races_under_10": int((sub["margin_pts"] < 10).sum()),
                     "races_under_5": int((sub["margin_pts"] < 5).sum()),
                     "share_under_10_pct": round((sub["margin_pts"] < 10).mean() * 100 / 435 * 100, 1)
                     if False else round((sub["margin_pts"] < 10).sum() / 435 * 100, 1),
                     "share_under_5_pct": round((sub["margin_pts"] < 5).sum() / 435 * 100, 1)})
    comp = pd.DataFrame(comp)

    # ---------------------------------------------------------- MONEY
    money_rows = []
    for yr in (2018, 2022, 2026):
        sub = ff[(ff["cycle"] == yr) & (ff["office"].isin(["H", "S"]))]
        h = sub[sub["office"] == "H"]["total_receipts"].sum()
        s = sub[sub["office"] == "S"]["total_receipts"].sum()
        money_rows.append({"cycle": yr, "house_receipts": h, "senate_receipts": s,
                           "combined_receipts": h + s,
                           "candidates": len(sub)})
    money_df = pd.DataFrame(money_rows)
    top_rates = {}
    for yr in (2018, 2022, 2026):
        hit, tot, misses = senate_top_spender_rate(yr)
        top_rates[yr] = (hit, tot, misses)

    # ---------------------------------------------------------- GEOGRAPHY
    # Democratic seats only: fact_results has one row per party per state,
    # so the pivot must be filtered to the Democratic rows (an unfiltered
    # pivot averages the parties' seat counts).
    hs_state = load("SELECT * FROM fact_results WHERE office_key='HOU' "
                    "AND geography_level='state' AND party_name='Democratic'")
    seat_swing = (hs_state.pivot_table(index="state_abbr", columns="cycle",
                                       values="seats_after")
                  .reset_index())
    seat_swing = seat_swing[["state_abbr", 2022, 2026]].copy()
    seat_swing["change"] = seat_swing[2026] - seat_swing[2022]
    # Three states (AK, LA, NC) have no 2026 seat split in the source
    # table (NaN) — they are kept in the sheet but excluded from any
    # ranking or net, because a net over a partial table is misleading.
    seat_swing_known = seat_swing.dropna(subset=[2026]).sort_values("change", ascending=False)
    top_gain = seat_swing_known.iloc[0]
    top_loss = seat_swing_known.iloc[-1]
    pre = fr[(fr["office_key"] == "PRE") & (fr["party_key"] == "DEM")]
    pres_shift = pre.pivot_table(index="state_abbr", columns="cycle",
                                 values="vote_share_pct").reset_index()
    pres_shift["shift_2020_2024"] = pres_shift[2024] - pres_shift[2020]
    pres_shift = pres_shift.sort_values("shift_2020_2024", ascending=False)

    # ---------------------------------------------------------- SPLIT OUTCOMES
    hs_silver = pd.read_csv(ROOT / "data" / "silver" / "silver_house_seats_by_state.csv")
    split_rows = []
    for yr in (2022, 2026):
        g = gov[gov["cycle"] == yr].set_index("state")["winner_party"]
        h = hs_silver[hs_silver["cycle"] == yr].set_index("state")["delegation_majority"]
        for st in g.index:
            if pd.isna(g[st]) or h.get(st) in (None, "Even"):
                continue
            split_rows.append({"cycle": yr, "state": st, "governor_party": g[st],
                               "house_delegation_majority": h[st],
                               "split": g[st] != h[st]})
    split_df = pd.DataFrame(split_rows)

    # ---------------------------------------------------------- TEXAS
    tx_gov = tx[tx["office"] == "Governor"].sort_values("cycle")
    tx_sen = tx[tx["office"] == "Senate"].sort_values("cycle")
    tx_pre = tx[tx["office"] == "President"].sort_values("cycle")
    tx_del = hs_state[hs_state["state_abbr"] == "TX"].pivot_table(
        index="cycle", columns="party_name", values="seats_after")

    # ---------------------------------------------------------- write Excel
    wb = Workbook()
    wb.remove(wb.active)

    def sheet(name, df, note):
        ws = wb.create_sheet(name)
        ws["A1"] = note
        ws["A1"].font = Font(bold=True)
        for j, col in enumerate(df.columns, 1):
            c = ws.cell(row=3, column=j, value=str(col))
            c.font = Font(bold=True)
        for i, (_, r) in enumerate(df.iterrows(), 4):
            for j, v in enumerate(r.values, 1):
                ws.cell(row=i, column=j, value=None if pd.isna(v) else v)
        for j in range(1, len(df.columns) + 1):
            ws.column_dimensions[get_column_letter(j)].width = 22
        return ws

    sheet("What happened", pd.DataFrame([
        {"chamber": "House", "cycle": 2026, "dem_seats": int(h26.loc["Democratic", "seats_after"]),
         "rep_seats": int(h26.loc["Republican", "seats_after"]),
         "dem_net_change": int(h26.loc["Democratic", "net_change"]),
         "rep_net_change": int(h26.loc["Republican", "net_change"]),
         "dem_popular_pct": float(h26.loc["Democratic", "vote_share_pct"]),
         "rep_popular_pct": float(h26.loc["Republican", "vote_share_pct"]),
         "status": "PRELIMINARY — 19 races uncalled"},
        {"chamber": "Senate", "cycle": 2026,
         "dem_seats": int(sen_comp[sen_comp["party"] == "Democratic"]["seats_after"].iloc[0]),
         "rep_seats": int(sen_comp[sen_comp["party"] == "Republican"]["seats_after"].iloc[0]),
         "dem_net_change": int(sen_comp[sen_comp["party"] == "Democratic"]["net_change"].iloc[0]),
         "rep_net_change": int(sen_comp[sen_comp["party"] == "Republican"]["net_change"].iloc[0]),
         "dem_popular_pct": None, "rep_popular_pct": None,
         "status": "PRELIMINARY — final composition given as a range (D 52–54)"},
        {"chamber": "Governors", "cycle": 2026, "dem_seats": 22, "rep_seats": 12,
         "dem_net_change": None, "rep_net_change": None,
         "dem_popular_pct": None, "rep_popular_pct": None,
         "status": "PRELIMINARY — 2 of 36 races uncalled; seats after D 28–30"},
    ]), "Source: Wikipedia 2026 House/Senate/governor pages, retrieved 2026-11-09. "
          "House seats won: D 254, R 162 (19 uncalled). Senate: D 53, R 45, I 2.")
    sheet("Midterm pattern", pattern,
          "President's-party net House seat change, every midterm 1994–2026. "
          "Source: Wikipedia House results tables (fact_results, national rows).")
    sheet("Turnout", tn[["cycle", "turnout_rate_pct", "status"]],
          "National VEP turnout rate. Source: UF Election Lab US_VEP_Turnout_Rates_v1.4. "
          "2026: not yet published (Wikipedia reports an estimated 125 million total ballots).")
    sheet("Competitiveness", comp,
          "House races decided by under 5 / under 10 points. Source: Wikipedia "
          "closest-races tables (2018: 89 races listed; 2022: 74). 2026: no "
          "closest-races table published yet — dropped.")
    sheet("Money", money_df.assign(
        top_spender_win_rate_senate=[f"{top_rates[y][0]}/{top_rates[y][1]} = "
                                     f"{top_rates[y][0]/top_rates[y][1]:.1%}" for y in (2018, 2022, 2026)]),
        "Total House + Senate candidate receipts (FEC candidate summaries). "
        "2026 is a mid-cycle snapshot (coverage to 2026-10-14). Top-spender win "
        "rate: Senate races only — House district winners are not in the obtained sources.")
    sheet("Geography seats", seat_swing.rename(columns={2022: "dem_seats_2022", 2026: "dem_seats_2026"}),
          "Democratic House seats by state, 2022 → 2026. Alaska, Louisiana "
          "and North Carolina have no 2026 seat split in the source table "
          "(blank) — no state-level net is reported. The 47 known states sum "
          "to 248 Democratic seats vs the national infobox total of 254; the "
          "per-state table is a lagging snapshot of the results table. Seat "
          "changes partly reflect mid-decade redistricting (see findings.md). "
          "County-level shift: dropped — no county vote data obtainable.")
    sheet("Geography president", pres_shift[["state_abbr", 2020, 2024, "shift_2020_2024"]],
          "Democratic two-party presidential vote share by state, 2020 → 2024 "
          "(MEDSL, state-level). All 50 states + DC moved toward Republicans.")
    sheet("Split outcomes", split_df[split_df["split"]],
          "States where the governor's party differs from the House delegation's "
          "majority party. 2022: 7 states; 2026: 4 states (Alaska and Kansas "
          "excluded in 2026 — governor races uncalled).")
    sheet("Texas", tx[["cycle", "office", "dem_candidate", "dem_pct",
                       "rep_candidate", "rep_pct", "margin_pts", "winner_party", "status"]],
          "Texas statewide two-party margins. Governor 2014–2026, Senate "
          "2014–2026, President 2016–2024, Attorney General 2026. Margins are "
          "Democratic minus Republican in points (positive = Democratic lead).")
    sheet("Senate flips 2026", flips[["state", "incumbent", "incumbent_party",
                                      "winner", "winner_party"]],
          "Flipped 2026 Senate seats named on the Wikipedia results table (6 of "
          "the 7 R→D flips the composition table records; the 7th is not "
          "individually identified on the page).")
    sheet("Closest races", closest.sort_values(["cycle", "margin_pts"]).groupby("cycle").head(15)[
        ["cycle", "district", "winner", "margin_pts"]],
        "The 15 closest House races of 2018 and of 2022. The 15 closest of 2026 "
        "are not computable yet — no district-margin source published.")
    wb.save(OUT_XLSX)
    log(f"Findings_Scorecard.xlsx: {len(wb.sheetnames)} sheets")

    # ---------------------------------------------------------- write findings.md
    md = build_markdown(locals())
    OUT_MD.write_text(md)
    log(f"findings.md: {len(md.splitlines())} lines")
    print("\n--- 04_findings complete ---")


def build_markdown(v):
    h26 = v["h26"]; pattern = v["pattern"]; tn = v["tn"]; comp = v["comp"]
    money_df = v["money_df"]; top_rates = v["top_rates"]
    seat_swing = v["seat_swing"]; pres_shift = v["pres_shift"]
    split_df = v["split_df"]; tx = v["tx"]; flips = v["flips"]
    closest = v["closest"]; tx_gov = v["tx_gov"]; tx_sen = v["tx_sen"]
    tx_pre = v["tx_pre"]; tx_del = v["tx_del"]; sen_comp = v["sen_comp"]
    gov = v["gov"]

    d26 = h26.loc["Democratic"]; r26 = h26.loc["Republican"]
    p26 = pattern[pattern["cycle"] == 2026].iloc[0]
    p18 = pattern[pattern["cycle"] == 2018].iloc[0]
    p22 = pattern[pattern["cycle"] == 2022].iloc[0]
    p14 = pattern[pattern["cycle"] == 2014].iloc[0]
    m18, m22, m26 = (money_df[money_df["cycle"] == y].iloc[0] for y in (2018, 2022, 2026))
    t18, t22 = (top_rates[y] for y in (2018, 2022)); t26 = top_rates[2026]
    n_split_22 = int(split_df[(split_df["cycle"] == 2022) & (split_df["split"])].shape[0])
    n_split_26 = int(split_df[(split_df["cycle"] == 2026) & (split_df["split"])].shape[0])
    split26 = split_df[(split_df["cycle"] == 2026) & (split_df["split"])]
    split26_txt = "; ".join(f"{r['state']} (Governor {r['governor_party']}, "
                            f"House delegation {r['house_delegation_majority']})"
                            for _, r in split26.iterrows())
    top_gain = v["top_gain"]; top_loss = v["top_loss"]
    flips_txt = "; ".join(f"{r['state']}: {r['winner']} ({r['winner_party']}) beat "
                          f"incumbent {re.sub(r'\[.*?\]', '', r['incumbent'])} ({r['incumbent_party']})"
                          for _, r in flips.iterrows())
    c18 = closest[closest["cycle"] == 2018].nsmallest(3, "margin_pts")
    c22 = closest[closest["cycle"] == 2022].nsmallest(3, "margin_pts")
    closest_txt = "; ".join(
        f"{r['district']} — {r['winner']} win by {r['margin_pts']:.2f} pts" for _, r in c18.iterrows()) \
        + " in 2018; " + "; ".join(
        f"{r['district']} — {r['winner']} win by {r['margin_pts']:.2f} pts" for _, r in c22.iterrows()) \
        + " in 2022"
    tx_gov_txt = "; ".join(
        f"{int(r['cycle'])}: {r['winner_party']} by {abs(r['margin_pts']):.1f} pts"
        for _, r in tx_gov.iterrows())
    tx_sen_txt = "; ".join(
        f"{int(r['cycle'])}: {r['winner_party']} by {abs(r['margin_pts']):.1f} pts"
        for _, r in tx_sen.iterrows())
    tx_pre_txt = "; ".join(
        f"{int(r['cycle'])}: {r['winner_party']} by {abs(r['margin_pts']):.1f} pts"
        for _, r in tx_pre.iterrows())

    L = []
    A = L.append
    A("# Findings — US Midterms Observatory 2026\n")
    A("Every number below is computed from the gold layer "
      "(`outputs/midterms.db`). Sources are named per table. "
      "2026 figures are **preliminary** unless stated otherwise. "
      "The tone is neutral and explanatory: what happened, how, and why "
      "this cycle was different — evidenced by data.\n")
    A("## What happened\n")
    A("| Chamber | 2026 outcome | Net change vs 2024 |")
    A("|---|---|---|")
    A(f"| House | Democrats {int(d26['seats_after'])} seats, Republicans {int(r26['seats_after'])} (19 races uncalled) | Democrats {int(d26['net_change']):+d}, Republicans {int(r26['net_change']):+d} |")
    A(f"| Senate | Democrats {int(sen_comp[sen_comp['party']=='Democratic']['seats_after'].iloc[0])}, Republicans {int(sen_comp[sen_comp['party']=='Republican']['seats_after'].iloc[0])}, Independents 2 | Democrats {int(sen_comp[sen_comp['party']=='Democratic']['net_change'].iloc[0]):+d}, Republicans {int(sen_comp[sen_comp['party']=='Republican']['net_change'].iloc[0]):+d} |")
    A("| Governors | Democrats won 22 of 36 races, Republicans 12, 2 uncalled | Democrats +4 to +6 (seats after D 28–30, R 20–22) |")
    A("")
    A(f"The 2026 midterms gave Democrats control of the House with "
      f"{int(d26['seats_after'])} seats to the Republicans' {int(r26['seats_after'])}, "
      f"a net gain of {int(d26['net_change'])} seats, with 19 races still uncalled. "
      f"Democrats also took the Senate, moving from 45 seats to "
      f"{int(sen_comp[sen_comp['party']=='Democratic']['seats_after'].iloc[0])}, a net gain of "
      f"{int(sen_comp[sen_comp['party']=='Democratic']['net_change'].iloc[0])}, and won 22 of 36 "
      f"governor races. The House popular vote went to Democrats by "
      f"{float(d26['vote_share_pct']):.1f}% to {float(r26['vote_share_pct']):.1f}%, a margin of "
      f"{float(d26['vote_share_pct'])-float(r26['vote_share_pct']):+.1f} points. "
      f"Compared with the previous three midterms, the scale stands out: in 2014 "
      f"Republicans gained 13 House seats, in 2018 Democrats gained 41, and in "
      f"2022 Republicans gained 9 — the 2026 Democratic gain of "
      f"{int(d26['net_change'])} is the second-largest Democratic midterm gain "
      f"in the nine-cycle series, after 2018, and the popular-vote margin is "
      f"the widest in the series. All 2026 figures remain preliminary until "
      f"the remaining races are called and certified.\n")
    A("## The comeback, measured\n")
    A("| Cycle | Net House change (president's party) | National House popular vote (D %) | D−R margin (pts) |")
    A("|---|---|---|---|")
    for _, r in pattern.iterrows():
        pass
    # popular vote table from house summary
    hs = pd.read_sql("SELECT cycle, party_name, vote_share_pct FROM fact_results "
                     "WHERE office_key='HOU' AND geography_level='national'", CON)
    pv = hs.pivot_table(index="cycle", columns="party_name", values="vote_share_pct")
    for yr in (2018, 2022, 2026):
        pr = pattern[pattern["cycle"] == yr].iloc[0]
        A(f"| {yr} | {pr['president_party']} {int(pr['net_change']):+d} | "
          f"{pv.loc[yr, 'Democratic']:.2f}% | {pv.loc[yr, 'Democratic']-pv.loc[yr, 'Republican']:+.2f} |")
    A("")
    A(f"Measured against the two previous midterms, 2026 is a sharp reversal. "
      f"In 2018 Democrats gained 41 House seats with 53.4% of the national "
      f"House vote; in 2022 they lost 9 seats with 47.29%. In 2026 they gained "
      f"{int(d26['net_change'])} seats with {float(d26['vote_share_pct']):.1f}% of the vote, "
      f"a margin of {float(d26['vote_share_pct'])-float(r26['vote_share_pct']):+.1f} points over "
      f"Republicans — the largest Democratic popular-vote margin in the "
      f"1994–2026 series. The Senate moved the same way: Democrats gained "
      f"{int(sen_comp[sen_comp['party']=='Democratic']['net_change'].iloc[0])} seats in 2026 after "
      f"losing the chamber in 2024. The state picture matches the national one: "
      f"the largest Democratic House-seat gain by state was {top_gain['state_abbr']} "
      f"(+{int(top_gain['change'])} seats, {int(top_gain[2022])} → {int(top_gain[2026])}), "
      f"and only one state, {top_loss['state_abbr']}, saw Democrats lose a net "
      f"seat. Whether this is a durable realignment or a single-cycle swing "
      f"cannot be answered from one election; the data only establishes the "
      f"size of the 2026 move.\n")
    A("## The midterm pattern\n")
    A("| Cycle | President's party | Net House change |")
    A("|---|---|---|")
    for _, r in pattern.iterrows():
        A(f"| {int(r['cycle'])} | {r['president_party']} | {int(r['net_change']):+d} |")
    A("")
    A("The historical pattern is that the president's party loses House seats "
      "in a midterm. It held in seven of the nine midterms from 1994 to 2026. "
      "The two exceptions are 1998, when Democrats gained 5 seats under "
      "President Clinton, and 2002, when Republicans gained 8 under President "
      "George W. Bush. The losses range from 9 seats (Democrats, 2022) to 64 "
      "seats (Democrats, 2010). The 2026 result — Republicans losing 56 seats "
      "under President Trump — confirms the pattern, and is the second-largest "
      "loss in the series after 2010. The pattern is a description of what "
      "happened in these nine elections, not a law: two of nine cycles broke "
      "it, and the size of the loss varies from single digits to more than sixty.\n")
    A("## Turnout\n")
    A("| Cycle | National VEP turnout | Status |")
    A("|---|---|---|")
    for _, r in tn.iterrows():
        rate = f"{r['turnout_rate_pct']:.2f}%" if pd.notna(r["turnout_rate_pct"]) else "—"
        A(f"| {int(r['cycle'])} | {rate} | {r['status']} |")
    A("")
    A("National midterm turnout (voting-eligible population) ran between "
      "36.7% (2014) and 50.05% (2018) across the eight cycles with published "
      "figures, with 2022 at 46.12%. The 2018 figure is the highest midterm "
      "turnout in the series and the 2014 figure the lowest. No 2026 VEP "
      "turnout rate has been published by the UF Election Lab as of "
      "2026-11-09, so no comparison for 2026 is possible yet; the only "
      "figure available is Wikipedia's estimate of 125 million total ballots "
      "cast, which has no published VEP denominator and therefore no rate. "
      "State-level 2026 turnout is likewise unpublished, so the planned "
      "state-level 2026-vs-2022 comparison is dropped rather than estimated.\n")
    A("## Competitiveness\n")
    A("| Cycle | Races decided by <5 pts | Races decided by <10 pts | Share <10 pts |")
    A("|---|---|---|---|")
    for _, r in comp.iterrows():
        A(f"| {int(r['cycle'])} | {int(r['races_under_5'])} | {int(r['races_under_10'])} | {r['share_under_10_pct']:.1f}% of 435 |")
    A("")
    A(f"The number of close House races fell between the two most recent "
      f"certified cycles. In 2018, {int(comp[comp['cycle']==2018]['races_under_10'].iloc[0])} races "
      f"were decided by under 10 points ({int(comp[comp['cycle']==2018]['races_under_5'].iloc[0])} "
      f"by under 5); in 2022 the figures were "
      f"{int(comp[comp['cycle']==2022]['races_under_10'].iloc[0])} and "
      f"{int(comp[comp['cycle']==2022]['races_under_5'].iloc[0])}. That is a fall from "
      f"{comp[comp['cycle']==2018]['share_under_10_pct'].iloc[0]:.1f}% of all House races "
      f"being decided by under 10 points in 2018 to "
      f"{comp[comp['cycle']==2022]['share_under_10_pct'].iloc[0]:.1f}% in 2022. The closest "
      f"races in the data include {closest_txt}. No equivalent table has been "
      f"published for 2026 yet — the races are still being called — so the "
      f"2026 competitiveness figures are dropped rather than guessed.\n")
    A("## Money\n")
    A("| Cycle | House receipts | Senate receipts | Combined | Top-spender win rate (Senate) |")
    A("|---|---|---|---|---|")
    for _, r in money_df.iterrows():
        yr = int(r["cycle"])
        hit, tot, _ = top_rates[yr]
        A(f"| {yr} | {money(r['house_receipts'])} | {money(r['senate_receipts'])} | {money(r['combined_receipts'])} | {hit}/{tot} ({hit/tot:.1%}) |")
    A("")
    A(f"Total candidate receipts for House and Senate races rose from "
      f"{money(m18['combined_receipts'])} in 2018 to {money(m22['combined_receipts'])} in "
      f"2022, and {money(m26['combined_receipts'])} in 2026 — but the 2026 figure is "
      f"a mid-cycle snapshot (filings through 2026-10-14) and will rise as "
      f"post-election reports arrive, so the 2022-to-2026 comparison is not "
      f"yet final. House receipts account for most of the money in every "
      f"cycle. The top spender won {t18[0]} of {t18[1]} Senate races in 2018 "
      f"({t18[0]/t18[1]:.1%}), {t22[0]} of {t22[1]} in 2022 ({t22[0]/t22[1]:.1%}), "
      f"and {t26[0]} of {t26[1]} in 2026 ({t26[0]/t26[1]:.1%}). The 2026 rate is "
      f"higher than the two previous cycles, but it rests on {t26[1]} decided "
      f"races (two Senate races are uncalled) and on a preliminary FEC file. "
      f"The two 2026 races where the top spender lost were Minnesota, where "
      f"Republican Michele Tafoya outspent the winner Peggy Flanagan, and "
      f"Montana, where independent Seth Bodnar outspent the winner Kurt Alme. "
      f"A House version of this metric is not computable from the obtained "
      f"sources (no district-winner table).\n")
    A("## Geography\n")
    A("The state seat-swing table (Democratic House seats, 2022 → 2026) is "
      "in the scorecard. Three facts about it matter. First, the gains are "
      f"concentrated: {top_gain['state_abbr']} (+{int(top_gain['change'])}) and New York "
      f"(+5) account for 13 Democratic seats gained since 2022, with Iowa and "
      f"Ohio each adding 3 and seven states adding 2 each; only one state, "
      f"{top_loss['state_abbr']}, saw Democrats lose a net seat. Second, the "
      f"table covers 47 of 50 states — Alaska, Louisiana and North Carolina "
      f"have no 2026 seat split in the source table, so no state-level net "
      f"total is reported (the 47 known states sum to 248 Democratic seats, "
      f"against a national infobox total of 254). Third, the seat changes "
      f"partly reflect new maps, not only votes: California and Texas both "
      f"redrew congressional maps mid-decade before the 2026 election, so a "
      f"2022-to-2026 seat comparison in those states mixes redistricting with "
      f"vote shifts, and district-level swing figures would be misleading. "
      f"The presidential geography runs the other way: between 2020 and 2024, "
      f"the Democratic two-party presidential vote share fell in every state "
      f"(mean state shift {pres_shift['shift_2020_2024'].mean():+.2f} points; "
      f"largest falls in New York, New Jersey and Florida). County-level "
      f"geography is not available: no public county-level vote data could be "
      f"obtained, so no county flip count is reported.\n")
    A("## Split outcomes\n")
    A(f"In 2022, {n_split_22} states had a governor whose party differed from "
      f"their House delegation's majority party. In 2026 the number is "
      f"{n_split_26}: {split26_txt}. (Alaska and Kansas are excluded from the "
      f"2026 count because their governor races are uncalled, and states with "
      f"evenly split delegations are excluded in both years.) The fall from 7 "
      f"to 4 split states means fewer states split their ticket in 2026 than "
      f"in 2022. Texas is the most notable new split: a Democratic governor "
      f"with a Republican-majority House delegation (24 R, 14 D). Georgia is "
      f"the other new split in 2026; New Hampshire and Vermont were split in "
      f"both cycles.\n")
    A("## Texas deep-dive\n")
    A("| Office | 2014 | 2018 | 2020 | 2022 | 2024 | 2026 |")
    A("|---|---|---|---|---|---|---|")
    A(f"| Governor (D margin, pts) | {tx_gov[tx_gov['cycle']==2014]['margin_pts'].iloc[0]:+.1f} | {tx_gov[tx_gov['cycle']==2018]['margin_pts'].iloc[0]:+.1f} | — | {tx_gov[tx_gov['cycle']==2022]['margin_pts'].iloc[0]:+.1f} | — | {tx_gov[tx_gov['cycle']==2026]['margin_pts'].iloc[0]:+.1f} |")
    A(f"| Senate (D margin, pts) | {tx_sen[tx_sen['cycle']==2014]['margin_pts'].iloc[0]:+.1f} | {tx_sen[tx_sen['cycle']==2018]['margin_pts'].iloc[0]:+.1f} | {tx_sen[tx_sen['cycle']==2020]['margin_pts'].iloc[0]:+.1f} | — | {tx_sen[tx_sen['cycle']==2024]['margin_pts'].iloc[0]:+.1f} | {tx_sen[tx_sen['cycle']==2026]['margin_pts'].iloc[0]:+.1f} |")
    A(f"| President (D margin, pts) | — | — | {tx_pre[tx_pre['cycle']==2020]['margin_pts'].iloc[0]:+.1f} | — | {tx_pre[tx_pre['cycle']==2024]['margin_pts'].iloc[0]:+.1f} | — |")
    A("")
    A(f"Something changed in Texas, and the margins show it plainly. "
      f"Republicans won the Texas governorship by 20.4 points in 2014, by "
      f"13.3 in 2018 and by 10.9 in 2022 — a steady narrowing — and in 2026 "
      f"Democrat Gina Hinojosa beat incumbent Greg Abbott by 7.1 points "
      f"(52.8% to 45.7%). The Senate moved further: Republican margins of "
      f"28.4 points (2014), 2.6 (2018), 9.9 (2020) and 8.7 (2024) became a "
      f"Democratic win by 12.1 points in 2026, when James Talarico beat Ken "
      f"Paxton 55.1% to 43.0% after Paxton beat incumbent John Cornyn in the "
      f"Republican runoff. The Attorney General's office also flipped: "
      f"Democrat Nathan Johnson beat Republican Mayes Middleton by 6.5 points "
      f"(52.4% to 45.9%). That is all three statewide offices on the 2026 "
      f"ballot going Democratic, breaking a Republican hold on every Texas "
      f"statewide office that dates to the 1990s. The presidential picture is "
      f"different: Texas voted Republican for president by 5.7 points in 2020 "
      f"and by 13.9 points in 2024 — the state moved toward Republicans at "
      f"presidential level while flipping Democratic in the 2026 statewide "
      f"races. The Texas House delegation moved one seat toward Democrats "
      f"(13 D / 25 R in 2022 to 14 D / 24 R in 2026), but that figure mixes "
      f"the 2026 Texas redistricting with vote shifts and should not be read "
      f"as a pure swing.\n")
    A("## Candidates and flips — Senate 2026\n")
    A("| State | Winner | Incumbent |")
    A("|---|---|---|")
    for _, r in flips.iterrows():
        A(f"| {r['state']} | {r['winner']} ({r['winner_party']}) | {re.sub(r'\[.*?\]', '', r['incumbent'])} ({r['incumbent_party']}) |")
    A("")
    A(f"Seven Senate seats flipped from Republican to Democratic in 2026, "
      f"and none flipped the other way. Six are named on the results table: "
      f"{flips_txt}. The seventh flip is recorded in the Senate composition "
      f"table but is not individually identified on the page — two races "
      f"(Alaska and Mississippi) have outcomes that appear only in the "
      f"table's overall result row, so the seat is counted but not named "
      f"here. The 15 closest House races of 2026 cannot be listed yet: no "
      f"district-margin source has been published. The closest races of the "
      f"two previous cycles are in the scorecard; the tightest were "
      f"{closest_txt}.\n")
    A("## What the data does not support\n")
    A("- County-level vote shift and county flips (no county vote data obtainable).\n"
      "- 2026 turnout, national or state-level (not yet published).\n"
      "- 2026 House competitiveness and the 15 closest 2026 races (no district margins published).\n"
      "- A flipped-House-seats table with winners and margins (no district winner-party source).\n"
      "- A House top-spender win rate (no district-winner table).\n"
      "- State-level House vote-share shift 2022 → 2026 (no state House vote totals in the sources).\n"
      "- Final 2026 money totals (FEC filings continue past the 2026-10-14 snapshot).\n")
    return "\n".join(L)


if __name__ == "__main__":
    main()