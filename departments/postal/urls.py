from django.urls import path

from . import views

app_name = "postal"
urlpatterns = [
    path("", views.postal_home, name="home"),
    path("schemes/", views.postal_schemes, name="schemes"),
    path("services/", views.postal_services, name="services"),
    path("apply/<slug:slug>/", views.postal_apply, name="apply"),
]
