with open(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.min.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'processWireContract', text)]
print(f"Found {len(matches)} occurrences")
for idx in matches:
    print("---", idx, "---")
    print(text[max(0, idx - 100):min(len(text), idx + 400)])
