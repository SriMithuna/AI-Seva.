from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
import json
from datetime import date
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


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_id", "full_name", "scheme", "status", "priority_group_verified", "health_urgency_state",
        "slps_priority_display", "slps_score_display", "created_at",
    )
    list_editable = ("priority_group_verified",)
    list_filter = ("status", "priority", "scheme__department", "scheme")
    search_fields = ("tracking_id", "full_name", "citizen__username", "scheme__name")
    readonly_fields = ("slps_priority_display", "slps_score_display", "slps_breakdown")
    ordering = ("-slps_score", "created_at")
    actions = ("verify_selected_health_urgency",)

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

    @admin.display(description="SLPS priority")
    def slps_priority_display(self, obj):
        if obj.scheme.department.code == "HLT" and not is_health_application(obj):
            return "Not scored"
        return obj.priority

    @admin.display(description="SLPS score")
    def slps_score_display(self, obj):
        if obj.scheme.department.code == "HLT" and not is_health_application(obj):
            return "—"
        return obj.slps_score

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
        factors = extra.get("health_slps_factors", extra.get("slps_factors", {}))
        if obj.scheme.department.code == "HLT" and not is_health_application(obj):
            return "SLPS is not used for this service."
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
        return super().get_queryset(request).order_by("-slps_score", "created_at")

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
        super().save_model(request, obj, form, change)
        if is_education_application(obj):
            refresh_application_slps(obj)
        elif is_health_application(obj):
            refresh_health_slps(obj)


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

    def delete_model(self, request, obj):
        application = obj.application
        super().delete_model(request, obj)
        if is_education_application(application):
            refresh_application_slps(application)
        elif is_health_application(application):
            refresh_health_slps(application)

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
