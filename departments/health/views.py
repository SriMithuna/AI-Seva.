from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from portal.models import Application, Department, Document, Scheme

from .schemes import HEALTH_ITEMS, HEALTH_ITEMS_BY_SLUG
from .services import HealthApplicationForm
from .slps import refresh_health_slps


def health_home(request):
    return _health_home(request, scheme_only=request.GET.get("type") == "scheme")


def health_schemes(request):
    return _health_home(request, scheme_only=True)


def _health_home(request, scheme_only=False):
    items = [item for item in HEALTH_ITEMS if item["item_type"] == "Scheme"] if scheme_only else HEALTH_ITEMS
    return render(request, "health/home.html", {
        "items": items,
        "scheme_only": scheme_only,
        "scheme_count": sum(item["item_type"] == "Scheme" for item in HEALTH_ITEMS),
        "service_count": sum(item["item_type"] == "Service" for item in HEALTH_ITEMS),
        "active_department": "health",
    })


@login_required
def health_apply(request, slug):
    item = HEALTH_ITEMS_BY_SLUG.get(slug)
    if item is None:
        raise Http404("Health scheme or service not found")
    initial = {"full_name": request.user.get_full_name()}
    profile = getattr(request.user, "citizenprofile", None)
    if profile:
        initial["mobile_number"] = profile.phone
        if item["slps_enabled"]:
            initial["is_rural"] = "yes" if profile.background == "RURAL" else "no"

    if request.method == "POST":
        form = HealthApplicationForm(request.POST, request.FILES, item=item, initial=initial)
        if form.is_valid():
            department, _ = Department.objects.update_or_create(
                code="HLT",
                defaults={
                    "name": "Health & Wellness",
                    "description": "Health coverage, maternal benefits and digital health services.",
                    "level": "Central",
                },
            )
            scheme, _ = Scheme.objects.update_or_create(
                department=department,
                name=item["name"],
                defaults={
                    "item_type": item["item_type"],
                    "description": item["summary"],
                    "official_link": item["official_url"],
                    "required_documents": "\n".join(
                        item["documents"]
                        + [label for values in item.get("conditional_documents", {}).values() for label in values]
                    ),
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
            cleaned = form.cleaned_data
            application = Application(
                citizen=request.user,
                scheme=scheme,
                full_name=cleaned["full_name"],
                date_of_birth=cleaned["date_of_birth"],
                gender=cleaned.get("gender", ""),
                mobile_number=cleaned["mobile_number"],
                address=cleaned.get("address", ""),
                purpose=f"Health & Wellness guidance request: {item['name']}",
                extra_data={
                    key: (value.isoformat() if hasattr(value, "isoformat") else str(value))
                    for key, value in cleaned.items()
                    if not key.startswith("document_") and value not in (None, "")
                },
            )
            application.extra_data["health_item_code"] = item["code"]
            application.extra_data["health_docs_required"] = len(form.required_document_labels)
            if item["slps_enabled"]:
                application.extra_data["has_prior_benefit"] = cleaned["has_prior_benefit"] == "Yes"
                application.extra_data["is_urgent"] = bool(cleaned["is_urgent"])
                application.extra_data["is_rural"] = cleaned["is_rural"]
                application.extra_data["urgency_verified"] = False
            application.save()

            for index, document_name in enumerate(form.document_labels, start=1):
                uploaded_file = cleaned.get(f"document_{index}")
                if uploaded_file:
                    Document.objects.create(
                        application=application,
                        name=document_name[:100],
                        file=uploaded_file,
                    )
            if item["slps_enabled"]:
                refresh_health_slps(application)
            return redirect("application_confirmation", tracking_id=application.tracking_id)
    else:
        form = HealthApplicationForm(item=item, initial=initial)

    document_fields = [form[f"document_{index}"] for index in range(1, len(form.document_labels) + 1)]
    document_stage_map = {}
    stage_required_fields = item.get("stage_required_fields", {})
    if item.get("stage_choices"):
        base_count = len(item.get("documents", []))
        conditional_labels = []
        for labels in item.get("conditional_documents", {}).values():
            conditional_labels.extend(label for label in labels if label not in conditional_labels)
        label_indexes = {label: base_count + index + 1 for index, label in enumerate(conditional_labels)}
        for stage, _label in item["stage_choices"]:
            document_stage_map[stage] = list(range(1, base_count + 1)) + [
                label_indexes[label]
                for label in item.get("conditional_documents", {}).get(stage, [])
                if label in label_indexes
            ]
    return render(request, "health/apply.html", {
        "item": item,
        "form": form,
        "document_fields": document_fields,
        "document_stage_map": document_stage_map,
        "stage_required_fields": stage_required_fields,
        "active_department": "health",
    })
