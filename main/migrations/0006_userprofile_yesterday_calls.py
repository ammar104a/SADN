# Generated by Django 5.1.5 on 2025-01-17 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_userprofile_last_daily_reset'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='yesterday_calls',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
