from django.urls import path

from . import views

app_name = "housing_rural"

urlpatterns = [
    path("", views.housing_home, name="home"),
    path("schemes/", views.housing_schemes, name="schemes"),
    path("apply/<slug:slug>/", views.housing_apply, name="apply"),
]
