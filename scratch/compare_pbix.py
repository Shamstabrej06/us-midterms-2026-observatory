import zipfile

pbix_bak = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-pre-automation-backup.pbix"
pbix_test = r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-automation-test.pbix"

with zipfile.ZipFile(pbix_bak) as zb, zipfile.ZipFile(pbix_test) as zt:
    bak_names = set(zb.namelist())
    test_names = set(zt.namelist())
    print("In bak only:", bak_names - test_names)
    print("In test only:", len(test_names - bak_names), "entries")
    for n in sorted(bak_names & test_names):
        ib = zb.getinfo(n)
        it = zt.getinfo(n)
        same_size = (ib.file_size == it.file_size)
        same_comp = (ib.compress_type == it.compress_type)
        same_bytes = (zb.read(n) == zt.read(n))
        print(f"{n:55} size_same={same_size} comp_same={same_comp} (bak={ib.compress_type}, test={it.compress_type}) bytes_same={same_bytes}")
