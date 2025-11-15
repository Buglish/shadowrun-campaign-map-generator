from django.contrib import admin
from .models import Campaign, Session, SessionObjective, CombatEncounter, CombatParticipant, CombatEffect, CombatLog


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


class CombatParticipantInline(admin.TabularInline):
    """Inline participant display in combat admin"""
    model = CombatParticipant
    extra = 0
    fields = ['name', 'team', 'initiative', 'current_hp', 'max_hp', 'is_active', 'is_defeated']
    readonly_fields = ['is_defeated']


class CombatLogInline(admin.TabularInline):
    """Inline combat log display in combat encounter admin"""
    model = CombatLog
    extra = 0
    fields = ['round_number', 'event_type', 'description', 'actor', 'target', 'timestamp']
    readonly_fields = ['round_number', 'event_type', 'description', 'actor', 'target', 'timestamp']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        """Prevent manual adding of logs through admin"""
        return False


@admin.register(CombatEncounter)
class CombatEncounterAdmin(admin.ModelAdmin):
    """Admin interface for CombatEncounter model"""
    list_display = ['__str__', 'session', 'status', 'current_round', 'participant_count', 'created_at']
    list_filter = ['status', 'session__campaign', 'created_at']
    search_fields = ['name', 'description', 'session__title', 'session__campaign__name']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'ended_at', 'participant_count', 'current_participant']
    inlines = [CombatParticipantInline, CombatLogInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('session', 'name', 'description', 'status')
        }),
        ('Combat Tracking', {
            'fields': ('current_round', 'current_turn', 'current_participant', 'participant_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'started_at', 'ended_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CombatParticipant)
class CombatParticipantAdmin(admin.ModelAdmin):
    """Admin interface for CombatParticipant model"""
    list_display = ['name', 'encounter', 'team', 'initiative', 'current_hp', 'max_hp', 'condition', 'is_active']
    list_filter = ['team', 'is_active', 'is_defeated', 'encounter__session__campaign']
    search_fields = ['name', 'notes', 'encounter__name']
    readonly_fields = ['created_at', 'hp_percentage', 'condition']

    fieldsets = (
        ('Basic Information', {
            'fields': ('encounter', 'character', 'name', 'team')
        }),
        ('Combat Stats', {
            'fields': ('initiative', 'max_hp', 'current_hp', 'hp_percentage', 'condition')
        }),
        ('Shadowrun Damage', {
            'fields': ('physical_damage', 'stun_damage', 'edge_current', 'edge_max')
        }),
        ('Defensive Stats', {
            'fields': ('armor', 'dodge_pool')
        }),
        ('Status', {
            'fields': ('is_active', 'is_defeated', 'notes')
        }),
        ('Position', {
            'fields': ('map_x', 'map_y'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CombatEffect)
class CombatEffectAdmin(admin.ModelAdmin):
    """Admin interface for CombatEffect model"""
    list_display = ['name', 'participant', 'effect_type', 'rounds_remaining', 'is_active', 'created_at']
    list_filter = ['effect_type', 'is_active', 'participant__encounter__session__campaign']
    search_fields = ['name', 'description', 'participant__name']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('participant', 'name', 'effect_type', 'description')
        }),
        ('Duration', {
            'fields': ('duration_rounds', 'rounds_remaining', 'is_active')
        }),
        ('Modifiers', {
            'fields': ('modifiers',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CombatLog)
class CombatLogAdmin(admin.ModelAdmin):
    """Admin interface for CombatLog model"""
    list_display = ['__str__', 'encounter', 'event_type', 'round_number', 'actor', 'target', 'formatted_timestamp']
    list_filter = ['event_type', 'round_number', 'encounter__session__campaign', 'timestamp']
    search_fields = ['description', 'encounter__name', 'actor__name', 'target__name']
    readonly_fields = ['encounter', 'event_type', 'round_number', 'description', 'actor', 'target', 'data', 'timestamp', 'formatted_timestamp']

    fieldsets = (
        ('Event Information', {
            'fields': ('encounter', 'event_type', 'round_number', 'description')
        }),
        ('Participants', {
            'fields': ('actor', 'target')
        }),
        ('Additional Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('timestamp', 'formatted_timestamp'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual adding of logs through admin"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup purposes"""
        return True
