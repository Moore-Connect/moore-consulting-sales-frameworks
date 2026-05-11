import csv
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent

DEFAULT_IN = ROOT / "activities_input.csv"
DEFAULT_OUT = ROOT / "derived_deal_signals.csv"

SIGNALS = [
    "engagement_depth",
    "stakeholder_expansion",
    "internal_activity",
    "reciprocity",
    "organizational_energy",
]

EXTERNAL_TYPES = {"email", "call", "meeting"}
INTERNAL_TYPES = {"note", "task"}


from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Iterable

import pandas as pd


EXTERNAL_ACTIVITY_TYPES = {"email", "call", "meeting"}
INTERNAL_ACTIVITY_TYPES = {"task", "note"}  # still tracked, but should not drive "buyer momentum"

BUYER_OWNED_TASK_KEYWORDS = {
    # tasks that indicate buyer-side progress or gating steps
    "security questionnaire",
    "questionnaire",
    "msa",
    "redline",
    "redlines",
    "contract",
    "implementation",
    "timeline",
    "kickoff",
    "procurement",
    "legal",
}

BUYER_OWNED_NOTE_KEYWORDS = {
    "approved",
    "sign",
    "signed",
    "redline",
    "redlines",
    "security",
    "procurement",
    "budget",
    "buy-in",
    "committee",
    "timeline",
    "kickoff",
}


def _to_dt(series: pd.Series) -> pd.Series:
    # Your file is m/d/yyyy. Keep it flexible.
    return pd.to_datetime(series, errors="coerce", infer_datetime_format=True)


def _norm_email(x: str | float | None) -> Optional[str]:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip().lower()
    return s if s else None


def _is_internal_row(row: pd.Series) -> bool:
    # Treat rows with activity_direction == "internal" as internal,
    # and tasks/notes as internal by default.
    direction = str(row.get("activity_direction", "")).strip().lower()
    a_type = str(row.get("activity_type", "")).strip().lower()
    return direction == "internal" or a_type in INTERNAL_ACTIVITY_TYPES



def parse_date(s: str) -> datetime:
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: '{s}'")


def clamp_1_5(x: int) -> int:
    return max(1, min(5, x))


def score_engagement_depth(rows):
    # Weighted activity volume: meetings matter more than emails.
    weights = {"meeting": 3, "call": 2, "email": 1, "note": 1, "task": 1}
    total = 0
    for r in rows:
        t = (r.get("activity_type") or "").strip().lower()
        total += weights.get(t, 0)

    # Simple v1 thresholds.
    if total <= 2:
        return 1
    if total <= 4:
        return 2
    if total <= 7:
        return 3
    if total <= 11:
        return 4
    return 5


def score_stakeholder_expansion(df_deal: pd.DataFrame, as_of: pd.Timestamp, window_days: int = 45) -> int:
    df = df_deal.copy()
    df["activity_date_dt"] = _to_dt(df["activity_date"])
    df = df[df["activity_date_dt"].notna()]

    # external touches only, within window
    df["activity_type_l"] = df["activity_type"].astype(str).str.strip().str.lower()
    df["contact_email_n"] = df["contact_email"].apply(_norm_email)

    cutoff = as_of - pd.Timedelta(days=window_days)
    external = df[
        (df["activity_date_dt"] >= cutoff)
        & (df["activity_type_l"].isin(EXTERNAL_ACTIVITY_TYPES))
        & (df["contact_email_n"].notna())
    ]

    engaged = external["contact_email_n"].nunique()

    # Map engaged stakeholders -> score 1..5
    if engaged <= 1:
        return 1
    if engaged == 2:
        return 2
    if engaged == 3:
        return 3
    if 4 <= engaged <= 5:
        return 4
    return 5

def parse_contact_list(s: str):
    if not s:
        return set()
    # semicolon or comma separated
    parts = [p.strip().lower() for p in s.replace(",", ";").split(";")]
    return {p for p in parts if p and "@" in p}


def is_internal_row(r):
    t = (r.get("activity_type") or "").strip().lower()
    email = (r.get("contact_email") or "").strip()
    role = (r.get("contact_role") or "").strip().lower()

    if t in INTERNAL_TYPES:
        return True
    if role == "internal":
        return True
    if not email and t not in EXTERNAL_TYPES:
        return True
    return False


def is_task_row(r):
    return (r.get("activity_type") or "").strip().lower() == "task"


def task_is_completed(r):
    status = (r.get("task_status") or "").strip().lower()
    return status in {"completed", "done", "closed"}


def task_is_overdue(r, as_of: datetime):
    if not is_task_row(r):
        return False
    if task_is_completed(r):
        return False
    due = (r.get("task_due_date") or "").strip()
    if not due:
        return False
    try:
        due_dt = parse_date(due)
    except ValueError:
        return False
    return due_dt < as_of


def score_internal_activity(df_deal: pd.DataFrame, as_of: pd.Timestamp, window_days: int = 45) -> int:
    df = df_deal.copy()
    df["activity_date_dt"] = _to_dt(df["activity_date"])
    df = df[df["activity_date_dt"].notna()]
    cutoff = as_of - pd.Timedelta(days=window_days)
    df = df[df["activity_date_dt"] >= cutoff]

    df["activity_type_l"] = df["activity_type"].astype(str).str.strip().str.lower()
    df["direction_l"] = df.get("activity_direction", "").astype(str).str.strip().str.lower()

    internal = df[(df["direction_l"] == "internal") | (df["activity_type_l"].isin({"task", "note"}))]

    # Completed internal tasks count more than open tasks
    task_status = internal.get("task_status", pd.Series(index=internal.index, dtype=str)).fillna("").astype(str).str.lower()
    completed = int((internal["activity_type_l"].eq("task") & task_status.eq("completed")).sum())
    open_tasks = int((internal["activity_type_l"].eq("task") & task_status.eq("open")).sum())
    notes = int(internal["activity_type_l"].eq("note").sum())

    raw = completed * 2 + open_tasks + notes

    # Convert raw -> 1..5 but CAP at 3 to avoid internal inflation
    if raw <= 0:
        score = 1
    elif raw <= 2:
        score = 2
    else:
        score = 3

    return score

def _days_since_last_external_touch(df_deal: pd.DataFrame, as_of: pd.Timestamp) -> Optional[int]:
    df = df_deal.copy()
    df["activity_date_dt"] = _to_dt(df["activity_date"])
    df = df[df["activity_date_dt"].notna()]
    df["activity_type_l"] = df["activity_type"].astype(str).str.strip().str.lower()

    external = df[df["activity_type_l"].isin(EXTERNAL_ACTIVITY_TYPES)]
    if external.empty:
        return None
    last_dt = external["activity_date_dt"].max()
    return int((as_of - last_dt).days)


def apply_time_decay(score: int, days_since: Optional[int]) -> int:
    if days_since is None:
        return max(1, score - 2)
    if days_since > 45:
        return max(1, score - 2)
    if days_since > 30:
        return max(1, score - 1)
    return score


def score_reciprocity(df_deal: pd.DataFrame, as_of: pd.Timestamp, window_days: int = 45) -> int:
    df = df_deal.copy()
    df["activity_date_dt"] = _to_dt(df["activity_date"])
    df = df[df["activity_date_dt"].notna()]
    cutoff = as_of - pd.Timedelta(days=window_days)
    df = df[df["activity_date_dt"] >= cutoff]

    a_type = df["activity_type"].astype(str).str.strip().str.lower()

    # Buyer-owned progress evidence
    task_mask = a_type.eq("task") & df.get("task_status", pd.Series(index=df.index, dtype=str)).astype(str).str.lower().eq("completed")
    note_mask = a_type.eq("note")

    note_text = df.get("note_body", pd.Series(index=df.index, dtype=str)).fillna("").astype(str).str.lower()
    task_text = df.get("note_body", pd.Series(index=df.index, dtype=str)).fillna("").astype(str).str.lower()

    buyer_task_hits = task_mask & task_text.apply(lambda t: any(k in t for k in BUYER_OWNED_TASK_KEYWORDS))
    buyer_note_hits = note_mask & note_text.apply(lambda t: any(k in t for k in BUYER_OWNED_NOTE_KEYWORDS))

    buyer_actions = int(buyer_task_hits.sum() + buyer_note_hits.sum())

    # Also count scheduled external meetings/calls as mild reciprocity (they showed up)
    external_meetings = int(a_type.isin({"meeting", "call"}).sum())

    signal = buyer_actions + (1 if external_meetings >= 1 else 0)

    if signal <= 0:
        return 1
    if signal == 1:
        return 2
    if signal == 2:
        return 3
    if signal == 3:
        return 4
    return 5

def score_organizational_energy(rows, global_max_date: datetime):
    dates = []
    for r in rows:
        try:
            dates.append(parse_date(r["activity_date"]))
        except Exception:
            continue

    if not dates:
        return 1

    last = max(dates)
    first = min(dates)
    days_since_last = (global_max_date - last).days
    span = max(1, (last - first).days)

    # Recency-based score (primary)
    if days_since_last <= 3:
        score = 5
    elif days_since_last <= 7:
        score = 4
    elif days_since_last <= 14:
        score = 3
    elif days_since_last <= 30:
        score = 2
    else:
        score = 1

    # Cadence adjustment (secondary)
    touches = len(rows)
    touches_per_week = touches / (span / 7)
    if touches_per_week < 0.5 and score > 1:
        score -= 1

    return clamp_1_5(score)

def _split_emails(s: str) -> set[str]:
    if not s:
        return set()
    # supports "a@x.com;b@y.com" or "a@x.com, b@y.com"
    parts = [p.strip().lower() for p in str(s).replace(",", ";").split(";")]
    return {p for p in parts if p and "@" in p}


def score_stakeholder_expansion_coverage(deal_df):
    """
    Stakeholder expansion based on engaged committee coverage.

    expected committee = distinct emails in associated_contacts (union across rows)
    engaged committee  = distinct contact_email on external activities
    """
    # expected
    expected = set()
    if "associated_contacts" in deal_df.columns:
        for v in deal_df["associated_contacts"].dropna().tolist():
            expected |= _split_emails(v)

    # engaged (external only)
    engaged = set()
    if "contact_email" in deal_df.columns:
        ext = deal_df[deal_df["activity_type"].isin(EXTERNAL_TYPES)].copy()
        for v in ext["contact_email"].dropna().tolist():
            vv = str(v).strip().lower()
            if vv and "@" in vv:
                engaged.add(vv)

    expected_n = len(expected)
    engaged_n = len(engaged)

    if expected_n == 0:
        # no committee listed, fall back to old behavior: engaged count
        # (still better than guessing)
        n = engaged_n
        if n <= 1:
            return 1
        if n == 2:
            return 2
        if n == 3:
            return 3
        if n == 4:
            return 4
        return 5

    coverage = min(1.0, engaged_n / expected_n)

    # coverage -> 1..5
    if coverage < 0.25:
        return 1
    if coverage < 0.50:
        return 2
    if coverage < 0.75:
        return 3
    if coverage < 1.00:
        return 4
    return 5


def main():
    ap = argparse.ArgumentParser(description="Generate Pipeline Momentum signals from activity-level exports.")
    ap.add_argument("--input", default=str(DEFAULT_IN), help="Path to activities_input.csv")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Path to write derived deal-level signals CSV")
    ap.add_argument(
        "--overwrite-test-deals",
        action="store_true",
        help="Also overwrite test_deals.csv with derived results (so run_pipeline_momentum.py can run unchanged).",
    )
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)

    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    # Load activity rows
    rows = []
    with open(in_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        required = {"deal_id", "deal_name", "activity_type", "activity_date"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns in {in_path.name}: {sorted(missing)}")

        for r in reader:
            if not (r.get("deal_id") and r.get("activity_date")):
                continue
            rows.append(r)

    if not rows:
        raise ValueError("No activity rows found after parsing.")

    # Global max date for recency scoring
    global_max = max(parse_date(r["activity_date"]) for r in rows)

    by_deal = defaultdict(list)
    deal_name_by_id = {}
    for r in rows:
        did = (r.get("deal_id") or "").strip()
        if not did:
            continue
        by_deal[did].append(r)
        if did not in deal_name_by_id:
            deal_name_by_id[did] = (r.get("deal_name") or "").strip()

    # Compute signals per deal
    derived = []
    as_of = pd.Timestamp(global_max)

    for did, deal_rows in sorted(by_deal.items()):
        dname = deal_name_by_id.get(did, "") or did

        # convert rows -> DataFrame once
        df_deal = pd.DataFrame(deal_rows)

        # base scores
        engagement_depth = score_engagement_depth(deal_rows)
        organizational_energy = score_organizational_energy(deal_rows, global_max)

        # corrected signals
        stakeholder_expansion = score_stakeholder_expansion_coverage(df_deal)

        reciprocity = score_reciprocity(df_deal, as_of)
        internal_activity = score_internal_activity(df_deal, as_of)

        # time decay
        days_since = _days_since_last_external_touch(df_deal, as_of)
        engagement_depth = apply_time_decay(engagement_depth, days_since)
        organizational_energy = apply_time_decay(organizational_energy, days_since)

        scores = {
            "engagement_depth": engagement_depth,
            "stakeholder_expansion": stakeholder_expansion,
            "internal_activity": internal_activity,
            "reciprocity": reciprocity,
            "organizational_energy": organizational_energy,
        }

        derived.append({"deal_id": did, "deal_name": dname, **scores})

    # Write deal-level file
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["deal_id", "deal_name", *SIGNALS])
        writer.writeheader()
        writer.writerows(derived)

    print(f"Wrote derived deal signals: {out_path}")

    if args.overwrite_test_deals:
        td = ROOT / "test_deals.csv"
        with open(td, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["deal_id", "deal_name", *SIGNALS])
            writer.writeheader()
            writer.writerows(derived)
        print(f"Overwrote test_deals.csv: {td}")


if __name__ == "__main__":
    main()
