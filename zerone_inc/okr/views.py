from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import SurveyForUser


# Create your views here.

class SurveyList(LoginRequiredMixin, ListView):
    model = SurveyForUser
    template_name = 'okr/survey_list.html'

    def get_queryset(self) -> QuerySet:
        qs = self.model.objects.filter(user=self.request.user, is_valid=True)
        return qs
