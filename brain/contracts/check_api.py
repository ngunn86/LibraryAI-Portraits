"""Checks the API contract (T-08): every component schema is valid JSON Schema 2020-12, every sample payload
validates, and payloads that must be refused are refused.

Run from the repo root:
  python3 brain/contracts/check_api.py brain/contracts/portraits-api.openapi.json brain/contracts/portraits-api.sample.json
Needs the jsonschema package (4.18 or later). Offline.
"""
import json, sys
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
doc = json.load(open(sys.argv[1])); sample = json.load(open(sys.argv[2]))
reg = Registry().with_resource("urn:api", Resource.from_contents(doc, default_specification=__import__("referencing.jsonschema").jsonschema.DRAFT202012))
def v(name): return Draft202012Validator({"$ref": f"urn:api#/components/schemas/{name}"}, registry=reg)
for n, s in doc["components"]["schemas"].items():
    Draft202012Validator.check_schema(s)
pairs = {"health":"Health","teacher_page":"TeacherPage","teacher":"Teacher","portrait":"Portrait","portrait_page":"PortraitPage","history":"History",
 "change_feed":"ChangeFeed","decision_approve":"Decision","decision_turn_down":"Decision","decision_set_main":"Decision","decision_correct":"Decision",
 "decision_result":"DecisionResult","new_request_try_again":"NewRequest","new_request_try_link":"NewRequest","request":"Request","request_page":"RequestPage","error":"Error"}
fails = 0
for k, n in pairs.items():
    errs = list(v(n).iter_errors(sample[k]))
    if errs: fails += 1; print("FAIL", k, [e.message for e in errs][:3])
assert set(pairs) == set(sample) - {"_note"}, set(sample) - set(pairs)
bad = {"turn_down without reason": ("Decision", {k: x for k, x in sample["decision_turn_down"].items() if k != "reason"}),
       "correct without value": ("Decision", {k: x for k, x in sample["decision_correct"].items() if k != "value"}),
       "unknown decision field": ("Decision", dict(sample["decision_approve"], email="a@b.c")),
       "try_link without link": ("NewRequest", {k: x for k, x in sample["new_request_try_link"].items() if k != "link"}),
       "try_again without portrait": ("NewRequest", dict(sample["new_request_try_again"], portrait_id=None)),
       "bad portrait id": ("PortraitSummary", dict(sample["portrait_page"]["portraits"][0], portrait_id="charles-fillmore")),
       "unknown file kind": ("File", dict(sample["portrait"]["files"][0], kind="sepia"))}
for k, (n, x) in bad.items():
    if v(n).is_valid(x): fails += 1; print("SHOULD FAIL", k)
print("schemas", len(doc["components"]["schemas"]), "samples", len(pairs), "negative", len(bad), "fails", fails)
sys.exit(1 if fails else 0)
