from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from characters.models import Character
from maps.models import Map


class Campaign(models.Model):
    """Campaign model for organizing game sessions"""

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Campaign overview and description")
    game_master = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='gm_campaigns',
        help_text="The Game Master running this campaign"
    )

    # Status and Settings
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    start_date = models.DateField(null=True, blank=True, help_text="Campaign start date")
    end_date = models.DateField(null=True, blank=True, help_text="Campaign end date (if completed)")

    # Campaign Settings
    starting_karma = models.IntegerField(
        default=25,
        validators=[MinValueValidator(0)],
        help_text="Starting karma for new characters"
    )
    starting_resources = models.IntegerField(
        default=50000,
        validators=[MinValueValidator(0)],
        help_text="Starting nuyen for new characters"
    )

    # Relationships
    characters = models.ManyToManyField(
        Character,
        related_name='campaigns',
        blank=True,
        help_text="Characters participating in this campaign"
    )
    maps = models.ManyToManyField(
        Map,
        related_name='campaigns',
        blank=True,
        help_text="Maps used in this campaign"
    )
    players = models.ManyToManyField(
        User,
        related_name='player_campaigns',
        blank=True,
        help_text="Players in this campaign"
    )

    # Campaign Notes
    gm_notes = models.TextField(
        blank=True,
        help_text="Private GM notes (not visible to players)"
    )
    player_notes = models.TextField(
        blank=True,
        help_text="Public campaign information visible to players"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return self.name

    @property
    def session_count(self):
        """Total number of sessions in this campaign"""
        return self.sessions.count()

    @property
    def completed_session_count(self):
        """Number of completed sessions"""
        return self.sessions.filter(status='completed').count()

    @property
    def active_characters(self):
        """Get active characters in the campaign"""
        return self.characters.filter(is_complete=True)


class Session(models.Model):
    """Individual game session within a campaign"""

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Basic Information
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_number = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Sequential session number"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Session summary or adventure hook")

    # Scheduling
    scheduled_date = models.DateTimeField(null=True, blank=True)
    actual_date = models.DateTimeField(null=True, blank=True, help_text="When the session actually occurred")
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Session duration in minutes"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned'
    )

    # Session Content
    gm_notes = models.TextField(
        blank=True,
        help_text="Private GM notes and preparation (not visible to players)"
    )
    session_notes = models.TextField(
        blank=True,
        help_text="Session recap and notes (visible to players)"
    )
    player_summary = models.TextField(
        blank=True,
        help_text="Player-written session summary"
    )

    # Relationships
    maps_used = models.ManyToManyField(
        Map,
        related_name='sessions',
        blank=True,
        help_text="Maps used during this session"
    )
    characters_present = models.ManyToManyField(
        Character,
        related_name='sessions_attended',
        blank=True,
        limit_choices_to={'is_npc': False},
        help_text="Player characters who participated in this session"
    )
    npcs_involved = models.ManyToManyField(
        Character,
        related_name='sessions_involved',
        blank=True,
        limit_choices_to={'is_npc': True},
        help_text="NPCs encountered or involved in this session"
    )

    # Rewards
    karma_awarded = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Karma awarded to characters this session"
    )
    nuyen_awarded = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Nuyen awarded to characters this session"
    )

    # Combat and Encounters
    encounters_faced = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of combat encounters"
    )
    enemies_defeated = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total enemies defeated"
    )

    # Important Events
    objectives_completed = models.TextField(
        blank=True,
        help_text="List of objectives completed (one per line)"
    )
    important_npcs = models.TextField(
        blank=True,
        help_text="Important NPCs encountered (one per line)"
    )
    loot_acquired = models.TextField(
        blank=True,
        help_text="Significant loot and rewards (one per line)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['campaign', 'session_number']
        unique_together = ['campaign', 'session_number']

    def __str__(self):
        return f"{self.campaign.name} - Session {self.session_number}: {self.title}"

    @property
    def duration_hours(self):
        """Session duration in hours"""
        if self.duration_minutes:
            return round(self.duration_minutes / 60, 1)
        return None

    @property
    def is_upcoming(self):
        """Check if session is scheduled in the future"""
        from django.utils import timezone
        return (
            self.status == 'planned' and
            self.scheduled_date and
            self.scheduled_date > timezone.now()
        )


class SessionObjective(models.Model):
    """Specific objectives for a session"""

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='objectives'
    )
    description = models.CharField(max_length=500)
    is_completed = models.BooleanField(default=False)
    completion_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_completed', 'created_at']

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.description}"
