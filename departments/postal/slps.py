"""Officer-side SLPS scoring for Postal Services claims and grievances."""

from datetime import date

from django.core.exceptions import ObjectDoesNotExist


PROFILES = {
    "deceased-claim": dict(category=25, income=15, waiting=25, documents=15,
                            dependents=12, age=5, background=3, tier=1.00, sla=30),
    "pli-rpli-claim": dict(category=15, income=10, waiting=35, documents=20,
                           dependents=5, age=10, background=5, tier=0.90, sla=30),
    "grievance": dict(category=35, income=5, waiting=40, documents=10,
                      dependents=0, age=5, background=5, tier=0.85, sla=21),
}
BREACH_BOOST = 15


def postal_service_type(application):
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    explicit = str(extra.get("postal_service_type") or "").strip().lower()
    if explicit in PROFILES:
        return explicit
    name = application.scheme.name.casefold()
    if "grievance" in name or "complaint" in name:
        return "grievance"
    if "pli" in name or "rpli" in name:
        return "pli-rpli-claim"
    if "deceased" in name or "death" in name:
        return "deceased-claim"
    return None


def is_postal_application(application):
    return bool(application.scheme_id and application.scheme.department.code == "POST"
                and postal_service_type(application))


def _number(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _profile(application):
    try:
        return application.citizen.citizenprofile
    except ObjectDoesNotExist:
        return None


def calculate_postal_slps(application, today=None):
    """Return (score, factor breakdown, priority); ineligible cases are unranked."""
    kind = postal_service_type(application)
    if not kind:
        return None, {}, "Not scored"
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}
    if extra.get("postal_eligible") is False:
        return None, {"eligibility": "Marked not eligible"}, "Not scored"

    profile = _profile(application)
    p = PROFILES[kind]
    today = today or date.today()
    waited = max(0, (today - application.created_at.date()).days) if application.created_at else 0
    docs_required = max(0, int(_number(extra.get("postal_docs_required"), 0)))
    docs_uploaded = application.documents.count()
    if docs_required == 0:
        docs_required = docs_uploaded
    factors = {
        "category": max(0, min(100, _number(extra.get("postal_category_points"), 0))),
        "income": max(0, min(100, _number(extra.get("postal_income_points"), 0))),
        "waiting": min(waited / p["sla"], 1) * 100,
        "documents": min(docs_uploaded / docs_required, 1) * 100 if docs_required else 0,
        "dependents": min(max(0, _number(extra.get("postal_dependents", getattr(profile, "dependents", 0)))), 4) / 4 * 100,
        "age": max(0, min(100, _number(extra.get("postal_age_points"), 0))),
        "background": max(0, min(100, _number(extra.get("postal_background_points"), 0))),
    }
    base = sum(factors[key] * p[key] / 100 for key in factors)
    breached = waited > p["sla"]
    if breached:
        base = min(base + BREACH_BOOST, 100)
    score = round(base * p["tier"], 2)
    priority = "Critical" if score >= 90 else "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    return score, {**factors, "weights": {k: p[k] for k in factors}, "service": kind,
                   "waiting_days": waited, "sla_days": p["sla"], "sla_breached": breached,
                   "breach_boost": BREACH_BOOST if breached else 0, "tier": p["tier"],
                   "final_score": score}, priority


def refresh_postal_slps(application, save=True, today=None):
    score, factors, priority = calculate_postal_slps(application, today=today)
    if save and is_postal_application(application):
        extra = application.extra_data if isinstance(application.extra_data, dict) else {}
        extra["postal_slps_factors"] = factors
        extra["postal_slps_priority"] = priority
        application.extra_data = extra
        application.slps_score = score or 0
        application.priority = priority if priority in {"Critical", "High", "Medium", "Low"} else "Low"
        application.save(update_fields=["slps_score", "priority", "extra_data"])
    return score, factors, priority
