from django.urls import path

from . import views

app_name = "labour_msme"

urlpatterns = [
    path("", views.labour_home, name="home"),
    path("schemes/", views.labour_schemes, name="schemes"),
    path("services/", views.labour_services, name="services"),
    path("apply/<slug:slug>/", views.labour_apply, name="apply"),
]
