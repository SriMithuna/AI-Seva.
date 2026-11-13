from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
import json
from datetime import date, timedelta
from django.db.models import Case, IntegerField, Value, When
from .models import (Department, Scheme, CategoryWeights, CitizenProfile,
                     OfficerProfile, Application, Document, StatusRemark)
from departments.education.slps import (
    ITEM_WEIGHTS,
    build_application_inputs,
    is_education_application,
    refresh_application_slps,
    sort_queue,
)
from departments.health.slps import (
    is_health_application,
    refresh_health_slps,
)
from departments.housing_rural.slps import (
    is_housing_application,
    refresh_housing_slps,
)
from departments.housing_rural.schemes import HOUSING_SLPS_CODES
from departments.labour_msme.slps import is_labour_application, refresh_labour_slps
from departments.postal.slps import is_postal_application, refresh_postal_slps


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'item_type', 'access_level', 'is_active')
    list_filter = ('department', 'item_type', 'access_level')
    search_fields = ('name',)


admin.site.register([Department, CategoryWeights, CitizenProfile, OfficerProfile])


@admin.register(StatusRemark)
class StatusRemarkAdmin(admin.ModelAdmin):
    list_display = ("application", "status", "officer", "created_at")
    list_filter = ("status",)
    search_fields = ("application__tracking_id", "application__full_name", "remark")

    def save_model(self, request, obj, form, change):
        if not obj.officer_id:
            obj.officer = request.user
        super().save_model(request, obj, form, change)
        application = obj.application
        if is_health_application(application):
            refresh_health_slps(application)
        elif is_housing_application(application):
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            if obj.status in {"Approved", "Rejected"}:
                extra["housing_decided_at"] = (obj.created_at or timezone.now()).isoformat()
            elif application.status not in {"Approved", "Rejected"}:
                extra.pop("housing_decided_at", None)
            application.extra_data = extra
            application.save(update_fields=["extra_data"])
            refresh_housing_slps(application)
        elif is_labour_application(application):
            refresh_labour_slps(application)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_id", "full_name", "scheme", "status", "priority_group_verified", "health_urgency_state",
        "housing_eligibility_state", "housing_urgency_state", "housing_deadline_state",
        "labour_critical_state", "slps_priority_display", "slps_score_display", "created_at",
    )
    list_editable = ("priority_group_verified",)
    list_filter = ("status", "priority", "scheme__department", "scheme")
    search_fields = ("tracking_id", "full_name", "citizen__username", "scheme__name")
    readonly_fields = ("slps_priority_display", "slps_score_display", "slps_breakdown")
    ordering = ("-slps_score", "created_at")
    actions = (
        "verify_selected_health_urgency",
        "mark_selected_housing_eligible",
        "mark_selected_housing_ineligible",
        "verify_selected_housing_urgency",
        "verify_selected_housing_vulnerability",
        "verify_selected_housing_deadline",
        "verify_selected_labour_critical",
        "verify_selected_labour_vulnerability",
        "verify_selected_labour_deadline",
    )

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        return list(dict.fromkeys(
            [
            "slps_priority_display" if field == "priority" else
            "slps_score_display" if field == "slps_score" else field
            for field in fields
            ]
        ))

    @admin.display(description="Health urgency")
    def health_urgency_state(self, obj):
        if not is_health_application(obj):
            return "—"
        extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
        if not extra.get("is_urgent"):
            return "Not requested"
        return "Verified" if extra.get("urgency_verified") else "Needs verification"

    @admin.display(description="Housing eligibility")
    def housing_eligibility_state(self, obj):
        if not is_housing_application(obj):
            return "—"
        extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
        code = extra.get("housing_item_code")
        if code == "VB-G-EMPLOYMENT":
            return "Employment-demand follow-up — separate review"
        if code == "NSAP-STATUS":
            return "Pension status enquiry — not scored"
        if code not in HOUSING_SLPS_CODES:
            return "Not scored"
        if not extra.get("housing_eligibility_verified"):
            return "Needs officer review"
        return "Eligible" if extra.get("housing_eligible") else "Not eligible"

    @admin.display(description="Housing urgency")
    def housing_urgency_state(self, obj):
        if not is_housing_application(obj):
            return "—"
        extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
        code = extra.get("housing_item_code")
        if code not in HOUSING_SLPS_CODES or not extra.get("is_urgent"):
            return "Not requested"
        return "Verified" if extra.get("urgency_verified") else "Needs verification"

    @admin.display(description="Employment demand timeline")
    def housing_deadline_state(self, obj):
        if not is_housing_application(obj):
            return "—"
        extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
        if extra.get("housing_item_code") != "VB-G-EMPLOYMENT":
            return "—"
        demand_date = extra.get("employment_demand_date")
        if not demand_date:
            return "Official demand date missing"
        if not extra.get("housing_deadline_verified"):
            return "Needs officer verification"
        due_date = extra.get("statutory_deadline_date")
        if due_date and due_date < timezone.localdate().isoformat():
            return f"Overdue — 15-day point was {due_date}"
        return f"Verified — 15-day point {due_date}" if due_date else "Verified — review separately"

    @admin.display(description="SLPS priority")
    def slps_priority_display(self, obj):
        if obj.scheme.department.code == "HLT" and not is_health_application(obj):
            return "Not scored"
        if is_housing_application(obj):
            extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
            if extra.get("housing_item_code") == "VB-G-EMPLOYMENT" and extra.get("housing_deadline_verified"):
                return "Verified employment deadline — review first"
            if (
                extra.get("housing_item_code") in HOUSING_SLPS_CODES
                and extra.get("is_urgent")
                and extra.get("urgency_verified")
            ):
                return "Verified emergency — review now"
            return extra.get("housing_slps_priority", "Not scored")
        if is_labour_application(obj):
            extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
            if obj.priority == "Critical" and not extra.get("critical_confirmed"):
                return "Critical — awaiting officer confirmation"
        if is_postal_application(obj):
            extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
            return extra.get("postal_slps_priority", "Not scored")
        return obj.priority

    @admin.display(description="Labour SLPS review")
    def labour_critical_state(self, obj):
        if not is_labour_application(obj):
            return "—"
        extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
        if obj.priority == "Critical":
            return "Confirmed" if extra.get("critical_confirmed") else "Needs officer confirmation"
        if extra.get("statutory_deadline_date"):
            return "Deadline verified" if extra.get("statutory_deadline_verified") else "Deadline needs verification"
        return "—"

    @admin.action(description="Confirm Critical priority after exceptional-urgency review")
    def verify_selected_labour_critical(self, request, queryset):
        count = 0
        for application in queryset.select_related("scheme__department"):
            if not is_labour_application(application) or application.priority != "Critical":
                continue
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            if not str(extra.get("critical_exception_reason") or "").strip():
                continue
            extra["critical_confirmed"] = True
            extra["critical_confirmed_by"] = request.user.get_username()
            extra["critical_confirmed_at"] = timezone.now().isoformat()
            application.extra_data = extra
            application.save(update_fields=["extra_data"])
            refresh_labour_slps(application)
            count += 1
        self.message_user(request, f"{count} Labour/Skill/MSME Critical case(s) confirmed after officer review. A recorded exceptional-urgency reason is required.")

    @admin.action(description="Verify reported worker vulnerability on selected applications")
    def verify_selected_labour_vulnerability(self, request, queryset):
        count = 0
        for application in queryset.select_related("scheme__department"):
            if not is_labour_application(application):
                continue
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            extra["worker_vulnerability_verified"] = extra.get("worker_vulnerability") != "none"
            extra["worker_vulnerability_verified_by"] = request.user.get_username()
            application.extra_data = extra
            application.save(update_fields=["extra_data"])
            refresh_labour_slps(application)
            count += 1
        self.message_user(request, f"{count} Labour/Skill/MSME vulnerability record(s) reviewed.")

    @admin.action(description="Verify official deadline on selected Labour/MSME applications")
    def verify_selected_labour_deadline(self, request, queryset):
        count = 0
        for application in queryset.select_related("scheme__department"):
            if not is_labour_application(application):
                continue
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            if not extra.get("statutory_deadline_date"):
                continue
            extra["statutory_deadline_verified"] = True
            extra["statutory_deadline_verified_by"] = request.user.get_username()
            extra["statutory_deadline_verified_at"] = timezone.now().isoformat()
            application.extra_data = extra
            application.save(update_fields=["extra_data"])
            refresh_labour_slps(application)
            count += 1
        self.message_user(request, f"{count} official deadline(s) verified. Check the applicable service timeline and meet it regardless of SLPS rank.")

    @admin.display(description="SLPS score")
    def slps_score_display(self, obj):
        if obj.scheme.department.code == "HLT" and not is_health_application(obj):
            return "—"
        if is_housing_application(obj):
            extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
            if extra.get("housing_slps_priority") in {"Not scored", "Pending verification"}:
                return "—"
        return obj.slps_score

    def _update_housing_flags(self, request, queryset, updates, message):
        count = 0
        for application in queryset.select_related("scheme__department"):
            if not is_housing_application(application):
                continue
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            if extra.get("housing_item_code") not in HOUSING_SLPS_CODES:
                continue
            extra.update(updates(application, extra) if callable(updates) else updates)
            application.extra_data = extra
            application.save(update_fields=["extra_data"])
            refresh_housing_slps(application)
            count += 1
        self.message_user(request, f"{count} Housing & Rural Development application(s): {message}.")

    @admin.action(description="Mark selected Housing applications eligible after officer review")
    def mark_selected_housing_eligible(self, request, queryset):
        self._update_housing_flags(
            request, queryset,
            {"housing_eligibility_verified": True, "housing_eligible": True},
            "eligibility marked verified and eligible",
        )

    @admin.action(description="Mark selected Housing applications not eligible after officer review")
    def mark_selected_housing_ineligible(self, request, queryset):
        self._update_housing_flags(
            request, queryset,
            {"housing_eligibility_verified": True, "housing_eligible": False},
            "eligibility marked verified and not eligible",
        )

    @admin.action(description="Verify urgency claims on selected Housing applications")
    def verify_selected_housing_urgency(self, request, queryset):
        self._update_housing_flags(
            request, queryset,
            lambda _application, extra: {"urgency_verified": bool(extra.get("is_urgent"))},
            "urgency reviewed",
        )

    @admin.action(description="Verify vulnerability claims on selected Housing applications")
    def verify_selected_housing_vulnerability(self, request, queryset):
        self._update_housing_flags(
            request, queryset,
            lambda _application, extra: {
                "vulnerability_verified": (
                    extra.get("vulnerability", "none") != "none"
                    or extra.get("housing_condition") not in (None, "", "adequate")
                    or bool(extra.get("livelihood_hardship"))
                )
            },
            "vulnerability reviewed",
        )

    @admin.action(description="Verify employment-demand dates for separate statutory follow-up")
    def verify_selected_housing_deadline(self, request, queryset):
        count = 0
        for application in queryset.select_related("scheme__department"):
            if not is_housing_application(application):
                continue
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            if extra.get("housing_item_code") != "VB-G-EMPLOYMENT" or not extra.get("employment_demand_date"):
                continue
            try:
                demand_date = date.fromisoformat(extra["employment_demand_date"])
            except (TypeError, ValueError):
                continue
            extra["housing_deadline_verified"] = True
            extra["statutory_deadline_date"] = (demand_date + timedelta(days=15)).isoformat()
            extra["statutory_deadline_handling"] = "Separate 15-day employment-demand follow-up"
            application.extra_data = extra
            application.save(update_fields=["extra_data"])
            refresh_housing_slps(application)
            count += 1
        self.message_user(request, f"{count} employment-demand date(s) verified for separate statutory review.")

    @admin.action(description="Verify urgency for selected Health applications")
    def verify_selected_health_urgency(self, request, queryset):
        for application in queryset.select_related("scheme__department"):
            if not is_health_application(application):
                continue
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            if not extra.get("is_urgent"):
                continue
            extra["urgency_verified"] = True
            application.extra_data = extra
            application.save(update_fields=["extra_data"])
            refresh_health_slps(application)

    @admin.display(description="SLPS factor breakdown")
    def slps_breakdown(self, obj):
        extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
        factors = extra.get(
            "postal_slps_factors",
            extra.get("housing_slps_factors",
                extra.get("labour_slps_factors", extra.get("health_slps_factors", extra.get("slps_factors", {})))),
        )
        if obj.scheme.department.code == "HLT" and not is_health_application(obj):
            return "SLPS is not used for this service."
        if is_housing_application(obj) and not factors:
            return "Housing SLPS has not been calculated."
        return format_html("<pre>{}</pre>", json.dumps(factors, indent=2))

    def get_queryset(self, request):
        applications = list(super().get_queryset(request).select_related(
            "citizen", "scheme", "scheme__department", "citizen__citizenprofile"
        ).prefetch_related("documents"))
        education_apps = []
        education_schemes = {}
        applications_by_id = {}
        for application in applications:
            if is_education_application(application):
                app_data = build_application_inputs(application)
                app_data["id"] = application.pk
                education_apps.append(app_data)
                applications_by_id[application.pk] = application
                education_schemes[application.scheme_id] = {
                    "income_limit": application.scheme.max_income,
                    "weight": ITEM_WEIGHTS.get(application.scheme.name, 1.0),
                }

        for score, app_data, breakdown in sort_queue(
            education_apps, education_schemes, today=date.today()
        ):
            application = applications_by_id[app_data["id"]]
            application.slps_score = score
            application.priority = (
                "High" if score >= 70 else "Medium" if score >= 40 else "Low"
            )
            extra = application.extra_data if isinstance(application.extra_data, dict) else {}
            extra["slps_factors"] = breakdown
            application.extra_data = extra
            application.save(update_fields=["slps_score", "priority", "extra_data"])
        for application in applications:
            if is_health_application(application):
                refresh_health_slps(application)
            elif is_housing_application(application):
                refresh_housing_slps(application)
            elif is_labour_application(application):
                refresh_labour_slps(application)
        return super().get_queryset(request).annotate(
            labour_verified_deadline_first=Case(
                When(
                    scheme__department__code="LSM",
                    extra_data__statutory_deadline_verified=True,
                    then=Value(0),
                ),
                default=Value(1),
                output_field=IntegerField(),
            ),
            labour_verified_critical_first=Case(
                When(
                    scheme__department__code="LSM",
                    extra_data__critical_confirmed=True,
                    priority="Critical",
                    then=Value(0),
                ),
                default=Value(1),
                output_field=IntegerField(),
            ),
            housing_statutory_deadline_first=Case(
                When(
                    scheme__department__code="HRD",
                    extra_data__housing_item_code="VB-G-EMPLOYMENT",
                    extra_data__housing_deadline_verified=True,
                    then=Value(0),
                ),
                default=Value(1),
                output_field=IntegerField(),
            ),
            housing_verified_emergency=Case(
                When(
                    scheme__department__code="HRD",
                    extra_data__housing_item_code__in=tuple(HOUSING_SLPS_CODES),
                    extra_data__is_urgent=True,
                    extra_data__urgency_verified=True,
                    then=Value(0),
                ),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("labour_verified_deadline_first", "extra_data__statutory_deadline_date", "housing_statutory_deadline_first", "labour_verified_critical_first", "housing_verified_emergency", "-slps_score", "created_at")

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = Application.objects.filter(pk=obj.pk).values_list("status", flat=True).first()
        if is_health_application(obj):
            extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
            if obj.status in {"Approved", "Rejected"} and previous_status != obj.status:
                extra["health_decided_at"] = timezone.now().isoformat()
            elif obj.status not in {"Approved", "Rejected"}:
                extra.pop("health_decided_at", None)
            obj.extra_data = extra
        elif is_housing_application(obj):
            extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
            if obj.status in {"Approved", "Rejected"} and previous_status != obj.status:
                extra["housing_decided_at"] = timezone.now().isoformat()
            elif obj.status not in {"Approved", "Rejected"}:
                extra.pop("housing_decided_at", None)
            obj.extra_data = extra
        elif is_labour_application(obj):
            extra = obj.extra_data if isinstance(obj.extra_data, dict) else {}
            if obj.status != "Pending":
                extra["labour_last_review_status"] = obj.status
            obj.extra_data = extra
        super().save_model(request, obj, form, change)
        if is_education_application(obj):
            refresh_application_slps(obj)
        elif is_health_application(obj):
            refresh_health_slps(obj)
        elif is_housing_application(obj):
            refresh_housing_slps(obj)
        elif is_labour_application(obj):
            refresh_labour_slps(obj)
        elif is_postal_application(obj):
            refresh_postal_slps(obj)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "application", "secure_download", "is_verified", "uploaded_at")
    list_filter = ("is_verified", "application__scheme__department")
    search_fields = ("name", "application__tracking_id", "application__scheme__name")
    list_editable = ("is_verified",)
    fields = ("application", "name", "uploaded_at", "secure_download", "is_verified")
    readonly_fields = ("application", "name", "uploaded_at", "secure_download")

    @admin.display(description="Private file")
    def secure_download(self, obj):
        if not obj.file:
            return "No file attached"
        url = reverse("officer_document_download", args=[obj.pk])
        return format_html('<a href="{}">Download document</a>', url)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        application = obj.application
        if is_education_application(application):
            refresh_application_slps(application)
        elif is_health_application(application):
            refresh_health_slps(application)
        elif is_housing_application(application):
            refresh_housing_slps(application)
        elif is_labour_application(application):
            refresh_labour_slps(application)
        elif is_postal_application(application):
            refresh_postal_slps(application)

    def delete_model(self, request, obj):
        application = obj.application
        super().delete_model(request, obj)
        if is_education_application(application):
            refresh_application_slps(application)
        elif is_health_application(application):
            refresh_health_slps(application)
        elif is_housing_application(application):
            refresh_housing_slps(application)
        elif is_labour_application(application):
            refresh_labour_slps(application)
        elif is_postal_application(application):
            refresh_postal_slps(application)

    def delete_queryset(self, request, queryset):
        applications = {
            document.application
            for document in queryset.select_related("application__scheme__department")
        }
        super().delete_queryset(request, queryset)
        for application in applications:
            if is_education_application(application):
                refresh_application_slps(application)
            elif is_health_application(application):
                refresh_health_slps(application)
            elif is_housing_application(application):
                refresh_housing_slps(application)
            elif is_labour_application(application):
                refresh_labour_slps(application)
            elif is_postal_application(application):
                refresh_postal_slps(application)
