from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Map(models.Model):
    """Main map model for campaign maps"""

    # Map ownership and metadata
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maps')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Map dimensions (in tiles)
    width = models.IntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(100)]
    )
    height = models.IntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(100)]
    )

    # Map settings
    tile_size = models.IntegerField(
        default=50,
        help_text="Size of each tile in pixels",
        validators=[MinValueValidator(10), MaxValueValidator(200)]
    )

    # Map type and environment
    MAP_TYPE_CHOICES = [
        ('urban', 'Urban'),
        ('wilderness', 'Wilderness'),
        ('corporate', 'Corporate Facility'),
        ('underground', 'Underground/Sewer'),
        ('mixed', 'Mixed Environment'),
    ]
    map_type = models.CharField(
        max_length=20,
        choices=MAP_TYPE_CHOICES,
        default='urban'
    )

    # Visibility and sharing
    is_public = models.BooleanField(
        default=False,
        help_text="Make this map visible to all players"
    )
    shared_with = models.ManyToManyField(
        User,
        related_name='shared_maps',
        blank=True,
        help_text="Specific users who can view this map"
    )

    # Generation metadata
    is_generated = models.BooleanField(
        default=False,
        help_text="Was this map procedurally generated?"
    )
    generation_seed = models.CharField(
        max_length=50,
        blank=True,
        help_text="Seed used for map generation (for reproducibility)"
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    @property
    def total_tiles(self):
        """Total number of tiles in the map"""
        return self.width * self.height


class MapTile(models.Model):
    """Individual tiles that make up a map"""

    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='tiles')

    # Position on the map (0-indexed)
    x = models.IntegerField(validators=[MinValueValidator(0)])
    y = models.IntegerField(validators=[MinValueValidator(0)])

    # Terrain type
    TERRAIN_CHOICES = [
        # Urban terrain
        ('street', 'Street'),
        ('sidewalk', 'Sidewalk'),
        ('building', 'Building'),
        ('alley', 'Alley'),
        ('parking', 'Parking Lot'),

        # Wilderness terrain
        ('grass', 'Grass'),
        ('forest', 'Forest'),
        ('water', 'Water'),
        ('mountain', 'Mountain'),
        ('desert', 'Desert'),

        # Indoor/Corporate terrain
        ('floor', 'Floor'),
        ('wall', 'Wall'),
        ('door', 'Door'),
        ('window', 'Window'),
        ('stairs', 'Stairs'),
        ('elevator', 'Elevator'),

        # Underground terrain
        ('tunnel', 'Tunnel'),
        ('sewer', 'Sewer'),
        ('cave', 'Cave'),

        # Special
        ('void', 'Void'),
        ('custom', 'Custom'),
    ]
    terrain_type = models.CharField(
        max_length=20,
        choices=TERRAIN_CHOICES,
        default='floor'
    )

    # Tile properties
    is_walkable = models.BooleanField(default=True)
    is_transparent = models.BooleanField(
        default=True,
        help_text="Can players see through this tile?"
    )

    # Visual properties
    color = models.CharField(
        max_length=7,
        default='#CCCCCC',
        help_text="Hex color code for the tile"
    )

    # Movement cost
    movement_cost = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="How many movement points to cross this tile"
    )

    # Notes and custom properties
    notes = models.TextField(blank=True)
    custom_properties = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom JSON properties for this tile"
    )

    class Meta:
        ordering = ['y', 'x']
        unique_together = ['map', 'x', 'y']

    def __str__(self):
        return f"{self.map.name} - Tile ({self.x}, {self.y})"


class MapObject(models.Model):
    """Objects placed on the map (NPCs, items, markers, etc.)"""

    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='map_objects')

    # Position
    x = models.IntegerField(validators=[MinValueValidator(0)])
    y = models.IntegerField(validators=[MinValueValidator(0)])

    # Object properties
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Object type
    OBJECT_TYPE_CHOICES = [
        ('npc', 'NPC'),
        ('enemy', 'Enemy'),
        ('item', 'Item'),
        ('objective', 'Objective Marker'),
        ('trap', 'Trap'),
        ('entrance', 'Entrance/Exit'),
        ('cover', 'Cover'),
        ('vehicle', 'Vehicle'),
        ('marker', 'Custom Marker'),
    ]
    object_type = models.CharField(
        max_length=20,
        choices=OBJECT_TYPE_CHOICES,
        default='marker'
    )

    # Visual representation
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon identifier or emoji for the object"
    )
    color = models.CharField(
        max_length=7,
        default='#FF0000',
        help_text="Hex color code for the object"
    )

    # Gameplay properties
    is_visible_to_players = models.BooleanField(
        default=True,
        help_text="Is this object visible to players?"
    )
    blocks_movement = models.BooleanField(default=False)
    blocks_vision = models.BooleanField(default=False)

    # Additional data
    stats = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom stats/properties (HP, damage, etc.)"
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['y', 'x', 'name']

    def __str__(self):
        return f"{self.name} ({self.x}, {self.y})"


class MapGenerationPreset(models.Model):
    """Presets for procedural map generation"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='map_presets')

    # Map dimensions
    width = models.IntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(100)]
    )
    height = models.IntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(100)]
    )

    # Generation parameters
    map_type = models.CharField(
        max_length=20,
        choices=Map.MAP_TYPE_CHOICES,
        default='urban'
    )

    # Density parameters (0-100)
    obstacle_density = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of tiles that are obstacles"
    )
    object_density = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of tiles that contain objects"
    )

    # Generation algorithm settings
    generation_algorithm = models.CharField(
        max_length=50,
        default='random',
        help_text="Algorithm to use for generation (e.g., 'random', 'cellular_automata', 'bsp')"
    )

    # Custom parameters
    custom_parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional custom parameters for generation"
    )

    # Public presets
    is_public = models.BooleanField(
        default=False,
        help_text="Make this preset available to all users"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
