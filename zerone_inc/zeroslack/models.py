import jdatetime
from django.db import models
from django.db.models import Sum
from django.contrib.auth import get_user_model
import logging
from django.conf import settings
from django.http import Http404
from slack_sdk import WebClient
from slack_bolt import App
from logging import Logger
from typing import Optional
from uuid import uuid4
from django.db.models import F
from django.utils import timezone
from slack_sdk.oauth import InstallationStore, OAuthStateStore
from slack_sdk.oauth.installation_store import Bot, Installation

logger = logging.getLogger(__name__)

# Create your models here.
User = get_user_model()


def get_date_range(year, month) -> tuple:
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


class SlackBot(models.Model):
    client_id = models.TextField(null=False)
    app_id = models.TextField(null=False)
    enterprise_id = models.TextField(null=True)
    enterprise_name = models.TextField(null=True)
    team_id = models.TextField(null=True)
    team_name = models.TextField(null=True)
    bot_token = models.TextField(null=True)
    bot_id = models.TextField(null=True)
    bot_user_id = models.TextField(null=True)
    bot_scopes = models.TextField(null=True)
    is_enterprise_install = models.BooleanField(null=True)
    installed_at = models.DateTimeField(null=False)

    class Meta:
        indexes = [
            models.Index(
                fields=["client_id", "enterprise_id", "team_id", "installed_at"]
            ),
        ]


class SlackInstallation(models.Model):
    client_id = models.TextField(null=False)
    app_id = models.TextField(null=False)
    enterprise_id = models.TextField(null=True)
    enterprise_name = models.TextField(null=True)
    enterprise_url = models.TextField(null=True)
    team_id = models.TextField(null=True)
    team_name = models.TextField(null=True)
    bot_token = models.TextField(null=True)
    bot_id = models.TextField(null=True)
    bot_user_id = models.TextField(null=True)
    bot_scopes = models.TextField(null=True)
    user_id = models.TextField(null=False)
    user_token = models.TextField(null=True)
    user_scopes = models.TextField(null=True)
    incoming_webhook_url = models.TextField(null=True)
    incoming_webhook_channel = models.TextField(null=True)
    incoming_webhook_channel_id = models.TextField(null=True)
    incoming_webhook_configuration_url = models.TextField(null=True)
    is_enterprise_install = models.BooleanField(null=True)
    token_type = models.TextField(null=True)
    installed_at = models.DateTimeField(null=False)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "client_id",
                    "enterprise_id",
                    "team_id",
                    "user_id",
                    "installed_at",
                ]
            ),
        ]


class SlackOAuthState(models.Model):
    state = models.TextField(null=False)
    expire_at = models.DateTimeField(null=False)


class DjangoInstallationStore(InstallationStore):
    client_id: str

    def __init__(
        self,
        client_id: str,
        logger: Logger,
    ):
        self.client_id = client_id
        self._logger = logger

    @property
    def logger(self) -> Logger:
        return self._logger

    def save(self, installation: Installation):
        i = installation.to_dict()
        i["client_id"] = self.client_id
        SlackInstallation(**i).save()
        b = installation.to_bot().to_dict()
        b["client_id"] = self.client_id
        SlackBot(**b).save()

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        e_id = enterprise_id or None
        t_id = team_id or None
        if is_enterprise_install:
            t_id = None
        rows = (
            SlackBot.objects.filter(enterprise_id=e_id)
                .filter(team_id=t_id)
                .order_by(F("installed_at").desc())[:1]
        )
        if len(rows) > 0:
            b = rows[0]
            return Bot(
                app_id=b.app_id,
                enterprise_id=b.enterprise_id,
                team_id=b.team_id,
                bot_token=b.bot_token,
                bot_id=b.bot_id,
                bot_user_id=b.bot_user_id,
                bot_scopes=b.bot_scopes,
                installed_at=b.installed_at.timestamp(),
            )
        return None

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        e_id = enterprise_id or None
        t_id = team_id or None
        if is_enterprise_install:
            t_id = None
        if user_id is None:
            rows = (
                SlackInstallation.objects.filter(enterprise_id=e_id)
                    .filter(team_id=t_id)
                    .order_by(F("installed_at").desc())[:1]
            )
        else:
            rows = (
                SlackInstallation.objects.filter(enterprise_id=e_id)
                    .filter(team_id=t_id)
                    .filter(user_id=user_id)
                    .order_by(F("installed_at").desc())[:1]
            )

        if len(rows) > 0:
            i = rows[0]
            return Installation(
                app_id=i.app_id,
                enterprise_id=i.enterprise_id,
                team_id=i.team_id,
                bot_token=i.bot_token,
                bot_id=i.bot_id,
                bot_user_id=i.bot_user_id,
                bot_scopes=i.bot_scopes,
                user_id=i.user_id,
                user_token=i.user_token,
                user_scopes=i.user_scopes,
                incoming_webhook_url=i.incoming_webhook_url,
                incoming_webhook_channel_id=i.incoming_webhook_channel_id,
                incoming_webhook_configuration_url=i.incoming_webhook_configuration_url,
                installed_at=i.installed_at.timestamp(),
            )
        return None


class DjangoOAuthStateStore(OAuthStateStore):
    expiration_seconds: int

    def __init__(
        self,
        expiration_seconds: int,
        logger: Logger,
    ):
        self.expiration_seconds = expiration_seconds
        self._logger = logger

    @property
    def logger(self) -> Logger:
        return self._logger

    def issue(self) -> str:
        state: str = str(uuid4())
        expire_at = timezone.now() + timezone.timedelta(seconds=self.expiration_seconds)
        row = SlackOAuthState(state=state, expire_at=expire_at)
        row.save()
        return state

    def consume(self, state: str) -> bool:
        rows = SlackOAuthState.objects.filter(state=state).filter(
            expire_at__gte=timezone.now()
        )
        if len(rows) > 0:
            for row in rows:
                row.delete()
            return True
        return False


app = App(
    signing_secret=settings.SLACK_SIGNING_SECRET,
    token=settings.SLACK_BOT_USER_TOKEN
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
        if not hasattr(in_user, 'taco_score'):
            TacoScoreBoard.objects.create(user=in_user, score=0)

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


@app.message(":taco:")
def handle_taco_giving(client, message, say, ack):
    import re
    regex = re.compile("<([@A-Z0-9]+)?>")
    logger.info(message)
    ack()
    user_id = f"@{message['user']}"
    awarded_user = re.findall(regex, message['text'])
    logger.info(f"{awarded_user}")

    if awarded_user:
        awarded_user = awarded_user[0]
        if user_id != awarded_user:
            user_awarding = User.objects.get(slack_id=user_id[1:])
            if not user_awarding.can_give_tacos():
                say(f"<{user_id}> you have given {user_awarding.tacos_given_today()} tacos. Wait for tomorrow.")
            else:
                say(f"Hey everyone! <{user_id}> just awarded <{awarded_user}>")
                user_awarded = User.objects.get(slack_id=awarded_user[1:])
                user_awarding.award_a_taco(user_awarded, taco_reason=message['text'])
                if user_awarding.can_give_tacos():
                    client.chat_postMessage(channel=user_awarding.slack_id,
                                            text=f"You have given {user_awarding.tacos_given_today()} tacos, "
                                                 f"you still have {':taco:' * user_awarding.tacos_left_to_give()} to give.")
                else:
                    client.chat_postMessage(channel=user_awarding.slack_id,
                                            text=f"You have given {user_awarding.tacos_given_today()} tacos, "
                                                 f"wait for tomorrow please.")
        else:
            say(f"Well...That's awkward <{user_id}>. You cannot award yourself a taco!")


@app.event("team_join")
def ask_for_introduction(event, say):
    welcome_channel_id = "C12345"
    user_id = event["user"]["id"]
    text = f"Welcome to the team, <@{user_id}>! 🎉 You can introduce yourself in this channel."
    say(text=text, channel=welcome_channel_id)
