from django.contrib import admin
from .models import DiceRoll, DicePreset


@admin.register(DiceRoll)
class DiceRollAdmin(admin.ModelAdmin):
    """Admin interface for DiceRoll model"""

    list_display = [
        'user',
        'description',
        'pool_size',
        'total_hits',
        'is_glitch',
        'is_critical_glitch',
        'success',
        'timestamp',
    ]
    list_filter = [
        'is_glitch',
        'is_critical_glitch',
        'success',
        'use_rule_of_six',
        'edge_used',
        'timestamp',
    ]
    search_fields = [
        'user__username',
        'description',
    ]
    readonly_fields = [
        'timestamp',
        'dice_results',
        'total_hits',
        'ones_count',
        'is_glitch',
        'is_critical_glitch',
        'success',
    ]
    fieldsets = (
        ('Roll Information', {
            'fields': ('user', 'timestamp', 'description')
        }),
        ('Parameters', {
            'fields': ('pool_size', 'threshold', 'use_rule_of_six', 'edge_used')
        }),
        ('Results', {
            'fields': (
                'dice_results',
                'total_hits',
                'ones_count',
                'is_glitch',
                'is_critical_glitch',
                'success',
            )
        }),
        ('Context', {
            'fields': ('campaign', 'session', 'character'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'timestamp'


@admin.register(DicePreset)
class DicePresetAdmin(admin.ModelAdmin):
    """Admin interface for DicePreset model"""

    list_display = [
        'name',
        'user',
        'pool_size',
        'threshold',
        'character',
        'created_at',
    ]
    list_filter = [
        'use_rule_of_six',
        'created_at',
    ]
    search_fields = [
        'name',
        'description',
        'user__username',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('Preset Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Default Parameters', {
            'fields': ('pool_size', 'threshold', 'use_rule_of_six')
        }),
        ('Context', {
            'fields': ('character',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
