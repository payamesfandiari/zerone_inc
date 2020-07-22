from django.urls import path

from zerone_inc.attend.api.views import AttendanceView

app_name = "attend"
urlpatterns = [
    # path("", view=event_hook, name="attend_event"),
    path("", view=AttendanceView.as_view())
]
