# Generated by Django 3.0.8 on 2021-01-18 14:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('zeroslack', '0002_tacogift_tacogiftpurchased_tacogiven_tacoscoreboard'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlackBot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.TextField()),
                ('app_id', models.TextField()),
                ('enterprise_id', models.TextField(null=True)),
                ('enterprise_name', models.TextField(null=True)),
                ('team_id', models.TextField(null=True)),
                ('team_name', models.TextField(null=True)),
                ('bot_token', models.TextField(null=True)),
                ('bot_id', models.TextField(null=True)),
                ('bot_user_id', models.TextField(null=True)),
                ('bot_scopes', models.TextField(null=True)),
                ('is_enterprise_install', models.BooleanField(null=True)),
                ('installed_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='SlackInstallation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.TextField()),
                ('app_id', models.TextField()),
                ('enterprise_id', models.TextField(null=True)),
                ('enterprise_name', models.TextField(null=True)),
                ('enterprise_url', models.TextField(null=True)),
                ('team_id', models.TextField(null=True)),
                ('team_name', models.TextField(null=True)),
                ('bot_token', models.TextField(null=True)),
                ('bot_id', models.TextField(null=True)),
                ('bot_user_id', models.TextField(null=True)),
                ('bot_scopes', models.TextField(null=True)),
                ('user_id', models.TextField()),
                ('user_token', models.TextField(null=True)),
                ('user_scopes', models.TextField(null=True)),
                ('incoming_webhook_url', models.TextField(null=True)),
                ('incoming_webhook_channel', models.TextField(null=True)),
                ('incoming_webhook_channel_id', models.TextField(null=True)),
                ('incoming_webhook_configuration_url', models.TextField(null=True)),
                ('is_enterprise_install', models.BooleanField(null=True)),
                ('token_type', models.TextField(null=True)),
                ('installed_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='SlackOAuthState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.TextField()),
                ('expire_at', models.DateTimeField()),
            ],
        ),
        migrations.AddIndex(
            model_name='slackinstallation',
            index=models.Index(fields=['client_id', 'enterprise_id', 'team_id', 'user_id', 'installed_at'],
                               name='zeroslack_s_client__1a92d4_idx'),
        ),
        migrations.AddIndex(
            model_name='slackbot',
            index=models.Index(fields=['client_id', 'enterprise_id', 'team_id', 'installed_at'],
                               name='zeroslack_s_client__365a0a_idx'),
        ),
    ]
