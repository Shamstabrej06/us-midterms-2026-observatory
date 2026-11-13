import os
import json
import zipfile
import glob

pbix_in = r'C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-pre-automation-backup.pbix'
pbix_out = r'C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-automation-test.pbix'
repo_dir = r'C:\Users\shams\us-midterms-2026-observatory'
p1_dir = os.path.join(repo_dir, 'MidtermsObservatory.Report', 'definition', 'pages', 'page1_the_night')

# Read all existing files from pbix_in
entries = {}
compression_types = {}

with zipfile.ZipFile(pbix_in, 'r') as zin:
    for item in zin.infolist():
        entries[item.filename] = zin.read(item.filename)
        compression_types[item.filename] = item.compress_type

print(f"Read {len(entries)} entries from backup pbix.")

# 1. Update Report/definition/pages/pages.json
pages_json = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
    "pageOrder": ["page1_the_night"],
    "activePageName": "page1_the_night"
}
entries["Report/definition/pages/pages.json"] = json.dumps(pages_json, indent=2).encode('utf-8')
compression_types["Report/definition/pages/pages.json"] = zipfile.ZIP_DEFLATED

# Remove the old blank page df2517be0509860010d1
old_keys = [k for k in entries if 'df2517be0509860010d1' in k]
for k in old_keys:
    del entries[k]
    del compression_types[k]
print(f"Removed {len(old_keys)} old page entries.")

# 2. Add Page 1 page.json
with open(os.path.join(p1_dir, 'page.json'), 'rb') as f:
    entries["Report/definition/pages/page1_the_night/page.json"] = f.read()
compression_types["Report/definition/pages/page1_the_night/page.json"] = zipfile.ZIP_DEFLATED

# 3. Add all visuals for Page 1
visual_dirs = glob.glob(os.path.join(p1_dir, 'visuals', '*'))
print(f"Found {len(visual_dirs)} visuals for Page 1.")
for vd in visual_dirs:
    vname = os.path.basename(vd)
    vfile = os.path.join(vd, 'visual.json')
    if os.path.exists(vfile):
        with open(vfile, 'rb') as f:
            vcontent = f.read()
        arcname = f"Report/definition/pages/page1_the_night/visuals/{vname}/visual.json"
        entries[arcname] = vcontent
        compression_types[arcname] = zipfile.ZIP_DEFLATED

# 4. Write new pbix
tmp_out = pbix_out + '.tmp'
with zipfile.ZipFile(tmp_out, 'w') as zout:
    for fname, data in entries.items():
        ctype = compression_types.get(fname, zipfile.ZIP_DEFLATED)
        zinfo = zipfile.ZipInfo(fname)
        zinfo.compress_type = ctype
        zout.writestr(zinfo, data)

if os.path.exists(pbix_out):
    os.remove(pbix_out)
os.rename(tmp_out, pbix_out)

print(f"Successfully generated {pbix_out} with {len(entries)} entries!")
