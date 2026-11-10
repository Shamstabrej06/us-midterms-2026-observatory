with open(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.min.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = 12227085
# search for Xe in the 20000 characters before idx
snippet = text[max(0, idx - 20000):idx]
import re
matches = list(re.finditer(r'class \w+\{.*?deserialize\(', snippet))
for m in matches:
    print("Class with deserialize:", m.group(0)[:200])
