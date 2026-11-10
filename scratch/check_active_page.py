import urllib.request
import json

u = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"
req = urllib.request.urlopen(u)
schema = json.loads(req.read().decode())
print("activePageName definition:")
print(json.dumps(schema.get("properties", {}).get("activePageName"), indent=2))
