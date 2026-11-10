import os
import json
import jsonschema

PAGES_DIR = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition\pages"

total_pages = 0
total_visuals = 0
errors = []

for page_folder in os.listdir(PAGES_DIR):
    page_path = os.path.join(PAGES_DIR, page_folder)
    if not os.path.isdir(page_path):
        continue
    total_pages += 1
    page_file = os.path.join(page_path, "page.json")
    if not os.path.exists(page_file):
        errors.append(f"Missing page.json in {page_folder}")
    else:
        with open(page_file, "r", encoding="utf-8") as f:
            try:
                pj = json.load(f)
                if not pj.get("name") or not pj.get("displayName"):
                    errors.append(f"Invalid page.json in {page_folder}")
            except Exception as e:
                errors.append(f"JSON error in {page_file}: {e}")

    vis_dir = os.path.join(page_path, "visuals")
    if os.path.exists(vis_dir):
        for vname in os.listdir(vis_dir):
            vpath = os.path.join(vis_dir, vname, "visual.json")
            if os.path.exists(vpath):
                total_visuals += 1
                with open(vpath, "r", encoding="utf-8") as f:
                    try:
                        vj = json.load(f)
                        if not vj.get("name") or not vj.get("position") or not vj.get("visual"):
                            errors.append(f"Invalid visual in {vpath}")
                    except Exception as e:
                        errors.append(f"JSON error in {vpath}: {e}")

print(f"Total Pages Checked: {total_pages}")
print(f"Total Visuals Checked: {total_visuals}")
print(f"Errors Found: {len(errors)}")
if errors:
    for e in errors[:10]:
        print(" -", e)
