from django.urls import path

from . import views

app_name = "agriculture"

urlpatterns = [
    path("", views.agriculture_home, name="home"),
    path("schemes/", views.agriculture_schemes, name="schemes"),
    path("apply/<slug:slug>/", views.agriculture_apply, name="apply"),
]
