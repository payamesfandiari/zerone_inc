from django.db import models
from django.db.models import Sum
from django.contrib.auth import get_user_model
import logging
from django.conf import settings
from slack_bolt import App
from slack_bolt.authorization import AuthorizeResult
from slack_sdk import WebClient

import re

logger = logging.getLogger(__name__)

# Create your models here.
User = get_user_model()


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sign_in = models.DateTimeField()
    sign_out = models.DateTimeField(null=True)
    sign_in_persian = models.CharField(max_length=999, null=True, blank=True)
    sign_out_persian = models.CharField(max_length=999, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}(in:{self.sign_in},out{self.sign_out})"


class TacoGiven(models.Model):
    awarding_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='awarding_user')
    awarded_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='awarded_user')
    taco_awarded_timestamp = models.DateTimeField(auto_now_add=True)
    taco_awarded_date = models.DateField(auto_now_add=True)
    reason = models.CharField(default="For being awesome", max_length=9999)


class TacoScoreBoard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='taco_score')
    score = models.IntegerField()

    @classmethod
    def get_team_score(cls):
        return cls.objects.all().aggregate(Sum('taco_score'))


class TacoGift(models.Model):
    taco_gift = models.CharField(max_length=999)
    number_of_available_gifts = models.PositiveIntegerField(default=1)
    auto_replenish = models.BooleanField(default=True)
    team_gifts = models.BooleanField(default=False)
    number_of_tacos_required = models.PositiveIntegerField(default=100)

    def can_purchased_the_gift(self):
        if self.number_of_available_gifts < 1:
            return False
        return True


class TacoGiftPurchased(models.Model):
    gift = models.ForeignKey('TacoGift', on_delete=models.CASCADE)
    purchased_date = models.DateTimeField(auto_now_add=True)
    purchased_by = models.ForeignKey(User, on_delete=models.CASCADE)


app = App(
    token=settings.SLACK_BOT_USER_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
)


@app.command('/attend')
def attend_command(body, ack, say, command):
    ack(f"<@{body['user_name']}> wait for me to check our records...")
    try:
        user = User.objects.get(slack_id=command['user_id'])
    except Exception:
        user = User.objects.get(username=command['username'])

    sub_command = command.get('text', None)
    if sub_command is None:
        say("Are you trying to log in? Specify [in|out] please...")
        return
    if sub_command.lower().strip() == 'in':
        what_to_say = user.sign_in()
    elif sub_command.lower().strip() == 'out':
        what_to_say = user.sign_out()
    else:
        what_to_say = {"text": "Are you trying to log in? Specify [in|out] please..."}

    say(**what_to_say)


@app.command('/updateusers')
def update_all_users(body, ack, say, client: WebClient):
    ack("Showing user list...")
    users = [u for u in client.users_list()["members"] if not (u['is_bot'] or u['deleted'])]
    for u in users:
        username = u['name']
        profile = u["profile"]
        email = profile.get("email", None)
        if email is None:
            continue
        in_user, created = User.objects.get_or_create(email=email,
                                                      username=username)
        if not created:
            logger.warning('User "%s" already exist.' % in_user.name)

        in_user.username = u.get('name', email)
        in_user.name = profile.get('real_name', email)
        in_user.is_superuser = u.get('is_admin', False)
        in_user.team_id = u.get('team_id', '')
        in_user.slack_id = u.get('id', '')
        in_user.first_name = profile.get('first_name', '')
        in_user.last_name = profile.get('last_name', '')
        in_user.title = profile.get('title', 'member')
        if in_user.password is None:
            in_user.set_password('1qazxsw@')
        in_user.save()

    say('Thanks...')


@app.action("sign_out_button_clicked")
def action_button_click(body, ack, respond):
    # Acknowledge the action
    ack()
    try:
        user = User.objects.get(slack_id=body['user']['id'])
    except Exception:
        user = User.objects.get(username=body['user']['username'])

    what_to_say = user.sign_out()
    respond(what_to_say['text'], replace_original=True)


@app.event("team_join")
def ask_for_introduction(event, say):
    welcome_channel_id = "C12345"
    user_id = event["user"]["id"]
    text = f"Welcome to the team, <@{user_id}>! 🎉 You can introduce yourself in this channel."
    say(text=text, channel=welcome_channel_id)
