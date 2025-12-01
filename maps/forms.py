from django import forms
from django.contrib.auth.models import User
from django.db import models as django_models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Div, HTML
from .models import Map, MapTile, MapObject, MapGenerationPreset


class MapForm(forms.ModelForm):
    """Form for creating and editing maps"""

    shared_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select specific users to share this map with (in addition to public setting)'
    )

    class Meta:
        model = Map
        fields = ['name', 'description', 'width', 'height', 'tile_size', 'map_type', 'is_public', 'shared_with']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Extract the current user from kwargs
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter users to exclude the current map owner
        if user:
            self.fields['shared_with'].queryset = User.objects.exclude(pk=user.pk).order_by('username')
        else:
            self.fields['shared_with'].queryset = User.objects.all().order_by('username')

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('description', css_class='form-control'),
            Row(
                Column('width', css_class='form-group col-md-4'),
                Column('height', css_class='form-group col-md-4'),
                Column('tile_size', css_class='form-group col-md-4'),
            ),
            Row(
                Column('map_type', css_class='form-group col-md-6'),
                Column('is_public', css_class='form-group col-md-6'),
            ),
            HTML('<hr><h5>Sharing Settings</h5>'),
            HTML('<p class="text-muted small">Share this map with specific users. Public maps are visible to everyone.</p>'),
            Field('shared_with', css_class='form-check'),
            Submit('submit', 'Save Map', css_class='btn btn-primary')
        )


class MapObjectForm(forms.ModelForm):
    """Form for creating and editing map objects"""

    COVER_LEVEL_CHOICES = [
        ('', '-- Select Cover Level --'),
        ('light', 'Light Cover (+2 defense)'),
        ('medium', 'Medium Cover (+4 defense)'),
        ('heavy', 'Heavy Cover (+6 defense, blocks movement/vision)'),
    ]

    cover_level = forms.ChoiceField(
        choices=COVER_LEVEL_CHOICES,
        required=False,
        help_text='Select cover level (only for Cover type objects)'
    )

    class Meta:
        model = MapObject
        fields = ['name', 'description', 'x', 'y', 'object_type', 'icon', 'color',
                  'is_visible_to_players', 'blocks_movement', 'blocks_vision', 'stats', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'stats': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('description', css_class='form-control'),
            Row(
                Column('x', css_class='form-group col-md-6'),
                Column('y', css_class='form-group col-md-6'),
            ),
            Row(
                Column('object_type', css_class='form-group col-md-6'),
                Column('icon', css_class='form-group col-md-3'),
                Column('color', css_class='form-group col-md-3'),
            ),
            Div(
                Field('cover_level', css_class='form-control'),
                css_class='cover-level-section',
                css_id='cover-level-container'
            ),
            Row(
                Column('is_visible_to_players', css_class='form-group col-md-4'),
                Column('blocks_movement', css_class='form-group col-md-4'),
                Column('blocks_vision', css_class='form-group col-md-4'),
            ),
            Field('stats', css_class='form-control'),
            Field('notes', css_class='form-control'),
            Submit('submit', 'Save Object', css_class='btn btn-primary')
        )

        # Pre-populate cover_level from stats if editing existing cover object
        if self.instance and self.instance.pk and self.instance.object_type == 'cover':
            if self.instance.stats and isinstance(self.instance.stats, dict):
                self.initial['cover_level'] = self.instance.stats.get('cover_level', '')

    def clean(self):
        cleaned_data = super().clean()
        object_type = cleaned_data.get('object_type')
        cover_level = cleaned_data.get('cover_level')

        # Require cover_level when object_type is 'cover'
        if object_type == 'cover' and not cover_level:
            self.add_error('cover_level', 'Please select a cover level for cover objects.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If this is a cover object, populate properties based on cover_level
        if instance.object_type == 'cover':
            cover_level = self.cleaned_data.get('cover_level')
            if cover_level:
                # Cover level properties
                cover_props = {
                    'light': {'defense_bonus': 2, 'icon': '🛡', 'blocks_movement': False, 'blocks_vision': False},
                    'medium': {'defense_bonus': 4, 'icon': '🛡️', 'blocks_movement': False, 'blocks_vision': False},
                    'heavy': {'defense_bonus': 6, 'icon': '🛡', 'blocks_movement': True, 'blocks_vision': True},
                }

                props = cover_props.get(cover_level, cover_props['light'])

                # Set icon if not already set
                if not instance.icon:
                    instance.icon = props['icon']

                # Set blocking properties based on cover level
                instance.blocks_movement = props['blocks_movement']
                instance.blocks_vision = props['blocks_vision']

                # Update stats with cover info
                if not instance.stats:
                    instance.stats = {}
                elif isinstance(instance.stats, str):
                    import json
                    try:
                        instance.stats = json.loads(instance.stats)
                    except:
                        instance.stats = {}

                instance.stats['cover_level'] = cover_level
                instance.stats['defense_bonus'] = props['defense_bonus']

                # Update description if not set
                if not instance.description:
                    level_names = {'light': 'Light', 'medium': 'Medium', 'heavy': 'Heavy'}
                    instance.description = f"{level_names[cover_level]} Cover providing +{props['defense_bonus']} defense"

        if commit:
            instance.save()
        return instance


class MapGenerationForm(forms.ModelForm):
    """Form for generating maps using presets"""

    ALGORITHM_CHOICES = [
        ('random', 'Random (Simple terrain distribution)'),
        ('bsp', 'BSP (Binary Space Partitioning - Rooms & Corridors)'),
        ('cellular_automata', 'Cellular Automata (Cave-like structures)'),
        ('random_walk', 'Random Walk (Winding paths)'),
        ('maze', 'Maze (Recursive backtracking)'),
    ]

    algorithm = forms.ChoiceField(
        choices=ALGORITHM_CHOICES,
        initial='random',
        help_text='Algorithm to use for map generation'
    )
    use_preset = forms.BooleanField(required=False, initial=False, label='Use existing preset')
    preset = forms.ModelChoiceField(
        queryset=MapGenerationPreset.objects.none(),
        required=False,
        help_text='Select a preset to load its settings'
    )
    seed = forms.CharField(
        required=False,
        max_length=50,
        help_text='Optional seed for reproducible generation (leave empty for random)'
    )

    # BSP Parameters
    min_room_size = forms.IntegerField(
        required=False,
        initial=4,
        min_value=3,
        max_value=15,
        help_text='Minimum room size for BSP algorithm (3-15)'
    )
    max_room_size = forms.IntegerField(
        required=False,
        initial=10,
        min_value=5,
        max_value=30,
        help_text='Maximum room size for BSP algorithm (5-30)'
    )
    corridor_width = forms.IntegerField(
        required=False,
        initial=1,
        min_value=1,
        max_value=3,
        help_text='Width of corridors for BSP algorithm (1-3)'
    )

    # Cellular Automata Parameters
    iterations = forms.IntegerField(
        required=False,
        initial=5,
        min_value=1,
        max_value=10,
        help_text='Number of smoothing iterations (1-10)'
    )
    wall_probability = forms.FloatField(
        required=False,
        initial=0.45,
        min_value=0.1,
        max_value=0.9,
        help_text='Initial wall density 0.1-0.9 (lower = more open)'
    )

    # Random Walk Parameters
    steps = forms.IntegerField(
        required=False,
        initial=None,
        min_value=10,
        help_text='Number of walk steps (leave empty for auto)'
    )
    tunnel_width_probability = forms.FloatField(
        required=False,
        initial=0.3,
        min_value=0.0,
        max_value=1.0,
        help_text='Probability of wider tunnels 0.0-1.0'
    )

    # Maze Parameters
    path_width = forms.IntegerField(
        required=False,
        initial=1,
        min_value=1,
        max_value=3,
        help_text='Width of maze paths (1-3)'
    )

    # Cover System Parameters
    cover_density = forms.FloatField(
        required=False,
        initial=0.15,
        min_value=0.0,
        max_value=0.5,
        help_text='Density of cover objects (0.0-0.5, 0.15 = 15% of floor tiles)'
    )

    class Meta:
        model = Map
        fields = ['name', 'width', 'height', 'map_type']

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Show user's presets and public presets
            self.fields['preset'].queryset = MapGenerationPreset.objects.filter(
                django_models.Q(owner=user) | django_models.Q(is_public=True)
            )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            HTML('<hr><h5>Generation Settings</h5>'),
            Field('algorithm', css_class='form-control', id='id_algorithm'),
            Row(
                Column('width', css_class='form-group col-md-4'),
                Column('height', css_class='form-group col-md-4'),
                Column('map_type', css_class='form-group col-md-4'),
            ),
            Field('seed', css_class='form-control'),

            HTML('<hr><h5>Algorithm Parameters</h5>'),
            HTML('<div id="bsp-params" style="display:none;">'),
            HTML('<h6>BSP (Binary Space Partitioning) Parameters</h6>'),
            Row(
                Column('min_room_size', css_class='form-group col-md-4'),
                Column('max_room_size', css_class='form-group col-md-4'),
                Column('corridor_width', css_class='form-group col-md-4'),
            ),
            HTML('</div>'),

            HTML('<div id="cellular-params" style="display:none;">'),
            HTML('<h6>Cellular Automata Parameters</h6>'),
            Row(
                Column('iterations', css_class='form-group col-md-6'),
                Column('wall_probability', css_class='form-group col-md-6'),
            ),
            HTML('</div>'),

            HTML('<div id="randomwalk-params" style="display:none;">'),
            HTML('<h6>Random Walk Parameters</h6>'),
            Row(
                Column('steps', css_class='form-group col-md-6'),
                Column('tunnel_width_probability', css_class='form-group col-md-6'),
            ),
            HTML('</div>'),

            HTML('<div id="maze-params" style="display:none;">'),
            HTML('<h6>Maze Parameters</h6>'),
            Field('path_width', css_class='form-control'),
            HTML('</div>'),

            HTML('<hr><h5>Cover System</h5>'),
            HTML('<p class="text-muted small">Add procedural cover objects (furniture, vehicles, etc.) for tactical gameplay</p>'),
            Field('cover_density', css_class='form-control'),

            HTML('<hr><h5>Or Use a Preset</h5>'),
            Div(
                Field('use_preset', css_class='form-check-input'),
                Field('preset', css_class='form-control'),
                css_class='preset-section'
            ),
            HTML('<hr>'),
            Submit('submit', 'Preview Map', css_class='btn btn-primary')
        )


class MapGenerationPresetForm(forms.ModelForm):
    """Form for creating and editing map generation presets"""

    class Meta:
        model = MapGenerationPreset
        fields = ['name', 'description', 'width', 'height', 'map_type',
                  'obstacle_density', 'object_density', 'generation_algorithm',
                  'custom_parameters', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'custom_parameters': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('description', css_class='form-control'),
            Row(
                Column('width', css_class='form-group col-md-4'),
                Column('height', css_class='form-group col-md-4'),
                Column('map_type', css_class='form-group col-md-4'),
            ),
            Row(
                Column('obstacle_density', css_class='form-group col-md-4'),
                Column('object_density', css_class='form-group col-md-4'),
                Column('generation_algorithm', css_class='form-group col-md-4'),
            ),
            Field('custom_parameters', css_class='form-control'),
            Field('is_public', css_class='form-check-input'),
            Submit('submit', 'Save Preset', css_class='btn btn-primary')
        )
