"""Proposed officer-side Housing & Rural Development SLPS."""

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .schemes import HOUSING_ITEMS_BY_CODE, HOUSING_SLPS_CODES

# These score mappings fill in details not specified in the proposal and must
# be calibrated with officers. They are project assumptions, not government rules.
INCOME_SCORE_BANDS = (
    (100_000, 100),
    (250_000, 80),
    (500_000, 60),
    (1_000_000, 30),
    (None, 0),
)
DEPENDENT_SCORE_PER_PERSON = 25
WAITING_DAYS_TO_MAX_SCORE = 30

WEIGHTS = {
    "vulnerability": 0.30,
    "income": 0.20,
    "family_dependency": 0.15,
    "urgency": 0.15,
    "waiting_time": 0.15,
    "document_verification": 0.05,
}


def is_housing_application(application):
    if not application.scheme_id or application.scheme.department.code != "HRD":
        return False
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    return str(extra.get("housing_item_code") or "") in HOUSING_ITEMS_BY_CODE


def income_score(annual_income):
    if annual_income in (None, ""):
        return 0
    amount = max(0, int(annual_income))
    for ceiling, score in INCOME_SCORE_BANDS:
        if ceiling is None or amount <= ceiling:
            return score
    return 0


def waiting_time_score(created_at, decided_at=None, now=None):
    end_time = decided_at or now or timezone.now()
    days_waited = max(0, (end_time - created_at).days)
    return round(min(days_waited / WAITING_DAYS_TO_MAX_SCORE, 1) * 100, 2)


def document_verification_score(application):
    documents = list(application.documents.all())
    if not documents:
        return 0, 0, 0
    verified = sum(bool(document.is_verified) for document in documents)
    return round(verified / len(documents) * 100, 2), verified, len(documents)


def build_housing_inputs(application, now=None):
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    code = str(extra.get("housing_item_code") or "")
    item = HOUSING_ITEMS_BY_CODE.get(code)
    docs_score, docs_verified, docs_submitted = document_verification_score(application)
    vulnerability = str(extra.get("vulnerability") or "none").lower()
    decided_at = parse_datetime(str(extra.get("housing_decided_at") or ""))
    if decided_at is None and application.status in {"Approved", "Rejected"}:
        remark = application.remarks.filter(
            status__in=["Approved", "Rejected"]
        ).order_by("-created_at").first()
        if remark:
            decided_at = remark.created_at
    return {
        "item_code": code,
        "item": item,
        "eligibility_verified": bool(extra.get("housing_eligibility_verified")),
        "eligible": bool(extra.get("housing_eligible")),
        "income": extra.get("annual_income"),
        "dependents": max(0, int(extra.get("dependents") or 0)),
        "vulnerability": vulnerability,
        "vulnerability_verified": bool(extra.get("vulnerability_verified")),
        "housing_condition": str(extra.get("housing_condition") or "").lower(),
        "livelihood_hardship": bool(extra.get("livelihood_hardship")),
        "is_urgent": bool(extra.get("is_urgent")),
        "urgency_verified": bool(extra.get("urgency_verified")),
        "waiting_time": waiting_time_score(application.created_at, decided_at=decided_at, now=now),
        "document_score": docs_score,
        "documents_verified": docs_verified,
        "documents_submitted": docs_submitted,
    }


def calculate_housing_slps(application, now=None):
    """Return the score, factor breakdown and label for a housing application."""
    if not is_housing_application(application):
        return None, {}, "Not scored"
    data = build_housing_inputs(application, now=now)
    item = data["item"]
    if not item.get("slps_enabled"):
        return None, {"scheme": item["name"], "scoring": "Status enquiry excluded from normal SLPS"}, "Not scored"
    if not data["eligibility_verified"]:
        return None, {"eligibility": "Awaiting officer verification"}, "Pending verification"
    if not data["eligible"]:
        return None, {"eligibility": "Officer marked not eligible"}, "Not scored"

    vulnerability_score = 0
    if data["vulnerability_verified"]:
        if data["vulnerability"] != "none":
            vulnerability_score = 100
        if data["housing_condition"] in {"unsafe", "disaster_damage"}:
            vulnerability_score = max(vulnerability_score, 100)
        elif data["housing_condition"] == "repair":
            vulnerability_score = max(vulnerability_score, 70)
        if data["livelihood_hardship"]:
            vulnerability_score = max(vulnerability_score, 70)
    family_score = min(data["dependents"] * DEPENDENT_SCORE_PER_PERSON, 100)
    urgency_score = 100 if data["is_urgent"] and data["urgency_verified"] else 0
    factor_scores = {
        "vulnerability": vulnerability_score,
        "income": income_score(data["income"]),
        "family_dependency": family_score,
        "urgency": urgency_score,
        "waiting_time": data["waiting_time"],
        "document_verification": data["document_score"],
    }
    base_score = sum(factor_scores[name] * WEIGHTS[name] for name in WEIGHTS)
    multiplier = float(item["importance_multiplier"])
    score = round(min(base_score * multiplier, 100), 2)
    if score >= 90:
        priority = "Critical"
    elif score >= 75:
        priority = "High"
    elif score >= 50:
        priority = "Medium"
    else:
        priority = "Low"
    breakdown = {
        **factor_scores,
        "weights": WEIGHTS,
        "base_score": round(base_score, 2),
        "scheme_multiplier": multiplier,
        "scheme": item["name"],
        "final_score": score,
        "documents_verified": data["documents_verified"],
        "documents_submitted": data["documents_submitted"],
        "urgency_requested": data["is_urgent"],
        "urgency_verified": data["urgency_verified"],
        "vulnerability_verified": data["vulnerability_verified"],
        "configuration_note": (
            "Income bands, dependent scaling, waiting-time cap, scheme-specific vulnerability "
            "mapping and Critical/High split are proposed project settings and require officer calibration."
        ),
    }
    return score, breakdown, priority


def refresh_housing_slps(application, save=True, now=None):
    score, factors, priority = calculate_housing_slps(application, now=now)
    if save and is_housing_application(application):
        extra = application.extra_data if isinstance(application.extra_data, dict) else {}
        extra["housing_slps_factors"] = factors
        extra["housing_slps_priority"] = priority
        application.extra_data = extra
        application.slps_score = score or 0
        application.priority = (
            "Documents Pending" if priority == "Pending verification" else
            priority if priority in {"Critical", "High", "Medium", "Low"} else "Low"
        )
        application.save(update_fields=["slps_score", "priority", "extra_data"])
    return score, factors, priority
