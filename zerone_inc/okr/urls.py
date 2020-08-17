from django.urls import path

from zerone_inc.okr.views import SurveyList

app_name = "okr"
urlpatterns = [
    # path("", view=event_hook, name="attend_event"),
    path("", view=SurveyList.as_view(),name="list")
]
