from django.contrib import admin
from django.urls import path, include
from portal import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # login
    path('login/', views.citizen_login, name='citizen_login'),
    path('logout/', views.citizen_logout, name='citizen_logout'),

    # Homepage
    path('', views.home, name='home'),

   path('departments/education/', include('departments.education.urls')),

   path('departments/agriculture/', include('departments.agriculture.urls')),

    # Scheme recommendations
    path(
        'api/recommendations/',
        views.scheme_recommendations,
        name='scheme_recommendations',
    ),

    # Chatbot
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
    path(
        'officer/documents/<int:document_id>/download/',
        views.officer_document_download,
        name='officer_document_download',
    ),

    # Citizen registration
    path('register/', views.citizen_register, name='citizen_register'),

    # Service application
    path('services/abha/', views.abha_service, name='abha_service'),
    path('services/abha/apply/', views.abha_apply, name='abha_apply'),

  path('dashboard/', views.citizen_dashboard, name='citizen_dashboard'),

    # Application confirmation and tracking
    path(
        'applications/track/',
        views.application_track,
        name='application_track',
    ),
    path(
        'applications/<str:tracking_id>/',
        views.application_confirmation,
        name='application_confirmation',
    ),
]
