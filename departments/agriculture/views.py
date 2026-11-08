from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from portal.models import Department, Scheme

from .schemes import AGRICULTURE_ITEMS, AGRICULTURE_ITEMS_BY_SLUG
from .services import APPLICANT_FORMS, AgricultureApplicantForm, DETAILS_FORMS
from .workflows import AGRICULTURE_PROCEDURES


def agriculture_home(request):
    return _agriculture_home(request, scheme_only=request.GET.get("type") == "scheme")


def agriculture_schemes(request):
    return _agriculture_home(request, scheme_only=True)


def _agriculture_home(request, scheme_only=False):
    items = [item for item in AGRICULTURE_ITEMS if item["item_type"] == "Scheme"] if scheme_only else AGRICULTURE_ITEMS
    return render(request, "agriculture/home.html", {
        "items": items,
        "scheme_only": scheme_only,
        "scheme_count": sum(item["item_type"] == "Scheme" for item in AGRICULTURE_ITEMS),
        "service_count": sum(item["item_type"] == "Service" for item in AGRICULTURE_ITEMS),
    })


@login_required
def agriculture_apply(request, slug):
    item = AGRICULTURE_ITEMS_BY_SLUG.get(slug)
    if item is None:
        raise Http404("Agriculture item not found")
    applicant_form_class = APPLICANT_FORMS.get(slug, AgricultureApplicantForm)
    details_form_class = DETAILS_FORMS[slug]

    if request.method == "POST":
        form = applicant_form_class(request.POST)
        details_form = details_form_class(request.POST)
        applicant_is_valid = form.is_valid()
        details_are_valid = details_form.is_valid()
        if applicant_is_valid and details_are_valid:
            department, _ = Department.objects.get_or_create(
                code="AGR",
                defaults={
                    "name": "Agriculture",
                    "description": "Central agriculture schemes and farmer services.",
                    "level": "Central",
                },
            )
            scheme, _ = Scheme.objects.update_or_create(
                department=department,
                name=item["name"],
                defaults={
                    "item_type": item["item_type"],
                    "description": item["description"],
                    "official_link": item["official_link"],
                    "access_level": "Partial",
                    "required_documents": "\n".join(item["documents"]),
                    "level": "Central",
                    "is_active": True,
                },
            )
            application = form.save(commit=False)
            application.citizen = request.user
            application.scheme = scheme
            application.purpose = details_form.cleaned_data.get(
                "credit_purpose",
                f"Assistance request for {item['name']}",
            )
            application.extra_data = {
                key: str(value)
                for key, value in details_form.cleaned_data.items()
                if value not in (None, "")
            }
            application.save()
            return redirect(
                "application_confirmation",
                tracking_id=application.tracking_id,
            )
    else:
        form = applicant_form_class()
        details_form = details_form_class()

    return render(request, "agriculture/application.html", {
        "item": item,
        "form": form,
        "details_form": details_form,
        "workflow": item["workflow"],
        "procedure": AGRICULTURE_PROCEDURES.get(slug, []),
    })
