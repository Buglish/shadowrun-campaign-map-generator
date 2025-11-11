from django.contrib import admin
from .models import Campaign, Session, SessionObjective


class SessionInline(admin.TabularInline):
    """Inline session display in campaign admin"""
    model = Session
    extra = 0
    fields = ['session_number', 'title', 'status', 'scheduled_date', 'actual_date']
    readonly_fields = ['session_number']


class SessionObjectiveInline(admin.TabularInline):
    """Inline objective display in session admin"""
    model = SessionObjective
    extra = 1
    fields = ['description', 'is_completed', 'completion_notes']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin interface for Campaign model"""
    list_display = ['name', 'game_master', 'status', 'session_count', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description', 'game_master__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['characters', 'maps', 'players']
    inlines = [SessionInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'game_master', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Campaign Settings', {
            'fields': ('starting_karma', 'starting_resources')
        }),
        ('Relationships', {
            'fields': ('characters', 'maps', 'players')
        }),
        ('Notes', {
            'fields': ('player_notes', 'gm_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin interface for Session model"""
    list_display = ['__str__', 'campaign', 'status', 'scheduled_date', 'actual_date', 'karma_awarded']
    list_filter = ['status', 'campaign', 'scheduled_date']
    search_fields = ['title', 'description', 'campaign__name']
    readonly_fields = ['created_at', 'updated_at', 'duration_hours', 'is_upcoming']
    filter_horizontal = ['maps_used', 'characters_present']
    inlines = [SessionObjectiveInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('campaign', 'session_number', 'title', 'description')
        }),
        ('Scheduling', {
            'fields': ('status', 'scheduled_date', 'actual_date', 'duration_minutes', 'duration_hours', 'is_upcoming')
        }),
        ('Session Content', {
            'fields': ('characters_present', 'maps_used')
        }),
        ('Notes', {
            'fields': ('gm_notes', 'session_notes', 'player_summary')
        }),
        ('Rewards & Combat', {
            'fields': ('karma_awarded', 'nuyen_awarded', 'encounters_faced', 'enemies_defeated')
        }),
        ('Important Events', {
            'fields': ('objectives_completed', 'important_npcs', 'loot_acquired')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessionObjective)
class SessionObjectiveAdmin(admin.ModelAdmin):
    """Admin interface for SessionObjective model"""
    list_display = ['__str__', 'session', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'session__campaign']
    search_fields = ['description', 'session__title', 'session__campaign__name']
    readonly_fields = ['created_at']

    fieldsets = (
        (None, {
            'fields': ('session', 'description', 'is_completed', 'completion_notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
