import json
from pymlb_statsapi import api

methods = api.Stats.get_method_names()
print(methods)

method = api.Stats.get_method("stats")
schema = method.get_schema()
print(json.dumps(schema, indent=2))

description = api.Stats.describe_method("stats")
print(description)
