from django.contrib import admin
from .models import Character, Quality, CharacterQuality, Gear, CharacterGear


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'race', 'archetype', 'role', 'is_complete', 'created_at']
    list_filter = ['race', 'archetype', 'role', 'is_complete']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Quality)
class QualityAdmin(admin.ModelAdmin):
    list_display = ['name', 'quality_type', 'karma_cost', 'is_default']
    list_filter = ['quality_type', 'is_default']
    search_fields = ['name', 'description']


@admin.register(CharacterQuality)
class CharacterQualityAdmin(admin.ModelAdmin):
    list_display = ['character', 'quality', 'added_at']
    list_filter = ['quality__quality_type']
    search_fields = ['character__name', 'quality__name']


@admin.register(Gear)
class GearAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'cost', 'availability', 'essence_cost', 'is_default']
    list_filter = ['category', 'is_default']
    search_fields = ['name', 'description']


@admin.register(CharacterGear)
class CharacterGearAdmin(admin.ModelAdmin):
    list_display = ['character', 'gear', 'quantity', 'total_cost', 'acquired_at']
    list_filter = ['gear__category']
    search_fields = ['character__name', 'gear__name']
