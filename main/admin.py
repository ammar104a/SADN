from django.contrib import admin
from .models import UserProfile
# Register your models here.
from django.contrib import admin
from .models import Company, CompanyComment, CustomerCallProfile, CallOutcome, UserProfile


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company_type', 'phone_number', 'location', 'website', 'industry', 'created_at', 'updated_at')
    list_filter = ('company_type', 'industry', 'created_at', 'updated_at')
    search_fields = ('name', 'location', 'industry', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company_type', 'phone_number', 'location', 'website', 'industry', 'description')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_handle', 'twitter_handle', 'linkedin_url', 'youtube_channel', 'tiktok_handle', 'social_links')
        }),
        ('Tracking', {
            'fields': ('previous_call_date', 'created_at', 'updated_at')
        }),
    )



class CompanyCommentAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company__name', 'user__username', 'comment')
    readonly_fields = ('created_at',)


class CustomerCallProfileAdmin(admin.ModelAdmin):
    list_display = ('company', 'best_contact_time', 'decision_maker_name', 'gatekeeper_name', 'direct_line', 'notes')
    search_fields = ('company__name', 'decision_maker_name', 'gatekeeper_name', 'direct_line')
    fieldsets = (
        ('Contact Details', {
            'fields': ('company', 'best_contact_time', 'decision_maker_name', 'decision_maker_title', 'gatekeeper_name', 'direct_line', 'extension', 'notes')
        }),
        ('Social Media Contact', {
            'fields': ('social_media_contact_name', 'social_media_contact_email', 'preferred_social_platform')
        }),
    )


class CallOutcomeAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'outcome_type', 'created_at', 'meeting_datetime', 'callback_datetime')
    list_filter = ('outcome_type', 'created_at')
    search_fields = ('company__name', 'user__username', 'outcome_type', 'meeting_notes', 'callback_notes')
    readonly_fields = ('created_at',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'role', 'shift', 'total_calls', 'total_sales', 'success_rate', 'daily_target', 'daily_progress', 'last_checkin_time')
    list_filter = ('status', 'role', 'shift')
    search_fields = ('user__username', 'role')
    readonly_fields = ('total_sales', 'total_calls', 'success_rate', 'yesterday_calls', 'daily_progress', 'last_checkin_time')


# Register the models with their custom admin configurations
admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyComment, CompanyCommentAdmin)
admin.site.register(CustomerCallProfile, CustomerCallProfileAdmin)
admin.site.register(CallOutcome, CallOutcomeAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
