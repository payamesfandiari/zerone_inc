import redis
import slack
import logging
from django.utils import timezone, datetime_safe
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response

from zerone_inc.attend.models import Attendance

logger = logging.getLogger(__name__)
User = get_user_model()

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=settings.REDIS_DB)


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
                Attendance.objects.create(user=user,
                                          sign_in=datetime_safe.datetime.fromtimestamp(
                                              float(existed),
                                              tz=timezone.get_current_timezone()),
                                          sign_out=timezone.localtime(timezone.now())
                                          )
                redis_instance.set(user.username, timezone.localtime(timezone.now()).timestamp())
            response_msg = ":wave:, Hello <@%s>" % user.name
        elif op == 'out':
            existed = redis_instance.get(user.username)
            if existed:
                Attendance.objects.create(user=user,
                                          sign_in=datetime_safe.datetime.fromtimestamp(
                                              float(existed),
                                              tz=timezone.get_current_timezone()),
                                          sign_out=timezone.localtime(timezone.now())
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
