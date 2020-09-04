from django.urls import path

from .views import ListAttendance
from .api.views import AttendanceDashboard, AttendanceView

app_name = "attend"
urlpatterns = [
    # path("", view=event_hook, name="attend_event"),
    path("attend/", view=AttendanceView.as_view()),
    path("dashboard/<int:year>/<int:month>/", ListAttendance.as_view(), name="dashboard"),
    path("table/<int:year>/<int:month>/", view=AttendanceDashboard.as_view(), name="dashboard-table")
]
