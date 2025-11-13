from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import DiceRoll, DicePreset
from .utils import (
    roll_d6,
    roll_shadowrun_dice,
    check_success,
    format_dice_results,
    calculate_opposed_test,
    get_hit_description
)
from characters.models import Character
from campaigns.models import Campaign


class DiceUtilsTestCase(TestCase):
    """Test dice rolling utility functions"""

    def test_roll_d6(self):
        """Test that roll_d6 returns value between 1 and 6"""
        for _ in range(100):
            roll = roll_d6()
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 6)

    def test_roll_shadowrun_dice_basic(self):
        """Test basic Shadowrun dice rolling"""
        result = roll_shadowrun_dice(pool_size=6, use_rule_of_six=False)

        # Check result structure
        self.assertIn('dice_results', result)
        self.assertIn('original_dice', result)
        self.assertIn('total_hits', result)
        self.assertIn('ones_count', result)
        self.assertIn('is_glitch', result)
        self.assertIn('is_critical_glitch', result)

        # Check dice count (should be exactly 6 without Rule of Six)
        self.assertEqual(len(result['original_dice']), 6)
        self.assertEqual(len(result['dice_results']), 6)

        # All dice should be between 1 and 6
        for die in result['dice_results']:
            self.assertGreaterEqual(die, 1)
            self.assertLessEqual(die, 6)

    def test_roll_shadowrun_dice_with_rule_of_six(self):
        """Test Shadowrun dice rolling with Rule of Six"""
        # Test multiple times to potentially trigger explosions
        for _ in range(10):
            result = roll_shadowrun_dice(pool_size=10, use_rule_of_six=True)

            # Original dice should be 10
            self.assertEqual(len(result['original_dice']), 10)

            # Total dice could be more due to explosions
            self.assertGreaterEqual(len(result['dice_results']), 10)

    def test_check_success(self):
        """Test success checking"""
        # Success cases
        self.assertTrue(check_success(5, 3))
        self.assertTrue(check_success(3, 3))

        # Failure cases
        self.assertFalse(check_success(2, 3))

        # No threshold
        self.assertIsNone(check_success(5, None))

    def test_format_dice_results(self):
        """Test dice result formatting"""
        dice_results = [5, 1, 3, 6, 2]
        formatted = format_dice_results(dice_results)

        # Should contain hits marked with []
        self.assertIn('[5]', formatted)
        self.assertIn('[6]', formatted)

        # Should contain ones marked with ()
        self.assertIn('(1)', formatted)

        # Should contain normal dice
        self.assertIn('3', formatted)
        self.assertIn('2', formatted)

    def test_format_dice_results_with_explosions(self):
        """Test dice result formatting with explosion separator"""
        dice_results = [5, 1, 3, 6, 2, 6, 4]  # 5 original, 2 explosions
        formatted = format_dice_results(dice_results, original_count=5)

        # Should contain separator
        self.assertIn('|', formatted)

    def test_calculate_opposed_test(self):
        """Test opposed test calculation"""
        # Attacker wins
        result = calculate_opposed_test(5, 3)
        self.assertEqual(result['winner'], 'attacker')
        self.assertEqual(result['net_hits'], 2)
        self.assertTrue(result['attacker_success'])

        # Defender wins
        result = calculate_opposed_test(2, 4)
        self.assertEqual(result['winner'], 'defender')
        self.assertEqual(result['net_hits'], 2)
        self.assertFalse(result['attacker_success'])

        # Tie (goes to defender)
        result = calculate_opposed_test(3, 3)
        self.assertEqual(result['winner'], 'tie')
        self.assertEqual(result['net_hits'], 0)
        self.assertFalse(result['attacker_success'])

    def test_get_hit_description(self):
        """Test hit description generation"""
        self.assertEqual(get_hit_description(0), "No hits")
        self.assertEqual(get_hit_description(1), "1 hit")
        self.assertIn("Marginal", get_hit_description(2))
        self.assertIn("Good", get_hit_description(4))
        self.assertIn("Great", get_hit_description(7))
        self.assertIn("Exceptional", get_hit_description(10))


class DiceRollModelTestCase(TestCase):
    """Test DiceRoll model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_dice_roll(self):
        """Test creating a dice roll"""
        dice_roll = DiceRoll.objects.create(
            user=self.user,
            description="Test Roll",
            pool_size=6,
            threshold=3,
            use_rule_of_six=True,
            edge_used=False,
            dice_results="5,6,3,1,4,2",
            total_hits=2,
            ones_count=1,
            is_glitch=False,
            is_critical_glitch=False,
            success=False
        )

        self.assertEqual(dice_roll.user, self.user)
        self.assertEqual(dice_roll.description, "Test Roll")
        self.assertEqual(dice_roll.pool_size, 6)
        self.assertEqual(dice_roll.total_hits, 2)
        self.assertFalse(dice_roll.success)

    def test_dice_roll_str(self):
        """Test DiceRoll string representation"""
        dice_roll = DiceRoll.objects.create(
            user=self.user,
            description="Attack Roll",
            pool_size=8,
            dice_results="5,6,6,3,1,4,2,5",
            total_hits=4,
            ones_count=1,
            is_glitch=False,
            is_critical_glitch=False
        )

        str_repr = str(dice_roll)
        self.assertIn(self.user.username, str_repr)
        self.assertIn("Attack Roll", str_repr)
        self.assertIn("4 hits", str_repr)

    def test_get_dice_list(self):
        """Test get_dice_list method"""
        dice_roll = DiceRoll.objects.create(
            user=self.user,
            pool_size=5,
            dice_results="5,3,6,1,4",
            total_hits=2,
            ones_count=1,
            is_glitch=False,
            is_critical_glitch=False
        )

        dice_list = dice_roll.get_dice_list()
        self.assertEqual(dice_list, [5, 3, 6, 1, 4])

    def test_get_result_summary(self):
        """Test get_result_summary method"""
        # Basic success
        dice_roll = DiceRoll.objects.create(
            user=self.user,
            pool_size=6,
            threshold=3,
            dice_results="5,6,6,3,1,4",
            total_hits=3,
            ones_count=1,
            is_glitch=False,
            is_critical_glitch=False,
            success=True
        )
        summary = dice_roll.get_result_summary()
        self.assertIn("3 hits", summary)
        self.assertIn("Success", summary)

        # Critical glitch
        dice_roll.is_critical_glitch = True
        dice_roll.total_hits = 0
        summary = dice_roll.get_result_summary()
        self.assertIn("CRITICAL GLITCH", summary)


class DicePresetModelTestCase(TestCase):
    """Test DicePreset model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_preset(self):
        """Test creating a dice preset"""
        preset = DicePreset.objects.create(
            user=self.user,
            name="Combat Pool",
            description="My standard combat dice pool",
            pool_size=12,
            threshold=4,
            use_rule_of_six=True
        )

        self.assertEqual(preset.user, self.user)
        self.assertEqual(preset.name, "Combat Pool")
        self.assertEqual(preset.pool_size, 12)
        self.assertEqual(preset.threshold, 4)
        self.assertTrue(preset.use_rule_of_six)

    def test_preset_str(self):
        """Test DicePreset string representation"""
        preset = DicePreset.objects.create(
            user=self.user,
            name="Perception Check",
            pool_size=8
        )

        str_repr = str(preset)
        self.assertIn("Perception Check", str_repr)
        self.assertIn("8d6", str_repr)

    def test_preset_unique_together(self):
        """Test that preset name must be unique per user"""
        DicePreset.objects.create(
            user=self.user,
            name="My Preset",
            pool_size=6
        )

        # Creating another preset with same name for same user should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            DicePreset.objects.create(
                user=self.user,
                name="My Preset",
                pool_size=8
            )


class DiceViewsTestCase(TestCase):
    """Test dice views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dice_roller_view_get(self):
        """Test dice roller page loads"""
        response = self.client.get(reverse('dice:roller'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dice/roller.html')
        self.assertIn('form', response.context)

    def test_dice_roller_view_post(self):
        """Test rolling dice via POST"""
        response = self.client.post(reverse('dice:roller'), {
            'pool_size': 6,
            'description': 'Test Roll',
            'threshold': 3,
            'use_rule_of_six': True,
            'edge_used': False
        })

        # Should redirect to roll detail
        self.assertEqual(response.status_code, 302)

        # Check that roll was created
        self.assertEqual(DiceRoll.objects.count(), 1)
        roll = DiceRoll.objects.first()
        self.assertEqual(roll.pool_size, 6)
        self.assertEqual(roll.description, 'Test Roll')

    def test_dice_roller_requires_login(self):
        """Test that dice roller requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('dice:roller'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_roll_detail_view(self):
        """Test roll detail page"""
        # Create a roll
        roll = DiceRoll.objects.create(
            user=self.user,
            pool_size=6,
            dice_results="5,6,3,1,4,2",
            total_hits=2,
            ones_count=1,
            is_glitch=False,
            is_critical_glitch=False
        )

        response = self.client.get(reverse('dice:roll_detail', args=[roll.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dice/roll_detail.html')
        self.assertEqual(response.context['dice_roll'], roll)

    def test_roll_history_view(self):
        """Test roll history page"""
        # Create some rolls
        for i in range(5):
            DiceRoll.objects.create(
                user=self.user,
                pool_size=6,
                dice_results="5,3,6,1,4,2",
                total_hits=2,
                ones_count=1,
                is_glitch=False,
                is_critical_glitch=False
            )

        response = self.client.get(reverse('dice:history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dice/history.html')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_preset_list_view(self):
        """Test preset list page"""
        # Create some presets
        DicePreset.objects.create(
            user=self.user,
            name="Combat",
            pool_size=12
        )
        DicePreset.objects.create(
            user=self.user,
            name="Perception",
            pool_size=8
        )

        response = self.client.get(reverse('dice:preset_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dice/preset_list.html')
        self.assertEqual(len(response.context['presets']), 2)

    def test_preset_create_view(self):
        """Test creating a preset"""
        response = self.client.post(reverse('dice:preset_create'), {
            'name': 'New Preset',
            'description': 'Test preset',
            'pool_size': 10,
            'threshold': 3,
            'use_rule_of_six': True
        })

        # Should redirect to preset list
        self.assertEqual(response.status_code, 302)

        # Check preset was created
        self.assertEqual(DicePreset.objects.count(), 1)
        preset = DicePreset.objects.first()
        self.assertEqual(preset.name, 'New Preset')
        self.assertEqual(preset.pool_size, 10)

    def test_preset_edit_view(self):
        """Test editing a preset"""
        preset = DicePreset.objects.create(
            user=self.user,
            name="Old Name",
            pool_size=6
        )

        response = self.client.post(
            reverse('dice:preset_edit', args=[preset.pk]),
            {
                'name': 'New Name',
                'pool_size': 8,
                'use_rule_of_six': True
            }
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Check preset was updated
        preset.refresh_from_db()
        self.assertEqual(preset.name, 'New Name')
        self.assertEqual(preset.pool_size, 8)

    def test_preset_delete_view(self):
        """Test deleting a preset"""
        preset = DicePreset.objects.create(
            user=self.user,
            name="To Delete",
            pool_size=6
        )

        response = self.client.post(
            reverse('dice:preset_delete', args=[preset.pk])
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Check preset was deleted
        self.assertEqual(DicePreset.objects.count(), 0)

    def test_preset_roll_view(self):
        """Test rolling from a preset"""
        preset = DicePreset.objects.create(
            user=self.user,
            name="Quick Roll",
            pool_size=8,
            threshold=3,
            use_rule_of_six=True
        )

        response = self.client.get(
            reverse('dice:preset_roll', args=[preset.pk])
        )

        # Should redirect to roll detail
        self.assertEqual(response.status_code, 302)

        # Check roll was created
        self.assertEqual(DiceRoll.objects.count(), 1)
        roll = DiceRoll.objects.first()
        self.assertEqual(roll.pool_size, 8)
        self.assertEqual(roll.threshold, 3)
        self.assertIn(preset.name, roll.description)


class DiceFormsTestCase(TestCase):
    """Test dice forms"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_dice_roll_form_valid(self):
        """Test valid dice roll form"""
        from .forms import DiceRollForm

        form = DiceRollForm(data={
            'pool_size': 6,
            'description': 'Test',
            'threshold': 3,
            'use_rule_of_six': True,
            'edge_used': False
        })

        self.assertTrue(form.is_valid())

    def test_dice_roll_form_invalid_pool_size(self):
        """Test invalid pool size"""
        from .forms import DiceRollForm

        # Too small
        form = DiceRollForm(data={'pool_size': 0})
        self.assertFalse(form.is_valid())

        # Too large
        form = DiceRollForm(data={'pool_size': 100})
        self.assertFalse(form.is_valid())

    def test_dice_preset_form_valid(self):
        """Test valid dice preset form"""
        from .forms import DicePresetForm

        form = DicePresetForm(
            user=self.user,
            data={
                'name': 'Test Preset',
                'pool_size': 8,
                'use_rule_of_six': True
            }
        )

        self.assertTrue(form.is_valid())


class DiceIntegrationTestCase(TestCase):
    """Integration tests for dice rolling with other apps"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create a character
        self.character = Character.objects.create(
            user=self.user,
            name="Test Runner",
            race="Human",
            role="Street Samurai"
        )

    def test_dice_roll_with_character(self):
        """Test dice roll associated with character"""
        dice_roll = DiceRoll.objects.create(
            user=self.user,
            character=self.character,
            pool_size=10,
            dice_results="5,6,6,3,1,4,2,5,6,4",
            total_hits=5,
            ones_count=1,
            is_glitch=False,
            is_critical_glitch=False
        )

        self.assertEqual(dice_roll.character, self.character)
        self.assertIn(dice_roll, self.character.dice_rolls.all())

    def test_preset_with_character(self):
        """Test preset associated with character"""
        preset = DicePreset.objects.create(
            user=self.user,
            character=self.character,
            name="Combat Pool",
            pool_size=12
        )

        self.assertEqual(preset.character, self.character)
        self.assertIn(preset, self.character.dice_presets.all())
