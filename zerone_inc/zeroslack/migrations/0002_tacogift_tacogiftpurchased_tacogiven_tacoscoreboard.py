# Generated by Django 3.0.8 on 2021-01-17 21:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zeroslack', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TacoGift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taco_gift', models.CharField(max_length=999)),
                ('number_of_available_gifts', models.PositiveIntegerField(default=1)),
                ('auto_replenish', models.BooleanField(default=True)),
                ('team_gifts', models.BooleanField(default=False)),
                ('number_of_tacos_required', models.PositiveIntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='TacoScoreBoard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='taco_score',
                                              to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TacoGiven',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taco_awarded_timestamp', models.DateTimeField(auto_now_add=True)),
                ('taco_awarded_date', models.DateField(auto_now_add=True)),
                ('reason', models.CharField(default='For being awesome', max_length=9999)),
                ('awarded_user',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awarded_user',
                                   to=settings.AUTH_USER_MODEL)),
                ('awarding_user',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awarding_user',
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TacoGiftPurchased',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchased_date', models.DateTimeField(auto_now_add=True)),
                ('gift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zeroslack.TacoGift')),
                ('purchased_by',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
