import os
import json
import shutil
import re
import uuid
import pandas as pd

REPO_DIR = r"C:\Users\shams\us-midterms-2026-observatory"
GOLD_DIR = os.path.join(REPO_DIR, "powerbi", "gold")
DATASET_DIR = os.path.join(REPO_DIR, "MidtermsObservatory.Dataset")
SEMANTIC_DIR = os.path.join(REPO_DIR, "MidtermsObservatory.SemanticModel")
REPORT_DIR = os.path.join(REPO_DIR, "MidtermsObservatory.Report")
PBIP_PATH = os.path.join(REPO_DIR, "MidtermsObservatory.pbip")
DAX_PATH = os.path.join(REPO_DIR, "powerbi", "dax_measures.md")
THEME_PATH = os.path.join(REPO_DIR, "powerbi", "theme.json")

def generate_uuid(name_seed):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"midterms.observatory.{name_seed}"))

print("=== STARTING FULL PBIP PROJECT GENERATION ===")

# -------------------------------------------------------------
# 1. Parse DAX Measures
# -------------------------------------------------------------
with open(DAX_PATH, "r", encoding="utf-8") as f:
    dax_text = f.read()

pattern = r"```dax\s*([\s\S]*?)```"
blocks = re.findall(pattern, dax_text)

measures = {}
for b in blocks:
    b = b.strip()
    if "=" in b:
        name = b.split("=", 1)[0].strip()
        formula = b.split("=", 1)[1].strip()
        measures[name] = formula

print(f"Parsed {len(measures)} DAX measures from dax_measures.md")

# Measure to home table mapping
MEASURE_HOMES = {
    # dim_cycle
    "House Majority 2026": "dim_cycle",
    "Senate Majority 2026": "dim_cycle",
    "Trifecta 2026": "dim_cycle",

    # dim_geography
    "State Name": "dim_geography",

    # fact_results
    "House Seats D 2026": "fact_results",
    "House Seats R 2026": "fact_results",
    "House Seats Uncalled 2026": "fact_results",
    "House Net Change D 2026": "fact_results",
    "House Net Change R 2026": "fact_results",
    "House Popular Vote D 2026": "fact_results",
    "House Popular Vote R 2026": "fact_results",
    "House Popular Vote Margin 2026": "fact_results",
    "Gov Wins D 2026": "fact_results",
    "Gov Wins R 2026": "fact_results",
    "Gov Races Uncalled 2026": "fact_results",
    "House Seats D": "fact_results",
    "House Seats R": "fact_results",
    "House Net Change D": "fact_results",
    "Dem House Vote Share": "fact_results",
    "Rep House Vote Share": "fact_results",
    "House Vote Margin D minus R": "fact_results",
    "Dem Seats Change 2022 to 2026": "fact_results",
    "Texas House Dem Seats": "fact_results",
    "Texas House Rep Seats": "fact_results",
    "Presidents Party Net Change": "fact_results",
    "State Dem Seats 2026": "fact_results",
    "State Rep Seats 2026": "fact_results",
    "State Governor 2026": "fact_results",

    # fact_finance
    "Total Receipts": "fact_finance",
    "House Receipts": "fact_finance",
    "Senate Receipts": "fact_finance",
    "Candidates Count": "fact_finance",

    # fact_turnout
    "Turnout Rate": "fact_turnout",

    # fact_texas_statewide
    "Texas Dem Margin": "fact_texas_statewide",
    "Texas Dem Pct": "fact_texas_statewide",
    "Texas Rep Pct": "fact_texas_statewide",

    # fact_senate_composition
    "Senate Seats D 2026": "fact_senate_composition",
    "Senate Seats R 2026": "fact_senate_composition",
    "Senate Seats I 2026": "fact_senate_composition",
    "Senate Net Change D 2026": "fact_senate_composition",
    "Senate Net Change D": "fact_senate_composition",

    # fact_senate_flips_2026
    "Senate Flips 2026": "fact_senate_flips_2026",

    # fact_house_closest_races
    "Races Under 5 Pts": "fact_house_closest_races",
    "Races Under 10 Pts": "fact_house_closest_races"
}

# Group measures by table
table_measures = {t: {} for t in [
    "dim_cycle", "dim_geography", "dim_office", "dim_party",
    "fact_finance", "fact_house_closest_races", "fact_results",
    "fact_senate_composition", "fact_senate_flips_2026",
    "fact_texas_statewide", "fact_turnout"
]}

for mname, mform in measures.items():
    ht = MEASURE_HOMES.get(mname, "fact_results")
    table_measures[ht][mname] = mform

# -------------------------------------------------------------
# 2. Setup Dataset Directory Structure
# -------------------------------------------------------------
if os.path.exists(DATASET_DIR):
    shutil.rmtree(DATASET_DIR)
os.makedirs(os.path.join(DATASET_DIR, "definition", "tables"), exist_ok=True)
os.makedirs(os.path.join(DATASET_DIR, "definition", "cultures"), exist_ok=True)

# definition.pbism
pbism_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "4.0",
    "settings": {}
}
with open(os.path.join(DATASET_DIR, "definition.pbism"), "w", encoding="utf-8") as f:
    json.dump(pbism_data, f, indent=2)

# database.tmdl
database_tmdl = """database MidtermsObservatory
	compatibilityLevel: 1567
	compatibilityMode: powerBI
"""
with open(os.path.join(DATASET_DIR, "definition", "database.tmdl"), "w", encoding="utf-8") as f:
    f.write(database_tmdl)

# expressions.tmdl
expr_tmdl = f'''expression RepoFolder = "{REPO_DIR}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
\tlineageTag: {generate_uuid("RepoFolder")}
'''
with open(os.path.join(DATASET_DIR, "definition", "expressions.tmdl"), "w", encoding="utf-8") as f:
    f.write(expr_tmdl)

# cultures/en-US.tmdl
with open(os.path.join(DATASET_DIR, "definition", "cultures", "en-US.tmdl"), "w", encoding="utf-8") as f:
    f.write("cultureInfo en-US\n")

# model.tmdl
model_tmdl_lines = [
    "model Model",
    "\tculture: en-US",
    "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
    "\tsourceQueryCulture: en-US",
    "\tdiscourageImplicitMeasures",
    ""
]
for tname in sorted(table_measures.keys()):
    model_tmdl_lines.append(f"ref table {tname}")
model_tmdl_lines.append("")
model_tmdl_lines.append("ref expression RepoFolder")
model_tmdl_lines.append("")
model_tmdl_lines.append("ref cultureInfo en-US")
model_tmdl_lines.append("")

with open(os.path.join(DATASET_DIR, "definition", "model.tmdl"), "w", encoding="utf-8") as f:
    f.write("\n".join(model_tmdl_lines))

# -------------------------------------------------------------
# 3. Build Tables & Measures in TMDL
# -------------------------------------------------------------
table_schemas = {
    "dim_cycle": [
        ("cycle", "int64", "Int64.Type", "0"),
        ("congress", "int64", "Int64.Type", "0"),
        ("election_type", "string", "type text", None),
        ("president", "string", "type text", None),
        ("president_party", "string", "type text", None),
        ("senate_majority", "string", "type text", None),
        ("house_majority", "string", "type text", None),
        ("trifecta", "boolean", "type logical", None)
    ],
    "dim_geography": [
        ("state_fips", "int64", "Int64.Type", "0"),
        ("state_abbr", "string", "type text", None),
        ("state_name", "string", "type text", None),
        ("region", "string", "type text", None),
        ("division", "string", "type text", None),
        ("population_2024", "double", "Double.Type", "#,0")
    ],
    "dim_office": [
        ("office_key", "string", "type text", None),
        ("office_name", "string", "type text", None),
        ("chamber", "string", "type text", None),
        ("seats_total", "int64", "Int64.Type", "0")
    ],
    "dim_party": [
        ("party_key", "string", "type text", None),
        ("party_name", "string", "type text", None)
    ],
    "fact_finance": [
        ("candidate_id", "string", "type text", None),
        ("candidate_name", "string", "type text", None),
        ("cycle", "int64", "Int64.Type", "0"),
        ("office", "string", "type text", None),
        ("office_name", "string", "type text", None),
        ("state_abbr", "string", "type text", None),
        ("state_name", "string", "type text", None),
        ("district", "double", "Double.Type", "0"),
        ("incumbent_status", "string", "type text", None),
        ("party_raw", "string", "type text", None),
        ("party_name", "string", "type text", None),
        ("total_receipts", "double", "Double.Type", "$#,0"),
        ("total_disbursements", "double", "Double.Type", "$#,0"),
        ("cash_on_hand_bop", "double", "Double.Type", "$#,0"),
        ("cash_on_hand_end", "double", "Double.Type", "$#,0"),
        ("debts_owed_by", "double", "Double.Type", "$#,0"),
        ("individual_contributions", "double", "Double.Type", "$#,0"),
        ("other_committee_contributions", "double", "Double.Type", "$#,0"),
        ("party_committee_contributions", "double", "Double.Type", "$#,0"),
        ("coverage_end_date", "string", "type text", None),
        ("status", "string", "type text", None),
        ("party_key", "string", "type text", None)
    ],
    "fact_house_closest_races": [
        ("cycle", "int64", "Int64.Type", "0"),
        ("district", "string", "type text", None),
        ("winner", "string", "type text", None),
        ("margin_pts", "double", "Double.Type", "0.0"),
        ("margin_band", "string", "type text", None)
    ],
    "fact_results": [
        ("race_id", "string", "type text", None),
        ("cycle", "int64", "Int64.Type", "0"),
        ("office_key", "string", "type text", None),
        ("geography_level", "string", "type text", None),
        ("state_fips", "double", "Double.Type", "0"),
        ("state_abbr", "string", "type text", None),
        ("party_key", "string", "type text", None),
        ("party_name", "string", "type text", None),
        ("candidate", "string", "type text", None),
        ("votes", "double", "Double.Type", "#,0"),
        ("vote_share_pct", "double", "Double.Type", "0.0\"%\""),
        ("seats_before", "double", "Double.Type", "0"),
        ("seats_after", "double", "Double.Type", "0"),
        ("net_change", "double", "Double.Type", "+0;-0;0"),
        ("margin_pts", "double", "Double.Type", "+0.0;-0.0;0.0"),
        ("winner_party", "string", "type text", None),
        ("status", "string", "type text", None)
    ],
    "fact_senate_composition": [
        ("cycle", "int64", "Int64.Type", "0"),
        ("congress", "int64", "Int64.Type", "0"),
        ("party_name", "string", "type text", None),
        ("seats_before", "double", "Double.Type", "0"),
        ("seats_after", "int64", "Int64.Type", "0"),
        ("net_change", "double", "Double.Type", "+0;-0;0"),
        ("status", "string", "type text", None)
    ],
    "fact_senate_flips_2026": [
        ("cycle", "int64", "Int64.Type", "0"),
        ("chamber", "string", "type text", None),
        ("state", "string", "type text", None),
        ("state_abbr", "string", "type text", None),
        ("incumbent", "string", "type text", None),
        ("incumbent_party", "string", "type text", None),
        ("winner", "string", "type text", None),
        ("winner_party", "string", "type text", None),
        ("result_text", "string", "type text", None),
        ("status", "string", "type text", None)
    ],
    "fact_texas_statewide": [
        ("cycle", "int64", "Int64.Type", "0"),
        ("state", "string", "type text", None),
        ("office", "string", "type text", None),
        ("dem_candidate", "string", "type text", None),
        ("dem_votes", "double", "Double.Type", "#,0"),
        ("dem_pct", "double", "Double.Type", "0.0\"%\""),
        ("rep_candidate", "string", "type text", None),
        ("rep_votes", "double", "Double.Type", "#,0"),
        ("rep_pct", "double", "Double.Type", "0.0\"%\""),
        ("margin_pts", "double", "Double.Type", "+0.0;-0.0;0.0"),
        ("winner_party", "string", "type text", None),
        ("status", "string", "type text", None)
    ],
    "fact_turnout": [
        ("cycle", "int64", "Int64.Type", "0"),
        ("geography_level", "string", "type text", None),
        ("state_abbr", "string", "type text", None),
        ("turnout_rate_pct", "double", "Double.Type", "0.00\"%\""),
        ("status", "string", "type text", None)
    ]
}

for tname, cols in table_schemas.items():
    t_lines = [
        f"table {tname}",
        f"\tlineageTag: {generate_uuid(tname)}",
        ""
    ]
    for cname, ctype, _, fmt in cols:
        t_lines.append(f"\tcolumn {cname}")
        t_lines.append(f"\t\tdataType: {ctype}")
        if fmt:
            t_lines.append(f"\t\tformatString: {fmt}")
        t_lines.append(f"\t\tlineageTag: {generate_uuid(f'{tname}.{cname}')}")
        t_lines.append("\t\tsummarizeBy: none")
        t_lines.append(f"\t\tsourceColumn: {cname}")
        if tname == "dim_geography" and cname == "state_name":
            t_lines.append("\t\tdataCategory: StateOrProvince")
        t_lines.append("")

    # Add DAX measures assigned to this table
    for mname, mformula in table_measures[tname].items():
        t_lines.append(f"\tmeasure '{mname}' =")
        for fline in mformula.split("\n"):
            t_lines.append(f"\t\t\t{fline}")
        t_lines.append(f"\t\tlineageTag: {generate_uuid(f'{tname}.measure.{mname}')}")
        # Format strings for specific measures
        if "Margin" in mname or "Pct" in mname or "Share" in mname:
            t_lines.append('\t\tformatString: 0.0"%"')
        elif "Receipts" in mname:
            t_lines.append('\t\tformatString: "$#,0"')
        elif "Rate" in mname:
            t_lines.append('\t\tformatString: 0.00"%"')
        t_lines.append("")

    # Partition definition
    col_transforms = ", ".join([f'{{"{cn}", {mtype}}}' for cn, _, mtype, _ in cols])
    t_lines.append(f"\tpartition {tname} = m")
    t_lines.append("\t\tmode: import")
    t_lines.append("\t\tsource =")
    t_lines.append("\t\t\tlet")
    t_lines.append(f'\t\t\t    Source = Csv.Document(File.Contents(RepoFolder & "/powerbi/gold/{tname}.csv"),[Delimiter=",", Columns={len(cols)}, Encoding=65001, QuoteStyle=QuoteStyle.None]),')
    t_lines.append('\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),')
    t_lines.append(f'\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{{col_transforms}}})')
    t_lines.append("\t\t\tin")
    t_lines.append('\t\t\t    #"Changed Type"')
    t_lines.append("")

    with open(os.path.join(DATASET_DIR, "definition", "tables", f"{tname}.tmdl"), "w", encoding="utf-8") as f:
        f.write("\n".join(t_lines))

print("Wrote all 11 table TMDL definitions with verbatim DAX measures")

# -------------------------------------------------------------
# 4. Relationships TMDL
# -------------------------------------------------------------
rels = [
    ("fact_results", "cycle", "dim_cycle", "cycle"),
    ("fact_results", "state_abbr", "dim_geography", "state_abbr"),
    ("fact_results", "office_key", "dim_office", "office_key"),
    ("fact_results", "party_key", "dim_party", "party_key"),
    ("fact_finance", "cycle", "dim_cycle", "cycle"),
    ("fact_turnout", "cycle", "dim_cycle", "cycle"),
    ("fact_texas_statewide", "cycle", "dim_cycle", "cycle"),
    ("fact_senate_composition", "cycle", "dim_cycle", "cycle"),
    ("fact_senate_flips_2026", "cycle", "dim_cycle", "cycle"),
    ("fact_house_closest_races", "cycle", "dim_cycle", "cycle")
]

rel_lines = []
for from_tbl, from_col, to_tbl, to_col in rels:
    rel_lines.append(f"relationship {generate_uuid(f'{from_tbl}.{from_col}->{to_tbl}.{to_col}')}")
    rel_lines.append(f"\tfromColumn: {from_tbl}.{from_col}")
    rel_lines.append(f"\ttoColumn: {to_tbl}.{to_col}")
    rel_lines.append("")

with open(os.path.join(DATASET_DIR, "definition", "relationships.tmdl"), "w", encoding="utf-8") as f:
    f.write("\n".join(rel_lines))

print("Wrote relationships.tmdl (10 relationships)")

# Create SemanticModel junction for dual compatibility
if os.path.exists(SEMANTIC_DIR):
    try:
        os.rmdir(SEMANTIC_DIR)
    except Exception:
        pass
if not os.path.exists(SEMANTIC_DIR):
    import subprocess
    subprocess.run(["cmd", "/c", f'mklink /J "{SEMANTIC_DIR}" "{DATASET_DIR}"'], capture_output=True)

# -------------------------------------------------------------
# 5. Build Report Files (PBIR Enhanced Report Format)
# -------------------------------------------------------------
if os.path.exists(REPORT_DIR):
    shutil.rmtree(REPORT_DIR)

pages_dir = os.path.join(REPORT_DIR, "definition", "pages")
static_dir = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
os.makedirs(pages_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

shutil.copyfile(THEME_PATH, os.path.join(static_dir, "theme.json"))

# definition.pbir
pbir_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
    "version": "4.0",
    "datasetReference": {
        "byPath": {
            "path": "../MidtermsObservatory.Dataset"
        }
    }
}
with open(os.path.join(REPORT_DIR, "definition.pbir"), "w", encoding="utf-8") as f:
    json.dump(pbir_data, f, indent=2)

# definition/version.json
version_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
    "version": "2.0.0"
}
with open(os.path.join(REPORT_DIR, "definition", "version.json"), "w", encoding="utf-8") as f:
    json.dump(version_data, f, indent=2)

# definition/report.json
report_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.0.0/schema.json",
    "themeCollection": {
        "baseTheme": {
            "name": "CY24SU10",
            "reportVersionAtImport": {
                "visual": "2.1.0",
                "report": "3.0.0",
                "page": "2.0.0"
            },
            "type": "SharedResources"
        },
        "customTheme": {
            "name": "theme.json",
            "reportVersionAtImport": {
                "visual": "2.1.0",
                "report": "3.0.0",
                "page": "2.0.0"
            },
            "type": "RegisteredResources"
        }
    },
    "resourcePackages": [
        {
            "name": "SharedResources",
            "type": "SharedResources",
            "items": [
                {
                    "name": "CY24SU10",
                    "path": "BaseThemes/CY24SU10.json",
                    "type": "BaseTheme"
                }
            ]
        },
        {
            "name": "RegisteredResources",
            "type": "RegisteredResources",
            "items": [
                {
                    "name": "theme.json",
                    "path": "theme.json",
                    "type": "CustomTheme"
                }
            ]
        }
    ]
}
with open(os.path.join(REPORT_DIR, "definition", "report.json"), "w", encoding="utf-8") as f:
    json.dump(report_data, f, indent=2)

# Root MidtermsObservatory.pbip
pbip_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [
        {
            "report": {
                "path": "MidtermsObservatory.Report"
            }
        }
    ],
    "settings": {
        "enableAutoRecovery": True
    }
}
with open(PBIP_PATH, "w", encoding="utf-8") as f:
    json.dump(pbip_data, f, indent=2)

print("Generated root PBIP and report metadata")
