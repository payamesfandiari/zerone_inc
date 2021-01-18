from django.urls import path

from . import views

from .api.views import AttendanceDashboard, AttendanceView

app_name = "zeroslack"

urlpatterns = [
    path("attend/", view=AttendanceView.as_view()),
    path("dashboard/<int:year>/<int:month>/", views.ListAttendance.as_view(), name="dashboard"),
    path("table/<int:year>/<int:month>/", view=AttendanceDashboard.as_view(), name="dashboard-table"),
    path("events", views.events, name="handle"),
    path("install", views.oauth, name="install"),
    path("oauth_redirect", views.oauth, name="oauth_redirect"),
]
