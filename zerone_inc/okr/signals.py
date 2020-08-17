from django.db.models.signals import post_save
from django.dispatch import receiver
from zerone_inc.okr.models import SurveyForUser

from survey.models import Response


@receiver(post_save, sender=Response)
def set_survey_to_invalid(sender, instance, created, **kwargs):
    s = SurveyForUser.objects.get(user=instance.user, survey=instance.survey)
    s.is_valid = False
    s.save()
