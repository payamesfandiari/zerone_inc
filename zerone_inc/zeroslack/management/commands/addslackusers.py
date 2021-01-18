from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings
import slack

# Create your models here.
User = get_user_model()


class Command(BaseCommand):
    help = 'Add Slack Team into Database'

    def handle(self, *args, **options):
        client = slack.WebClient(token=settings.SLACK_BOT_USER_TOKEN)
        response = client.users_list()
        users = [u for u in response["members"] if not u['is_bot']]
        for u in users:
            if u.get('deleted', False):
                continue
            profile = u["profile"]
            email = profile.get("email", None)
            if email is None:
                continue
            in_user, created = User.objects.get_or_create(email=email)
            if not created:
                self.stdout.write(self.style.WARNING('User "%s" already exist.' % in_user.name))
                continue
            in_user.username = u.get('name',email)
            in_user.name = profile.get('real_name', email)
            in_user.is_superuser = u.get('is_admin', False)
            in_user.team_id = u.get('team_id', '')
            in_user.slack_id = u.get('id', '')
            in_user.title = profile.get('title', 'member')
            in_user.save()
            self.stdout.write(self.style.SUCCESS('Successfully Add User "%s"' % in_user.name))
