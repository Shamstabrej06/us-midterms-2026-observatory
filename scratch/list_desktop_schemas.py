import glob
import re

paths = glob.glob(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.schema.json.*.min.js')
ids = set()
for p in paths:
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    for m in re.finditer(r'https://developer\.microsoft\.com/json-schemas/fabric/[^\"]+', text):
        clean = m.group(0).split('#')[0]
        ids.add(clean)

for s in sorted(ids):
    print(s)
