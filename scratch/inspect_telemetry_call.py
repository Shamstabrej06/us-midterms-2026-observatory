with open(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.min.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('"ReportDeserialization"')
snippet = text[max(0, idx - 200):min(len(text), idx + 400)]
print(snippet)
