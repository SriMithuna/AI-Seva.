
from django.urls import path
from . import views

urlpatterns = [
    path('', views.education_home, name='education_home'),
    path('schemes/', views.education_schemes, name='education_schemes'),
    path('apply/<slug:slug>/', views.education_apply, name='education_apply'),
]
