
import json
import logging
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


def parse_list(value):
    """Convert comma-separated eligibility values into a list."""
    return [
        item.strip().casefold()
        for item in (value or "").split(",")
        if item.strip()
    ]


def home(request):
    return render(request, "portal/home.html")


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


def get_recommendations(profile):
    """Filter and rank schemes using configured eligibility criteria."""
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

        if scheme.max_income is not None:
            if income is None:
                missing_details.append("annual income")
            elif income > scheme.max_income:
                excluded = True
            else:
                score += 1
                reasons.append("Your annual income is within the configured limit.")

        allowed_categories = parse_list(scheme.allowed_categories)
        if allowed_categories:
            if not category:
                missing_details.append("category")
            elif category not in allowed_categories:
                excluded = True
            else:
                score += 1
                reasons.append("Your category matches the configured criteria.")

        allowed_occupations = parse_list(scheme.allowed_occupations)
        if allowed_occupations:
            if not occupation:
                missing_details.append("occupation")
            elif occupation not in allowed_occupations:
                excluded = True
            else:
                score += 1
                reasons.append("Your occupation matches the configured criteria.")

        scheme_level = (
            scheme.level or scheme.department.level or ""
        ).casefold()
        scheme_state = (scheme.state or "").strip().casefold()

        if scheme_level == "state" or scheme_state:
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
                "rules configured in the database. Check official "
                "scheme requirements before applying."
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
