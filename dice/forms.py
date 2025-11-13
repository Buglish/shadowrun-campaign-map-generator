from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from .models import DicePreset


class DiceRollForm(forms.Form):
    """Form for rolling Shadowrun dice"""

    pool_size = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=6,
        label="Dice Pool",
        help_text="Number of dice to roll (1-50)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter pool size'
        })
    )

    description = forms.CharField(
        max_length=200,
        required=False,
        label="Description",
        help_text="What is this roll for? (Optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Pistols Attack, Perception Check'
        })
    )

    threshold = forms.IntegerField(
        min_value=1,
        max_value=20,
        required=False,
        label="Threshold",
        help_text="Number of hits needed to succeed (Optional)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave empty if not needed'
        })
    )

    use_rule_of_six = forms.BooleanField(
        initial=True,
        required=False,
        label="Rule of Six",
        help_text="6s explode and add additional dice"
    )

    edge_used = forms.BooleanField(
        initial=False,
        required=False,
        label="Use Edge",
        help_text="Spend Edge to push your luck"
    )

    # Optional context fields
    campaign_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    session_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    character_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'dice-roll-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('pool_size', css_class='form-group col-md-4 mb-3'),
                Column('threshold', css_class='form-group col-md-4 mb-3'),
                Column('description', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('use_rule_of_six', css_class='form-group col-md-6 mb-3'),
                Column('edge_used', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'campaign_id',
            'session_id',
            'character_id',
            Submit('submit', 'Roll Dice', css_class='btn btn-primary btn-lg')
        )


class QuickRollForm(forms.Form):
    """Simplified form for quick dice rolls"""

    pool_size = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Pool Size'
        })
    )

    use_rule_of_six = forms.BooleanField(
        initial=True,
        required=False,
        label="Rule of Six"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'quick-roll-form'
        self.helper.form_class = 'd-flex gap-2 align-items-center'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                'pool_size',
                css_class='flex-grow-1'
            ),
            'use_rule_of_six',
            Submit('submit', 'Roll', css_class='btn btn-success')
        )


class DicePresetForm(forms.ModelForm):
    """Form for creating and editing dice presets"""

    class Meta:
        model = DicePreset
        fields = [
            'name',
            'description',
            'pool_size',
            'threshold',
            'use_rule_of_six',
            'character',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'name',
            'description',
            Row(
                Column('pool_size', css_class='form-group col-md-6 mb-3'),
                Column('threshold', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'use_rule_of_six',
            'character',
            Submit('submit', 'Save Preset', css_class='btn btn-primary')
        )

        # Filter character choices to only show user's characters
        if user:
            self.fields['character'].queryset = self.fields['character'].queryset.filter(
                user=user
            )
