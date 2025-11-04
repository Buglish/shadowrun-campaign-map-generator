from django.contrib import admin
from .models import (
    Character, Quality, CharacterQuality, Gear, CharacterGear,
    Skill, CharacterSkill, Contact, Language,
    Spell, CharacterSpell, AdeptPower, CharacterAdeptPower,
    ComplexForm, CharacterComplexForm
)


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
    list_display = ['name', 'category', 'cost', 'damage', 'armor_rating', 'availability', 'essence_cost', 'is_default']
    list_filter = ['category', 'is_default']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'description', 'cost', 'availability', 'essence_cost', 'is_default')
        }),
        ('Weapon Stats', {
            'fields': ('damage', 'armor_penetration', 'firing_mode', 'recoil_compensation', 'ammo', 'weapon_range'),
            'classes': ('collapse',)
        }),
        ('Armor Stats', {
            'fields': ('armor_rating',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CharacterGear)
class CharacterGearAdmin(admin.ModelAdmin):
    list_display = ['character', 'gear', 'quantity', 'total_cost', 'acquired_at']
    list_filter = ['gear__category']
    search_fields = ['character__name', 'gear__name']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'linked_attribute', 'is_default']
    list_filter = ['category', 'linked_attribute', 'is_default']
    search_fields = ['name', 'description']


@admin.register(CharacterSkill)
class CharacterSkillAdmin(admin.ModelAdmin):
    list_display = ['character', 'skill', 'rating', 'specialization', 'dice_pool']
    list_filter = ['skill__category', 'rating']
    search_fields = ['character__name', 'skill__name', 'specialization']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'character', 'archetype', 'connection', 'loyalty']
    list_filter = ['connection', 'loyalty']
    search_fields = ['name', 'character__name', 'archetype', 'description']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['character', 'name', 'proficiency']
    list_filter = ['proficiency']
    search_fields = ['character__name', 'name']


@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'spell_type', 'range_type', 'duration', 'drain', 'is_default']
    list_filter = ['category', 'spell_type', 'range_type', 'duration', 'is_default']
    search_fields = ['name', 'description']


@admin.register(CharacterSpell)
class CharacterSpellAdmin(admin.ModelAdmin):
    list_display = ['character', 'spell']
    list_filter = ['spell__category']
    search_fields = ['character__name', 'spell__name']


@admin.register(AdeptPower)
class AdeptPowerAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'is_default']
    list_filter = ['is_default']
    search_fields = ['name', 'description']


@admin.register(CharacterAdeptPower)
class CharacterAdeptPowerAdmin(admin.ModelAdmin):
    list_display = ['character', 'power', 'level']
    list_filter = ['level']
    search_fields = ['character__name', 'power__name']


@admin.register(ComplexForm)
class ComplexFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'target', 'duration', 'fading', 'is_default']
    list_filter = ['target', 'duration', 'is_default']
    search_fields = ['name', 'description']


@admin.register(CharacterComplexForm)
class CharacterComplexFormAdmin(admin.ModelAdmin):
    list_display = ['character', 'form']
    search_fields = ['character__name', 'form__name']
