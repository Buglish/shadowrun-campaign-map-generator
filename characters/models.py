from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Character(models.Model):
    """Shadowrun character model"""

    # Race choices
    RACE_CHOICES = [
        ('human', 'Human'),
        ('dwarf', 'Dwarf'),
        ('elf', 'Elf'),
        ('ork', 'Ork'),
        ('troll', 'Troll'),
    ]

    # Archetype choices
    ARCHETYPE_CHOICES = [
        ('adept', 'Adept'),
        ('combat_mage', 'Combat Mage'),
        ('covert_ops', 'Covert Ops Specialist'),
        ('decker', 'Decker'),
        ('face', 'Face'),
        ('rigger', 'Rigger'),
        ('street_samurai', 'Street Samurai'),
        ('street_shaman', 'Street Shaman'),
        ('technomancer', 'Technomancer'),
        ('weapon_specialist', 'Weapon Specialist'),
    ]

    # Role choices
    ROLE_CHOICES = [
        ('arcane_specialist', 'Arcane Specialist'),
        ('face', 'Face'),
        ('street_samurai', 'Street Samurai'),
        ('technology_specialist', 'Technology Specialist'),
    ]

    # Priority choices
    PRIORITY_CHOICES = [
        ('A', 'A (Highest)'),
        ('B', 'B (High)'),
        ('C', 'C (Medium)'),
        ('D', 'D (Low)'),
        ('E', 'E (Lowest)'),
    ]

    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=100)
    race = models.CharField(max_length=20, choices=RACE_CHOICES)
    archetype = models.CharField(max_length=30, choices=ARCHETYPE_CHOICES)

    # Role and History
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    birthplace = models.CharField(max_length=200, blank=True)
    raised_location = models.CharField(max_length=200, blank=True)
    trained_location = models.CharField(max_length=200, blank=True)
    current_location = models.CharField(max_length=200, blank=True)
    dark_aspects_feeling = models.TextField(blank=True, help_text="How character feels about darker aspects of the world")
    wetwork_attitude = models.TextField(blank=True, help_text="Character's attitude toward wetwork")
    background = models.TextField(blank=True, help_text="Character background and history")

    # Priorities
    metatype_priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='C')
    attributes_priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='C')
    magic_priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='C')
    skills_priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='C')
    resources_priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='C')

    # Attributes (Shadowrun core attributes)
    body = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    agility = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    reaction = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    strength = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    charisma = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    intuition = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    logic = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    willpower = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])

    # Derived Attributes
    edge = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    essence = models.DecimalField(max_digits=3, decimal_places=2, default=6.00)
    magic = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    resonance = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    # Resources and Karma
    starting_resources = models.IntegerField(default=0)
    current_resources = models.IntegerField(default=0)
    karma_total = models.IntegerField(default=0)
    karma_spent = models.IntegerField(default=0)
    karma_available = models.IntegerField(default=0)

    # Character Status
    is_complete = models.BooleanField(default=False, help_text="Character creation completed")
    creation_step = models.IntegerField(default=1, help_text="Current step in character creation")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_race_display()})"

    @property
    def karma_remaining(self):
        """Calculate remaining karma"""
        return self.karma_total + self.karma_available - self.karma_spent


class Quality(models.Model):
    """Character qualities (positive and negative traits)"""

    QUALITY_TYPE_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
    ]

    name = models.CharField(max_length=100)
    quality_type = models.CharField(max_length=10, choices=QUALITY_TYPE_CHOICES)
    karma_cost = models.IntegerField(help_text="Karma cost (negative for positive qualities)")
    description = models.TextField()
    is_default = models.BooleanField(default=True, help_text="Available for all characters")

    class Meta:
        ordering = ['quality_type', 'name']
        verbose_name_plural = 'Qualities'

    def __str__(self):
        return f"{self.name} ({self.get_quality_type_display()})"


class CharacterQuality(models.Model):
    """Junction table for character qualities"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='qualities')
    quality = models.ForeignKey(Quality, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['character', 'quality']

    def __str__(self):
        return f"{self.character.name} - {self.quality.name}"


class Gear(models.Model):
    """Equipment and gear catalog"""

    GEAR_CATEGORY_CHOICES = [
        ('weapon', 'Weapon'),
        ('armor', 'Armor'),
        ('cyberware', 'Cyberware'),
        ('bioware', 'Bioware'),
        ('electronics', 'Electronics'),
        ('magical', 'Magical Equipment'),
        ('vehicle', 'Vehicle'),
        ('misc', 'Miscellaneous'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=GEAR_CATEGORY_CHOICES)
    description = models.TextField()
    cost = models.IntegerField(help_text="Cost in nuyen")
    availability = models.CharField(max_length=10, blank=True)
    essence_cost = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_default = models.BooleanField(default=True, help_text="Available in base catalog")

    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'Gear'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class CharacterGear(models.Model):
    """Character's equipment"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='equipment')
    gear = models.ForeignKey(Gear, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['character', 'gear']

    def __str__(self):
        return f"{self.character.name} - {self.gear.name} (x{self.quantity})"

    @property
    def total_cost(self):
        """Calculate total cost for this gear"""
        return self.gear.cost * self.quantity
