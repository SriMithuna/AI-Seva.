from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from portal.models import Department, Scheme

from .schemes import HOUSING_ITEMS, HOUSING_ITEMS_BY_SLUG
from .services import RuralApplicantForm, RuralDetailsForm


def housing_home(request):
    scheme_only = request.GET.get("type") == "scheme"
    items = [i for i in HOUSING_ITEMS if i["item_type"] == "Scheme"] if scheme_only else HOUSING_ITEMS
    return render(request, "housing_rural/home.html", {
        "items": items, "scheme_only": scheme_only,
        "scheme_count": sum(i["item_type"] == "Scheme" for i in HOUSING_ITEMS),
        "service_count": sum(i["item_type"] == "Service" for i in HOUSING_ITEMS),
    })


def housing_schemes(request):
    items = [i for i in HOUSING_ITEMS if i["item_type"] == "Scheme"]
    return render(request, "housing_rural/home.html", {
        "items": items, "scheme_only": True,
        "scheme_count": len(items), "service_count": 0,
    })


@login_required
def housing_apply(request, slug):
    item = HOUSING_ITEMS_BY_SLUG.get(slug)
    if item is None:
        raise Http404("Housing or rural development item not found")
    if request.method == "POST":
        form = RuralApplicantForm(request.POST)
        details_form = RuralDetailsForm(request.POST)
        if form.is_valid() and details_form.is_valid():
            department, _ = Department.objects.update_or_create(
                code="HRD", defaults={"name": "Housing & Rural Development", "description": "Housing assistance and rural services guidance.", "level": "Central"}
            )
            scheme, _ = Scheme.objects.update_or_create(
                department=department, name=item["name"], defaults={
                    "item_type": item["item_type"], "description": item["description"],
                    "official_link": item["official_link"], "required_documents": "\n".join(item["documents"]),
                    "access_level": "Partial", "level": "Central", "is_active": True,
                }
            )
            application = form.save(commit=False)
            application.citizen = request.user
            application.scheme = scheme
            application.purpose = f"Housing & Rural Development guidance: {item['name']}"
            application.extra_data = {key: str(value) for key, value in details_form.cleaned_data.items()}
            application.save()
            return redirect("application_confirmation", tracking_id=application.tracking_id)
    else:
        initial = {"full_name": request.user.get_full_name()}
        profile = getattr(request.user, "citizenprofile", None)
        if profile:
            initial["mobile_number"] = profile.phone
        form = RuralApplicantForm(initial=initial)
        details_form = RuralDetailsForm()
    return render(request, "housing_rural/application.html", {"item": item, "form": form, "details_form": details_form})
