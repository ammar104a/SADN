#signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone

from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, last_checkin_time=timezone.now())

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # When user is saved, save the related profile
    instance.userprofile.save()
