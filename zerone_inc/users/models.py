import jdatetime
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, DateField, Sum, F
from django.db.models.functions import Cast
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, date
from django.conf import settings


# from zerone_inc.zeroslack.models import TacoScoreBoard


class User(AbstractUser):
    """Default user for ZerOne Inc.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    team_id = CharField(_("Team ID"), blank=True, null=True, max_length=999)
    slack_id = CharField(_("Slack ID"), blank=True, null=True, max_length=999)
    title = CharField(_("Title"), blank=True, null=True, max_length=999)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def tacos_given_today(self):
        num_tacos_give = self.awarding_user.filter(
            taco_awarded_date=date.today()
        ).count()
        return num_tacos_give

    def can_give_tacos(self):
        if self.tacos_given_today() >= settings.NUMBER_OF_TACOS_PER_DAY:
            return False
        else:
            return True

    def tacos_left_to_give(self):
        return settings.NUMBER_OF_TACOS_PER_DAY - self.tacos_given_today()

    def award_a_taco(self, another_user, taco_reason):
        if self.can_give_tacos():
            other_user = User.objects.get(username=another_user)
            self.awarding_user.create(
                awarded_user=other_user,
                reason=taco_reason,
            )
            other_user.taco_score.score += 1
            other_user.taco_score.save()
            return f"{self.username} awarded {another_user.username} with a Taco..."
        else:
            return f"{self.username} cannot award more tacos today..."

    def get_today_sign_ins(self):
        return self.attendance_set.filter(sign_in__date=date.today(), sign_out=None)

    def check_if_already_signed_in(self):
        todays_sign_ins = self.get_today_sign_ins()
        if todays_sign_ins.count() > 0:
            return True
        else:
            return False

    def check_if_still_on(self):
        pass

    def check_if_signed_off(self):
        pass

    def sign_in(self):
        out = {
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"Hey there <@{self.username}>!"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Sign Out !"},
                        "action_id": "sign_out_button_clicked"
                    }
                }
            ],
            "text": f"Hey there <@{self.username}>!"}
        sign_in_datetime = timezone.localtime(timezone.now())
        if self.check_if_already_signed_in():
            return {"text": 'You have already signed in...Please sign out first and try again.'}
        self.attendance_set.create(
            sign_in=sign_in_datetime,
            sign_in_persian=jdatetime.datetime.fromgregorian(datetime=sign_in_datetime,
                                                             locale='fa_IR').strftime(
                "%a, %d %b %Y %H:%M:%S")
        )
        return out

    def sign_out(self):
        sign_out_datetime = timezone.localtime(timezone.now())

        if self.check_if_already_signed_in():
            todays_sign_in = self.get_today_sign_ins().first()
            todays_sign_in.sign_out = sign_out_datetime
            todays_sign_in.sign_out_persian = jdatetime.datetime.fromgregorian(datetime=sign_out_datetime,
                                                                               locale='fa_IR').strftime(
                "%a, %d %b %Y %H:%M:%S")
            todays_sign_in.save()
            return {"text": f"Goodbye  <@{self.username}> :wave:. Take care."}
        return {"text": f"Hmmmm...I don't think you have signed in <@{self.username}>!"}

    def get_length_of_stay_per_day(self, start_date, end_date):
        return self.attendance_set.filter(sign_in__lte=end_date, sign_in__gte=start_date).annotate(
            length_of_stay=F('sign_out') - F('sign_in'), day_of_work=Cast('sign_in', DateField())).values(
            'day_of_work').order_by('day_of_work').annotate(stay_per_day=Sum('length_of_stay'))

    def get_list_of_signins(self, start_date, end_date):
        return self.attendance_set.filter(sign_in__lte=end_date, sign_in__gte=start_date).order_by('sign_in')
