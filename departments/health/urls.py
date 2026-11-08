from django.urls import path

from . import views

app_name = "health"

urlpatterns = [
    path("", views.health_home, name="home"),
    path("schemes/", views.health_schemes, name="schemes"),
    path("apply/<slug:slug>/", views.health_apply, name="apply"),
]
