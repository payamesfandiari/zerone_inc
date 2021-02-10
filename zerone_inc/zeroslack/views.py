from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import jdatetime
import logging
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from slack_bolt.adapter.django import SlackRequestHandler
# Create your views here.
from .models import app, get_date_range

logger = logging.getLogger(__name__)

# Create your views here.
handler = SlackRequestHandler(app=app)


@csrf_exempt
def events(request: HttpRequest):
    return handler.handle(request)


def oauth(request: HttpRequest):
    return handler.handle(request)


class ListAttendance(LoginRequiredMixin, TemplateView):
    template_name = "zeroslack/graph.html"
    date_field = 'sign_in'

    def get_context_data(self, **kwargs):
        context = super(ListAttendance, self).get_context_data(**kwargs)
        year = self.kwargs.get('year', jdatetime.datetime.today().year)
        month = self.kwargs.get('month', jdatetime.datetime.today().month)
        start_date, end_date = get_date_range(year=year, month=month)
        qs = self.request.user.get_lenght_of_stay_in_month(start_date, end_date)
        context['next_month'] = month + 1
        context['next_year'] = year
        context['prev_month'] = month - 1
        context['prev_year'] = year
        if month > 12:
            context['next_month'] = 1
            context['next_year'] = year + 1
        if month < 1:
            context['prev_month'] = 12
            context['prev_year'] = year - 1
        context['next_month_label'] = jdatetime.date(
            year=context['next_year'],
            month=context['next_month'],
            day=1).strftime('%B %Y')
        context['prev_month_label'] = jdatetime.date(
            year=context['prev_year'],
            month=context['prev_month'],
            day=1).strftime('%B %Y')
        if qs:
            context['attendance_overall'] = round(qs.seconds / (192 * 3600), 3)
            return context
        else:
            return context
