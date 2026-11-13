import zipfile, json

pbix_bak = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-pre-automation-backup.pbix"
theme_file = r"C:\Users\shams\us-midterms-2026-observatory\powerbi\theme.json"

with zipfile.ZipFile(pbix_bak) as z:
    zip_theme = json.loads(z.read("Report/StaticResources/RegisteredResources/theme.json").decode("utf-8"))

with open(theme_file, "r", encoding="utf-8") as f:
    repo_theme = json.load(f)

print("Repo theme dataColors:", repo_theme.get("dataColors"))
print("Zip theme dataColors: ", zip_theme.get("dataColors"))
print("Repo theme name:      ", repo_theme.get("name"))
print("Zip theme name:       ", zip_theme.get("name"))
