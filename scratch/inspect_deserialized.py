import json

with open(r'C:\Users\shams\us-midterms-2026-observatory\scratch\deserialized_exploration.json') as f:
    data = json.load(f)

pages_list = data.get('pages', {}).get('pages', [])
print(f"Number of pages: {len(pages_list)}")
for p in pages_list:
    pdata = p.get('page', {})
    vcs = p.get('visualContainers', [])
    print(f"Page: {pdata.get('name')} | Display: \"{pdata.get('displayName')}\" | Visuals: {len(vcs)}")
