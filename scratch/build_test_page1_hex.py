import os
import json
import zipfile
import glob
import hashlib

pbix_in = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-pre-automation-backup.pbix"
pbix_out = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-automation-test.pbix"
repo_dir = r"C:\Users\shams\us-midterms-2026-observatory"
p1_dir = os.path.join(repo_dir, "MidtermsObservatory.Report", "definition", "pages", "page1_the_night")

# Read all existing files from pbix_in
entries = {}
compression_types = {}

with zipfile.ZipFile(pbix_in, "r") as zin:
    for item in zin.infolist():
        entries[item.filename] = zin.read(item.filename)
        compression_types[item.filename] = item.compress_type

print(f"Read {len(entries)} entries from backup pbix.")

# Keep the page ID df2517be0509860010d1
page_id = "df2517be0509860010d1"

# 1. Update pages.json
pages_json = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
    "pageOrder": [page_id],
    "activePageName": page_id
}
entries["Report/definition/pages/pages.json"] = json.dumps(pages_json, indent=2).encode("utf-8")
compression_types["Report/definition/pages/pages.json"] = zipfile.ZIP_DEFLATED

# 2. Update page.json for df2517be0509860010d1
page_meta = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
    "name": page_id,
    "displayName": "The Night",
    "displayOption": "FitToPage",
    "height": 720,
    "width": 1280
}
entries[f"Report/definition/pages/{page_id}/page.json"] = json.dumps(page_meta, indent=2).encode("utf-8")
compression_types[f"Report/definition/pages/{page_id}/page.json"] = zipfile.ZIP_DEFLATED

# 3. Add all visuals for Page 1 with 20-hex IDs
visual_dirs = glob.glob(os.path.join(p1_dir, "visuals", "*"))
print(f"Found {len(visual_dirs)} visuals for Page 1.")
for vd in sorted(visual_dirs):
    vname = os.path.basename(vd)
    vfile = os.path.join(vd, "visual.json")
    if os.path.exists(vfile):
        with open(vfile, "r", encoding="utf-8") as f:
            vdata = json.load(f)
        hex_id = hashlib.sha256(vname.encode("utf-8")).hexdigest()[:20]
        vdata["name"] = hex_id
        
        vcontent = json.dumps(vdata, indent=2).encode("utf-8")
        arcname = f"Report/definition/pages/{page_id}/visuals/{hex_id}/visual.json"
        entries[arcname] = vcontent
        compression_types[arcname] = zipfile.ZIP_DEFLATED
        print(f"  Added {vname} -> {hex_id}")

# 4. Write new pbix
tmp_out = pbix_out + ".tmp"
with zipfile.ZipFile(tmp_out, "w") as zout:
    for fname, data in entries.items():
        ctype = compression_types.get(fname, zipfile.ZIP_DEFLATED)
        zinfo = zipfile.ZipInfo(fname)
        zinfo.compress_type = ctype
        zout.writestr(zinfo, data)

if os.path.exists(pbix_out):
    os.remove(pbix_out)
os.rename(tmp_out, pbix_out)

print(f"Successfully generated {pbix_out} with {len(entries)} entries!")
