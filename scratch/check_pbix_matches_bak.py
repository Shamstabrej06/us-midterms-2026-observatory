import filecmp

pbix_orig = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbix"
pbix_bak = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-pre-automation-backup.pbix"

same = filecmp.cmp(pbix_orig, pbix_bak, shallow=False)
print(f"MidtermsObservatory.pbix matches backup: {same}")
