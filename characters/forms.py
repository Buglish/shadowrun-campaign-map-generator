from django import forms
from .models import (
    Character, Quality, CharacterQuality, Gear, CharacterGear, Skill, CharacterSkill,
    Spell, CharacterSpell, AdeptPower, CharacterAdeptPower, ComplexForm, CharacterComplexForm,
    Contact, Language
)
from .npc_generator import get_archetype_choices, get_threat_level_choices, ARCHETYPE_TEMPLATES, THREAT_LEVELS


class CharacterBasicInfoForm(forms.ModelForm):
    """Step 1: Basic character information - Race and Archetype"""

    class Meta:
        model = Character
        fields = ['name', 'race', 'archetype']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter character name'}),
        }
        help_texts = {
            'race': 'Select your character\'s metatype',
            'archetype': 'Choose your character\'s archetype/profession',
        }


class CharacterRoleHistoryForm(forms.ModelForm):
    """Step 2: Character role and history"""

    class Meta:
        model = Character
        fields = [
            'role',
            'birthplace',
            'raised_location',
            'trained_location',
            'current_location',
            'dark_aspects_feeling',
            'wetwork_attitude',
            'background',
        ]
        widgets = {
            'birthplace': forms.TextInput(attrs={'placeholder': 'Where was your character born?'}),
            'raised_location': forms.TextInput(attrs={'placeholder': 'Where were they raised?'}),
            'trained_location': forms.TextInput(attrs={'placeholder': 'Where did they receive training?'}),
            'current_location': forms.TextInput(attrs={'placeholder': 'Where are they now?'}),
            'dark_aspects_feeling': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'How does your character feel about the darker aspects of the world?'
            }),
            'wetwork_attitude': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What is your character\'s attitude toward wetwork and violence?'
            }),
            'background': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell us your character\'s story...'
            }),
        }


class CharacterPrioritiesForm(forms.ModelForm):
    """Step 3: Priority selection"""

    class Meta:
        model = Character
        fields = [
            'metatype_priority',
            'attributes_priority',
            'magic_priority',
            'skills_priority',
            'resources_priority',
        ]
        help_texts = {
            'metatype_priority': 'Priority for metatype/race',
            'attributes_priority': 'Priority for attributes',
            'magic_priority': 'Priority for magic/resonance',
            'skills_priority': 'Priority for skills',
            'resources_priority': 'Priority for starting resources',
        }

    def clean(self):
        """Ensure all priorities are unique"""
        cleaned_data = super().clean()
        priorities = [
            cleaned_data.get('metatype_priority'),
            cleaned_data.get('attributes_priority'),
            cleaned_data.get('magic_priority'),
            cleaned_data.get('skills_priority'),
            cleaned_data.get('resources_priority'),
        ]

        # Remove None values
        priorities = [p for p in priorities if p is not None]

        if len(priorities) != len(set(priorities)):
            raise forms.ValidationError('Each priority (A, B, C, D, E) must be used exactly once.')

        return cleaned_data


class CharacterQualitySelectionForm(forms.Form):
    """Step 4: Quality selection"""

    positive_qualities = forms.ModelMultipleChoiceField(
        queryset=Quality.objects.filter(quality_type='positive', is_default=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Select positive qualities for your character'
    )

    negative_qualities = forms.ModelMultipleChoiceField(
        queryset=Quality.objects.filter(quality_type='negative', is_default=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Select negative qualities (these give you karma)'
    )


class CharacterAttributesForm(forms.ModelForm):
    """Step 5: Attributes allocation"""

    class Meta:
        model = Character
        fields = [
            'body', 'agility', 'reaction', 'strength',
            'charisma', 'intuition', 'logic', 'willpower',
            'edge', 'magic', 'resonance'
        ]
        widgets = {
            'body': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'agility': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'reaction': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'strength': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'charisma': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'intuition': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'logic': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'willpower': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'edge': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'magic': forms.NumberInput(attrs={'min': 0, 'max': 10}),
            'resonance': forms.NumberInput(attrs={'min': 0, 'max': 10}),
        }


class CharacterKarmaForm(forms.ModelForm):
    """Step 6: Karma customization"""

    class Meta:
        model = Character
        fields = ['karma_total', 'karma_spent', 'karma_available']
        widgets = {
            'karma_total': forms.NumberInput(attrs={'min': 0}),
            'karma_spent': forms.NumberInput(attrs={'min': 0}),
            'karma_available': forms.NumberInput(attrs={'min': 0}),
        }
        help_texts = {
            'karma_total': 'Total karma earned',
            'karma_spent': 'Karma spent on improvements',
            'karma_available': 'Additional karma available',
        }


class CharacterGearSelectionForm(forms.Form):
    """Step 7: Gear/equipment selection"""

    gear_items = forms.ModelMultipleChoiceField(
        queryset=Gear.objects.filter(is_default=True).order_by('category', 'name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Select gear for your character'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group gear by category for better display
        self.fields['gear_items'].queryset = Gear.objects.filter(is_default=True).order_by('category', 'name')


class CharacterFinishingForm(forms.ModelForm):
    """Step 8: Final touches and completion"""

    class Meta:
        model = Character
        fields = ['starting_resources', 'current_resources', 'essence']
        widgets = {
            'starting_resources': forms.NumberInput(attrs={'min': 0}),
            'current_resources': forms.NumberInput(attrs={'min': 0}),
            'essence': forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 6}),
        }
        help_texts = {
            'starting_resources': 'Starting nuyen amount',
            'current_resources': 'Current nuyen (after gear purchases)',
            'essence': 'Character essence (reduced by cyberware)',
        }


class CharacterSkillForm(forms.ModelForm):
    """Form for adding/editing character skills"""

    class Meta:
        model = CharacterSkill
        fields = ['skill', 'rating', 'specialization', 'notes']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 12}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Pistols (Semi-Automatics)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'skill': 'Skill',
            'rating': 'Skill Rating (0-12)',
            'specialization': 'Specialization (Optional)',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        character = kwargs.pop('character', None)
        super().__init__(*args, **kwargs)

        # Filter out skills the character already has (unless editing)
        if character and not self.instance.pk:
            existing_skill_ids = character.skills.values_list('skill_id', flat=True)
            self.fields['skill'].queryset = Skill.objects.exclude(id__in=existing_skill_ids)


class NPCGeneratorForm(forms.Form):
    """Form for generating random NPCs"""

    RACE_CHOICES = [
        ('', '-- Random Race --'),
        ('human', 'Human'),
        ('dwarf', 'Dwarf'),
        ('elf', 'Elf'),
        ('ork', 'Ork'),
        ('troll', 'Troll'),
    ]

    archetype = forms.ChoiceField(
        choices=get_archetype_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Archetype',
        help_text='Select the NPC archetype/profession'
    )

    threat_level = forms.ChoiceField(
        choices=get_threat_level_choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Threat Level',
        help_text='Determines NPC power level and competence'
    )

    race = forms.ChoiceField(
        choices=RACE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Race',
        help_text='Leave blank for random race selection'
    )

    use_alias = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Use Shadowrun Alias',
        help_text='Generate name with street alias (e.g., "Ghost" Jake Reyes)'
    )

    quantity = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        label='Quantity',
        help_text='Number of NPCs to generate (1-20)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add descriptions to threat level choices as HTML data attributes
        for field_name in ['archetype', 'threat_level']:
            self.fields[field_name].widget.attrs['class'] = 'form-select'

    def get_archetype_description(self, archetype_key):
        """Get description for selected archetype"""
        template = ARCHETYPE_TEMPLATES.get(archetype_key, {})
        skills = ', '.join(template.get('typical_skills', [])[:4])
        return f"Primary skills: {skills}"

    def get_threat_description(self, threat_key):
        """Get description for selected threat level"""
        threat = THREAT_LEVELS.get(threat_key, {})
        return threat.get('description', '')


class CharacterSpellForm(forms.ModelForm):
    """Form for adding/editing character spells"""

    class Meta:
        model = CharacterSpell
        fields = ['spell', 'notes']
        widgets = {
            'spell': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes about this spell'}),
        }
        labels = {
            'spell': 'Spell',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        character = kwargs.pop('character', None)
        super().__init__(*args, **kwargs)

        # Filter out spells the character already has (unless editing)
        if character and not self.instance.pk:
            existing_spell_ids = character.spells.values_list('spell_id', flat=True)
            self.fields['spell'].queryset = Spell.objects.exclude(id__in=existing_spell_ids)


class CharacterAdeptPowerForm(forms.ModelForm):
    """Form for adding/editing character adept powers"""

    class Meta:
        model = CharacterAdeptPower
        fields = ['power', 'level', 'notes']
        widgets = {
            'power': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes about this power'}),
        }
        labels = {
            'power': 'Adept Power',
            'level': 'Level',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        character = kwargs.pop('character', None)
        super().__init__(*args, **kwargs)

        # Filter out powers the character already has (unless editing)
        if character and not self.instance.pk:
            existing_power_ids = character.adept_powers.values_list('power_id', flat=True)
            self.fields['power'].queryset = AdeptPower.objects.exclude(id__in=existing_power_ids)


class CharacterComplexFormForm(forms.ModelForm):
    """Form for adding/editing character complex forms"""

    class Meta:
        model = CharacterComplexForm
        fields = ['form', 'notes']
        widgets = {
            'form': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes about this form'}),
        }
        labels = {
            'form': 'Complex Form',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        character = kwargs.pop('character', None)
        super().__init__(*args, **kwargs)

        # Filter out forms the character already has (unless editing)
        if character and not self.instance.pk:
            existing_form_ids = character.complex_forms.values_list('form_id', flat=True)
            self.fields['form'].queryset = ComplexForm.objects.exclude(id__in=existing_form_ids)


class CharacterContactForm(forms.ModelForm):
    """Form for adding/editing character contacts"""

    class Meta:
        model = Contact
        fields = ['name', 'archetype', 'connection', 'loyalty', 'description', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact name'}),
            'archetype': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Fixer, Street Doc, Corporate Manager'}),
            'connection': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'loyalty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Physical description, personality, location...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'How you met, services provided, etc.'}),
        }
        labels = {
            'name': 'Contact Name',
            'archetype': 'Archetype/Profession',
            'connection': 'Connection Rating (1-12)',
            'loyalty': 'Loyalty Rating (1-6)',
            'description': 'Description',
            'notes': 'Notes',
        }
        help_texts = {
            'connection': 'How influential and resourceful is this contact?',
            'loyalty': 'How loyal is this contact to you?',
        }


class CharacterLanguageForm(forms.ModelForm):
    """Form for adding/editing character languages"""

    class Meta:
        model = Language
        fields = ['name', 'proficiency', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., English, Japanese, Sperethiel'}),
            'proficiency': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Where learned, dialects, etc.'}),
        }
        labels = {
            'name': 'Language Name',
            'proficiency': 'Proficiency Level',
            'notes': 'Notes',
        }
        help_texts = {
            'proficiency': 'Native: Speaks as first language | Fluent: Professional level | Conversational: Basic dialogue | Basic: Simple phrases',
        }
