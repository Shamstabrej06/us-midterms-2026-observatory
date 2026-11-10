with open(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.initialVendors.min.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('const $e="__ngContext__";')
print(text[idx+500:idx+2500])
