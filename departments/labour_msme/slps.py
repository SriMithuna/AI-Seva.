"""Seven-factor SLPS for Labour, Skill & MSME applications."""

from django.utils import timezone

from .schemes import LABOUR_ITEMS_BY_CODE

WEIGHTS = {
    "economic_vulnerability": 25,
    "livelihood_urgency": 25,
    "waiting_time": 20,
    "worker_vulnerability": 15,
    "family_dependents": 8,
    "support_gap": 5,
    "time_sensitivity": 2,
}

INCOME_CUTOFFS = ((100_000, 100), (250_000, 80), (500_000, 60), (800_000, 40), (None, 20))
BUSINESS_IMPACT_SCORES = {"severe": 100, "major": 80, "significant": 60, "manageable": 40, "limited": 20}
LIVELIHOOD_SCORES = {"lost": 100, "reduced": 80, "unemployed": 60, "underemployed": 40, "stable": 20}
VULNERABILITY_SCORES = {"multiple": 100, "barriers": 80, "other": 60, "none": 40}
SUPPORT_SCORES = {"very_high": 100, "moderate": 70, "low": 40, "none": 0}
DEADLINE_SCORES = {"7": 100, "15": 70, "30": 40, "none": 0}


def is_labour_application(application):
    if not application.scheme_id or application.scheme.department.code != "LSM":
        return False
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    return str(extra.get("labour_item_code") or "") in LABOUR_ITEMS_BY_CODE


def income_score(income):
    amount = max(0, int(income or 0))
    for ceiling, score in INCOME_CUTOFFS:
        if ceiling is None or amount <= ceiling:
            return score
    return 20


def calculate_labour_slps(application, now=None):
    if not is_labour_application(application):
        return None, {}, "Not scored"
    now = now or timezone.now()
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    days_waiting = max(0, (now - application.created_at).days)
    vulnerability = extra.get("worker_vulnerability", "none")
    vulnerability_score = VULNERABILITY_SCORES.get(vulnerability, 40)
    # A multiple-vulnerability score of 100 requires officer verification.
    if vulnerability == "multiple" and not extra.get("worker_vulnerability_verified"):
        vulnerability_score = 80
    economic_score = (
        BUSINESS_IMPACT_SCORES.get(extra.get("economic_impact"), 20)
        if extra.get("labour_item_code") == "MSME-DELAYED-PAYMENT"
        else income_score(extra.get("annual_income"))
    )
    factors = {
        "economic_vulnerability": economic_score,
        "livelihood_urgency": LIVELIHOOD_SCORES.get(extra.get("livelihood_situation"), 20),
        "waiting_time": round(min(days_waiting / 45, 1) * 100, 2),
        "worker_vulnerability": vulnerability_score,
        "family_dependents": round(min(max(0, int(extra.get("dependents") or 0)) / 4, 1) * 100, 2),
        "support_gap": SUPPORT_SCORES.get(extra.get("support_gap"), 0),
        "time_sensitivity": DEADLINE_SCORES.get(extra.get("deadline_window"), 0),
    }
    score = round(sum(factors[name] * weight for name, weight in WEIGHTS.items()) / 100, 2)
    priority = "Critical" if score >= 85 else "High" if score >= 75 else "Medium" if score >= 50 else "Low"
    if priority != "Critical":
        extra["critical_confirmed"] = False
    factors.update({
        "weights": WEIGHTS,
        "economic_vulnerability_basis": "enterprise payment impact" if extra.get("labour_item_code") == "MSME-DELAYED-PAYMENT" else "annual family income",
        "time_sensitivity_basis": extra.get("deadline_window", "none"),
        "days_waiting": days_waiting,
        "exceptional_urgency_reason": str(extra.get("critical_exception_reason") or ""),
        "critical_confirmed": bool(extra.get("critical_confirmed")),
        "worker_vulnerability_verified": bool(extra.get("worker_vulnerability_verified")),
        "statutory_deadline_date": extra.get("statutory_deadline_date"),
        "statutory_deadline_verified": bool(extra.get("statutory_deadline_verified")),
        "score": score,
        "priority": priority,
    })
    return score, factors, priority


def refresh_labour_slps(application, save=True, now=None):
    score, factors, priority = calculate_labour_slps(application, now=now)
    if save and is_labour_application(application):
        extra = application.extra_data if isinstance(application.extra_data, dict) else {}
        extra["labour_slps_factors"] = factors
        extra["labour_slps_priority"] = priority
        application.extra_data = extra
        application.slps_score = score or 0
        application.priority = priority if priority in {"Critical", "High", "Medium", "Low"} else "Low"
        application.save(update_fields=["slps_score", "priority", "extra_data"])
    return score, factors, priority
