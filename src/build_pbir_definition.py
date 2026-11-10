import os
import json
import uuid

REPO_DIR = r"C:\Users\shams\us-midterms-2026-observatory"
REPORT_DIR = os.path.join(REPO_DIR, "MidtermsObservatory.Report")
DEF_DIR = os.path.join(REPORT_DIR, "definition")
PAGES_DIR = os.path.join(DEF_DIR, "pages")

def make_uuid(seed):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"midterms.observatory.{seed}"))

# Page metadata definitions
PAGES = [
    {
        "id": "page1_the_night",
        "displayName": "The Night",
        "order": 1,
        "isDrillthrough": False
    },
    {
        "id": "page2_the_comeback_measured",
        "displayName": "The Comeback, Measured",
        "order": 2,
        "isDrillthrough": False
    },
    {
        "id": "page3_texas_deep_dive",
        "displayName": "Texas Deep-Dive",
        "order": 3,
        "isDrillthrough": False
    },
    {
        "id": "page4_why_this_one_was_different",
        "displayName": "Why This One Was Different",
        "order": 4,
        "isDrillthrough": False
    },
    {
        "id": "page5_the_midterm_pattern",
        "displayName": "The Midterm Pattern",
        "order": 5,
        "isDrillthrough": False
    },
    {
        "id": "page6_what_changes_now",
        "displayName": "What Changes Now",
        "order": 6,
        "isDrillthrough": False
    },
    {
        "id": "page7_state_detail",
        "displayName": "State Detail",
        "order": 7,
        "isDrillthrough": True
    }
]

def make_textbox(name, text, x, y, w, h, font_size="13pt", is_bold=False, bg_color=None):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 1000,
            "width": w,
            "height": h,
            "tabOrder": 1000
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": text,
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold" if is_bold else "Segoe UI",
                                                "fontSize": font_size,
                                                "color": "#2F3337"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

def make_card(name, measure_name, title, x, y, w, h, subtitle=None):
    v = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 2000,
            "width": w,
            "height": h,
            "tabOrder": 2000
        },
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "entity": "fact_results"
                                            }
                                        },
                                        "property": measure_name
                                    }
                                },
                                "queryRef": f"Measure.{measure_name}"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {
                                "expr": {
                                    "Literal": {
                                        "Value": f"'{title}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }
    return v

def make_static_card(name, display_value, title, x, y, w, h, subtitle=None):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 2000,
            "width": w,
            "height": h,
            "tabOrder": 2000
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": f"{title}\n",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "10pt",
                                                "color": "#605E5C"
                                            }
                                        },
                                        {
                                            "value": f"{display_value}\n",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold",
                                                "fontSize": "22pt",
                                                "color": "#0C2340"
                                            }
                                        },
                                        {
                                            "value": subtitle if subtitle else "",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "9pt",
                                                "color": "#8A8886"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }

def make_chart(name, vtype, entity, cat_col, measure_cols, title, x, y, w, h):
    projections_val = []
    for m in measure_cols:
        projections_val.append({
            "field": {
                "Measure": {
                    "Expression": {
                        "SourceRef": {
                            "entity": entity
                        }
                    },
                    "property": m
                }
            },
            "queryRef": f"{entity}.{m}"
        })
    
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 3000,
            "width": w,
            "height": h,
            "tabOrder": 3000
        },
        "visual": {
            "visualType": vtype,
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {
                                            "SourceRef": {
                                                "entity": entity
                                            }
                                        },
                                        "property": cat_col
                                    }
                                },
                                "queryRef": f"{entity}.{cat_col}"
                            }
                        ]
                    },
                    "Y": {
                        "projections": projections_val
                    }
                }
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {
                                "expr": {
                                    "Literal": {
                                        "Value": f"'{title}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

def make_table(name, entity, cols, measures_list, title, x, y, w, h):
    projections = []
    for c in cols:
        projections.append({
            "field": {
                "Column": {
                    "Expression": {
                        "SourceRef": {
                            "entity": entity
                        }
                    },
                    "property": c
                }
            },
            "queryRef": f"{entity}.{c}"
        })
    for m in measures_list:
        projections.append({
            "field": {
                "Measure": {
                    "Expression": {
                        "SourceRef": {
                            "entity": entity
                        }
                    },
                    "property": m
                }
            },
            "queryRef": f"{entity}.{m}"
        })

    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": 4000,
            "width": w,
            "height": h,
            "tabOrder": 4000
        },
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": projections
                    }
                }
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {
                                "expr": {
                                    "Literal": {
                                        "Value": f"'{title}'"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

# -------------------------------------------------------------------------
# Build Pages and Visuals
# -------------------------------------------------------------------------

pages_dict = {}

# PAGE 1: The Night
p1_visuals = [
    make_textbox("p1_headline", "Democrats took the House, the Senate and 22 governor races in 2026 \u2014 with 19 House races still uncalled.", 20, 15, 1240, 45, "15pt", True),
    make_textbox("p1_how_to_read", "Card numbers labeled (preliminary) reflect counts as of election night. Uncalled races remain in recount or canvass.", 20, 65, 1240, 30, "10pt"),
    make_card("p1_kpi_house_d", "House Seats D 2026", "House Seats (D)", 20, 110, 140, 110, "(preliminary)"),
    make_card("p1_kpi_house_r", "House Seats R 2026", "House Seats (R)", 175, 110, 140, 110, "(preliminary)"),
    make_card("p1_kpi_house_uncalled", "House Seats Uncalled 2026", "Uncalled Races", 330, 110, 140, 110),
    make_card("p1_kpi_senate_d", "Senate Seats D 2026", "Senate Seats (D+I)", 485, 110, 140, 110, "(preliminary)"),
    make_card("p1_kpi_senate_r", "Senate Seats R 2026", "Senate Seats (R)", 640, 110, 140, 110),
    make_card("p1_kpi_gov_d", "Gov Wins D 2026", "Governor Races Won (D)", 795, 110, 140, 110),
    make_card("p1_kpi_net_d", "House Net Change D 2026", "Net House Change (D)", 950, 110, 140, 110),
    make_card("p1_kpi_pop_margin", "House Popular Vote Margin 2026", "Popular Vote Margin", 1105, 110, 155, 110, "(D +13.1 pts)"),
    make_chart("p1_chart_house_balance", "columnChart", "dim_cycle", "cycle", ["House Seats D 2026", "House Seats R 2026"], "House Seat Balance (2026)", 20, 240, 600, 450),
    make_table("p1_table_senate_flips", "fact_senate_flips_2026", ["state", "incumbent", "winner", "result_text"], [], "Key Senate Flips (2026)", 640, 240, 620, 450)
]
pages_dict["page1_the_night"] = p1_visuals

# PAGE 2: The Comeback, Measured
p2_visuals = [
    make_textbox("p2_headline", "A 40-seat House swing and 8-seat Senate gain reversed the 2024 red wave across 47 states.", 20, 15, 1240, 45, "15pt", True),
    make_textbox("p2_how_to_read", "AK, LA, NC have no 2026 split in source data and appear blank on the map.", 20, 65, 1240, 30, "10pt"),
    make_card("p2_kpi_net_d", "House Net Change D 2026", "House Net Change D (2026)", 20, 110, 290, 95),
    make_card("p2_kpi_seat_change", "Dem Seats Change 2022 to 2026", "Dem Seat Change (2022 vs 2026)", 335, 110, 290, 95),
    make_card("p2_kpi_pop_margin", "House Popular Vote Margin 2026", "House Popular Vote Margin (2026)", 650, 110, 290, 95),
    make_card("p2_kpi_senate_net", "Senate Net Change D 2026", "Senate Net Change D (2026)", 965, 110, 295, 95),
    make_chart("p2_chart_house_trend", "columnChart", "dim_cycle", "cycle", ["House Seats D", "House Seats R"], "House Seats by Party (2018\u20132026)", 20, 220, 600, 230),
    make_chart("p2_chart_vote_share", "lineChart", "dim_cycle", "cycle", ["Dem House Vote Share", "Rep House Vote Share"], "National House Vote Share % (2018\u20132026)", 640, 220, 620, 230),
    make_chart("p2_chart_margin_trend", "lineChart", "dim_cycle", "cycle", ["House Vote Margin D minus R"], "House Popular Vote Margin Trend (2018\u20132026)", 20, 465, 600, 235),
    make_table("p2_table_state_swings", "dim_geography", ["state_name", "region"], ["Dem Seats Change 2022 to 2026"], "State House Seat Changes (47 States)", 640, 465, 620, 235)
]
pages_dict["page2_the_comeback_measured"] = p2_visuals

# PAGE 3: Texas Deep-Dive
p3_visuals = [
    make_textbox("p3_headline", "Democrats swept Texas statewide races (Gov +7.1, Sen +12.1, AG +6.5) and gained 14 House seats.", 20, 15, 1240, 45, "15pt", True),
    make_textbox("p3_how_to_read", "Margins reflect statewide general election certified totals, with 2026 preliminary.", 20, 65, 1240, 30, "10pt"),
    make_card("p3_kpi_gov_margin", "Texas Dem Margin", "Texas Gov Dem Margin", 20, 110, 235, 95),
    make_card("p3_kpi_sen_margin", "Texas Dem Margin", "Texas Senate Dem Margin", 270, 110, 235, 95),
    make_card("p3_kpi_ag_margin", "Texas Dem Margin", "Texas AG Dem Margin", 520, 110, 235, 95),
    make_card("p3_kpi_tx_house_d", "Texas House Dem Seats", "Texas House Dem Seats", 770, 110, 235, 95),
    make_card("p3_kpi_tx_net_gain", "Texas House Dem Seats", "Texas House Net Dem Gain", 1020, 110, 240, 95),
    make_chart("p3_chart_tx_margins", "barChart", "fact_texas_statewide", "office", ["Texas Dem Margin"], "Texas Statewide Margins (2026)", 20, 220, 600, 230),
    make_chart("p3_chart_tx_shares", "columnChart", "fact_texas_statewide", "office", ["Texas Dem Pct", "Texas Rep Pct"], "Texas Democratic vs Republican Vote Share (2026)", 640, 220, 620, 230),
    make_chart("p3_chart_tx_house_trend", "columnChart", "dim_cycle", "cycle", ["Texas House Dem Seats", "Texas House Rep Seats"], "Texas US House Delegation by Party (2018\u20132026)", 20, 465, 600, 235),
    make_table("p3_table_tx_candidates", "fact_texas_statewide", ["office", "dem_candidate", "rep_candidate"], ["Texas Dem Margin"], "Texas Statewide Election Summary", 640, 465, 620, 235)
]
pages_dict["page3_texas_deep_dive"] = p3_visuals

# PAGE 4: Why This One Was Different
p4_visuals = [
    make_textbox("p4_headline", "Record campaign receipts ($4.24B) met high midterm turnout and narrowed margins in 74 competitive House races.", 20, 15, 1240, 45, "15pt", True),
    make_textbox("p4_how_to_read", "Turnout data ends at 2022; official 2026 VEPM turnout is not yet published.", 20, 65, 1240, 30, "10pt"),
    make_card("p4_kpi_total_receipts", "Total Receipts", "Total Receipts (2026)", 20, 110, 235, 95),
    make_static_card("p4_kpi_top_spender", "87.4%", "Top-Spender Win Rate", 270, 110, 235, 95, "(findings.md)"),
    make_card("p4_kpi_under_5", "Races Under 5 Pts", "Races Under 5 Pts", 520, 110, 235, 95),
    make_card("p4_kpi_under_10", "Races Under 10 Pts", "Races Under 10 Pts", 770, 110, 235, 95),
    make_static_card("p4_kpi_turnout_2026", "not yet published", "Turnout Rate 2026", 1020, 110, 240, 95, "(VEPM pending)"),
    make_chart("p4_chart_receipts_trend", "columnChart", "dim_cycle", "cycle", ["Total Receipts"], "Total Campaign Receipts by Cycle (2018\u20132026)", 20, 220, 600, 230),
    make_chart("p4_chart_receipts_chamber", "columnChart", "dim_cycle", "cycle", ["House Receipts", "Senate Receipts"], "Receipts by Chamber (House vs Senate)", 640, 220, 620, 230),
    make_chart("p4_chart_turnout_trend", "lineChart", "fact_turnout", "cycle", ["Turnout Rate"], "VEPM Midterm Turnout Rate (2018\u20132022)", 20, 465, 600, 235),
    make_table("p4_table_closest_races", "fact_house_closest_races", ["district", "winner", "margin_band"], [], "Closest House Races (2026)", 640, 465, 620, 235)
]
pages_dict["page4_why_this_one_was_different"] = p4_visuals

# PAGE 5: The Midterm Pattern
p5_visuals = [
    make_textbox("p5_headline", "Midterms reliably penalize the president's party (-56 seats in 2026, the steepest penalty since 2010).", 20, 15, 1240, 45, "15pt", True),
    make_textbox("p5_how_to_read", "Negative values indicate seat losses for the party holding the White House.", 20, 65, 1240, 30, "10pt"),
    make_card("p5_kpi_pres_net", "Presidents Party Net Change", "Presidents Party Net Loss 2026", 20, 110, 395, 95),
    make_static_card("p5_kpi_worst_since", "2010", "Steepest Loss Since", 435, 110, 395, 95, "(-63 seats in 2010)"),
    make_static_card("p5_kpi_hist_avg", "-28 seats", "Historical Average Loss", 850, 110, 410, 95, "(1974\u20132022 midterms)"),
    make_chart("p5_chart_pres_loss", "columnChart", "dim_cycle", "cycle", ["Presidents Party Net Change"], "President's Party Net Seat Change Across Midterms (1974\u20132026)", 20, 220, 750, 480),
    make_table("p5_table_presidents", "dim_cycle", ["cycle", "president", "president_party"], ["Presidents Party Net Change"], "Midterm Summary Table", 790, 220, 470, 480)
]
pages_dict["page5_the_midterm_pattern"] = p5_visuals

# PAGE 6: What Changes Now
p6_visuals = [
    make_textbox("p6_headline", "Divided government returns as Democrats gain trifecta-breaking control of both congressional chambers.", 20, 15, 1240, 45, "15pt", True),
    make_textbox("p6_how_to_read", "Trifecta is broken when the presidency and both chambers of Congress are not held by the same party.", 20, 65, 1240, 30, "10pt"),
    make_card("p6_kpi_house_maj", "House Majority 2026", "House Majority (2026)", 20, 110, 195, 95),
    make_card("p6_kpi_senate_maj", "Senate Majority 2026", "Senate Majority (2026)", 230, 110, 195, 95),
    make_card("p6_kpi_trifecta", "Trifecta 2026", "Trifecta Status (2026)", 440, 110, 195, 95),
    make_card("p6_kpi_sen_flips", "Senate Flips 2026", "Senate Flips (2026)", 650, 110, 195, 95),
    make_static_card("p6_kpi_split_outcomes", "4 states", "Split-Outcome States", 860, 110, 195, 95, "(Gov vs Senate split)"),
    make_static_card("p6_kpi_gov_net", "+3 net D", "Net Governor Change", 1070, 110, 190, 95, "(22 D won)"),
    make_chart("p6_chart_senate_comp", "columnChart", "fact_senate_composition", "party_name", ["Senate Seats D 2026", "Senate Seats R 2026"], "Senate Composition (119th Congress)", 20, 220, 600, 230),
    make_chart("p6_chart_gov_wins", "columnChart", "dim_party", "party_name", ["Gov Wins D 2026", "Gov Wins R 2026"], "Governors Won by Party (2026)", 640, 220, 620, 230),
    make_table("p6_table_flips", "fact_senate_flips_2026", ["state", "incumbent", "winner", "result_text"], [], "All 6 Senate Seat Flips (2026)", 20, 465, 1240, 235)
]
pages_dict["page6_what_changes_now"] = p6_visuals

# PAGE 7: State Detail (Drill-through)
p7_visuals = [
    make_textbox("p7_title", "State Detail Drill-Through", 20, 15, 600, 40, "16pt", True),
    make_card("p7_kpi_state_name", "State Name", "Selected State", 640, 15, 620, 80),
    make_textbox("p7_how_to_read", "Drill-through target page filtered by selected state from Page 2 map or table.", 20, 60, 600, 35, "10pt"),
    make_card("p7_kpi_state_dem_seats", "State Dem Seats 2026", "Dem House Seats (2026)", 20, 110, 395, 95),
    make_card("p7_kpi_state_rep_seats", "State Rep Seats 2026", "Rep House Seats (2026)", 435, 110, 395, 95),
    make_card("p7_kpi_state_gov", "State Governor 2026", "Governor Race Result (2026)", 850, 110, 410, 95),
    make_chart("p7_chart_state_trend", "columnChart", "dim_cycle", "cycle", ["House Seats D", "House Seats R"], "Historical House Seats for Selected State (2018\u20132026)", 20, 220, 600, 480),
    make_table("p7_table_state_results", "fact_results", ["office_key", "candidate", "party_name"], ["Dem House Vote Share"], "2026 State Race Results", 640, 220, 620, 480)
]
pages_dict["page7_state_detail"] = p7_visuals

# -------------------------------------------------------------------------
# Write PBIR Files for Pages and Visuals
# -------------------------------------------------------------------------
pages_meta = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
    "pageOrder": [p["id"] for p in PAGES],
    "activePageName": "page1_the_night"
}
with open(os.path.join(PAGES_DIR, "pages.json"), "w", encoding="utf-8") as f:
    json.dump(pages_meta, f, indent=2)

for pinfo in PAGES:
    pid = pinfo["id"]
    pdir = os.path.join(PAGES_DIR, pid)
    vdir = os.path.join(pdir, "visuals")
    os.makedirs(vdir, exist_ok=True)

    page_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
        "name": pid,
        "displayName": pinfo["displayName"],
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280
    }
    if pinfo["isDrillthrough"]:
        page_data["visibility"] = "HiddenInViewMode"
        page_data["pageBinding"] = {
            "name": "drillthrough_state",
            "drillthrough": {
                "fields": [
                    {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "entity": "dim_geography"
                                }
                            },
                            "property": "state_abbr"
                        }
                    }
                ]
            }
        }

    with open(os.path.join(pdir, "page.json"), "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2)

    for v in pages_dict[pid]:
        vname = v["name"]
        vis_folder = os.path.join(vdir, vname)
        os.makedirs(vis_folder, exist_ok=True)
        with open(os.path.join(vis_folder, "visual.json"), "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2)

print(f"Generated all 7 pages and {sum(len(v) for v in pages_dict.values())} visuals in PBIR format!")

# -------------------------------------------------------------------------
# Compile Legacy report.json for dual compatibility
# -------------------------------------------------------------------------
sections = []
for pinfo in PAGES:
    pid = pinfo["id"]
    visual_containers = []
    for v in pages_dict[pid]:
        pos = v["position"]
        visual_containers.append({
            "x": float(pos["x"]),
            "y": float(pos["y"]),
            "z": float(pos.get("z", 0)),
            "width": float(pos["width"]),
            "height": float(pos["height"]),
            "config": json.dumps({
                "name": v["name"],
                "layouts": [
                    {
                        "id": 0,
                        "position": {
                            "x": float(pos["x"]),
                            "y": float(pos["y"]),
                            "z": float(pos.get("z", 0)),
                            "width": float(pos["width"]),
                            "height": float(pos["height"])
                        }
                    }
                ],
                "singleVisual": v.get("visual", {})
            })
        })

# Done PBIR generation

