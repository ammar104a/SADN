# Generated by Django 5.1.5 on 2025-01-16 09:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked_in', models.BooleanField(default=False)),
                ('total_sales', models.PositiveIntegerField(default=0)),
                ('total_hours', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('total_calls', models.PositiveIntegerField(default=0)),
                ('success_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('last_checkin_time', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
