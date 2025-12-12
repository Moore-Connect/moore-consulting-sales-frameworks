import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Any

ROOT = Path(__file__).parent

FRAMEWORK_PATH = ROOT / "json" / "pipeline-momentum-framework.json"
DATA_PATH = ROOT / "test_deals.csv"

OUTPUT_DIR = ROOT / "output"
RESULTS_CSV_PATH = OUTPUT_DIR / "pipeline_momentum_results.csv"
REPORT_MD_PATH = OUTPUT_DIR / "pipeline_momentum_report.md"

SIGNALS = [
    "engagement_depth",
    "stakeholder_expansion",
    "internal_activity",
    "reciprocity",
    "organizational_energy",
]


def load_framework() -> Dict[str, Any]:
    with open(FRAMEWORK_PATH, "r", encoding="utf-8") as f:
        fw = json.load(f)
    return fw


def band_for_score(fw: Dict[str, Any], score: int) -> Dict[str, Any]:
    bands = fw["scoring_model"]["total_score_interpretation"]
    matches = [b for b in bands if b["min"] <= score <= b["max"]]
    if len(matches) != 1:
        raise ValueError(f"Score {score} matched {len(matches)} bands: {matches}")
    return matches[0]


def weakest_signals(deal_scores: Dict[str, int]) -> Tuple[List[str], int]:
    min_val = min(deal_scores[s] for s in SIGNALS)
    return [s for s in SIGNALS if deal_scores[s] == min_val], min_val


def parse_int(row: Dict[str, str], key: str) -> int:
    try:
        v = int(row[key])
    except Exception:
        raise ValueError(f"Missing or non-integer value for '{key}' in row: {row}")
    if v < 1 or v > 5:
        raise ValueError(f"Value for '{key}' must be 1-5. Got {v} in row: {row}")
    return v


def load_rows(path: Path) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"No rows found in {path.name}")

    return rows


def score_rows(rows: List[Dict[str, str]], fw: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for row in rows:
        deal_scores = {s: parse_int(row, s) for s in SIGNALS}
        total = sum(deal_scores.values())
        band = band_for_score(fw, total)
        weak, weak_val = weakest_signals(deal_scores)

        results.append(
            {
                "deal_id": row.get("deal_id", "").strip(),
                "deal_name": row.get("deal_name", "").strip(),
                "engagement_depth": deal_scores["engagement_depth"],
                "stakeholder_expansion": deal_scores["stakeholder_expansion"],
                "internal_activity": deal_scores["internal_activity"],
                "reciprocity": deal_scores["reciprocity"],
                "organizational_energy": deal_scores["organizational_energy"],
                "total_score": total,
                "band_id": band["id"],
                "band_label": band["label"],
                "weakest_signals": ", ".join(weak),
                "weakest_score": weak_val,
            }
        )

    return results


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_results_csv(results: List[Dict[str, Any]], out_path: Path) -> None:
    ensure_output_dir()

    fieldnames = list(results[0].keys())
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def build_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    band_counts = Counter(r["band_label"] for r in results)
    weakest_counts = Counter()

    for r in results:
        weakest_list = [s.strip() for s in str(r["weakest_signals"]).split(",") if s.strip()]
        weakest_counts.update(weakest_list)

    lowest_total = min(r["total_score"] for r in results)
    highest_total = max(r["total_score"] for r in results)

    return {
        "total_deals": len(results),
        "band_counts": band_counts,
        "weakest_counts": weakest_counts,
        "lowest_total": lowest_total,
        "highest_total": highest_total,
    }


def write_report_md(results: List[Dict[str, Any]], fw: Dict[str, Any], out_path: Path) -> None:
    ensure_output_dir()
    summary = build_summary(results)

    sorted_by_risk = sorted(results, key=lambda r: (r["total_score"], r["weakest_score"]))
    top_risks = sorted_by_risk[:5]

    lines: List[str] = []
    lines.append(f"# Pipeline Momentum Report\n")
    lines.append(f"Framework: **{fw.get('framework_name', 'pipeline-momentum')}**\n")
    lines.append(f"Deals analyzed: **{summary['total_deals']}**\n")
    lines.append(f"Score range: **{summary['lowest_total']} to {summary['highest_total']}**\n")

    lines.append("## Deals by band\n")
    for label, cnt in summary["band_counts"].most_common():
        lines.append(f"- {label}: {cnt}\n")

    lines.append("\n## Most common weakest signals\n")
    for signal, cnt in summary["weakest_counts"].most_common():
        lines.append(f"- {signal}: {cnt}\n")

    lines.append("\n## Top 5 at-risk deals (lowest total first)\n")
    for r in top_risks:
        lines.append(
            f"- **{r['deal_id']} | {r['deal_name']}**  "
            f"(Total {r['total_score']}, Band {r['band_label']}, Weakest {r['weakest_signals']}={r['weakest_score']})\n"
        )

    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def print_results(results: List[Dict[str, Any]], fw: Dict[str, Any]) -> None:
    print(fw.get("framework_name", "pipeline-momentum-framework"))
    print("\nResults:")

    for r in results:
        print("\n---")
        print(f"{r['deal_id']} | {r['deal_name']}")
        scores = {
            "engagement_depth": r["engagement_depth"],
            "stakeholder_expansion": r["stakeholder_expansion"],
            "internal_activity": r["internal_activity"],
            "reciprocity": r["reciprocity"],
            "organizational_energy": r["organizational_energy"],
        }
        print(f"Scores: {scores}  Total={r['total_score']}")
        print(f"Band: {r['band_label']} ({r['band_id']})")
        print(f"Weakest signal(s): {r['weakest_signals']} (score {r['weakest_score']})")


def main() -> None:
    fw = load_framework()
    rows = load_rows(DATA_PATH)
    results = score_rows(rows, fw)

    print_results(results, fw)

    write_results_csv(results, RESULTS_CSV_PATH)
    write_report_md(results, fw, REPORT_MD_PATH)

    print(f"\nWrote results CSV: {RESULTS_CSV_PATH}")
    print(f"Wrote report MD:   {REPORT_MD_PATH}")


if __name__ == "__main__":
    main()
