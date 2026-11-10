import urllib.request
import json

u = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.0.0/schema.json"
req = urllib.request.urlopen(u)
schema = json.loads(req.read().decode())
print("report/3.0.0 required:", schema.get("required"))
print("report/3.0.0 properties:", list(schema.get("properties", {}).keys()))
