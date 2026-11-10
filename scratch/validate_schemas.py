import json
import urllib.request
import jsonschema

schemas = {}
def get_schema(url):
    if url not in schemas:
        print(f"Fetching {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        schemas[url] = json.loads(urllib.request.urlopen(req).read().decode())
    return schemas[url]

# 1. pages.json
with open(r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition\pages\pages.json") as f:
    pages_data = json.load(f)
s1 = get_schema(pages_data["$schema"])
try:
    jsonschema.validate(pages_data, s1)
    print("pages.json: VALID")
except Exception as e:
    print("pages.json INVALID:", e.message)

# 2. page.json
with open(r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition\pages\page1_the_night\page.json") as f:
    page_data = json.load(f)
s2 = get_schema(page_data["$schema"])
try:
    jsonschema.validate(page_data, s2)
    print("page.json: VALID")
except Exception as e:
    print("page.json INVALID:", e.message)

# 3. visual.json (textbox)
with open(r"C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.Report\definition\pages\page1_the_night\visuals\p1_headline\visual.json") as f:
    vis_data = json.load(f)
s3 = get_schema(vis_data["$schema"])
try:
    # Need resolver for schema references
    resolver = jsonschema.RefResolver(base_uri=vis_data["$schema"], referrer=s3)
    jsonschema.validate(vis_data, s3, resolver=resolver)
    print("visual.json (textbox): VALID")
except Exception as e:
    print("visual.json INVALID:", e.message)
