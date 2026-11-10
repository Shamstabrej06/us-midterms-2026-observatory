with open(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.min.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pos = 0
found = 0
key = '.UL('
while True:
    idx = text.find(key, pos)
    if idx == -1:
        break
    found += 1
    snippet = text[max(0, idx - 100):min(len(text), idx + 200)]
    print(f"=== Occurrence {found} at {idx} ===")
    print(snippet)
    pos = idx + 1
    if found >= 10:
        break
