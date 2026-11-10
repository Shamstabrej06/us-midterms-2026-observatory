import urllib.request
import json

urls = [
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
]

for u in urls:
    try:
        req = urllib.request.urlopen(u)
        schema = json.loads(req.read().decode())
        print(f"=== {u} ===")
        print("Required:", schema.get("required"))
        print("Properties:", list(schema.get("properties", {}).keys()))
    except Exception as e:
        print(f"Error {u}: {e}")
