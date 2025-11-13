from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class DiceRoll(models.Model):
    """
    Model to store individual dice rolls with Shadowrun mechanics.

    Shadowrun uses pools of D6 dice with the following rules:
    - Each 5 or 6 is a "hit"
    - Optionally, 6s can "explode" (Rule of Six) - roll additional dice
    - Glitch: More than half the dice show 1
    - Critical Glitch: Glitch + zero hits
    """

    # Roll Information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dice_rolls',
        help_text="User who made this roll"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When this roll was made"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Description of what this roll is for (e.g., 'Perception Check', 'Pistols Attack')"
    )

    # Roll Parameters
    pool_size = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Number of dice in the pool"
    )
    threshold = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Number of hits needed to succeed (optional)"
    )
    use_rule_of_six = models.BooleanField(
        default=True,
        help_text="If True, 6s explode and add additional dice"
    )
    edge_used = models.BooleanField(
        default=False,
        help_text="Whether Edge was used on this roll"
    )

    # Roll Results (stored as JSON-like comma-separated string)
    dice_results = models.TextField(
        help_text="Comma-separated list of individual die results (e.g., '5,3,6,1,4')"
    )
    total_hits = models.IntegerField(
        default=0,
        help_text="Number of hits rolled (5s and 6s)"
    )
    ones_count = models.IntegerField(
        default=0,
        help_text="Number of 1s rolled (for glitch detection)"
    )

    # Glitch Detection
    is_glitch = models.BooleanField(
        default=False,
        help_text="True if more than half the dice showed 1"
    )
    is_critical_glitch = models.BooleanField(
        default=False,
        help_text="True if glitch occurred with zero hits"
    )

    # Success/Failure
    success = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the roll succeeded (null if no threshold set)"
    )

    # Optional Relationships
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dice_rolls',
        help_text="Campaign this roll belongs to (optional)"
    )
    session = models.ForeignKey(
        'campaigns.Session',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dice_rolls',
        help_text="Session this roll belongs to (optional)"
    )
    character = models.ForeignKey(
        'characters.Character',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dice_rolls',
        help_text="Character making this roll (optional)"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Dice Roll'
        verbose_name_plural = 'Dice Rolls'

    def __str__(self):
        desc = self.description or f"{self.pool_size}d6"
        return f"{self.user.username} - {desc} ({self.total_hits} hits)"

    def get_dice_list(self):
        """Return list of individual die results as integers"""
        if not self.dice_results:
            return []
        return [int(d) for d in self.dice_results.split(',')]

    def get_result_summary(self):
        """Return a human-readable summary of the roll"""
        summary = f"{self.total_hits} hit{'s' if self.total_hits != 1 else ''}"

        if self.is_critical_glitch:
            summary += " - CRITICAL GLITCH!"
        elif self.is_glitch:
            summary += " - Glitch"

        if self.threshold:
            if self.success:
                summary += f" (Success - needed {self.threshold})"
            else:
                summary += f" (Failed - needed {self.threshold})"

        return summary


class DicePreset(models.Model):
    """
    Model to store reusable dice roll configurations.
    Allows users to save common rolls for quick access.
    """

    # Preset Information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dice_presets',
        help_text="User who created this preset"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of this preset (e.g., 'Combat Pool', 'Perception Check')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of when to use this preset"
    )

    # Preset Parameters
    pool_size = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Default number of dice in the pool"
    )
    threshold = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Default threshold (optional)"
    )
    use_rule_of_six = models.BooleanField(
        default=True,
        help_text="Whether to use Rule of Six by default"
    )

    # Optional Relationships
    character = models.ForeignKey(
        'characters.Character',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dice_presets',
        help_text="Character this preset is associated with (optional)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Dice Preset'
        verbose_name_plural = 'Dice Presets'
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.pool_size}d6)"
