import os
import glob
import re
import json

dataset_dir = r'MidtermsObservatory.Dataset/definition'
tables = {}
all_measures = set()

# Parse TMDL files
for tmdl_file in glob.glob(f'{dataset_dir}/tables/*.tmdl'):
    t_name = None
    with open(tmdl_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        stripped = line.strip()
        m_table = re.match(r'^table\s+(.+)$', stripped)
        if m_table and not t_name:
            t_name = m_table.group(1).strip("'` ")
            tables[t_name] = set()
        m_col = re.match(r'^column\s+(.+)$', stripped)
        if m_col and t_name:
            col_name = m_col.group(1).strip().split('=')[0].strip("'` ")
            tables[t_name].add(col_name)
        m_meas = re.match(r'^measure\s+(.+?)(?:=|\s*=|$)', stripped)
        if m_meas and t_name:
            meas_name = m_meas.group(1).strip("'` ")
            tables[t_name].add(meas_name)
            all_measures.add(meas_name)

print(f"Model tables ({len(tables)}):")
for t, cols in sorted(tables.items()):
    print(f"  {t}: {len(cols)} items")
print(f"Total measures: {len(all_measures)}")

# Now check all visuals
visual_files = glob.glob('MidtermsObservatory.Report/definition/pages/**/visuals/**/visual.json', recursive=True)
print(f"Total visual files: {len(visual_files)}")

broken_refs = []

def check_obj(obj, v_path):
    if isinstance(obj, dict):
        if 'Entity' in obj and 'Property' in obj:
            entity = obj['Entity']
            prop = obj['Property']
            if entity in tables:
                if prop not in tables[entity]:
                    broken_refs.append((v_path, f"Table '{entity}' missing property/measure: '{prop}'"))
            else:
                broken_refs.append((v_path, f"Unknown table: '{entity}'"))
        for k, v in obj.items():
            check_obj(v, v_path)
    elif isinstance(obj, list):
        for item in obj:
            check_obj(item, v_path)

for vf in visual_files:
    with open(vf, 'r', encoding='utf-8') as f:
        data = json.load(f)
    check_obj(data, vf)

if broken_refs:
    print(f"Broken references found ({len(broken_refs)}):")
    for p, b in broken_refs:
        print(f"  {p}: {b}")
else:
    print("All visual field/measure references match the semantic model exactly!")
