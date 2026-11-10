import urllib.request
import json

u = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"
req = urllib.request.urlopen(u)
schema = json.loads(req.read().decode())
print("pageOrder definition:")
print(json.dumps(schema.get("properties", {}).get("pageOrder"), indent=2))
