from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from portal.models import Department, Document, Scheme

from .schemes import HOUSING_ITEMS, HOUSING_ITEMS_BY_SLUG
from .services import HousingDetailsForm, RuralApplicantForm
from .slps import refresh_housing_slps
from .workflows import HOUSING_PROCEDURES


def housing_home(request):
    scheme_only = request.GET.get("type") == "scheme"
    items = [i for i in HOUSING_ITEMS if i["item_type"] == "Scheme"] if scheme_only else HOUSING_ITEMS
    return render(request, "housing_rural/home.html", {
        "items": items, "scheme_only": scheme_only, "active_department": "housing_rural",
        "scheme_count": sum(i["item_type"] == "Scheme" for i in HOUSING_ITEMS),
        "service_count": sum(i["item_type"] == "Service" for i in HOUSING_ITEMS),
    })


def housing_schemes(request):
    items = [i for i in HOUSING_ITEMS if i["item_type"] == "Scheme"]
    return render(request, "housing_rural/home.html", {
        "items": items, "scheme_only": True, "active_department": "housing_rural",
        "scheme_count": len(items), "service_count": 0,
    })


@login_required
def housing_apply(request, slug):
    item = HOUSING_ITEMS_BY_SLUG.get(slug)
    if item is None:
        raise Http404("Housing or rural development item not found")
    procedure = HOUSING_PROCEDURES[slug]
    if request.method == "POST":
        form = RuralApplicantForm(request.POST, item=item)
        details_form = HousingDetailsForm(request.POST, request.FILES, item=item)
        if form.is_valid() and details_form.is_valid():
            department, _ = Department.objects.update_or_create(
                code="HRD",
                defaults={
                    "name": "Housing & Rural Development",
                    "description": "Housing assistance and rural services guidance.",
                    "level": "Central",
                },
            )
            scheme, _ = Scheme.objects.update_or_create(
                department=department, name=item["name"], defaults={
                    "item_type": item["item_type"], "description": item["description"],
                    "official_link": item["official_link"], "required_documents": "\n".join(item["documents"]),
                    "access_level": "Partial", "level": "Central", "is_active": True,
                },
            )
            application = form.save(commit=False)
            application.citizen = request.user
            application.scheme = scheme
            application.purpose = f"Housing & Rural Development guidance: {item['name']}"
            cleaned_details = details_form.cleaned_data
            application.extra_data = {
                key: value.isoformat() if hasattr(value, "isoformat") else value
                for key, value in cleaned_details.items()
                if key not in HousingDetailsForm.DOCUMENT_FIELDS and value not in (None, "")
            }
            application.extra_data.update({
                "housing_item_code": item["code"],
                "housing_eligibility_verified": False,
                "housing_eligible": False,
                "vulnerability_verified": False,
                "urgency_verified": False,
            })
            application.save()
            for field_name, document_label in HousingDetailsForm.DOCUMENT_FIELDS.items():
                uploaded_file = cleaned_details.get(field_name)
                if uploaded_file:
                    Document.objects.create(
                        application=application,
                        name=document_label,
                        file=uploaded_file,
                    )
            if item.get("slps_enabled"):
                refresh_housing_slps(application)
            return redirect("application_confirmation", tracking_id=application.tracking_id)
    else:
        initial = {"full_name": request.user.get_full_name()}
        profile = getattr(request.user, "citizenprofile", None)
        if profile:
            initial["mobile_number"] = profile.phone
        form = RuralApplicantForm(initial=initial, item=item)
        details_form = HousingDetailsForm(item=item)
    return render(request, "housing_rural/application.html", {"item": item, "form": form, "details_form": details_form, "procedure": procedure, "workflow": item["workflow"], "active_department": "housing_rural"})
