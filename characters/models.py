from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import math


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

    # Physical Description
    age = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=50, blank=True)
    height = models.CharField(max_length=50, blank=True, help_text="e.g., 6'2\" or 188cm")
    weight = models.CharField(max_length=50, blank=True, help_text="e.g., 180 lbs or 82kg")
    eyes = models.CharField(max_length=50, blank=True)
    hair = models.CharField(max_length=50, blank=True)
    skin = models.CharField(max_length=50, blank=True)
    distinguishing_features = models.TextField(blank=True, help_text="Scars, tattoos, cyberware, etc.")

    # Lifestyle
    LIFESTYLE_CHOICES = [
        ('street', 'Street (0¥)'),
        ('squatter', 'Squatter (500¥)'),
        ('low', 'Low (2,000¥)'),
        ('medium', 'Medium (5,000¥)'),
        ('high', 'High (10,000¥)'),
        ('luxury', 'Luxury (100,000¥)'),
    ]
    lifestyle = models.CharField(max_length=20, choices=LIFESTYLE_CHOICES, default='low')
    lifestyle_details = models.TextField(blank=True, help_text="Description of living situation")

    # Reputation
    street_cred = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    notoriety = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    public_awareness = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Condition Monitors
    physical_damage = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stun_damage = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Character Status
    is_complete = models.BooleanField(default=False, help_text="Character creation completed")
    creation_step = models.IntegerField(default=1, help_text="Current step in character creation")
    is_npc = models.BooleanField(default=False, help_text="Is this character an NPC (generated)")

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

    # Derived Attributes
    @property
    def initiative_base(self):
        """Base initiative (Reaction + Intuition)"""
        return self.reaction + self.intuition

    @property
    def initiative_dice(self):
        """Initiative dice (usually 1 + modifiers from cyberware/magic)"""
        # TODO: Calculate from augmentations
        return 1

    @property
    def physical_monitor_max(self):
        """Maximum physical damage boxes (8 + ⌈Body/2⌉)"""
        return 8 + math.ceil(self.body / 2)

    @property
    def stun_monitor_max(self):
        """Maximum stun damage boxes (8 + ⌈Willpower/2⌉)"""
        return 8 + math.ceil(self.willpower / 2)

    @property
    def physical_limit(self):
        """Physical limit [(Strength × 2 + Body + Reaction) ÷ 3] rounded up"""
        return math.ceil((self.strength * 2 + self.body + self.reaction) / 3)

    @property
    def mental_limit(self):
        """Mental limit [(Logic × 2 + Intuition + Willpower) ÷ 3] rounded up"""
        return math.ceil((self.logic * 2 + self.intuition + self.willpower) / 3)

    @property
    def social_limit(self):
        """Social limit [(Charisma × 3 + Willpower + Essence) ÷ 3] rounded up"""
        return math.ceil((self.charisma * 3 + self.willpower + float(self.essence)) / 3)

    @property
    def armor_rating(self):
        """Total armor rating from equipped armor"""
        # TODO: Calculate from equipped armor gear
        total = 0
        for item in self.equipment.filter(gear__category='armor'):
            if hasattr(item.gear, 'armor_rating'):
                total += item.gear.armor_rating or 0
        return total


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

    # Weapon-specific fields
    damage = models.CharField(max_length=20, blank=True, help_text="e.g., 8P, 6S, 10P")
    armor_penetration = models.IntegerField(null=True, blank=True, help_text="AP value (negative number)")
    firing_mode = models.CharField(max_length=20, blank=True, help_text="e.g., SS, SA, BF, FA")
    recoil_compensation = models.IntegerField(null=True, blank=True, help_text="RC value")
    ammo = models.CharField(max_length=50, blank=True, help_text="e.g., 15(c), 30(c), 6(cy)")
    weapon_range = models.CharField(max_length=50, blank=True, help_text="e.g., 0-5/6-20/21-40/41-60")

    # Armor-specific fields
    armor_rating = models.IntegerField(null=True, blank=True, help_text="Armor value")

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


class Skill(models.Model):
    """Skills catalog"""

    SKILL_CATEGORY_CHOICES = [
        ('combat', 'Combat'),
        ('physical', 'Physical'),
        ('social', 'Social'),
        ('technical', 'Technical'),
        ('vehicle', 'Vehicle'),
        ('magical', 'Magical'),
        ('resonance', 'Resonance'),
        ('knowledge', 'Knowledge'),
        ('language', 'Language'),
    ]

    LINKED_ATTRIBUTE_CHOICES = [
        ('body', 'Body'),
        ('agility', 'Agility'),
        ('reaction', 'Reaction'),
        ('strength', 'Strength'),
        ('charisma', 'Charisma'),
        ('intuition', 'Intuition'),
        ('logic', 'Logic'),
        ('willpower', 'Willpower'),
        ('magic', 'Magic'),
        ('resonance', 'Resonance'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORY_CHOICES)
    linked_attribute = models.CharField(max_length=20, choices=LINKED_ATTRIBUTE_CHOICES)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=True, help_text="Available for all characters")

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class CharacterSkill(models.Model):
    """Character's skills with ratings"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(12)])
    specialization = models.CharField(max_length=100, blank=True, help_text="Optional specialization")
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['character', 'skill']
        ordering = ['skill__category', 'skill__name']

    def __str__(self):
        spec = f" ({self.specialization})" if self.specialization else ""
        return f"{self.character.name} - {self.skill.name} {self.rating}{spec}"

    @property
    def dice_pool(self):
        """Calculate dice pool (linked attribute + skill rating)"""
        attr_name = self.skill.linked_attribute
        attr_value = getattr(self.character, attr_name, 0)
        return attr_value + self.rating


class Contact(models.Model):
    """Character contacts (NPCs)"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    archetype = models.CharField(max_length=100, blank=True, help_text="e.g., Fixer, Street Doc, Corporate Manager")
    connection = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], help_text="Contact's influence and resources")
    loyalty = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)], help_text="Contact's loyalty to character")
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (C{self.connection}/L{self.loyalty})"


class Language(models.Model):
    """Languages known by character"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=100, help_text="Language name")

    PROFICIENCY_CHOICES = [
        ('native', 'Native (N)'),
        ('fluent', 'Fluent'),
        ('conversational', 'Conversational'),
        ('basic', 'Basic'),
    ]
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='conversational')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['character', 'name']
        ordering = ['-proficiency', 'name']

    def __str__(self):
        return f"{self.character.name} - {self.name} ({self.get_proficiency_display()})"


class Spell(models.Model):
    """Spells catalog (for mages and shamans)"""

    SPELL_CATEGORY_CHOICES = [
        ('combat', 'Combat'),
        ('detection', 'Detection'),
        ('health', 'Health'),
        ('illusion', 'Illusion'),
        ('manipulation', 'Manipulation'),
    ]

    SPELL_TYPE_CHOICES = [
        ('physical', 'Physical'),
        ('mana', 'Mana'),
    ]

    SPELL_RANGE_CHOICES = [
        ('touch', 'Touch (T)'),
        ('los', 'Line of Sight (LOS)'),
        ('los_area', 'Line of Sight (Area)'),
    ]

    SPELL_DURATION_CHOICES = [
        ('instant', 'Instant (I)'),
        ('sustained', 'Sustained (S)'),
        ('permanent', 'Permanent (P)'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SPELL_CATEGORY_CHOICES)
    spell_type = models.CharField(max_length=20, choices=SPELL_TYPE_CHOICES)
    range_type = models.CharField(max_length=20, choices=SPELL_RANGE_CHOICES)
    duration = models.CharField(max_length=20, choices=SPELL_DURATION_CHOICES)
    drain = models.CharField(max_length=20, help_text="Drain value (e.g., F-3, F-2, F+1)")
    description = models.TextField()
    is_default = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class CharacterSpell(models.Model):
    """Spells known by character"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='spells')
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['character', 'spell']
        ordering = ['spell__category', 'spell__name']

    def __str__(self):
        return f"{self.character.name} - {self.spell.name}"


class AdeptPower(models.Model):
    """Adept Powers catalog"""
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=3, decimal_places=2, help_text="Power point cost")
    description = models.TextField()
    is_default = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.cost} PP)"


class CharacterAdeptPower(models.Model):
    """Adept powers for character"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='adept_powers')
    power = models.ForeignKey(AdeptPower, on_delete=models.CASCADE)
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['character', 'power']
        ordering = ['power__name']

    def __str__(self):
        return f"{self.character.name} - {self.power.name} (Level {self.level})"


class ComplexForm(models.Model):
    """Complex Forms catalog (for technomancers)"""

    FORM_TARGET_CHOICES = [
        ('device', 'Device'),
        ('file', 'File'),
        ('persona', 'Persona'),
        ('sprite', 'Sprite'),
    ]

    FORM_DURATION_CHOICES = [
        ('instant', 'Instant (I)'),
        ('sustained', 'Sustained (S)'),
        ('permanent', 'Permanent (P)'),
    ]

    name = models.CharField(max_length=100)
    target = models.CharField(max_length=20, choices=FORM_TARGET_CHOICES)
    duration = models.CharField(max_length=20, choices=FORM_DURATION_CHOICES)
    fading = models.CharField(max_length=20, help_text="Fading value (e.g., L-1, L+2)")
    description = models.TextField()
    is_default = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CharacterComplexForm(models.Model):
    """Complex forms known by character"""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='complex_forms')
    form = models.ForeignKey(ComplexForm, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['character', 'form']
        ordering = ['form__name']

    def __str__(self):
        return f"{self.character.name} - {self.form.name}"
