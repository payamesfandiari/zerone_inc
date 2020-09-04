from django.db.models import F, Sum
from django.db.models.fields import DateField
from django.db.models.functions import Cast
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.views.generic import TemplateView
import jdatetime
from .models import Attendance
import logging

logger = logging.getLogger(__name__)


# Create your views here.


class ListAttendance(LoginRequiredMixin, TemplateView):
    template_name = "attend/graph.html"
    date_field = 'sign_in'

    def get_queryset(self):
        return Attendance.objects.filter(user=self.request.user)

    def get_date_range(self, year, month) -> tuple:
        """Return the year for which this view should display data."""
        format = "%Y-%m"
        datestr = f"{year}-{month}"
        start_date = jdatetime.datetime.strptime(datestr, format).date()
        end_date = start_date + jdatetime.timedelta(days=30)
        try:
            return start_date.togregorian(), end_date.togregorian()
        except ValueError:
            raise Http404('Invalid date string “%(datestr)s” given format “%(format)s”' % {
                'datestr': datestr,
                'format': format,
            })

    def get_if_have_next_month(self, current_month):
        qs = self.get_queryset()
        x = qs.values_list('sign_in').latest('sign_in')[0]
        if current_month >= x.month:
            return False
        return True

    def get_if_have_prev_month(self, current_month):
        qs = self.get_queryset()
        x = qs.values_list('sign_in').earlist('sign_in')[0]
        if current_month >= x.month:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(ListAttendance, self).get_context_data(**kwargs)
        year = self.kwargs.get('year', jdatetime.datetime.today().year)
        month = self.kwargs.get('month', jdatetime.datetime.today().month)
        qs = self.get_queryset()
        start_date, end_date = self.get_date_range(year=year, month=month)

        qs = qs.filter(sign_in__lte=end_date, sign_in__gte=start_date) \
            .annotate(length_of_stay=F('sign_out') - F('sign_in'),
                      day_of_work=Cast('sign_in', DateField())) \
            .values('day_of_work') \
            .order_by('day_of_work') \
            .annotate(stay_per_day=Sum('length_of_stay'))
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
        if qs.count() > 0:
            context['attendance_list'] = qs
            context['attendance_overall'] = qs.aggregate(Sum('stay_per_day'))['stay_per_day__sum'].seconds / (
                    192 * 3600)
            return context
        else:
            context['attendance_list'] = None
            return context
