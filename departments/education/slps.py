from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist


FACTOR_WEIGHTS = {
    "category": 0.30,
    "income": 0.25,
    "waiting": 0.20,
    "docs": 0.15,
    "age": 0.05,
    "background": 0.05,
}

CATEGORY_SCORE = {
    "orphan_or_pwd": 90,
    "sc_st": 75,
    "minority_obc": 55,
    "girl_student": 45,
    "general": 20,
}

ITEM_WEIGHTS = {
    "Post-Matric Scholarship": 1.15,
    "Central Sector Scholarship": 1.10,
    "PM Vidyalaxmi": 1.05,
    "Scholarship Application Status and Document Verification": 1.00,
    "NSP Student Registration": 0.95,
    "ABC ID Creation": 0.90,
}


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def _date_only(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def _number(value, fallback=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _category_key(value):
    key = str(value or "general").strip().casefold().replace(" ", "_").replace("/", "_")
    return {
        "sc": "sc_st",
        "st": "sc_st",
        "sc_st": "sc_st",
        "obc": "minority_obc",
        "minority": "minority_obc",
        "minority_obc": "minority_obc",
        "pwd": "orphan_or_pwd",
        "orphan": "orphan_or_pwd",
        "orphan_or_pwd": "orphan_or_pwd",
        "girl": "girl_student",
        "girl_student": "girl_student",
        "general": "general",
        "bpl": "general",
    }.get(key, "general")


def slps_score(app, scheme, today=None):
    """Return an SLPS score and its factor breakdown for an application mapping.

    If a scheme has no configured income limit, use a neutral income factor
    rather than inventing an eligibility threshold or treating missing data as
    zero income.
    """
    today = today or date.today()
    first_submitted = _date_only(app.get("first_submitted")) or today
    first_submitted = _date_only(first_submitted)
    days_waited = max(0, (today - first_submitted).days)

    income = _number(app.get("income"), None)
    income_limit = _number(scheme.get("income_limit"), None)
    if income is None or income_limit is None or income_limit <= 0:
        income_factor = 50
    else:
        income_factor = clamp(100 * (1 - income / income_limit))

    applicable = max(int(_number(app.get("applicable_supporting"), 0)), 1)
    verified = max(int(_number(app.get("verified_supporting"), 0)), 0)
    age_score = clamp(_number(app.get("age_score"), 50))
    factors = {
        "category": CATEGORY_SCORE.get(_category_key(app.get("category")), 20),
        "income": income_factor,
        "waiting": clamp(100 * days_waited / 30),
        "docs": clamp(100 * verified / applicable),
        "age": age_score,
        "background": 70 if app.get("rural") else 30,
    }

    base = sum(FACTOR_WEIGHTS[key] * value for key, value in factors.items())
    score = round(_number(scheme.get("weight"), 1.0) * base, 2)
    return score, factors


def sort_queue(applications, schemes, today=None):
    """Rank application mappings by score, then by oldest submission date."""
    scored = []
    for app in applications:
        score, breakdown = slps_score(app, schemes[app["scheme_id"]], today=today)
        submitted = _date_only(app["first_submitted"])
        scored.append((score, app, breakdown, submitted))
    scored.sort(key=lambda row: (-row[0], row[3]))
    return [(score, app, breakdown) for score, app, breakdown, _ in scored]


def age_priority_score(age):
    if age is None:
        return 50
    if age >= 60:
        return 100
    if age < 18:
        return 80
    if age <= 25:
        return 60
    return 40


def _profile_for(application):
    try:
        return application.citizen.citizenprofile
    except ObjectDoesNotExist:
        return None


def build_application_inputs(application):
    """Adapt the Django Education application and verified documents to SLPS."""
    profile = _profile_for(application)
    extra = application.extra_data if isinstance(application.extra_data, dict) else {}

    age = None
    if application.date_of_birth:
        today = date.today()
        age = today.year - application.date_of_birth.year - (
            (today.month, today.day)
            < (application.date_of_birth.month, application.date_of_birth.day)
        )
    elif profile and profile.age is not None:
        age = profile.age

    if application.priority_group_verified:
        category = extra.get("priority_group") or extra.get("category")
        if not category:
            category = profile.category if profile else "general"
        if str(category).casefold() in {"general", "bpl"} and application.gender.casefold() == "female":
            category = "girl_student"
    else:
        category = "general"

    income = extra.get("annual_income")
    if income in (None, ""):
        income = extra.get("annual_family_income")
    if income in (None, "") and profile:
        income = profile.annual_income
    documents = list(application.documents.all())
    applicable_supporting = len([
        line for line in (application.scheme.required_documents or "").splitlines()
        if line.strip()
    ])

    return {
        "scheme_id": application.scheme_id,
        "first_submitted": application.created_at.date() if application.created_at else date.today(),
        "category": category,
        "income": income,
        "verified_supporting": sum(1 for document in documents if document.is_verified),
        "applicable_supporting": applicable_supporting,
        "age_score": age_priority_score(age),
        "rural": bool(profile and profile.background == "RURAL"),
    }


def calculate_application_slps(application, today=None):
    app_data = build_application_inputs(application)
    scheme_data = {
        "income_limit": application.scheme.max_income,
        "weight": ITEM_WEIGHTS.get(application.scheme.name, 1.0),
    }
    return slps_score(app_data, scheme_data, today=today)


def refresh_application_slps(application, today=None, save=True):
    """Recalculate and optionally persist the internal score and priority."""
    score, breakdown = calculate_application_slps(application, today=today)
    if score >= 70:
        priority = "High"
    elif score >= 40:
        priority = "Medium"
    else:
        priority = "Low"

    if save:
        extra = application.extra_data if isinstance(application.extra_data, dict) else {}
        extra["slps_factors"] = breakdown
        application.extra_data = extra
        application.slps_score = score
        application.priority = priority
        application.save(update_fields=["slps_score", "priority", "extra_data"])

    return score, breakdown, priority


def is_education_application(application):
    return bool(application.scheme_id and application.scheme.department.code == "EDU")
