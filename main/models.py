#models.py
from datetime import date

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone


class Company(models.Model):
    COMPANY_TYPES = [
        ('PROSPECT', 'Prospect'),
        ('CLIENT', 'Client'),
        ('FORMER_CLIENT', 'Former Client'),
        ('LEAD', 'Lead'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    description = models.TextField()

    # Social Media Fields
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    instagram_handle = models.CharField(max_length=30, blank=True, verbose_name="Instagram Handle")
    twitter_handle = models.CharField(max_length=15, blank=True, verbose_name="Twitter Handle")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    youtube_channel = models.URLField(blank=True, verbose_name="YouTube Channel")
    tiktok_handle = models.CharField(max_length=30, blank=True, verbose_name="TikTok Handle")

    # Additional Social Profiles
    social_links = models.JSONField(default=dict, blank=True,
                                    help_text="Store additional social media links as key-value pairs")

    # Tracking Fields
    previous_call_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_social_links(self):
        """Returns a dictionary of all social media links"""
        social_links = {
            'Facebook': self.facebook_url,
            'Instagram': f'https://instagram.com/{self.instagram_handle}' if self.instagram_handle else '',
            'Twitter': f'https://twitter.com/{self.twitter_handle}' if self.twitter_handle else '',
            'LinkedIn': self.linkedin_url,
            'YouTube': self.youtube_channel,
            'TikTok': f'https://tiktok.com/@{self.tiktok_handle}' if self.tiktok_handle else '',
        }
        # Add any additional social links from the JSONField
        social_links.update(self.social_links)
        return {k: v for k, v in social_links.items() if v}  # Remove empty values

    class Meta:
        verbose_name_plural = "Companies"


class CompanyComment(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.company.name}"


class CustomerCallProfile(models.Model):
    BEST_CONTACT_TIMES = [
        ('MORNING', 'Morning (9AM-12PM)'),
        ('AFTERNOON', 'Afternoon (12PM-5PM)'),
        ('EVENING', 'Evening (5PM-8PM)'),
    ]

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='call_profile')
    best_contact_time = models.CharField(max_length=20, choices=BEST_CONTACT_TIMES, null=True, blank=True)
    decision_maker_name = models.CharField(max_length=200, blank=True)
    decision_maker_title = models.CharField(max_length=200, blank=True)
    gatekeeper_name = models.CharField(max_length=200, blank=True)
    direct_line = models.CharField(max_length=20, blank=True)
    extension = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)

    # Social Media Contact Information
    social_media_contact_name = models.CharField(max_length=200, blank=True,
                                                 help_text="Name of social media manager or contact")
    social_media_contact_email = models.EmailField(blank=True)
    preferred_social_platform = models.CharField(max_length=50, blank=True,
                                                 help_text="Preferred platform for communication")

    def __str__(self):
        return f"Call Profile for {self.company.name}"


class CallOutcome(models.Model):
    OUTCOME_TYPES = [
        ('MEETING_SCHEDULED', 'Meeting Scheduled'),
        ('CALLBACK', 'Call Back Later'),
        ('NOT_AVAILABLE', 'Not Available'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='call_outcomes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call_outcomes')
    outcome_type = models.CharField(max_length=20, choices=OUTCOME_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    # Meeting scheduled details
    meeting_datetime = models.DateTimeField(null=True, blank=True)
    meeting_notes = models.TextField(blank=True)
    meeting_platform = models.CharField(max_length=50, blank=True,
                                        help_text="Platform for virtual meetings (Zoom, Teams, etc.)")

    # Callback details
    callback_datetime = models.DateTimeField(null=True, blank=True)
    callback_notes = models.TextField(blank=True)
    preferred_contact_method = models.CharField(max_length=50, blank=True,
                                                help_text="Phone, Email, or specific social platform")

    # Not available details
    not_available_reason = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Update the company's previous_call_date
        self.company.previous_call_date = timezone.now()
        self.company.save()

        # Update user profile statistics
        profile = self.user.userprofile
        profile.total_calls += 1
        if self.outcome_type == 'MEETING_SCHEDULED':
            profile.total_sales += 1

        # Update success rate
        if profile.total_calls > 0:
            profile.success_rate = (profile.total_sales / profile.total_calls) * 100

        profile.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_outcome_type_display()} - {self.company.name}"

# Add these to your existing UserProfile model if needed
class UserProfile(models.Model):
    """
    Extends the default Django user with dialer-specific fields
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # New fields
    STATUS_CHOICES = (
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Offline')
    role = models.CharField(max_length=50, default='Sales Representative')
    shift = models.CharField(max_length=50, default='9:00 AM - 5:00 PM')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    checked_in = models.BooleanField(default=False)
    total_sales = models.PositiveIntegerField(default=0)
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_calls = models.PositiveIntegerField(default=0)
    yesterday_calls = models.PositiveIntegerField(default=0)  # <--- Add this
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_checkin_time = models.DateTimeField(null=True, blank=True)
    daily_target = models.PositiveIntegerField(default=50)  # how many calls you want in a day
    daily_progress = models.PositiveIntegerField(default=0)  # how many calls done today
    # Store total work seconds
    total_work_seconds = models.PositiveIntegerField(default=0)
    # When user started this session
    session_start = models.DateTimeField(null=True, blank=True)
    # NEW FIELD: "bookmark" which company the user was on last
    last_company = models.ForeignKey(
        'Company',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # If that company is deleted, set last_company to null
        related_name='+',  # We don't need a reverse relationship name
    )
    # For daily reset
    last_daily_reset = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def reset_daily_stats(self):
        """
        Resets total_calls, total_sales, total_hours, and success_rate to 0.
        Call this once per day, e.g. at login or checkin if date has changed.
        """
        self.total_calls = 0
        self.total_sales = 0
        self.total_hours = 0.0
        self.success_rate = 0.0
        self.save()


    def check_and_reset_daily_stats(self):
        today = date.today()
        if self.last_daily_reset != today:
            # 1) Store today's calls into 'yesterday_calls'
            self.yesterday_calls = self.total_calls

            # 2) Reset daily stats (calls, hours, etc.)
            self.reset_daily_stats()  # sets total_calls=0, total_sales=0, etc.

            self.last_daily_reset = today
            self.save()

    def increment_work_time(self, seconds):
        """
        Add 'seconds' to total_work_seconds.
        """
        self.total_work_seconds += seconds
        self.save()

    def get_total_time_hhmmss(self):
        """
        Convert total_work_seconds -> "hh:mm:ss"
        """
        hours = self.total_work_seconds // 3600
        remainder = self.total_work_seconds % 3600
        minutes = remainder // 60
        seconds = remainder % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"