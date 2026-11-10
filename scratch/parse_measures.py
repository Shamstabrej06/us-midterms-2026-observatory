import re

with open(r"C:\Users\shams\us-midterms-2026-observatory\powerbi\dax_measures.md", "r", encoding="utf-8") as f:
    text = f.read()

pattern = r"```dax\s*([\s\S]*?)```"
blocks = re.findall(pattern, text)

measures = []
for b in blocks:
    b = b.strip()
    if "=" in b:
        name = b.split("=", 1)[0].strip()
        formula = b.split("=", 1)[1].strip()
        measures.append((name, formula))

print(f"Total measures found: {len(measures)}")
for i, (name, formula) in enumerate(measures, 1):
    first_line = formula.split("\n")[0]
    print(f"{i:2d}. {name} = {first_line[:40]}...")
