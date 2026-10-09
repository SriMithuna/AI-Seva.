from django.contrib import admin
from .models import (Department, Scheme, CategoryWeights, CitizenProfile,
                     OfficerProfile, Application, Document, StatusRemark)


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'item_type', 'access_level', 'is_active')
    list_filter = ('department', 'item_type', 'access_level')
    search_fields = ('name',)


admin.site.register([Department, CategoryWeights, CitizenProfile,
                     OfficerProfile, Application, Document, StatusRemark])