from django.db import models

from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sign_in = models.DateTimeField()
    sign_out = models.DateTimeField(null=True)
    sign_in_persian = models.CharField(max_length=999,null=True,blank=True)
    sign_out_persian = models.CharField(max_length=999,null=True,blank=True)
