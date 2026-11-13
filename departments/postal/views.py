from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from portal.models import Application, Department, Document, Scheme

from .schemes import POSTAL_ITEMS, POSTAL_ITEMS_BY_SLUG
from .services import PostalApplicationForm
from .slps import refresh_postal_slps


def postal_home(request):
    return _postal_catalog(request, "all")


def postal_schemes(request):
    return _postal_catalog(request, "scheme")


def postal_services(request):
    return redirect("postal:home")


def _postal_catalog(request, filter_type):
    items = POSTAL_ITEMS if filter_type == "all" else [
        item for item in POSTAL_ITEMS if item["item_type"].lower() == filter_type
    ]
    return render(request, "postal/home.html", {
        "items": items,
        "show_all": filter_type == "all",
        "scheme_only": filter_type == "scheme",
        "postal_filter": filter_type,
        "scheme_count": sum(i["item_type"] == "Scheme" for i in POSTAL_ITEMS),
        "service_count": sum(i["item_type"] == "Service" for i in POSTAL_ITEMS),
        "active_department": "postal",
    })


@login_required
def postal_apply(request, slug):
    item = POSTAL_ITEMS_BY_SLUG.get(slug)
    if item is None:
        raise Http404("Postal scheme or service not found")
    initial = {"full_name": request.user.get_full_name()}
    profile = getattr(request.user, "citizenprofile", None)
    if profile:
        initial["mobile_number"] = profile.phone
        initial["date_of_birth"] = None
    form = PostalApplicationForm(request.POST or None, request.FILES or None, item=item, initial=initial)
    if request.method == "POST" and form.is_valid():
        department, _ = Department.objects.update_or_create(
            code="POST", defaults={"name": "Postal Services", "description": "India Post schemes, claims and grievance assistance.", "level": "Central"}
        )
        scheme, _ = Scheme.objects.update_or_create(
            department=department, name=item["name"],
            defaults={
                "item_type": item["item_type"], "description": item["summary"],
                "official_link": item["official_url"],
                "required_documents": "\n".join(item["documents"]),
                "access_level": "Partial", "level": "Central", "is_active": True,
                "min_age": None, "max_age": None, "max_income": None,
                "allowed_categories": "", "allowed_occupations": "",
            },
        )
        cleaned = form.cleaned_data
        extra = {
            key: value.isoformat() if hasattr(value, "isoformat") else str(value)
            for key, value in cleaned.items()
            if not key.startswith("document_") and value not in (None, "")
        }
        extra["postal_service_type"] = item.get("postal_service_type", "")
        extra["postal_docs_required"] = len(form.required_document_labels)
        extra["postal_eligible"] = True
        application = Application.objects.create(
            citizen=request.user, scheme=scheme, full_name=cleaned["full_name"],
            date_of_birth=cleaned.get("date_of_birth") or cleaned.get("child_dob"),
            mobile_number=cleaned["mobile_number"], address=cleaned.get("address", ""),
            purpose=f"Postal {item['item_type'].lower()} preparation: {item['name']}",
            extra_data=extra,
        )
        for index, label in enumerate(form.document_labels, 1):
            uploaded = cleaned.get(f"document_{index}")
            if uploaded:
                Document.objects.create(application=application, name=label[:100], file=uploaded)
        if item.get("slps_enabled"):
            refresh_postal_slps(application)
        return redirect("application_confirmation", tracking_id=application.tracking_id)
    document_fields = [form[f"document_{i}"] for i in range(1, len(form.document_labels) + 1)]
    return render(request, "postal/apply.html", {
        "item": item, "form": form, "document_fields": document_fields,
        "active_department": "postal",
    })
