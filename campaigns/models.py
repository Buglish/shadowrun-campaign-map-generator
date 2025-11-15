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


class CombatEncounter(models.Model):
    """Combat encounter tracker for real-time combat management"""

    STATUS_CHOICES = [
        ('setup', 'Setup'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='combat_encounters',
        help_text="Session this encounter belongs to"
    )
    name = models.CharField(max_length=200, help_text="Name of the encounter")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='setup')

    # Combat tracking
    current_round = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    current_turn = models.IntegerField(default=0, help_text="Index of current participant's turn")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.session.campaign.name} - {self.name} (Round {self.current_round})"

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def current_participant(self):
        """Get the participant whose turn it is"""
        participants = self.participants.filter(is_active=True).order_by('-initiative')
        if participants.exists() and 0 <= self.current_turn < participants.count():
            return participants[self.current_turn]
        return None


class CombatParticipant(models.Model):
    """Participant in a combat encounter"""

    TEAM_CHOICES = [
        ('player', 'Player Character'),
        ('ally', 'Ally/NPC'),
        ('enemy', 'Enemy'),
        ('neutral', 'Neutral'),
    ]

    encounter = models.ForeignKey(
        CombatEncounter,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    character = models.ForeignKey(
        Character,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Linked character (if applicable)"
    )

    # Basic info
    name = models.CharField(max_length=200)
    team = models.CharField(max_length=20, choices=TEAM_CHOICES, default='enemy')

    # Combat stats
    initiative = models.IntegerField(
        default=0,
        help_text="Initiative score (higher goes first)"
    )
    current_hp = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)]
    )
    max_hp = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)]
    )

    # Shadowrun specific
    physical_damage = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stun_damage = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    edge_current = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    edge_max = models.IntegerField(default=1, validators=[MinValueValidator(0)])

    # Defensive stats
    armor = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    dodge_pool = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    # Status
    is_active = models.BooleanField(default=True, help_text="Is this participant still in combat?")
    is_defeated = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    # Position on map (if map is being used)
    map_x = models.IntegerField(null=True, blank=True)
    map_y = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-initiative', 'name']

    def __str__(self):
        return f"{self.name} (Init: {self.initiative})"

    @property
    def hp_percentage(self):
        """Calculate HP as a percentage"""
        if self.max_hp > 0:
            return int((self.current_hp / self.max_hp) * 100)
        return 0

    @property
    def condition(self):
        """Get current condition based on HP"""
        if self.is_defeated:
            return "Defeated"
        percentage = self.hp_percentage
        if percentage >= 75:
            return "Healthy"
        elif percentage >= 50:
            return "Wounded"
        elif percentage >= 25:
            return "Badly Wounded"
        else:
            return "Critical"


class CombatEffect(models.Model):
    """Status effects applied to combat participants"""

    EFFECT_TYPE_CHOICES = [
        ('buff', 'Buff'),
        ('debuff', 'Debuff'),
        ('damage', 'Damage Over Time'),
        ('healing', 'Healing Over Time'),
        ('condition', 'Condition'),
    ]

    participant = models.ForeignKey(
        CombatParticipant,
        on_delete=models.CASCADE,
        related_name='effects'
    )
    name = models.CharField(max_length=200)
    effect_type = models.CharField(max_length=20, choices=EFFECT_TYPE_CHOICES, default='condition')
    description = models.TextField(blank=True)

    # Duration tracking
    duration_rounds = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="How many rounds this effect lasts"
    )
    rounds_remaining = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0)]
    )

    # Effect modifiers (stored as JSON for flexibility)
    modifiers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Stat modifiers (e.g., {'initiative': -2, 'armor': 4})"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_active', 'name']

    def __str__(self):
        return f"{self.name} on {self.participant.name} ({self.rounds_remaining}r)"


class CombatLog(models.Model):
    """Log of combat events for history tracking and replay"""

    EVENT_TYPE_CHOICES = [
        ('combat_start', 'Combat Started'),
        ('combat_end', 'Combat Ended'),
        ('round_start', 'Round Started'),
        ('turn_start', 'Turn Started'),
        ('attack', 'Attack'),
        ('damage', 'Damage Taken'),
        ('healing', 'Healing Received'),
        ('effect_applied', 'Effect Applied'),
        ('effect_expired', 'Effect Expired'),
        ('movement', 'Movement'),
        ('defeated', 'Defeated'),
        ('revived', 'Revived'),
        ('edge_used', 'Edge Used'),
        ('other', 'Other Action'),
    ]

    encounter = models.ForeignKey(
        CombatEncounter,
        on_delete=models.CASCADE,
        related_name='combat_logs',
        help_text="The combat encounter this log belongs to"
    )

    # Event details
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        help_text="Type of combat event"
    )
    round_number = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Combat round when this event occurred"
    )
    description = models.TextField(help_text="Human-readable description of the event")

    # Participants involved
    actor = models.ForeignKey(
        CombatParticipant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions_performed',
        help_text="Participant who performed the action"
    )
    target = models.ForeignKey(
        CombatParticipant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions_received',
        help_text="Participant who was targeted/affected"
    )

    # Additional data (for dice rolls, damage amounts, etc.)
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional event data (damage, dice results, etc.)"
    )

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['encounter', 'timestamp']
        indexes = [
            models.Index(fields=['encounter', 'round_number']),
            models.Index(fields=['encounter', 'event_type']),
        ]

    def __str__(self):
        return f"[Round {self.round_number}] {self.event_type}: {self.description[:50]}"

    @property
    def formatted_timestamp(self):
        """Return formatted timestamp"""
        return self.timestamp.strftime("%H:%M:%S")

    @classmethod
    def log_event(cls, encounter, event_type, description, actor=None, target=None, data=None):
        """
        Helper method to create a combat log entry

        Args:
            encounter: CombatEncounter instance
            event_type: Type of event from EVENT_TYPE_CHOICES
            description: Human-readable description
            actor: CombatParticipant who performed the action (optional)
            target: CombatParticipant who received the action (optional)
            data: Additional event data dict (optional)

        Returns:
            CombatLog instance
        """
        return cls.objects.create(
            encounter=encounter,
            event_type=event_type,
            round_number=encounter.current_round,
            description=description,
            actor=actor,
            target=target,
            data=data or {}
        )
