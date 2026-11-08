from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from portal.forms import (
    ABCCreationForm,
    CentralSectorScholarshipForm,
    EducationApplicationForm,
    NSPStudentRegistrationForm,
    PMVidyalaxmiForm,
    PostMatricScholarshipDetailsForm,
    ScholarshipDocumentVerificationForm,
)
from portal.models import Department, Document, Scheme

from .schemes import EDUCATION_SCHEMES
from .services import EDUCATION_SERVICES
from .slps import refresh_application_slps
from .workflows import EDUCATION_PROCEDURES


EDUCATION_ITEMS = EDUCATION_SCHEMES + EDUCATION_SERVICES
EDUCATION_ITEMS_BY_SLUG = {item["slug"]: item for item in EDUCATION_ITEMS}
DETAIL_FORMS = {
    "post-matric-scholarship": PostMatricScholarshipDetailsForm,
    "central-sector-scholarship": CentralSectorScholarshipForm,
    "pm-vidyalaxmi": PMVidyalaxmiForm,
    "nsp-student-registration": NSPStudentRegistrationForm,
    "abc-id-creation": ABCCreationForm,
    "scholarship-status-document-verification": ScholarshipDocumentVerificationForm,
}


def education_home(request):
    return _education_home(request, scheme_only=request.GET.get("type") == "scheme")


def education_schemes(request):
    return _education_home(request, scheme_only=True)


def _education_home(request, scheme_only=False):
    items = EDUCATION_SCHEMES if scheme_only else EDUCATION_ITEMS
    return render(request, "education/index.html", {
        "items": items,
        "scheme_count": len(EDUCATION_SCHEMES),
        "service_count": len(EDUCATION_SERVICES),
        "scheme_only": scheme_only,
        "active_department": "education",
    })


@login_required
def education_apply(request, slug):
    item = EDUCATION_ITEMS_BY_SLUG.get(slug)
    if item is None:
        raise Http404("Education scheme or service not found")

    details_form_class = DETAIL_FORMS[slug]
    initial = {
        "full_name": request.user.get_full_name(),
    }
    profile = getattr(request.user, "citizenprofile", None)
    if profile and profile.phone:
        initial["mobile_number"] = profile.phone

    if request.method == "POST":
        form = EducationApplicationForm(
            request.POST,
            initial=initial,
            require_slps_profile=True,
        )
        details_form = details_form_class(request.POST, request.FILES)
        form_is_valid = form.is_valid()
        details_are_valid = details_form.is_valid()
        if form_is_valid and details_are_valid:
            department, _ = Department.objects.update_or_create(
                code="EDU",
                defaults={
                    "name": "Education",
                    "description": "Scholarships, student services and higher education guidance.",
                    "level": "Central",
                },
            )
            scheme, _ = Scheme.objects.update_or_create(
                department=department,
                name=item["name"],
                defaults={
                    "item_type": item["item_type"],
                    "description": item["description"],
                    "official_link": item["official_url"],
                    "required_documents": "\n".join(item["documents"]),
                    "access_level": "Partial",
                    "level": "Central",
                    "is_active": True,
                    "min_age": None,
                    "max_age": None,
                    "max_income": None,
                    "allowed_categories": "",
                    "allowed_occupations": "",
                },
            )

            application = form.save(commit=False)
            application.citizen = request.user
            application.scheme = scheme
            if not application.purpose:
                application.purpose = f"AI Seva assistance request for {item['name']}"
            application.extra_data = {
                key: str(value)
                for key, value in details_form.cleaned_data.items()
                if value not in (None, "") and not hasattr(value, "read")
            }
            priority_group = form.cleaned_data.get("priority_group")
            if priority_group:
                application.extra_data["priority_group"] = priority_group
            application.save()

            for field_name, uploaded_file in request.FILES.items():
                field = (
                    details_form.fields.get(field_name)
                    or form.fields.get(field_name)
                )
                document_name = (field.label if field else field_name)[:100]
                Document.objects.create(
                    application=application,
                    name=document_name,
                    file=uploaded_file,
                )

            refresh_application_slps(application)

            return redirect(
                "application_confirmation",
                tracking_id=application.tracking_id,
            )
    else:
        form = EducationApplicationForm(
            initial=initial,
            require_slps_profile=True,
        )
        details_form = details_form_class()

    template_name = (
        "education/central_sector_apply.html"
        if slug == "central-sector-scholarship"
        else "education/apply.html"
    )
    return render(request, template_name, {
        "form": form,
        "details_form": details_form,
        "item": item,
        "active_department": "education",
        "procedure": EDUCATION_PROCEDURES.get(slug, []),
    })
