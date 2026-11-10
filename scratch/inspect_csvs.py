import os
import glob
import pandas as pd

gold_dir = r"C:\Users\shams\us-midterms-2026-observatory\powerbi\gold"
csvs = sorted(glob.glob(os.path.join(gold_dir, "*.csv")))

print(f"Total CSVs: {len(csvs)}")
for c in csvs:
    df = pd.read_csv(c)
    print(f"\nTable: {os.path.basename(c)[:-4]} ({len(df)} rows)")
    for col in df.columns:
        dtype = df[col].dtype
        print(f"  {col}: {dtype}")
