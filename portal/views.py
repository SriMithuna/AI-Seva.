
import json
import logging
import re
import secrets
from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Scheme, Application, CitizenProfile, Document, EmailOTP
from .forms import CitizenRegistrationForm, EmailOTPForm
from .chatbot_service import answer_chat_message


logger = logging.getLogger(__name__)


MIN_RECOMMENDATION_SCORE = 50
OPEN_SCHEME_SCORE = 55
OPEN_SCHEME_LIMIT = 2

# ``target`` identifies the intended audience. A target has to match positively
# before a scheme is recommended. ``criteria`` are limits used to qualify and
# label a match. These are guidance rules, not official eligibility decisions.
SCHEME_MATCH_RULES = {
    "pm-kisan": {"target": {"occupation": ["farmer"]}, "weight": 1.0},
    "pmfby": {"target": {"occupation": ["farmer"]}, "weight": 1.0},
    "kcc": {"target": {"occupation": ["farmer"]}, "weight": 0.92},
    "pmmvy": {"target": {"pregnant": True}, "weight": 0.92},
    "jsy": {"target": {"pregnant": True}, "weight": 1.0},
    "sukanya-samriddhi": {"target": {"girl_child_under_10": True}, "weight": 0.92},
    "scss": {"target": {"age": (60, None)}, "weight": 0.92},
    "pm-svanidhi": {"target": {"occupation": ["street_vendor"]}, "weight": 1.0},
    "pm-vishwakarma": {
        "target": {"occupation": ["artisan"]}, "criteria": {"age": (18, None)}, "weight": 1.0,
    },
    "pmkvy": {
        "target": {"seeking_training": True}, "criteria": {"age": (15, 45)}, "weight": 0.92,
    },
    "pmay-gramin": {
        "target": {"area": ["rural"], "has_pucca_house": False}, "weight": 1.0,
    },
    "pmay-urban": {
        "target": {"area": ["urban"], "has_pucca_house": False}, "weight": 1.0,
    },
    "day-nrlm": {
        "target": {"area": ["rural"], "gender": ["female"]}, "weight": 0.92,
    },
    "nsap": {"target": {"nsap_group": True}, "weight": 1.0},
    "post-matric": {"target": {"student_level": ["post_matric"]}, "weight": 0.92},
    "central-sector": {"target": {"student_level": ["undergraduate"]}, "weight": 0.92},
    "pm-vidyalaxmi": {
        "target": {"student_level": ["undergraduate", "postgraduate"], "needs_loan": True},
        "weight": 0.92,
    },
    # Income is a rough discovery proxy here. The official PM-JAY system
    # determines beneficiary eligibility.
    "pm-jay": {"target": {"income": (None, 300000)}, "weight": 1.0},
    "nyaya-bandhu": {"target": {"legal_aid_group": True}, "weight": 0.92},
    "free-legal-aid": {"target": {"legal_aid_group": True}, "weight": 0.92},
    "kalaignar-magalir-urimai-thogai": {
        "target": {"state": ["tamil nadu"], "gender": ["female"], "head_of_household": True},
        "weight": 0.92,
    },
    "pudhumai-penn": {
        "target": {"state": ["tamil nadu"], "gender": ["female"], "govt_school_girl": True},
        "weight": 0.92,
    },
    "makkalai-thedi-maruthuvam": {
        "target": {"state": ["tamil nadu"], "age": (45, None)}, "weight": 0.92,
    },
    "ppf": {"target": {}, "open": True, "weight": 0.92},
    "tele-law": {"target": {}, "open": True, "weight": 0.92},
}

SCHEME_NAME_TO_SLUG = {
    "pm-kisan": "pm-kisan",
    "pm-fasal-bima-yojana": "pmfby",
    "kisan-credit-card": "kcc",
    "pm-matru-vandana-yojana": "pmmvy",
    "janani-suraksha-yojana": "jsy",
    "sukanya-samriddhi-yojana-ssy": "sukanya-samriddhi",
    "senior-citizens-savings-scheme-scss": "scss",
    "pm-svanidhi": "pm-svanidhi",
    "pm-vishwakarma-yojana": "pm-vishwakarma",
    "pradhan-mantri-kaushal-vikas-yojana-pmkvy": "pmkvy",
    "pmay-gramin": "pmay-gramin",
    "pmay-urban-2-0": "pmay-urban",
    "day-nrlm": "day-nrlm",
    "nsap-pensions": "nsap",
    "post-matric-scholarship": "post-matric",
    "central-sector-scholarship": "central-sector",
    "pm-vidyalaxmi": "pm-vidyalaxmi",
    "ayushman-bharat-pm-jay": "pm-jay",
    "nyaya-bandhu": "nyaya-bandhu",
    "free-legal-aid": "free-legal-aid",
    "kalaignar-magalir-urimai-thogai": "kalaignar-magalir-urimai-thogai",
    "pudhumai-penn": "pudhumai-penn",
    "makkalai-thedi-maruthuvam": "makkalai-thedi-maruthuvam",
    "public-provident-fund-ppf": "ppf",
    "tele-law": "tele-law",
}


def parse_list(value):
    """Convert comma-separated eligibility values into a list."""
    return [
        item.strip().casefold()
        for item in (value or "").split(",")
        if item.strip()
    ]


def _profile_scheme_slug(name):
    normalized = re.sub(r"[^a-z0-9]+", "-", (name or "").casefold()).strip("-")
    return SCHEME_NAME_TO_SLUG.get(normalized)


def _matches_value(value, requirement):
    """Return True/False for known values and None when the answer is missing."""
    if value is None or value == "":
        return None
    if isinstance(requirement, list):
        return str(value).strip().casefold() in {
            str(option).strip().casefold() for option in requirement
        }
    if isinstance(requirement, bool):
        return bool(value) == requirement
    lower, upper = requirement
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return (lower is None or number >= lower) and (upper is None or number <= upper)


def _optional_bool(value):
    """Parse an optional JSON/form boolean without treating 'false' as true."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    normalized = str(value).strip().casefold()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    return None


def home(request):
    return render(request, "portal/home.html")


def scheme_results(request):
    """Show the last recommendation run on its own results page."""
    recommendations = request.session.get("scheme_recommendations")
    if recommendations is None:
        return redirect("home")
    return render(request, "portal/scheme_results.html", {
        "recommendations": recommendations,
        "recommendation_count": len(recommendations),
    })


@staff_member_required
def officer_document_download(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.name,
        content_type="application/octet-stream",
    )

@require_POST
@login_required
def application_track_api(request):
    tracking_id = request.POST.get("tracking_id", "").strip()

    if not tracking_id:
        return JsonResponse({
            "success": False,
            "message": "Please enter a tracking ID."
        }, status=400)

    application = Application.objects.filter(
        tracking_id=tracking_id,
        citizen=request.user
    ).select_related("scheme").first()

    if application is None:
        return JsonResponse({
            "success": False,
            "message": "No application found with this tracking ID in your account."
        }, status=404)

    status = application.status

    progress = {
        "Pending": 1,
        "Under Review": 2,
        "More Documents": 2,
        "Approved": 3,
        "Rejected": 3,
    }.get(status, 1)

    return JsonResponse({
        "success": True,
        "tracking_id": application.tracking_id,
        "scheme": application.scheme.name if application.scheme else "Service Application",
        "status": status,
        "progress": progress,
        "message": f"Your application status is: {status}"
    })


def get_recommendations(profile, tree_probs=None, top_k=6):
    """Rank configured scheme matches with the target/criteria scoring model."""
    catalogue = {
        _profile_scheme_slug(scheme.name): scheme
        for scheme in Scheme.objects.filter(
            is_active=True, item_type="Scheme"
        ).select_related("department")
    }
    results, open_items = [], []

    for slug, rule in SCHEME_MATCH_RULES.items():
        scheme = catalogue.get(slug)
        if scheme is None:
            continue

        if rule.get("open"):
            open_items.append({
                "id": scheme.id,
                "name": scheme.name,
                "department": scheme.department.name,
                "description": scheme.description,
                "official_link": scheme.official_link,
                "required_documents": scheme.required_documents.splitlines(),
                "access_level": scheme.access_level,
                "eligibility_status": "General option",
                "relevance_score": OPEN_SCHEME_SCORE,
                "score": OPEN_SCHEME_SCORE,
                "scheme": slug,
                "status": "General option",
                "reasons": ["Available as a general option; check official eligibility and account requirements."],
            })
            continue

        target_checks = [
            _matches_value(profile.get(field), requirement)
            for field, requirement in rule.get("target", {}).items()
        ]
        # A target audience must be affirmatively matched. Missing answers do
        # not produce speculative target matches.
        if not all(check is True for check in target_checks):
            continue

        criteria_checks = [
            _matches_value(profile.get(field), requirement)
            for field, requirement in rule.get("criteria", {}).items()
        ]
        failed = [check for check in criteria_checks if check is False]
        if len(failed) > 1:
            continue

        hit_score = (
            100 * sum(check is True for check in target_checks) / len(target_checks)
            if target_checks else 40
        )
        need_score = 50
        income = profile.get("income")
        income_target = rule.get("target", {}).get("income")
        if income is not None and income_target is not None and income_target[1]:
            need_score = max(0, min(100, 100 * (1 - income / income_target[1])))
        completeness = 100 if all(check is not None for check in criteria_checks) else 70
        relevance_score = (
            0.40 * hit_score
            + 0.25 * need_score
            + 0.20 * rule.get("weight", 1.0) * 100
            + 0.15 * completeness
        )
        if tree_probs and slug in tree_probs:
            relevance_score = 0.75 * relevance_score + 0.25 * 100 * tree_probs[slug]

        if failed:
            status = "Almost eligible"
            relevance_score *= 0.6
        elif any(check is None for check in criteria_checks):
            status = "Check eligibility"
        else:
            status = "Strong match"

        if relevance_score < MIN_RECOMMENDATION_SCORE:
            continue

        reasons = [
            f"Matches the target profile: {field.replace('_', ' ')}."
            for field, requirement in rule.get("target", {}).items()
        ]
        if failed:
            reasons.append("One configured eligibility limit did not match; confirm the official rules.")
        elif any(check is None for check in criteria_checks):
            reasons.append("Some eligibility details still need confirmation.")
        else:
            reasons.append("Configured eligibility criteria match your answers; confirm with the official scheme authority.")

        results.append({
            "id": scheme.id,
            "name": scheme.name,
            "department": scheme.department.name,
            "description": scheme.description,
            "official_link": scheme.official_link,
            "required_documents": scheme.required_documents.splitlines(),
            "access_level": scheme.access_level,
            "eligibility_status": status,
            "relevance_score": round(relevance_score, 1),
            "score": round(relevance_score, 1),
            "scheme": slug,
            "status": status,
            "reasons": reasons,
        })

    results.sort(key=lambda item: -item["relevance_score"])
    return results[:top_k] + open_items[:OPEN_SCHEME_LIMIT]


@require_POST
def scheme_recommendations(request):
    """Return scheme recommendations for submitted citizen details."""
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
            "income": income,
            "annual_income": income,
            "occupation": (profile.get("occupation", "") or "").strip().casefold().replace(" ", "_"),
            "category": profile.get("category", ""),
            "state": (profile.get("state", "") or "").strip().casefold(),
            "gender": (profile.get("gender", "") or "").strip().casefold(),
            "area": (profile.get("area", "") or "").strip().casefold(),
            "pregnant": _optional_bool(profile.get("pregnant")),
            "girl_child_under_10": _optional_bool(profile.get("girl_child_under_10")),
            "seeking_training": _optional_bool(profile.get("seeking_training")),
            "student_level": (profile.get("student_level", "") or "").strip().casefold(),
            "needs_loan": _optional_bool(profile.get("needs_loan")),
            "has_pucca_house": _optional_bool(profile.get("has_pucca_house")),
            "nsap_group": _optional_bool(profile.get("nsap_group")),
            "head_of_household": _optional_bool(profile.get("head_of_household")),
            "govt_school_girl": _optional_bool(profile.get("govt_school_girl")),
            "legal_aid_group": _optional_bool(profile.get("legal_aid_group")),
        }

        results = get_recommendations(normalized_profile)
        request.session["scheme_recommendations"] = results

        return JsonResponse({
            "count": len(results),
            "recommendations": results,
            "results_url": "/recommendations/results/",
            "message": (
                "These ranked results are guidance matches based on the "
                "configured audience and criteria. Confirm requirements "
                "with the official scheme authority."
            ),
        })

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse(
            {"error": "Invalid input. Check the citizen details and try again."},
            status=400,
        )


@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body or "{}")
        message = data.get("message", "")

        if not isinstance(message, str) or not message.strip():
            return JsonResponse(
                {"reply": "Please enter a message."},
                status=400,
            )

        if len(message) > 1000:
            return JsonResponse(
                {"reply": "Please keep your message under 1000 characters."},
                status=400,
            )

        return JsonResponse({"reply": answer_chat_message(request, message)})

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"reply": "Invalid message. Please try again."},
            status=400,
        )

def citizen_register(request):
    if request.method == "POST":
        form = CitizenRegistrationForm(request.POST)

        if form.is_valid():
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                form.add_error(
                    None,
                    "Email verification isn't configured yet. Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to D:\\Ai-Seva\\.env, then restart Django.",
                )
            else:
                try:
                    with transaction.atomic():
                        user = form.save(commit=False)
                        user.is_active = False
                        user.save()
                        CitizenProfile.objects.update_or_create(
                            user=user,
                            defaults={"phone": form.cleaned_data["phone"]},
                        )
                        _issue_email_otp(user)
                except Exception:
                    logger.exception("Failed to send citizen email verification OTP")
                    form.add_error(
                        None,
                        "We couldn't send the verification email. Check your Gmail App Password and SMTP settings, then try again.",
                    )
                else:
                    request.session["email_otp_user_id"] = user.pk
                    return redirect("verify_email")
    else:
        form = CitizenRegistrationForm()

    return render(request, "portal/register.html", {"form": form})


def _issue_email_otp(user):
    code = f"{secrets.randbelow(1_000_000):06d}"
    EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            "code_hash": make_password(code),
            "expires_at": timezone.now() + timedelta(minutes=5),
            "attempts": 0,
        },
    )
    send_mail(
        subject="Your AI Seva verification code",
        message=(
            f"Your AI Seva email verification code is {code}. "
            "It expires in 5 minutes. If you did not register, ignore this email."
        ),
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )


def _pending_email_user(request):
    user_id = request.session.get("email_otp_user_id")
    if not user_id:
        return None
    return User.objects.filter(pk=user_id, is_active=False).first()


def verify_email(request):
    user = _pending_email_user(request)
    if user is None:
        request.session.pop("email_otp_user_id", None)
        messages.info(request, "Register first to verify your email address.")
        return redirect("citizen_register")

    form = EmailOTPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        otp = EmailOTP.objects.filter(user=user).first()
        if otp is None:
            form.add_error(None, "No verification code is available. Request a new code.")
        elif otp.attempts >= 5:
            form.add_error("code", "Too many attempts. Request a new code to continue.")
        elif otp.expires_at <= timezone.now():
            form.add_error("code", "This code has expired. Request a new code.")
        elif check_password(form.cleaned_data["code"], otp.code_hash):
            user.is_active = True
            user.save(update_fields=["is_active"])
            otp.delete()
            request.session.pop("email_otp_user_id", None)
            messages.success(request, "Your email is verified. You can now sign in.")
            return redirect("citizen_login")
        else:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            form.add_error("code", "That code is incorrect. Check the email and try again.")

    return render(request, "portal/verify_email.html", {
        "form": form,
        "email": user.email,
    })


@require_POST
def resend_email_otp(request):
    user = _pending_email_user(request)
    if user is None:
        request.session.pop("email_otp_user_id", None)
        messages.info(request, "Register first to request a verification code.")
        return redirect("citizen_register")

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        messages.error(request, "Email verification isn't configured. Add EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to .env, then restart Django.")
        return redirect("verify_email")

    try:
        _issue_email_otp(user)
    except Exception:
        logger.exception("Failed to resend citizen email verification OTP")
        messages.error(request, "We couldn't send a new code. Check the Gmail SMTP settings and try again.")
    else:
        messages.success(request, "A new verification code was sent to your email.")
    return redirect("verify_email")

def abha_service(request):
    return render(request, "portal/services/abha.html")


def abha_apply(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        dob = request.POST.get("date_of_birth", "").strip()
        gender = request.POST.get("gender", "").strip()
        mobile = request.POST.get("mobile_number", "").strip()
        address = request.POST.get("address", "").strip()
        purpose = request.POST.get("purpose", "").strip()

        if not all([full_name, dob, gender, mobile, address, purpose]):
            messages.error(request, "Please complete all fields.")
            return render(request, "portal/services/abha_apply.html")

        if not mobile.isdigit() or len(mobile) != 10:
            messages.error(request, "Enter a valid 10-digit mobile number.")
            return render(request, "portal/services/abha_apply.html")

        try:
            date_of_birth = date.fromisoformat(dob)
            if date_of_birth >= date.today():
                raise ValueError
        except ValueError:
            messages.error(request, "Enter a valid date of birth.")
            return render(request, "portal/services/abha_apply.html")

        # This is a college demonstration, not official ABHA registration.
        scheme = Scheme.objects.filter(
            is_active=True,
            item_type="Service",
        ).first()

        if scheme is None:
            scheme = Scheme.objects.filter(is_active=True).first()

        if scheme is None:
            messages.error(
                request,
                "No active service is configured. Add a service in the admin panel first."
            )
            return render(request, "portal/services/abha_apply.html")

        citizen, _ = User.objects.get_or_create(
            username="aiseva_demo_citizen",
            defaults={"email": ""},
        )

        application = Application.objects.create(
            citizen=citizen,
            scheme=scheme,
            full_name=full_name,
            date_of_birth=date_of_birth,
            gender=gender,
            mobile_number=mobile,
            address=address,
            purpose=purpose,
        )

        return redirect(
            "application_confirmation",
            tracking_id=application.tracking_id,
        )

    return render(request, "portal/services/abha_apply.html")

def citizen_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            next_url = request.POST.get("next") or request.GET.get("next")

            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)

            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(
        request,
        "portal/login.html",
        {"next": request.GET.get("next", "")}
    )


def citizen_logout(request):
    logout(request)
    return redirect("home")


@login_required
def application_confirmation(request, tracking_id):
    application = get_object_or_404(
        Application,
        tracking_id=tracking_id,
        citizen=request.user,
    )

    return render(
        request,
        "portal/services/confirmation.html",
        {
            "application": application,
            "active_department": (
                "education"
                if application.scheme.department.code == "EDU"
                else "agriculture"
            ),
        },
    )


@login_required
def application_track(request):
    application = None
    error = ""

    if request.method == "POST":
        tracking_id = request.POST.get("tracking_id", "").strip()

        if tracking_id:
            application = Application.objects.filter(
                tracking_id=tracking_id,
                citizen=request.user
            ).first()

        if application is None:
            error = "No application found with that tracking ID."

    return render(
        request,
        "portal/services/track.html",
        {"application": application, "error": error},
    )

@login_required
def citizen_dashboard(request):
    applications = Application.objects.filter(
        citizen=request.user
    ).select_related("scheme", "scheme__department").order_by("-created_at")

    context = {
        "applications": applications,
        "total_applications": applications.count(),
        "pending_applications": applications.filter(status="Pending").count(),
        "approved_applications": applications.filter(status="Approved").count(),
        "rejected_applications": applications.filter(status="Rejected").count(),
    }

    return render(request, "portal/dashboard.html", context)
