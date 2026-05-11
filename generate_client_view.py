import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent

DEFAULT_RESULTS = ROOT / "output" / "pipeline_momentum_results.csv"
DEFAULT_SIGNALS = ROOT / "derived_deal_signals.csv"
DEFAULT_ACTIVITIES = ROOT / "activities_input.csv"
DEFAULT_OUT = ROOT / "output" / "pipeline_momentum_client_view.csv"

EXTERNAL_TYPES = {"email", "call", "meeting"}


def to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")


def compute_recency_and_touch_counts(activities: pd.DataFrame) -> pd.DataFrame:
    df = activities.copy()
    df["deal_id"] = df["deal_id"].astype(str).str.strip()
    df["activity_type"] = df["activity_type"].astype(str).str.strip().str.lower()
    df["activity_date_dt"] = to_dt(df["activity_date"])
    df = df[df["activity_date_dt"].notna()]

    # external touch definition
    ext = df[df["activity_type"].isin(EXTERNAL_TYPES)].copy()

    # If no external touches, return empty frame with expected columns
    if ext.empty:
        return pd.DataFrame(
            columns=["deal_id", "external_touches_45d", "days_since_last_external_touch", "as_of_dt"]
        )

    # last external touch per deal
    last_touch = (
        ext.groupby("deal_id", as_index=False)["activity_date_dt"]
        .max()
        .rename(columns={"activity_date_dt": "last_external_touch_dt"})
    )

    # count external touches in last 45 days relative to max date in file
    as_of = ext["activity_date_dt"].max()
    cutoff = as_of - pd.Timedelta(days=45)
    recent = ext[ext["activity_date_dt"] >= cutoff]

    touch_ct = (
        recent.groupby("deal_id", as_index=False)
        .size()
        .rename(columns={"size": "external_touches_45d"})
    )

    # merge + compute days since
    out = last_touch.merge(touch_ct, on="deal_id", how="left")
    out["external_touches_45d"] = out["external_touches_45d"].fillna(0).astype(int)
    out["days_since_last_external_touch"] = (as_of - out["last_external_touch_dt"]).dt.days.astype(int)
    out["as_of_dt"] = as_of

    return out[["deal_id", "external_touches_45d", "days_since_last_external_touch", "as_of_dt"]]

def extract_role_map_from_activities(activities: pd.DataFrame) -> dict:
    """
    Build email -> role mapping from activities rows where both are present.
    """
    df = activities.copy()
    df["contact_email"] = df.get("contact_email", "").astype(str).str.strip().str.lower()
    df["contact_role"] = df.get("contact_role", "").astype(str).str.strip().str.lower()
    df = df[(df["contact_email"] != "") & (df["contact_role"] != "")]
    # If the same email appears with different roles, keep the first non-empty occurrence
    return dict(df.drop_duplicates(subset=["contact_email"])[["contact_email", "contact_role"]].values)


def compute_roles_coverage(activities: pd.DataFrame) -> pd.DataFrame:
    """
    For each deal_id, compute roles_engaged + roles_engaged_count using:
    - contact_email/contact_role on the row
    - associated_contacts emails mapped to roles via extract_role_map_from_activities
    """
    df = activities.copy()
    df["deal_id"] = df["deal_id"].astype(str).str.strip()
    df["contact_email"] = df.get("contact_email", "").astype(str).str.strip().str.lower()
    df["contact_role"] = df.get("contact_role", "").astype(str).str.strip().str.lower()
    df["associated_contacts"] = df.get("associated_contacts", "").astype(str)

    email_to_role = extract_role_map_from_activities(df)

    def roles_from_row(r) -> set:
        roles = set()
        if r["contact_role"]:
            roles.add(r["contact_role"])
        assoc = [e.strip().lower() for e in r["associated_contacts"].split(";") if e.strip()]
        for e in assoc:
            role = email_to_role.get(e)
            if role:
                roles.add(role)
        return roles

    df["roles_set"] = df.apply(roles_from_row, axis=1)

    agg = df.groupby("deal_id")["roles_set"].apply(lambda sets: sorted(set().union(*sets) if len(sets) else set()))
    out = agg.reset_index().rename(columns={"roles_set": "roles_engaged_list"})
    out["roles_engaged"] = out["roles_engaged_list"].apply(lambda xs: " | ".join(xs) if xs else "")
    out["roles_engaged_count"] = out["roles_engaged_list"].apply(lambda xs: len(xs))
    return out[["deal_id", "roles_engaged", "roles_engaged_count"]]


def map_momentum_status(band_id: str) -> str:
    m = {
        "strong_positive": "Strong",
        "conditional": "Conditional",
        "at_risk": "At Risk",
        "stalled": "Stalled",
    }
    return m.get(str(band_id).strip().lower(), "Conditional")


def map_confidence(external_touches_45d: int, days_since: int) -> str:
    if external_touches_45d >= 3 and days_since <= 14:
        return "High"
    if external_touches_45d >= 2 and days_since <= 30:
        return "Medium"
    return "Low"


def build_explanations(row: pd.Series) -> dict:
    status = row["momentum_status"]
    weakest = str(row.get("weakest_signals", "")).strip().lower()
    weakest_set = {w.strip() for w in weakest.split(",") if w.strip()} if weakest else set()

    stakeholder = int(row.get("stakeholder_expansion", 0))
    reciprocity = int(row.get("reciprocity", 0))
    energy = int(row.get("organizational_energy", 0))

    if status == "Stalled":
        return {
            "primary_risk": "Stalled opportunity",
            "what_it_means": "There is no active engagement or buyer movement.",
            "recommended_focus": "Close out or recycle",
            "next_best_actions": "Send a final close-the-loop note | Move to nurture with a clear trigger",
            "buyer_commitment_needed": "Clear yes or no",
            "watchouts": "Zombie deals inflate pipeline and distract the team",
        }

    if "stakeholder_expansion" in weakest_set and stakeholder <= 2:
        if "reciprocity" in weakest_set and reciprocity <= 2:
            return {
                "primary_risk": "Limited buying-committee traction",
                "what_it_means": "Engagement is narrow and the buyer is not taking actions that advance a decision.",
                "recommended_focus": "Get commitment and expand stakeholders",
                "next_best_actions": "Ask for 1 additional stakeholder + a dated next step | Introduce a simple Mutual Action Plan",
                "buyer_commitment_needed": "Intro plus dated buyer-owned action",
                "watchouts": "Avoid free work without buyer-owned steps",
            }

        if energy >= 4:
            return {
                "primary_risk": "Bottlenecked to one lane",
                "what_it_means": "There is urgency, but traction is concentrated in a narrow set of stakeholders.",
                "recommended_focus": "Broaden approval coverage",
                "next_best_actions": "Confirm approval path (budget, risk, legal) | Add the next gatekeeper to the next meeting",
                "buyer_commitment_needed": "Stakeholder intro aligned to approval step",
                "watchouts": "Do not assume a single champion can carry approval",
            }

        return {
            "primary_risk": "Narrow stakeholder coverage" if status == "Strong" else "Single-threaded risk",
            "what_it_means": "The deal has not expanded across the roles that typically influence approval.",
            "recommended_focus": "Multi-thread the deal",
            "next_best_actions": "Ask champion to bring 1 additional stakeholder | Confirm who signs off on budget and timeline",
            "buyer_commitment_needed": "Intro to one additional decision-influencer",
            "watchouts": "Do not advance without broader buyer involvement",
        }

    if ("reciprocity" in weakest_set) and reciprocity <= 2:
        return {
            "primary_risk": "Low buyer reciprocity",
            "what_it_means": (
                "The buyer is not matching effort with actions like follow-ups, "
                "sharing internal context, or committing time."
            ),
            "recommended_focus": "Create a clear give-to-get moment",
            "next_best_actions": (
                "Ask for a concrete next step tied to value | "
                "Confirm decision criteria and timeline explicitly"
            ),
            "buyer_commitment_needed": "Explicit next-step commitment",
            "watchouts": "High risk of demo-only or tire-kicker behavior",
        }

    if "organizational_energy" in weakest_set and energy <= 2:
        return {
            "primary_risk": "Low urgency",
            "what_it_means": "There is no forcing event driving a decision timeline.",
            "recommended_focus": "Surface or create urgency",
            "next_best_actions": "Quantify cost of delay | Align on a decision date",
            "buyer_commitment_needed": "Decision date or explicit deprioritization",
            "watchouts": "Long gaps between interactions create silent stalls",
        }

    return {
        "primary_risk": "Execution risk",
        "what_it_means": "Momentum exists, but the next decision step is not fully secured.",
        "recommended_focus": "Confirm decision path",
        "next_best_actions": "Confirm decision criteria | Confirm evaluation owner | Align on next meeting purpose",
        "buyer_commitment_needed": "Dated next step",
        "watchouts": "",
    }


def _pick_col(df: pd.DataFrame, *candidates: str) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(DEFAULT_RESULTS))
    ap.add_argument("--signals", default=str(DEFAULT_SIGNALS))
    ap.add_argument("--activities", default=str(DEFAULT_ACTIVITIES))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    results = pd.read_csv(args.results, dtype=str).fillna("")
    signals = pd.read_csv(args.signals, dtype=str).fillna("")
    activities = pd.read_csv(args.activities, dtype=str).fillna("")

    # Normalize keys for merges
    for df_ in (results, signals, activities):
        if "deal_id" in df_.columns:
            df_["deal_id"] = df_["deal_id"].astype(str).str.strip()
        if "deal_name" in df_.columns:
            df_["deal_name"] = df_["deal_name"].astype(str).str.strip()

    # numeric conversions in signals (if present)
    for col in [
        "engagement_depth",
        "stakeholder_expansion",
        "internal_activity",
        "reciprocity",
        "organizational_energy",
    ]:
        if col in signals.columns:
            signals[col] = pd.to_numeric(signals[col], errors="coerce").fillna(0).astype(int)

    if "total_score" in results.columns:
        results["total_score"] = pd.to_numeric(results["total_score"], errors="coerce").fillna(0).astype(int)
    else:
        results["total_score"] = 0

    recency = compute_recency_and_touch_counts(activities)
    roles_cov = compute_roles_coverage(activities)


    df = (
        results.merge(
            signals,
            on=["deal_id", "deal_name"],
            how="left",
            suffixes=("_res", "_sig"),
        )
        .merge(recency, on="deal_id", how="left")
        .merge(roles_cov, on="deal_id", how="left")
    )
   
    df["roles_engaged"] = df.get("roles_engaged", "").fillna("")
    df["roles_engaged_count"] = pd.to_numeric(
        df.get("roles_engaged_count", 0), errors="coerce"
    ).fillna(0).astype(int)



    # Normalize signal columns so downstream logic can always rely on base names
    for base in ["stakeholder_expansion", "reciprocity", "organizational_energy", "engagement_depth", "internal_activity"]:
        c = _pick_col(df, f"{base}_sig", base, f"{base}_res")
        if c is None:
            df[base] = 0
        else:
            df[base] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    # Recency defaults
    if "external_touches_45d" in df.columns:
        df["external_touches_45d"] = pd.to_numeric(df["external_touches_45d"], errors="coerce").fillna(0).astype(int)
    else:
        df["external_touches_45d"] = 0

    if "days_since_last_external_touch" in df.columns:
        df["days_since_last_external_touch"] = (
            pd.to_numeric(df["days_since_last_external_touch"], errors="coerce").fillna(9999).astype(int)
        )
    else:
        df["days_since_last_external_touch"] = 9999

    # Derived labels
    df["momentum_status"] = df["band_id"].apply(map_momentum_status) if "band_id" in df.columns else "Conditional"
    df["confidence"] = df.apply(
        lambda r: map_confidence(int(r["external_touches_45d"]), int(r["days_since_last_external_touch"])),
        axis=1,
    )

    explanations = df.apply(build_explanations, axis=1, result_type="expand")
    df = pd.concat([df, explanations], axis=1)

    df["signal_summary"] = df.apply(
        lambda r: f"Stakeholders:{int(r.get('stakeholder_expansion', 0))} | "
                  f"Reciprocity:{int(r.get('reciprocity', 0))} | "
                  f"Energy:{int(r.get('organizational_energy', 0))}",
        axis=1,
    )

    out_cols = [
        "deal_id",
        "deal_name",
        "momentum_status",
        "confidence",
        "primary_risk",
        "what_it_means",
        "recommended_focus",
        "next_best_actions",
        "buyer_commitment_needed",
        "watchouts",
        "signal_summary",
        "total_score",
        "weakest_signals",
    ]

    # Make sure weakest_signals exists even if upstream changes
    if "weakest_signals" not in df.columns:
        df["weakest_signals"] = ""

    out = df[out_cols].copy()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    print(f"Wrote client view CSV: {out_path}")


if __name__ == "__main__":
    main()
