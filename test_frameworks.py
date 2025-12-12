import json

with open("json/pipeline-momentum-framework.json") as f:
    momentum = json.load(f)

print(momentum["framework_name"])
print(len(momentum["momentum_signals"]))

score = 4 + 2 + 3 + 4 + 3

bands = momentum["scoring_model"]["total_score_interpretation"]

result = next(
    band for band in bands
    if band["min"] <= score <= band["max"]
)

print(result["label"])
