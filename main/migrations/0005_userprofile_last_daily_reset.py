# Generated by Django 5.1.5 on 2025-01-16 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_userprofile_last_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_daily_reset',
            field=models.DateField(blank=True, null=True),
        ),
    ]
