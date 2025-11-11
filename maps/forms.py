from django import forms
from django.contrib.auth.models import User
from django.db import models as django_models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Div, HTML
from .models import Map, MapTile, MapObject, MapGenerationPreset


class MapForm(forms.ModelForm):
    """Form for creating and editing maps"""

    class Meta:
        model = Map
        fields = ['name', 'description', 'width', 'height', 'tile_size', 'map_type', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
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
                Column('tile_size', css_class='form-group col-md-4'),
            ),
            Row(
                Column('map_type', css_class='form-group col-md-6'),
                Column('is_public', css_class='form-group col-md-6'),
            ),
            Submit('submit', 'Save Map', css_class='btn btn-primary')
        )


class MapObjectForm(forms.ModelForm):
    """Form for creating and editing map objects"""

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
            Row(
                Column('is_visible_to_players', css_class='form-group col-md-4'),
                Column('blocks_movement', css_class='form-group col-md-4'),
                Column('blocks_vision', css_class='form-group col-md-4'),
            ),
            Field('stats', css_class='form-control'),
            Field('notes', css_class='form-control'),
            Submit('submit', 'Save Object', css_class='btn btn-primary')
        )


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
