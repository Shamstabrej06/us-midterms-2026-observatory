import re

dax_path = r"C:\Users\shams\us-midterms-2026-observatory\powerbi\dax_measures.md"
with open(dax_path, "r", encoding="utf-8") as f:
    content = f.read()

# Extract measure names
measures = re.findall(r"###\s+([^\n]+)", content)
print(f"Total measures defined in dax_measures.md: {len(measures)}")
for i, m in enumerate(measures, 1):
    print(f"  {i:2d}. {m}")
