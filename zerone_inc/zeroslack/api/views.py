
import logging
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
import jdatetime
from zerone_inc.zeroslack.models import Attendance
from .serializers import AttendanceSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class AttendanceDashboard(ListAPIView):
    http_method_names = ['get', ]
    permission_classes = [IsAuthenticated, ]
    serializer_class = AttendanceSerializer
    renderer_classes = [JSONRenderer, ]

    def get_date_range(self) -> tuple:
        """Return the year for which this view should display data."""
        year = self.kwargs.get('year', jdatetime.datetime.today().year)
        month = self.kwargs.get('month', jdatetime.datetime.today().month)
        format = "%Y-%m"
        datestr = f"{year}-{month}"
        start_date = jdatetime.datetime.strptime(datestr, format).date()
        end_date = start_date + jdatetime.timedelta(days=30)
        try:
            return start_date.togregorian(), end_date.togregorian()
        except ValueError:
            raise NotFound('Invalid date string “%(datestr)s” given format “%(format)s”' % {
                'datestr': datestr,
                'format': format,
            })

    def get_queryset(self):
        return Attendance.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        start_date, end_date = self.get_date_range()
        queryset = self.request.user.get_list_of_signins(start_date=start_date, end_date=end_date)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data={
            'data': serializer.data,
            "draw": request.GET.get('draw', 1),
            "recordsTotal": queryset.count(),
            "recordsFiltered": queryset.count(),
        })
