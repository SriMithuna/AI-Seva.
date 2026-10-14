
from django.contrib import admin
from django.urls import path
from portal import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path(
        'api/recommendations/',
        views.scheme_recommendations,
        name='scheme_recommendations',
    ),
]
