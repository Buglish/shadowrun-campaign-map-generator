from django import forms
from .models import Campaign, Session, SessionObjective, CombatEncounter, CombatParticipant, CombatEffect
from characters.models import Character
from maps.models import Map


class CampaignForm(forms.ModelForm):
    """Form for creating and editing campaigns"""

    class Meta:
        model = Campaign
        fields = [
            'name', 'description', 'status', 'start_date', 'end_date',
            'starting_karma', 'starting_resources', 'characters', 'maps',
            'players', 'player_notes', 'gm_notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter campaign name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Campaign overview and description'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'starting_karma': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'starting_resources': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'characters': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'maps': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'players': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'player_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Public information visible to all players'
            }),
            'gm_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Private GM notes (not visible to players)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Filter characters to only show user's characters
            self.fields['characters'].queryset = Character.objects.filter(
                user=user, is_complete=True
            )
            # Filter maps to only show user's maps
            self.fields['maps'].queryset = Map.objects.filter(owner=user)


class SessionForm(forms.ModelForm):
    """Form for creating and editing sessions"""

    class Meta:
        model = Session
        fields = [
            'session_number', 'title', 'description', 'scheduled_date',
            'actual_date', 'duration_minutes', 'status', 'gm_notes',
            'session_notes', 'player_summary', 'maps_used', 'characters_present',
            'npcs_involved', 'karma_awarded', 'nuyen_awarded', 'encounters_faced',
            'enemies_defeated', 'objectives_completed', 'important_npcs', 'loot_acquired'
        ]
        widgets = {
            'session_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter session title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Session summary or adventure hook'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'actual_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Duration in minutes'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'gm_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Private GM preparation notes'
            }),
            'session_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Session recap visible to players'
            }),
            'player_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Player-written session summary'
            }),
            'maps_used': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '4'
            }),
            'characters_present': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '4'
            }),
            'npcs_involved': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '4'
            }),
            'karma_awarded': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'nuyen_awarded': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'encounters_faced': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'enemies_defeated': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'objectives_completed': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List objectives completed (one per line)'
            }),
            'important_npcs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List important NPCs encountered (one per line)'
            }),
            'loot_acquired': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List significant loot and rewards (one per line)'
            }),
        }

    def __init__(self, *args, **kwargs):
        campaign = kwargs.pop('campaign', None)
        super().__init__(*args, **kwargs)

        if campaign:
            # Filter player characters (not NPCs) from campaign characters
            self.fields['characters_present'].queryset = campaign.characters.filter(is_npc=False)

            # Filter NPCs from all NPCs owned by the GM
            # This allows selecting any NPC, not just campaign-assigned ones
            self.fields['npcs_involved'].queryset = Character.objects.filter(
                user=campaign.game_master,
                is_npc=True
            )

            # Filter maps to show all maps owned by the GM (campaign owner)
            # This allows selecting maps even if they're not yet assigned to the campaign
            self.fields['maps_used'].queryset = Map.objects.filter(owner=campaign.game_master)

            # Auto-suggest next session number
            if not self.instance.pk:
                last_session = campaign.sessions.order_by('-session_number').first()
                if last_session:
                    self.initial['session_number'] = last_session.session_number + 1
                else:
                    self.initial['session_number'] = 1


class SessionObjectiveForm(forms.ModelForm):
    """Form for creating session objectives"""

    class Meta:
        model = SessionObjective
        fields = ['description', 'is_completed', 'completion_notes']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter objective description'
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'completion_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes about completing this objective'
            }),
        }


class CombatEncounterForm(forms.ModelForm):
    """Form for creating and editing combat encounters"""

    class Meta:
        model = CombatEncounter
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter encounter name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Encounter description'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CombatParticipantForm(forms.ModelForm):
    """Form for adding/editing combat participants"""

    class Meta:
        model = CombatParticipant
        fields = [
            'name', 'team', 'character', 'initiative', 'max_hp', 'current_hp',
            'physical_damage', 'stun_damage', 'edge_current', 'edge_max',
            'armor', 'dodge_pool', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Participant name'
            }),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'character': forms.Select(attrs={'class': 'form-select'}),
            'initiative': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'max_hp': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '10'
            }),
            'current_hp': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'physical_damage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'stun_damage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'edge_current': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'edge_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'armor': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'dodge_pool': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes'
            }),
        }


class CombatEffectForm(forms.ModelForm):
    """Form for adding/editing combat effects"""

    class Meta:
        model = CombatEffect
        fields = ['name', 'effect_type', 'description', 'duration_rounds', 'rounds_remaining']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Effect name'
            }),
            'effect_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Effect description'
            }),
            'duration_rounds': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'rounds_remaining': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
