from django.contrib.auth import get_user_model
from rest_framework import serializers

from zerone_inc.zeroslack.models import Attendance

User = get_user_model()


class AttendanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    user = serializers.StringRelatedField()
    sign_in = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    sign_out = serializers.DateTimeField(allow_null=True, format="%Y-%m-%d %H:%M:%S")
    sign_in_persian = serializers.CharField()
    sign_out_persian = serializers.CharField()

    class Meta:
        model = Attendance
        fields = ['id',
                  'user',
                  'sign_in',
                  'sign_out',
                  'sign_in_persian',
                  'sign_out_persian'
                  ]
