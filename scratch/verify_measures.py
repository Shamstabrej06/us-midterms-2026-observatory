import re, glob

dax_path = r"C:\Users\shams\us-midterms-2026-observatory\powerbi\dax_measures.md"
with open(dax_path, "r", encoding="utf-8") as f:
    text = f.read()

# Extract measures: pattern is ```dax\n([^\n=]+)\s*=
dax_blocks = re.findall(r"```dax\s*\n\s*([^=\n]+?)\s*=", text)
measures = [m.strip() for m in dax_blocks if m.strip()]
print(f"Measures in dax_measures.md: {len(measures)}")

# Check against TMDL files
tmdl_files = glob.glob(r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Dataset\definition\tables\*.tmdl")
all_tmdl = ""
for tf in tmdl_files:
    with open(tf, "r", encoding="utf-8") as f:
        all_tmdl += f.read() + "\n"

found = 0
missing = []
for m in measures:
    # Look for measure 'Name' or measure Name
    if f"measure '{m}'" in all_tmdl or f"measure {m}" in all_tmdl:
        found += 1
    else:
        missing.append(m)

print(f"Found in TMDL model: {found}/{len(measures)}")
if missing:
    print("Missing in TMDL:", missing)
else:
    print("ALL measures present in TMDL model!")
