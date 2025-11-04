from django.core.management.base import BaseCommand
from characters.models import Quality, Gear


class Command(BaseCommand):
    help = 'Populate database with sample Shadowrun qualities and gear'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating sample data...')

        # Create sample positive qualities
        positive_qualities = [
            {
                'name': 'Ambidextrous',
                'karma_cost': -4,
                'description': 'No penalty for using off-hand weapons or tools.'
            },
            {
                'name': 'Catlike',
                'karma_cost': -7,
                'description': '+2 dice to Sneaking tests, reduce falling damage by 1 meter.'
            },
            {
                'name': 'High Pain Tolerance',
                'karma_cost': -7,
                'description': 'Ignore wound modifiers until you\'re one box away from unconsciousness.'
            },
            {
                'name': 'Lucky',
                'karma_cost': -12,
                'description': 'Re-roll one failed test per session.'
            },
            {
                'name': 'Natural Athlete',
                'karma_cost': -7,
                'description': '+2 dice to all Athletics tests.'
            },
            {
                'name': 'Toughness',
                'karma_cost': -9,
                'description': 'Gain +1 to Physical damage resistance tests.'
            },
        ]

        for quality_data in positive_qualities:
            Quality.objects.get_or_create(
                name=quality_data['name'],
                defaults={
                    'quality_type': 'positive',
                    'karma_cost': quality_data['karma_cost'],
                    'description': quality_data['description'],
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created positive quality: {quality_data["name"]}')

        # Create sample negative qualities
        negative_qualities = [
            {
                'name': 'Allergy (Common)',
                'karma_cost': 10,
                'description': 'Suffer penalties when exposed to common allergen.'
            },
            {
                'name': 'Bad Luck',
                'karma_cost': 12,
                'description': 'GM can force re-roll of one successful test per session.'
            },
            {
                'name': 'Code of Honor',
                'karma_cost': 15,
                'description': 'Must follow a strict personal code.'
            },
            {
                'name': 'Combat Paralysis',
                'karma_cost': 12,
                'description': 'Must make Willpower test to act in combat.'
            },
            {
                'name': 'Distinctive Style',
                'karma_cost': 5,
                'description': '-1 die to disguise, easier to track and identify.'
            },
            {
                'name': 'Phobia (Common)',
                'karma_cost': 10,
                'description': 'Fear of common object or situation causes penalties.'
            },
        ]

        for quality_data in negative_qualities:
            Quality.objects.get_or_create(
                name=quality_data['name'],
                defaults={
                    'quality_type': 'negative',
                    'karma_cost': quality_data['karma_cost'],
                    'description': quality_data['description'],
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created negative quality: {quality_data["name"]}')

        # Create sample weapons
        weapons = [
            {
                'name': 'Ares Predator V',
                'category': 'weapon',
                'description': 'Heavy pistol, the classic shadowrunner sidearm',
                'cost': 725,
                'availability': '5R'
            },
            {
                'name': 'Fichetti Security 600',
                'category': 'weapon',
                'description': 'Light pistol, easy to conceal',
                'cost': 350,
                'availability': '4R'
            },
            {
                'name': 'AK-97',
                'category': 'weapon',
                'description': 'Assault rifle, reliable and popular',
                'cost': 950,
                'availability': '4R'
            },
            {
                'name': 'Remington 990',
                'category': 'weapon',
                'description': 'Shotgun, devastating at close range',
                'cost': 650,
                'availability': '4R'
            },
            {
                'name': 'Knife',
                'category': 'weapon',
                'description': 'Basic melee weapon',
                'cost': 10,
                'availability': '—'
            },
        ]

        for weapon_data in weapons:
            Gear.objects.get_or_create(
                name=weapon_data['name'],
                defaults={
                    'category': weapon_data['category'],
                    'description': weapon_data['description'],
                    'cost': weapon_data['cost'],
                    'availability': weapon_data['availability'],
                    'essence_cost': 0.00,
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created weapon: {weapon_data["name"]}')

        # Create sample armor
        armor_items = [
            {
                'name': 'Armor Jacket',
                'category': 'armor',
                'description': 'Standard shadowrunner armor',
                'cost': 1000,
                'availability': '2'
            },
            {
                'name': 'Lined Coat',
                'category': 'armor',
                'description': 'Concealed armor for social situations',
                'cost': 900,
                'availability': '4'
            },
            {
                'name': 'Full Body Armor',
                'category': 'armor',
                'description': 'Heavy protection for combat',
                'cost': 2000,
                'availability': '10R'
            },
        ]

        for armor_data in armor_items:
            Gear.objects.get_or_create(
                name=armor_data['name'],
                defaults={
                    'category': armor_data['category'],
                    'description': armor_data['description'],
                    'cost': armor_data['cost'],
                    'availability': armor_data['availability'],
                    'essence_cost': 0.00,
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created armor: {armor_data["name"]}')

        # Create sample cyberware
        cyberware_items = [
            {
                'name': 'Cybereyes (Rating 1)',
                'category': 'cyberware',
                'description': 'Replacement eyes with basic enhancements',
                'cost': 500,
                'availability': '2',
                'essence_cost': 0.10
            },
            {
                'name': 'Wired Reflexes (Rating 1)',
                'category': 'cyberware',
                'description': '+1 Reaction, +1D6 Initiative',
                'cost': 13000,
                'availability': '6R',
                'essence_cost': 2.00
            },
            {
                'name': 'Dermal Plating (Rating 1)',
                'category': 'cyberware',
                'description': '+1 Armor',
                'cost': 2000,
                'availability': '6',
                'essence_cost': 1.00
            },
        ]

        for cyber_data in cyberware_items:
            Gear.objects.get_or_create(
                name=cyber_data['name'],
                defaults={
                    'category': cyber_data['category'],
                    'description': cyber_data['description'],
                    'cost': cyber_data['cost'],
                    'availability': cyber_data['availability'],
                    'essence_cost': cyber_data['essence_cost'],
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created cyberware: {cyber_data["name"]}')

        # Create sample electronics
        electronics = [
            {
                'name': 'Commlink (Meta Link)',
                'category': 'electronics',
                'description': 'Basic communication device',
                'cost': 100,
                'availability': '—'
            },
            {
                'name': 'Commlink (Sony Emperor)',
                'category': 'electronics',
                'description': 'High-end communication device',
                'cost': 700,
                'availability': '3'
            },
            {
                'name': 'Credstick (Standard)',
                'category': 'electronics',
                'description': 'For electronic transactions',
                'cost': 5,
                'availability': '—'
            },
        ]

        for elec_data in electronics:
            Gear.objects.get_or_create(
                name=elec_data['name'],
                defaults={
                    'category': elec_data['category'],
                    'description': elec_data['description'],
                    'cost': elec_data['cost'],
                    'availability': elec_data['availability'],
                    'essence_cost': 0.00,
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created electronics: {elec_data["name"]}')

        # Create miscellaneous gear
        misc_gear = [
            {
                'name': 'Fake SIN (Rating 4)',
                'category': 'misc',
                'description': 'Fake identification',
                'cost': 10000,
                'availability': '12F'
            },
            {
                'name': 'Medkit (Rating 6)',
                'category': 'misc',
                'description': 'Advanced medical supplies',
                'cost': 1000,
                'availability': '6R'
            },
            {
                'name': 'Lockpick Set',
                'category': 'misc',
                'description': 'Tools for bypassing mechanical locks',
                'cost': 150,
                'availability': '4R'
            },
        ]

        for misc_data in misc_gear:
            Gear.objects.get_or_create(
                name=misc_data['name'],
                defaults={
                    'category': misc_data['category'],
                    'description': misc_data['description'],
                    'cost': misc_data['cost'],
                    'availability': misc_data['availability'],
                    'essence_cost': 0.00,
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created misc gear: {misc_data["name"]}')

        self.stdout.write(self.style.SUCCESS('\nSample data populated successfully!'))
