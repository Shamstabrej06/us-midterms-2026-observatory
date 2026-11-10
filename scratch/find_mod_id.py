with open(r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\WebView2Resources\minerva\scripts\desktop.min.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = 12227085
# Search backwards for module definition e.g. 123456:(e,t,i)=>
last_colon = text.rfind(':(', 0, idx)
mod_start = text.rfind(',', 0, last_colon)
if mod_start == -1:
    mod_start = text.rfind('{', 0, last_colon)
print("Module ID snippet:", text[mod_start:last_colon+5])
