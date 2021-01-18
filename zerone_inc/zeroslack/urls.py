from django.urls import path

from . import views

app_name = "zeroslack"

urlpatterns = [
    path("events", views.events, name="handle"),
    path("install", views.oauth, name="install"),
    path("oauth_redirect", views.oauth, name="oauth_redirect"),
]
