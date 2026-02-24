from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("config/", views.config_dashboard, name="config_dashboard"),
]
