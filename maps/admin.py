from django.contrib import admin
from .models import Map, MapTile, MapObject, MapGenerationPreset


class MapTileInline(admin.TabularInline):
    model = MapTile
    extra = 0
    fields = ['x', 'y', 'terrain_type', 'is_walkable', 'is_transparent', 'color']


class MapObjectInline(admin.TabularInline):
    model = MapObject
    extra = 0
    fields = ['x', 'y', 'name', 'object_type', 'is_visible_to_players']


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'map_type', 'width', 'height', 'is_public', 'is_generated', 'updated_at']
    list_filter = ['map_type', 'is_public', 'is_generated', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at', 'total_tiles']
    filter_horizontal = ['shared_with']

    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'description', 'owner']
        }),
        ('Map Settings', {
            'fields': ['width', 'height', 'tile_size', 'map_type']
        }),
        ('Sharing & Visibility', {
            'fields': ['is_public', 'shared_with']
        }),
        ('Generation Settings', {
            'fields': ['is_generated', 'generation_seed']
        }),
        ('Metadata', {
            'fields': ['total_tiles', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    inlines = [MapTileInline, MapObjectInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


@admin.register(MapTile)
class MapTileAdmin(admin.ModelAdmin):
    list_display = ['map', 'x', 'y', 'terrain_type', 'is_walkable', 'is_transparent', 'movement_cost']
    list_filter = ['terrain_type', 'is_walkable', 'is_transparent', 'map']
    search_fields = ['map__name', 'notes']

    fieldsets = [
        ('Location', {
            'fields': ['map', 'x', 'y']
        }),
        ('Terrain', {
            'fields': ['terrain_type', 'color']
        }),
        ('Properties', {
            'fields': ['is_walkable', 'is_transparent', 'movement_cost']
        }),
        ('Additional', {
            'fields': ['notes', 'custom_properties'],
            'classes': ['collapse']
        }),
    ]


@admin.register(MapObject)
class MapObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'map', 'x', 'y', 'object_type', 'is_visible_to_players', 'blocks_movement']
    list_filter = ['object_type', 'is_visible_to_players', 'blocks_movement', 'blocks_vision', 'map']
    search_fields = ['name', 'description', 'map__name']
    readonly_fields = ['created_at']

    fieldsets = [
        ('Basic Information', {
            'fields': ['map', 'name', 'description']
        }),
        ('Location', {
            'fields': ['x', 'y']
        }),
        ('Type & Appearance', {
            'fields': ['object_type', 'icon', 'color']
        }),
        ('Properties', {
            'fields': ['is_visible_to_players', 'blocks_movement', 'blocks_vision']
        }),
        ('Additional Data', {
            'fields': ['stats', 'notes'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(MapGenerationPreset)
class MapGenerationPresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'map_type', 'width', 'height', 'generation_algorithm', 'is_public']
    list_filter = ['map_type', 'is_public', 'generation_algorithm']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'description', 'owner']
        }),
        ('Map Settings', {
            'fields': ['width', 'height', 'map_type']
        }),
        ('Generation Parameters', {
            'fields': ['generation_algorithm', 'obstacle_density', 'object_density', 'custom_parameters']
        }),
        ('Sharing', {
            'fields': ['is_public']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
