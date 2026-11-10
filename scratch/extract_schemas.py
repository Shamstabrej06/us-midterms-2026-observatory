import re

files = [
    r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.schema-validator.worker.js',
    r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.min.js'
]

found = set()
for fn in files:
    try:
        with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        for m in re.finditer(r'https://developer\.microsoft\.com/json-schemas/fabric/[^\s"\'\\]+', text):
            found.add(m.group(0))
    except Exception as e:
        print(f"Error reading {fn}: {e}")

print(f"Found {len(found)} schemas:")
for s in sorted(found):
    print("  ", s)
