from django.core.management.base import BaseCommand
from characters.models import Quality, Gear, Skill, Spell, AdeptPower, ComplexForm


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
                'availability': '2',
                'armor_rating': 12
            },
            {
                'name': 'Lined Coat',
                'category': 'armor',
                'description': 'Concealed armor for social situations',
                'cost': 900,
                'availability': '4',
                'armor_rating': 9
            },
            {
                'name': 'Full Body Armor',
                'category': 'armor',
                'description': 'Heavy protection for combat',
                'cost': 2000,
                'availability': '10R',
                'armor_rating': 18
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
                    'armor_rating': armor_data.get('armor_rating'),
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
                'essence_cost': 0.10,
                'armor_bonus': 0,
                'initiative_dice_bonus': 0,
                'reaction_bonus': 0
            },
            {
                'name': 'Wired Reflexes (Rating 1)',
                'category': 'cyberware',
                'description': '+1 Reaction, +1D6 Initiative',
                'cost': 13000,
                'availability': '6R',
                'essence_cost': 2.00,
                'armor_bonus': 0,
                'initiative_dice_bonus': 1,
                'reaction_bonus': 1
            },
            {
                'name': 'Dermal Plating (Rating 1)',
                'category': 'cyberware',
                'description': '+1 Armor',
                'cost': 2000,
                'availability': '6',
                'essence_cost': 1.00,
                'armor_bonus': 1,
                'initiative_dice_bonus': 0,
                'reaction_bonus': 0
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
                    'armor_bonus': cyber_data.get('armor_bonus', 0),
                    'initiative_dice_bonus': cyber_data.get('initiative_dice_bonus', 0),
                    'reaction_bonus': cyber_data.get('reaction_bonus', 0),
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

        # Create sample skills
        self.stdout.write('\nPopulating skills...')

        skills = [
            # Combat Skills
            {'name': 'Archery', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Bows and crossbows'},
            {'name': 'Automatics', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Automatic weapons (SMGs, assault rifles)'},
            {'name': 'Blades', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Swords, knives, and edged weapons'},
            {'name': 'Clubs', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Bludgeoning weapons'},
            {'name': 'Heavy Weapons', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Machine guns, missile launchers, assault cannons'},
            {'name': 'Longarms', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Rifles and shotguns'},
            {'name': 'Pistols', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Handguns'},
            {'name': 'Throwing Weapons', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Thrown projectiles'},
            {'name': 'Unarmed Combat', 'category': 'combat', 'linked_attribute': 'agility', 'description': 'Hand-to-hand fighting'},

            # Physical Skills
            {'name': 'Disguise', 'category': 'physical', 'linked_attribute': 'intuition', 'description': 'Change appearance'},
            {'name': 'Diving', 'category': 'physical', 'linked_attribute': 'body', 'description': 'Underwater activity'},
            {'name': 'Escape Artist', 'category': 'physical', 'linked_attribute': 'agility', 'description': 'Get out of bonds and tight spaces'},
            {'name': 'Free-Fall', 'category': 'physical', 'linked_attribute': 'body', 'description': 'Skydiving and parachuting'},
            {'name': 'Gymnastics', 'category': 'physical', 'linked_attribute': 'agility', 'description': 'Acrobatics and balance'},
            {'name': 'Palming', 'category': 'physical', 'linked_attribute': 'agility', 'description': 'Sleight of hand'},
            {'name': 'Perception', 'category': 'physical', 'linked_attribute': 'intuition', 'description': 'Notice details and spot threats'},
            {'name': 'Running', 'category': 'physical', 'linked_attribute': 'strength', 'description': 'Sprinting and endurance'},
            {'name': 'Sneaking', 'category': 'physical', 'linked_attribute': 'agility', 'description': 'Move silently and avoid detection'},
            {'name': 'Survival', 'category': 'physical', 'linked_attribute': 'willpower', 'description': 'Wilderness survival'},
            {'name': 'Swimming', 'category': 'physical', 'linked_attribute': 'strength', 'description': 'Move through water'},
            {'name': 'Tracking', 'category': 'physical', 'linked_attribute': 'intuition', 'description': 'Follow trails and tracks'},

            # Social Skills
            {'name': 'Con', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Deception and trickery'},
            {'name': 'Etiquette', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Social grace and customs'},
            {'name': 'Impersonation', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Pretend to be someone else'},
            {'name': 'Instruction', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Teaching others'},
            {'name': 'Intimidation', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Coerce through fear'},
            {'name': 'Leadership', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Command and inspire'},
            {'name': 'Negotiation', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Bargaining and deal-making'},
            {'name': 'Performance', 'category': 'social', 'linked_attribute': 'charisma', 'description': 'Entertain an audience'},

            # Technical Skills
            {'name': 'Aeronautics Mechanic', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Repair aircraft'},
            {'name': 'Armorer', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Maintain and repair weapons'},
            {'name': 'Automotive Mechanic', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Repair ground vehicles'},
            {'name': 'Biotechnology', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Biological science and modification'},
            {'name': 'Chemistry', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Chemical knowledge'},
            {'name': 'Computer', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Use and program computers'},
            {'name': 'Cybercombat', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Hacking and Matrix combat'},
            {'name': 'Cybertechnology', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Install and maintain cyberware'},
            {'name': 'Demolitions', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Explosives'},
            {'name': 'Electronic Warfare', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Jam and intercept signals'},
            {'name': 'First Aid', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Emergency medical care'},
            {'name': 'Forgery', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Create fake documents'},
            {'name': 'Hacking', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Intrude into computer systems'},
            {'name': 'Hardware', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Build and repair electronics'},
            {'name': 'Industrial Mechanic', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Repair industrial equipment'},
            {'name': 'Locksmith', 'category': 'technical', 'linked_attribute': 'agility', 'description': 'Pick locks and bypass security'},
            {'name': 'Medicine', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Professional medical care'},
            {'name': 'Nautical Mechanic', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Repair watercraft'},
            {'name': 'Navigation', 'category': 'technical', 'linked_attribute': 'intuition', 'description': 'Find your way'},
            {'name': 'Software', 'category': 'technical', 'linked_attribute': 'logic', 'description': 'Program and design software'},

            # Vehicle Skills
            {'name': 'Gunnery', 'category': 'vehicle', 'linked_attribute': 'agility', 'description': 'Operate vehicle-mounted weapons'},
            {'name': 'Pilot Aerospace', 'category': 'vehicle', 'linked_attribute': 'reaction', 'description': 'Fly spacecraft'},
            {'name': 'Pilot Aircraft', 'category': 'vehicle', 'linked_attribute': 'reaction', 'description': 'Fly aircraft'},
            {'name': 'Pilot Ground Craft', 'category': 'vehicle', 'linked_attribute': 'reaction', 'description': 'Drive ground vehicles'},
            {'name': 'Pilot Watercraft', 'category': 'vehicle', 'linked_attribute': 'reaction', 'description': 'Operate watercraft'},

            # Magical Skills
            {'name': 'Alchemy', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Create magical preparations'},
            {'name': 'Arcana', 'category': 'magical', 'linked_attribute': 'logic', 'description': 'Magical theory'},
            {'name': 'Artificing', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Create foci'},
            {'name': 'Assensing', 'category': 'magical', 'linked_attribute': 'intuition', 'description': 'Perceive astral space'},
            {'name': 'Astral Combat', 'category': 'magical', 'linked_attribute': 'willpower', 'description': 'Fight in astral space'},
            {'name': 'Banishing', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Dismiss spirits'},
            {'name': 'Binding', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Bind spirits to service'},
            {'name': 'Counterspelling', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Defend against magic'},
            {'name': 'Disenchanting', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Remove magical effects'},
            {'name': 'Ritual Spellcasting', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Cast ritual spells'},
            {'name': 'Spellcasting', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Cast spells'},
            {'name': 'Summoning', 'category': 'magical', 'linked_attribute': 'magic', 'description': 'Call forth spirits'},

            # Resonance Skills
            {'name': 'Compiling', 'category': 'resonance', 'linked_attribute': 'resonance', 'description': 'Create sprites'},
            {'name': 'Decompiling', 'category': 'resonance', 'linked_attribute': 'resonance', 'description': 'Destroy sprites'},
            {'name': 'Registering', 'category': 'resonance', 'linked_attribute': 'resonance', 'description': 'Bind sprites to service'},
        ]

        for skill_data in skills:
            Skill.objects.get_or_create(
                name=skill_data['name'],
                category=skill_data['category'],
                defaults={
                    'linked_attribute': skill_data['linked_attribute'],
                    'description': skill_data['description'],
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created {skill_data["category"]} skill: {skill_data["name"]}')

        # Create sample spells
        self.stdout.write('\nPopulating spells...')

        spells = [
            # Combat Spells
            {'name': 'Acid Stream', 'category': 'combat', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'instant', 'drain': 'F-3', 'description': 'Projects a stream of acid that burns through armor and flesh.'},
            {'name': 'Ball Lightning', 'category': 'combat', 'spell_type': 'physical', 'range_type': 'los_area', 'duration': 'instant', 'drain': 'F-1', 'description': 'Creates a sphere of lightning that damages all in the area.'},
            {'name': 'Clout', 'category': 'combat', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'instant', 'drain': 'F-3', 'description': 'Invisible force strikes a target, causing stun damage.'},
            {'name': 'Fireball', 'category': 'combat', 'spell_type': 'physical', 'range_type': 'los_area', 'duration': 'instant', 'drain': 'F-1', 'description': 'Conjures an explosive ball of fire that damages all in the area.'},
            {'name': 'Lightning Bolt', 'category': 'combat', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'instant', 'drain': 'F-3', 'description': 'Hurls a bolt of lightning at a single target.'},
            {'name': 'Manabolt', 'category': 'combat', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'instant', 'drain': 'F-3', 'description': 'Channels mana energy to cause stun damage to a living target.'},
            {'name': 'Powerbolt', 'category': 'combat', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'instant', 'drain': 'F-3', 'description': 'Channels raw energy to cause physical damage.'},
            {'name': 'Punch', 'category': 'combat', 'spell_type': 'physical', 'range_type': 'touch', 'duration': 'instant', 'drain': 'F-6', 'description': 'Amplifies the force of a melee strike with magical energy.'},
            {'name': 'Shatter', 'category': 'combat', 'spell_type': 'physical', 'range_type': 'touch', 'duration': 'instant', 'drain': 'F-4', 'description': 'Destroys inanimate objects.'},
            {'name': 'Stunball', 'category': 'combat', 'spell_type': 'mana', 'range_type': 'los_area', 'duration': 'instant', 'drain': 'F-1', 'description': 'Area effect spell that stuns all living targets.'},
            {'name': 'Stunbolt', 'category': 'combat', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'instant', 'drain': 'F-3', 'description': 'Stuns a single living target.'},

            # Detection Spells
            {'name': 'Analyze Device', 'category': 'detection', 'spell_type': 'physical', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-3', 'description': 'Reveals how a device operates and how to use it.'},
            {'name': 'Analyze Truth', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Determines if the target is lying.'},
            {'name': 'Clairaudience', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-3', 'description': 'Hear sounds from a distant location.'},
            {'name': 'Clairvoyance', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-3', 'description': 'See a distant location.'},
            {'name': 'Combat Sense', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F', 'description': 'Provides a dice bonus to defense tests.'},
            {'name': 'Detect Enemies', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Detects hostile individuals within range.'},
            {'name': 'Detect Life', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-3', 'description': 'Senses living beings in an area.'},
            {'name': 'Detect Magic', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Senses active magic in the area.'},
            {'name': 'Mind Link', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Creates telepathic communication between targets.'},
            {'name': 'Mind Probe', 'category': 'detection', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F', 'description': 'Reads surface thoughts and memories.'},

            # Health Spells
            {'name': 'Antidote', 'category': 'health', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'permanent', 'drain': 'F-3', 'description': 'Neutralizes toxins in the target.'},
            {'name': 'Cure Disease', 'category': 'health', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'permanent', 'drain': 'F-4', 'description': 'Eliminates disease from the target.'},
            {'name': 'Decrease Attribute', 'category': 'health', 'spell_type': 'physical', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Temporarily reduces one of the target\'s attributes.'},
            {'name': 'Heal', 'category': 'health', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'permanent', 'drain': 'F-4', 'description': 'Heals physical damage on a living target.'},
            {'name': 'Increase Attribute', 'category': 'health', 'spell_type': 'physical', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-3', 'description': 'Temporarily boosts one of the target\'s attributes.'},
            {'name': 'Increase Reflexes', 'category': 'health', 'spell_type': 'physical', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F', 'description': 'Increases Reaction and adds Initiative Dice.'},
            {'name': 'Prophylaxis', 'category': 'health', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-4', 'description': 'Provides protection against toxins and diseases.'},
            {'name': 'Resist Pain', 'category': 'health', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'permanent', 'drain': 'F-4', 'description': 'Allows the target to ignore wound modifiers.'},
            {'name': 'Stabilize', 'category': 'health', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'permanent', 'drain': 'F-4', 'description': 'Stabilizes a dying character.'},

            # Illusion Spells
            {'name': 'Chaos', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Creates disturbing sensory illusions to confuse targets.'},
            {'name': 'Confusion', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-3', 'description': 'Causes the target to become disoriented.'},
            {'name': 'Entertainment', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F-3', 'description': 'Creates entertaining illusions for an audience.'},
            {'name': 'Hush', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F-4', 'description': 'Muffles sounds in an area.'},
            {'name': 'Improved Invisibility', 'category': 'illusion', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Makes target invisible to both normal and technological perception.'},
            {'name': 'Invisibility', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Makes target invisible to natural perception.'},
            {'name': 'Mask', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Changes the appearance of the target.'},
            {'name': 'Physical Mask', 'category': 'illusion', 'spell_type': 'physical', 'range_type': 'touch', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Changes appearance, affects cameras and sensors.'},
            {'name': 'Phantasm', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Creates a realistic illusion of any scene.'},
            {'name': 'Silence', 'category': 'illusion', 'spell_type': 'mana', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Creates a zone of complete silence.'},
            {'name': 'Stealth', 'category': 'illusion', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Muffles sounds made by the target.'},

            # Manipulation Spells
            {'name': 'Armor', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Creates a magical barrier that provides armor.'},
            {'name': 'Barrier', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Creates a physical barrier wall.'},
            {'name': 'Control Actions', 'category': 'manipulation', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Forces the target to perform a specific action.'},
            {'name': 'Control Thoughts', 'category': 'manipulation', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Controls the thoughts of the target.'},
            {'name': 'Fling', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'instant', 'drain': 'F-2', 'description': 'Telekinetically hurls an object at a target.'},
            {'name': 'Gravity', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Increases gravity in an area.'},
            {'name': 'Ignite', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'permanent', 'drain': 'F-1', 'description': 'Sets flammable objects on fire.'},
            {'name': 'Influence', 'category': 'manipulation', 'spell_type': 'mana', 'range_type': 'los', 'duration': 'permanent', 'drain': 'F-1', 'description': 'Implants a single suggestion in the target\'s mind.'},
            {'name': 'Levitate', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Allows target to fly.'},
            {'name': 'Light', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F-4', 'description': 'Creates a mobile light source.'},
            {'name': 'Magic Fingers', 'category': 'manipulation', 'spell_type': 'physical', 'range_type': 'los', 'duration': 'sustained', 'drain': 'F-2', 'description': 'Creates telekinetic force for fine manipulation.'},
            {'name': 'Mob Control', 'category': 'manipulation', 'spell_type': 'mana', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F-1', 'description': 'Controls the actions of a crowd.'},
            {'name': 'Mob Mind', 'category': 'manipulation', 'spell_type': 'mana', 'range_type': 'los_area', 'duration': 'sustained', 'drain': 'F', 'description': 'Controls the thoughts of a group.'},
        ]

        for spell_data in spells:
            Spell.objects.get_or_create(
                name=spell_data['name'],
                defaults={
                    'category': spell_data['category'],
                    'spell_type': spell_data['spell_type'],
                    'range_type': spell_data['range_type'],
                    'duration': spell_data['duration'],
                    'drain': spell_data['drain'],
                    'description': spell_data['description'],
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created {spell_data["category"]} spell: {spell_data["name"]}')

        # Create sample adept powers
        self.stdout.write('\nPopulating adept powers...')

        adept_powers = [
            {'name': 'Astral Perception', 'cost': 1.00, 'description': 'Allows the adept to perceive the astral plane while remaining in the physical world.'},
            {'name': 'Combat Sense', 'cost': 0.50, 'description': 'Each level adds +1 die to surprise and perception tests in combat. Maximum levels equal to Magic.'},
            {'name': 'Critical Strike', 'cost': 0.50, 'description': 'Each level adds +1 DV to unarmed combat attacks. Maximum levels equal to Magic.'},
            {'name': 'Danger Sense', 'cost': 0.25, 'description': 'Each level adds +1 die to surprise tests. Maximum levels equal to Magic.'},
            {'name': 'Enhanced Accuracy', 'cost': 0.25, 'description': 'Increases accuracy of a skill group by 1 per level.'},
            {'name': 'Enhanced Perception', 'cost': 0.50, 'description': 'Each level adds +1 die to Perception tests. Maximum levels equal to Magic.'},
            {'name': 'Improved Ability (Combat)', 'cost': 0.50, 'description': 'Each level adds +1 die to a specific combat skill. Maximum levels equal to half current skill rating.'},
            {'name': 'Improved Ability (Physical)', 'cost': 0.25, 'description': 'Each level adds +1 die to a specific physical skill. Maximum levels equal to half current skill rating.'},
            {'name': 'Improved Physical Attribute (AGI)', 'cost': 1.00, 'description': 'Each level adds +1 to Agility. Maximum levels equal to natural maximum for metatype.'},
            {'name': 'Improved Physical Attribute (BOD)', 'cost': 1.00, 'description': 'Each level adds +1 to Body. Maximum levels equal to natural maximum for metatype.'},
            {'name': 'Improved Physical Attribute (REA)', 'cost': 1.50, 'description': 'Each level adds +1 to Reaction. Maximum levels equal to natural maximum for metatype.'},
            {'name': 'Improved Physical Attribute (STR)', 'cost': 1.00, 'description': 'Each level adds +1 to Strength. Maximum levels equal to natural maximum for metatype.'},
            {'name': 'Improved Reflexes', 'cost': 1.50, 'description': 'Level 1: +1 Reaction, +1D6 Initiative. Level 2: +2 Reaction, +2D6. Level 3: +3 Reaction, +3D6. Maximum 3 levels.'},
            {'name': 'Improved Sense', 'cost': 0.25, 'description': 'Grants enhanced versions of natural senses (low-light, thermographic, etc.).'},
            {'name': 'Killing Hands', 'cost': 0.50, 'description': 'Unarmed attacks deal physical damage instead of stun. Can affect dual-natured targets.'},
            {'name': 'Kinesics', 'cost': 0.25, 'description': 'Each level adds +1 die to resist social reading and +1 to social defense. Maximum levels equal to Magic.'},
            {'name': 'Light Body', 'cost': 0.25, 'description': 'Each level reduces effective body weight by 25% for movement and falling damage.'},
            {'name': 'Missile Parry', 'cost': 0.25, 'description': 'Each level adds +1 die to defense against ranged attacks when aware.'},
            {'name': 'Mystic Armor', 'cost': 0.50, 'description': 'Each level adds +1 to armor. Maximum levels equal to Magic.'},
            {'name': 'Pain Resistance', 'cost': 0.50, 'description': 'Each level ignores 1 box of damage for wound modifiers. Maximum levels equal to Magic.'},
            {'name': 'Penetrating Strike', 'cost': 0.25, 'description': 'Each level gives unarmed attacks -1 AP. Maximum levels equal to Magic.'},
            {'name': 'Rapid Draw', 'cost': 0.50, 'description': 'Draw a weapon as a free action.'},
            {'name': 'Spell Resistance', 'cost': 0.50, 'description': 'Each level adds +1 die to resist spells. Maximum levels equal to Magic.'},
            {'name': 'Traceless Walk', 'cost': 1.00, 'description': 'Leave no physical trace of passage and cannot be tracked by scent.'},
            {'name': 'Wall Running', 'cost': 0.50, 'description': 'Run along vertical surfaces for a number of meters equal to running distance.'},
        ]

        for power_data in adept_powers:
            AdeptPower.objects.get_or_create(
                name=power_data['name'],
                defaults={
                    'cost': power_data['cost'],
                    'description': power_data['description'],
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created adept power: {power_data["name"]}')

        # Create sample complex forms
        self.stdout.write('\nPopulating complex forms...')

        complex_forms = [
            {'name': 'Cleaner', 'target': 'persona', 'duration': 'permanent', 'fading': 'L+1', 'description': 'Erases marks from a persona\'s matrix icon.'},
            {'name': 'Derezz', 'target': 'sprite', 'duration': 'instant', 'fading': 'L+1', 'description': 'Attacks a sprite, reducing its tasks.'},
            {'name': 'Diffusion', 'target': 'device', 'duration': 'sustained', 'fading': 'L+1', 'description': 'Reduces a device\'s attributes.'},
            {'name': 'Editor', 'target': 'file', 'duration': 'permanent', 'fading': 'L+2', 'description': 'Edit a file\'s contents in the Matrix.'},
            {'name': 'Infusion', 'target': 'device', 'duration': 'sustained', 'fading': 'L+1', 'description': 'Increases a device\'s attributes.'},
            {'name': 'Mirrored Persona', 'target': 'persona', 'duration': 'sustained', 'fading': 'L-1', 'description': 'Creates copies of your persona icon to confuse attackers.'},
            {'name': 'Pulse Storm', 'target': 'device', 'duration': 'instant', 'fading': 'L+3', 'description': 'Damages all devices in the area.'},
            {'name': 'Puppeteer', 'target': 'device', 'duration': 'sustained', 'fading': 'L+2', 'description': 'Control a device remotely.'},
            {'name': 'Resonance Channel', 'target': 'device', 'duration': 'sustained', 'fading': 'L+1', 'description': 'Creates a hidden communication channel.'},
            {'name': 'Resonance Spike', 'target': 'device', 'duration': 'instant', 'fading': 'L+2', 'description': 'Deals matrix damage to a device.'},
            {'name': 'Resonance Veil', 'target': 'persona', 'duration': 'sustained', 'fading': 'L-2', 'description': 'Changes your persona\'s matrix icon appearance.'},
            {'name': 'Static Bomb', 'target': 'device', 'duration': 'instant', 'fading': 'L+2', 'description': 'Creates noise in an area.'},
            {'name': 'Static Veil', 'target': 'persona', 'duration': 'sustained', 'fading': 'L-1', 'description': 'Reduces your noise signature.'},
            {'name': 'Stitches', 'target': 'sprite', 'duration': 'instant', 'fading': 'L+1', 'description': 'Repairs matrix damage on a sprite.'},
            {'name': 'Transcendent Grid', 'target': 'persona', 'duration': 'sustained', 'fading': 'L', 'description': 'Allows you to access any grid without penalty.'},
        ]

        for form_data in complex_forms:
            ComplexForm.objects.get_or_create(
                name=form_data['name'],
                defaults={
                    'target': form_data['target'],
                    'duration': form_data['duration'],
                    'fading': form_data['fading'],
                    'description': form_data['description'],
                    'is_default': True
                }
            )
            self.stdout.write(f'  Created complex form: {form_data["name"]}')

        self.stdout.write(self.style.SUCCESS('\nSample data populated successfully!'))
