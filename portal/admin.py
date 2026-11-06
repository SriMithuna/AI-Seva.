from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
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


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'item_type', 'access_level', 'is_active')
    list_filter = ('department', 'item_type', 'access_level')
    search_fields = ('name',)


admin.site.register([Department, CategoryWeights, CitizenProfile,
                     OfficerProfile, StatusRemark])


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_id", "full_name", "scheme", "status", "priority_group_verified", "priority",
        "slps_score", "created_at",
    )
    list_editable = ("priority_group_verified",)
    list_filter = ("status", "priority", "scheme__department", "scheme")
    search_fields = ("tracking_id", "full_name", "citizen__username", "scheme__name")
    readonly_fields = ("slps_score", "priority", "slps_breakdown")
    ordering = ("-slps_score", "created_at")

    @admin.display(description="SLPS factor breakdown")
    def slps_breakdown(self, obj):
        factors = (obj.extra_data or {}).get("slps_factors", {})
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
        return super().get_queryset(request).order_by("-slps_score", "created_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if is_education_application(obj):
            refresh_application_slps(obj)


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
