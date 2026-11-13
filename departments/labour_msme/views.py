from django.contrib.auth.decorators import login_required
from hashlib import sha256
from django.http import Http404
from django.shortcuts import redirect, render

from portal.models import Application, Department, Document, Scheme

from .schemes import LABOUR_ITEMS, LABOUR_ITEMS_BY_SLUG, seed_labour_catalog
from .services import LabourApplicationForm
from .slps import refresh_labour_slps


def labour_home(request):
    return _labour_catalog(request, "all")


def labour_schemes(request):
    return _labour_catalog(request, "scheme")


def labour_services(request):
    return redirect("labour_msme:home")


def _labour_catalog(request, filter_type):
    items = LABOUR_ITEMS if filter_type == "all" else [
        item for item in LABOUR_ITEMS
        if item["item_type"] == ("Scheme" if filter_type == "scheme" else "Service")
    ]
    return render(request, "labour_msme/home.html", {
        "items": items,
        "filter_type": filter_type,
        "show_all": filter_type == "all",
        "scheme_count": sum(item["item_type"] == "Scheme" for item in LABOUR_ITEMS),
        "service_count": sum(item["item_type"] == "Service" for item in LABOUR_ITEMS),
        "active_department": "labour_msme",
    })


@login_required
def labour_apply(request, slug):
    item = LABOUR_ITEMS_BY_SLUG.get(slug)
    if item is None:
        raise Http404("Labour, Skill & MSME service not found")
    initial = {"full_name": request.user.get_full_name()}
    profile = getattr(request.user, "citizenprofile", None)
    if profile:
        initial["mobile_number"] = profile.phone
        initial["annual_income"] = profile.annual_income
    form = LabourApplicationForm(request.POST or None, request.FILES or None, item=item, initial=None if request.method == "POST" else initial)
    if request.method == "POST" and form.is_valid():
        seed_labour_catalog()
        department = Department.objects.get(code="LSM")
        scheme = Scheme.objects.get(department=department, name=item["name"])
        data = form.cleaned_data
        extra = {key: (value.isoformat() if hasattr(value, "isoformat") else value) for key, value in data.items() if key not in LabourApplicationForm.FILE_FIELDS}
        extra.update({
            "labour_item_code": item["code"],
            "worker_vulnerability_verified": False,
            "critical_confirmed": False,
            "statutory_deadline_verified": False,
        })
        if item["code"] in {"PMKVY", "PMKVY-TRAINING"}:
            enrolment_material = "|".join([
                str(request.user.pk), str(data.get("pmkvy_pathway", "")),
                data.get("job_role", "").strip().casefold(), data.get("sector", "").strip().casefold(),
                data.get("training_district", "").strip().casefold(), data.get("training_centre", "").strip().casefold(),
            ])
            extra["pmkvy_enrolment_key"] = sha256(enrolment_material.encode("utf-8")).hexdigest()
            existing = Application.objects.filter(
                citizen=request.user,
                scheme__department__code="LSM",
                extra_data__pmkvy_enrolment_key=extra["pmkvy_enrolment_key"],
                status__in=["Pending", "Under Review", "More Documents"],
            ).order_by("created_at").first()
            if existing:
                existing_extra = existing.extra_data if isinstance(existing.extra_data, dict) else {}
                existing_extra.update(extra)
                existing_extra["pmkvy_registration_source"] = item["code"]
                existing.extra_data = existing_extra
                existing.full_name = data["full_name"]
                existing.mobile_number = data["mobile_number"]
                existing.address = data["address"]
                existing.save(update_fields=["extra_data", "full_name", "mobile_number", "address"])
                refresh_labour_slps(existing)
                return redirect("application_confirmation", tracking_id=existing.tracking_id)
        application = Application.objects.create(
            citizen=request.user,
            scheme=scheme,
            full_name=data["full_name"],
            mobile_number=data["mobile_number"],
            address=data["address"],
            purpose=f"Labour, Skill & MSME guidance request: {item['name']}",
            extra_data=extra,
        )
        for field_name, label in LabourApplicationForm.FILE_FIELDS.items():
            uploaded = data.get(field_name)
            if uploaded:
                Document.objects.create(application=application, name=label, file=uploaded)
        refresh_labour_slps(application)
        return redirect("application_confirmation", tracking_id=application.tracking_id)
    slps_field_names = {
        "annual_income", "economic_impact", "livelihood_situation", "worker_vulnerability",
        "dependents", "support_gap", "deadline_window", "statutory_deadline_date",
        "critical_exception_reason",
    }
    contact_names = {"full_name", "mobile_number", "address"}
    file_names = set(LabourApplicationForm.FILE_FIELDS) & set(form.fields)
    service_names = set(form.fields) - contact_names - slps_field_names - file_names - {"service_details"}
    procedure = [
        {"title": "Your details", "description": "Start with the contact information for this guidance request.", "field_names": [name for name in ("full_name", "mobile_number", "address") if name in form.fields]},
    ]
    if service_names:
        procedure.append({"title": "Scheme or service details", "description": "Enter the information relevant to this specific scheme or service.", "field_names": [name for name in form.fields if name in service_names]})
    document_and_request_fields = [name for name in form.fields if name in file_names or name == "service_details"]
    if document_and_request_fields:
        procedure.append({"title": "Request details & documents", "description": "Explain what guidance you need and attach any relevant supporting records.", "field_names": document_and_request_fields})
    if slps_field_names & set(form.fields):
        procedure.append({"title": "Priority information", "description": "These answers support transparent SLPS queue prioritisation; they do not decide eligibility.", "field_names": [name for name in form.fields if name in slps_field_names]})
    procedure.append({"title": "Review request", "description": "Check your answers before creating the AI Seva guidance record.", "review": True, "field_names": []})
    for step in procedure:
        step["fields"] = [form[name] for name in step["field_names"]]
    return render(request, "labour_msme/application.html", {
        "item": item, "form": form, "active_department": "labour_msme",
        "procedure": procedure,
        "weights": [("Economic vulnerability", "25%"), ("Livelihood / employment urgency", "25%"), ("Waiting time in the AI Seva officer queue", "20%"), ("Worker vulnerability", "15%"), ("Family dependents", "8%"), ("Skill / financial support gap", "5%"), ("Time sensitivity", "2%")],
    })
