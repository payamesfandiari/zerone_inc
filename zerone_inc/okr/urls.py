from django.urls import path,re_path

from .views import SurveyList,ConfirmView, IndexView, SurveyCompleted, SurveyDetail,serve_result_csv

app_name = "okr"
urlpatterns = [
    # path("", view=event_hook, name="attend_event"),
    path("", view=SurveyList.as_view(), name="survey-list"),
    # url(r"^$", IndexView.as_view(), name="survey-list"),
    re_path(r"^(?P<id>\d+)/", SurveyDetail.as_view(), name="survey-detail"),
    re_path(r"^csv/(?P<primary_key>\d+)/", serve_result_csv, name="survey-result"),
    re_path(r"^(?P<id>\d+)/completed/", SurveyCompleted.as_view(), name="survey-completed"),
    re_path(r"^(?P<id>\d+)-(?P<step>\d+)/", SurveyDetail.as_view(), name="survey-detail-step"),
    re_path(r"^confirm/(?P<uuid>\w+)/", ConfirmView.as_view(), name="survey-confirmation"),
]
