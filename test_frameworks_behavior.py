import json
from pathlib import Path

ROOT = Path(__file__).parent

def load(path):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)

def band_for_score(framework, score: int):
    bands = framework["scoring_model"]["total_score_interpretation"]
    matches = [b for b in bands if b["min"] <= score <= b["max"]]
    assert len(matches) == 1, f"Score {score} matched {len(matches)} bands: {matches}"
    return matches[0]["id"]

def test_momentum_boundaries():
    f = load("json/pipeline-momentum-framework.json")
    expected = {
        0: "stalled",
        7: "stalled",
        8: "at_risk",
        13: "at_risk",
        14: "conditional",
        19: "conditional",
        20: "strong_positive",
        25: "strong_positive",
    }
    for score, band_id in expected.items():
        got = band_for_score(f, score)
        assert got == band_id, f"Score {score}: expected {band_id}, got {got}"

def test_index_paths_exist():
    # Support index.json either at repo root or inside /json
    if (ROOT / "index.json").exists():
        idx = load("index.json")
    elif (ROOT / "json/index.json").exists():
        idx = load("json/index.json")
    else:
        raise FileNotFoundError("Could not find index.json in root or /json")

    for fw in idx.get("frameworks", []):
        files = fw.get("files")

        assert files is not None, f"Missing 'files' for framework {fw.get('id')}"
        assert isinstance(files, (list, dict)), f"'files' must be list or dict: {fw.get('id')}"

        # Your current structure: files is a dict like {"frameworks": "...", "json": "..."}
        if isinstance(files, dict):
            for key, path in files.items():
                assert isinstance(path, str) and path.strip(), f"Invalid path for {fw.get('id')}:{key}"
                assert (ROOT / path).exists(), f"Index path does not exist: {path}"

        # Also support older structure: files is a list of strings or objects
        if isinstance(files, list):
            for item in files:
                if isinstance(item, str):
                    path = item
                elif isinstance(item, dict):
                    path = item.get("path")
                else:
                    raise TypeError(f"Unexpected file entry type: {type(item)} -> {item}")

                assert path, f"Missing path in index entry: {item}"
                assert (ROOT / path).exists(), f"Index path does not exist: {path}"

def test_taxonomy_rnba_aliasing():
    tax = load("taxonomy.json")
    concepts = {c["id"]: c for c in tax["concepts"]}
    rn = concepts.get("required_next_buyer_action")
    assert rn, "Missing required_next_buyer_action concept"
    assert rn.get("canonical_term") == "RNBA", "RNBA should be canonical_term"
    aliases = set(rn.get("aliases", []))
    assert "RMA" in aliases, "RMA should be an alias of RNBA"

if __name__ == "__main__":
    test_momentum_boundaries()
    test_index_paths_exist()
    test_taxonomy_rnba_aliasing()
    print("All behavioral tests passed.")
