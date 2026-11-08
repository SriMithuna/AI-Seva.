"""Health & Wellness SLPS, adapted to AI Seva's shared application records."""

from datetime import date

from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .schemes import HEALTH_ITEMS_BY_CODE, HEALTH_SLPS_CODES


WEIGHTS = {
    "category": 0.25,
    "urgency": 0.20,
    "waiting": 0.15,
    "docs": 0.10,
    "income": 0.10,
    "dependents": 0.07,
    "prev_benefit": 0.05,
    "gender": 0.03,
    "age": 0.03,
    "background": 0.02,
}

CATEGORY_SCORES = {
    "disabled": 100,
    "widow": 100,
    "orphan": 100,
    "destitute": 100,
    "sc_st": 80,
    "eligible": 50,
    "general": 20,
}


def income_score(income):
    income = float(income)
    if income < 100_000:
        return 100
    if income < 250_000:
        return 70
    if income < 500_000:
        return 40
    return 10


def dependents_score(number):
    number = int(number)
    if number >= 5:
        return 100
    if number >= 3:
        return 70
    if number >= 1:
        return 40
    return 10


def waiting_score(submitted_at, decided_at, target_days, now=None):
    end_date = decided_at or now or timezone.now()
    days_waited = max(0, (end_date - submitted_at).days)
    return round(min(days_waited / target_days, 1) * 100, 2)


def document_score(uploaded, required):
    if required <= 0:
        return 0
    return min(uploaded / required, 1) * 100


def age_from_dob(birth_date, today=None):
    if not birth_date:
        return None
    today = today or timezone.localdate()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def is_health_application(application):
    if not application.scheme_id or application.scheme.department.code != "HLT":
        return False
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    try:
        return _item_code(application, extra) in HEALTH_SLPS_CODES
    except ValueError:
        return False


def _item_code(application, extra):
    code = str(extra.get("health_item_code") or "").upper()
    if code in HEALTH_ITEMS_BY_CODE:
        return code
    for item_code, item in HEALTH_ITEMS_BY_CODE.items():
        if item["name"] == application.scheme.name:
            return item_code
    raise ValueError(f"Unknown Health scheme/service: {application.scheme.name}")


def build_health_inputs(application, now=None):
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    item_code = _item_code(application, extra)
    item = HEALTH_ITEMS_BY_CODE[item_code]
    docs_required = extra.get("health_docs_required")
    if docs_required is None:
        docs_required = len([
            line for line in (application.scheme.required_documents or "").splitlines()
            if line.strip()
        ])
    docs_required = max(0, int(docs_required))
    documents = list(application.documents.all())
    decided_at = parse_datetime(str(extra.get("health_decided_at", "")))
    if decided_at is None and application.status in {"Approved", "Rejected"}:
        remark = application.remarks.filter(
            status__in=["Approved", "Rejected"]
        ).order_by("-created_at").first()
        if remark:
            decided_at = remark.created_at

    gender = str(application.gender or "").upper()
    return {
        "item_code": item_code,
        "item": item,
        "category": str(extra.get("category") or "general").lower(),
        "is_urgent": bool(extra.get("is_urgent")),
        "urgency_verified": bool(extra.get("urgency_verified")),
        "submitted_at": application.created_at or now or timezone.now(),
        "decided_at": decided_at,
        "docs_uploaded": len(documents),
        "docs_required": docs_required,
        "income": extra.get("income"),
        "dependents": extra.get("dependents", 0),
        "has_prior_benefit": bool(extra.get("has_prior_benefit")),
        "gender": "F" if gender in {"F", "FEMALE"} else gender,
        "age": age_from_dob(application.date_of_birth),
        "is_rural": str(extra.get("is_rural", "no")).lower() in {"yes", "true", "1"},
    }


def calculate_health_slps(application, now=None):
    """Return score, factor breakdown and priority using the supplied Health SLPS."""
    now = now or timezone.now()
    data = build_health_inputs(application, now=now)
    docs_uploaded = data["docs_uploaded"]
    docs_required = data["docs_required"]
    if docs_uploaded < docs_required:
        return None, {
            "docs": document_score(docs_uploaded, docs_required),
            "docs_uploaded": docs_uploaded,
            "docs_required": docs_required,
            "readiness": "Documents Pending",
        }, "Documents Pending"

    item = data["item"]
    if not item.get("slps_enabled"):
        raise ValueError(f"SLPS is not used for {item['name']}")
    waiting = waiting_score(
        data["submitted_at"],
        data["decided_at"],
        item["target_days"],
        now=now,
    )
    scores = {
        "category": CATEGORY_SCORES.get(data["category"], 20),
        "urgency": 100 if data["is_urgent"] and data["urgency_verified"] else 0,
        "waiting": waiting,
        "docs": document_score(docs_uploaded, docs_required),
        "income": income_score(data["income"]),
        "dependents": dependents_score(data["dependents"]),
        "prev_benefit": 30 if data["has_prior_benefit"] else 100,
        "gender": 100 if data["gender"] == "F" else 50,
        "age": 100 if data["age"] is not None and data["age"] >= 60 else 30,
        "background": 100 if data["is_rural"] else 40,
    }
    applicant_score = sum(scores[factor] * weight for factor, weight in WEIGHTS.items())
    score = round(min(applicant_score * item["weight"], 100), 2)
    if score >= 80:
        priority = "Critical"
    elif score >= 60:
        priority = "High"
    elif score >= 40:
        priority = "Medium"
    else:
        priority = "Low"
    scores["docs_uploaded"] = docs_uploaded
    scores["docs_required"] = docs_required
    return score, scores, priority


def refresh_health_slps(application, save=True, now=None):
    score, factors, priority = calculate_health_slps(application, now=now)
    if save:
        extra = application.extra_data if isinstance(application.extra_data, dict) else {}
        extra["health_slps_factors"] = factors
        extra["health_slps_priority"] = priority
        extra["health_item_code"] = _item_code(application, extra)
        application.extra_data = extra
        application.slps_score = score or 0
        application.priority = priority
        application.save(update_fields=["slps_score", "priority", "extra_data"])
    return score, factors, priority
