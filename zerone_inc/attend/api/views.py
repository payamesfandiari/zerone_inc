import redis
import slack
import logging
from django.utils import timezone, datetime_safe
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
import jdatetime
from zerone_inc.attend.models import Attendance
from .serializers import AttendanceSerializer

logger = logging.getLogger(__name__)
User = get_user_model()

redis_instance = redis.StrictRedis.from_url(settings.REDIS_URL)


class AttendanceView(APIView):
    http_method_names = ['get', 'post']

    def check_permissions(self, request):
        json_dict = request.POST
        for permission in self.get_permissions():
            if json_dict.get('token', '') != settings.SLACK_VERIFICATION_TOKEN:
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )

    def get(self, request, **kwargs):
        return self.post(request, **kwargs)

    def post(self, request, **kwargs):
        client = slack.WebClient(token=settings.SLACK_BOT_USER_TOKEN)
        json_dict = request.POST
        op = json_dict['text'].strip()
        user = User.objects.get(username=json_dict['user_name'])
        channel = json_dict['channel_id']

        if op == 'in':
            # check if previous time exist
            existed = redis_instance.get(user.username)
            if not existed:
                redis_instance.set(user.username, timezone.localtime(timezone.now()).timestamp())
            else:
                sign_in_datetime = datetime_safe.datetime.fromtimestamp(
                    float(existed),
                    tz=timezone.get_current_timezone())
                sign_out_datetime = timezone.localtime(timezone.now())
                Attendance.objects.create(user=user,
                                          sign_in=sign_in_datetime,
                                          sign_out=sign_out_datetime,
                                          sign_in_persian=jdatetime.datetime.fromgregorian(datetime=sign_in_datetime,
                                                                                           locale='fa_IR').strftime(
                                              "%a, %d %b %Y %H:%M:%S"),
                                          sign_out_persian=jdatetime.datetime.fromgregorian(datetime=sign_out_datetime,
                                                                                            locale='fa_IR').strftime(
                                              "%a, %d %b %Y %H:%M:%S")
                                          )
                redis_instance.set(user.username, timezone.localtime(timezone.now()).timestamp())
            response_msg = ":wave:, Hello <@%s>" % user.name
        elif op == 'out':
            existed = redis_instance.get(user.username)
            if existed:
                sign_in_datetime = datetime_safe.datetime.fromtimestamp(
                    float(existed),
                    tz=timezone.get_current_timezone())
                sign_out_datetime = timezone.localtime(timezone.now())
                Attendance.objects.create(user=user,
                                          sign_in=sign_in_datetime,
                                          sign_out=sign_out_datetime,
                                          sign_in_persian=jdatetime.datetime.fromgregorian(datetime=sign_in_datetime,
                                                                                           locale='fa_IR').strftime(
                                              "%a, %d %b %Y %H:%M:%S"),
                                          sign_out_persian=jdatetime.datetime.fromgregorian(datetime=sign_out_datetime,
                                                                                            locale='fa_IR').strftime(
                                              "%a, %d %b %Y %H:%M:%S")
                                          )
                redis_instance.delete(user.username)
                response_msg = ":wave:, Goodbye <@%s>" % user.name
            else:
                response_msg = "Are you sure you had logged in?<@%s>" % user.name

        elif op == 'dashboard':
            response_msg = ":wave:, Not implemented yet <@%s>" % user.name
        else:
            response_msg = """Use the command like this : `/attend [in | out]`"""
        client.chat_postMessage(channel=channel, text=response_msg)
        return Response(status=200)


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
        queryset = self.filter_queryset(self.get_queryset()).filter(sign_in__lte=end_date, sign_in__gte=start_date)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data={
            'data': serializer.data,
            "draw": request.GET.get('draw', 1),
            "recordsTotal": queryset.count(),
            "recordsFiltered": queryset.count(),
        })
