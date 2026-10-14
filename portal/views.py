
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render

from .models import Scheme


def parse_list(value):
    """Convert comma-separated eligibility values into a list."""
    return [
        item.strip().casefold()
        for item in (value or "").split(",")
        if item.strip()
    ]

def home(request):
    return render(request, "portal/home.html")

def get_recommendations(profile):
    """
    Filter schemes using their configured eligibility criteria.
    Rank matches transparently using matching profile attributes.
    """
    age = profile.get("age")
    income = profile.get("annual_income")
    occupation = (profile.get("occupation") or "").strip().casefold()
    category = (profile.get("category") or "").strip().casefold()
    state = (profile.get("state") or "").strip().casefold()

    schemes = Scheme.objects.filter(
        is_active=True,
        item_type="Scheme",
    ).select_related("department")

    recommendations = []

    for scheme in schemes:
        reasons = []
        missing_details = []
        score = 0
        excluded = False

        # Age eligibility
        if scheme.min_age is not None or scheme.max_age is not None:
            if age is None:
                missing_details.append("age")
            elif scheme.min_age is not None and age < scheme.min_age:
                excluded = True
            elif scheme.max_age is not None and age > scheme.max_age:
                excluded = True
            else:
                score += 1
                reasons.append("Your age matches the configured age criteria.")

        # Income eligibility
        if scheme.max_income is not None:
            if income is None:
                missing_details.append("annual income")
            elif income > scheme.max_income:
                excluded = True
            else:
                score += 1
                reasons.append("Your annual income is within the configured limit.")

        # Category eligibility
        allowed_categories = parse_list(scheme.allowed_categories)
        if allowed_categories:
            if not category:
                missing_details.append("category")
            elif category not in allowed_categories:
                excluded = True
            else:
                score += 1
                reasons.append("Your category matches the configured criteria.")

        # Occupation eligibility
        allowed_occupations = parse_list(scheme.allowed_occupations)
        if allowed_occupations:
            if not occupation:
                missing_details.append("occupation")
            elif occupation not in allowed_occupations:
                excluded = True
            else:
                score += 1
                reasons.append("Your occupation matches the configured criteria.")

        # Central schemes can be considered across states.
        # State schemes are considered only for the matching state.
        scheme_level = (scheme.level or scheme.department.level or "").casefold()
        scheme_state = (scheme.state or "").strip().casefold()

        is_state_scheme = scheme_level == "state" or bool(scheme_state)

        if is_state_scheme:
            required_state = scheme_state
            if not required_state:
                required_state = scheme.department.name.strip().casefold()

            if not state:
                missing_details.append("state")
            elif required_state and required_state not in state:
                excluded = True
            else:
                score += 1
                reasons.append("Your state matches the scheme's configured state.")

        if excluded:
            continue

        if missing_details:
            eligibility_status = "Needs more information"
            reasons.append(
                "Please provide: " + ", ".join(sorted(set(missing_details))) + "."
            )
        else:
            eligibility_status = "Potential match"
            if not reasons:
                reasons.append(
                    "No conflicting configured criteria were found. "
                    "Verify the official eligibility requirements."
                )

        recommendations.append({
            "id": scheme.id,
            "name": scheme.name,
            "department": scheme.department.name,
            "description": scheme.description,
            "official_link": scheme.official_link,
            "required_documents": scheme.required_documents.splitlines(),
            "access_level": scheme.access_level,
            "eligibility_status": eligibility_status,
            "relevance_score": score,
            "reasons": reasons,
        })

    # Transparent baseline ranking: number of configured criteria matched.
    # This is not a trained Decision Tree model.
    recommendations.sort(
        key=lambda item: (
            item["eligibility_status"] == "Potential match",
            item["relevance_score"],
        ),
        reverse=True,
    )

    return recommendations


@require_POST
def scheme_recommendations(request):
    """POST citizen details and receive matching scheme recommendations."""
    try:
        if request.content_type == "application/json":
            profile = json.loads(request.body or "{}")
        else:
            profile = request.POST

        age_value = profile.get("age")
        income_value = profile.get("annual_income")

        age = int(age_value) if age_value not in (None, "") else None
        income = int(income_value) if income_value not in (None, "") else None

        if age is not None and not 0 <= age <= 120:
            return JsonResponse(
                {"error": "Enter a valid age between 0 and 120."},
                status=400,
            )

        if income is not None and income < 0:
            return JsonResponse(
                {"error": "Annual income cannot be negative."},
                status=400,
            )

        normalized_profile = {
            "age": age,
            "annual_income": income,
            "occupation": profile.get("occupation", ""),
            "category": profile.get("category", ""),
            "state": profile.get("state", ""),
        }

        results = get_recommendations(normalized_profile)

        return JsonResponse({
            "count": len(results),
            "recommendations": results,
            "message": (
                "These are potential matches based on the eligibility "
                "rules configured in the database. Check the official "
                "scheme requirements before applying."
            ),
        })

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse(
            {"error": "Invalid input. Check the citizen details and try again."},
            status=400,
        )
