import glob, json, os

vfiles = glob.glob(r'C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition\pages\page1_the_night\visuals\*\visual.json')
print(f'Total visuals in page 1: {len(vfiles)}')
for vf in sorted(vfiles):
    vdir = os.path.basename(os.path.dirname(vf))
    with open(vf, 'r', encoding='utf-8') as f:
        data = json.load(f)
    vtype = data.get('visual', {}).get('visualType')
    pos = data.get('position', {})
    schema = data.get('$schema')
    print(f'{vdir:25} | type={vtype:12} | schema={schema}')
