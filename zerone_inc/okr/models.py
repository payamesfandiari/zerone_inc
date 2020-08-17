from django.db import models
from django.contrib.auth import get_user_model
from survey.models import Survey

# Create your models here.
User = get_user_model()


class SurveyForUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField("Date of Assignment", auto_now_add=True)
    is_valid = models.BooleanField("Is this valid?", default=True)

