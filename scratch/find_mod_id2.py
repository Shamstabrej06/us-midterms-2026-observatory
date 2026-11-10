with open(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.min.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = 12227085
import re
matches = list(re.finditer(r'(\d+):(?:\s*\([e,\s*t,\s*i\)]*=>|\s*function)', text[:idx]))
if matches:
    last = matches[-1]
    print("Matched module id:", last.group(1), "at", last.start())
