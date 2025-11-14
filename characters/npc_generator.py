"""
NPC Generator for Shadowrun
Procedurally generates NPCs with randomized attributes based on archetype and threat level
"""
import random
from decimal import Decimal


# NPC Threat Levels - determines attribute ranges and skill levels
THREAT_LEVELS = {
    'low': {
        'name': 'Low Threat (Grunt)',
        'attribute_range': (1, 3),
        'skill_range': (0, 3),
        'resource_multiplier': 1,
        'karma_base': 0,
        'description': 'Street thugs, low-level gangers, untrained civilians'
    },
    'medium': {
        'name': 'Medium Threat (Professional)',
        'attribute_range': (2, 5),
        'skill_range': (2, 5),
        'resource_multiplier': 3,
        'karma_base': 25,
        'description': 'Trained security, experienced runners, competent professionals'
    },
    'high': {
        'name': 'High Threat (Elite)',
        'attribute_range': (4, 7),
        'skill_range': (4, 7),
        'resource_multiplier': 10,
        'karma_base': 100,
        'description': 'Corporate elite guards, veteran shadowrunners, magical adepts'
    },
    'extreme': {
        'name': 'Extreme Threat (Legendary)',
        'attribute_range': (6, 10),
        'skill_range': (6, 10),
        'resource_multiplier': 50,
        'karma_base': 300,
        'description': 'Dragon human forms, immortal elves, legendary runners'
    }
}


# Archetype templates - define attribute priorities and typical skills
ARCHETYPE_TEMPLATES = {
    'street_samurai': {
        'name': 'Street Samurai',
        'primary_attributes': ['body', 'agility', 'reaction'],
        'secondary_attributes': ['strength', 'willpower'],
        'tertiary_attributes': ['charisma', 'intuition', 'logic'],
        'typical_skills': ['Automatics', 'Pistols', 'Blades', 'Unarmed Combat', 'Athletics', 'Sneaking'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['weapon', 'armor', 'cyberware']
    },
    'combat_mage': {
        'name': 'Combat Mage',
        'primary_attributes': ['magic', 'willpower', 'logic'],
        'secondary_attributes': ['intuition', 'charisma'],
        'tertiary_attributes': ['body', 'agility', 'reaction', 'strength'],
        'typical_skills': ['Spellcasting', 'Counterspelling', 'Assensing', 'Perception'],
        'magic_range': (3, 6),
        'resonance': 0,
        'edge_range': (1, 3),
        'typical_gear': ['magical', 'misc']
    },
    'decker': {
        'name': 'Decker',
        'primary_attributes': ['logic', 'intuition', 'willpower'],
        'secondary_attributes': ['charisma', 'agility'],
        'tertiary_attributes': ['body', 'strength', 'reaction'],
        'typical_skills': ['Hacking', 'Computer', 'Cybercombat', 'Electronic Warfare', 'Hardware'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['electronics', 'misc']
    },
    'face': {
        'name': 'Face',
        'primary_attributes': ['charisma', 'willpower', 'intuition'],
        'secondary_attributes': ['logic', 'agility'],
        'tertiary_attributes': ['body', 'strength', 'reaction'],
        'typical_skills': ['Negotiation', 'Con', 'Etiquette', 'Leadership', 'Performance'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (3, 5),
        'typical_gear': ['misc', 'electronics']
    },
    'adept': {
        'name': 'Adept',
        'primary_attributes': ['magic', 'agility', 'reaction'],
        'secondary_attributes': ['strength', 'body', 'willpower'],
        'tertiary_attributes': ['charisma', 'intuition', 'logic'],
        'typical_skills': ['Unarmed Combat', 'Blades', 'Pistols', 'Athletics', 'Sneaking'],
        'magic_range': (3, 6),
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['weapon', 'misc']
    },
    'rigger': {
        'name': 'Rigger',
        'primary_attributes': ['logic', 'intuition', 'reaction'],
        'secondary_attributes': ['agility', 'willpower'],
        'tertiary_attributes': ['body', 'strength', 'charisma'],
        'typical_skills': ['Gunnery', 'Pilot Ground Craft', 'Pilot Aircraft', 'Electronic Warfare'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['vehicle', 'electronics', 'cyberware']
    },
    'street_shaman': {
        'name': 'Street Shaman',
        'primary_attributes': ['magic', 'charisma', 'willpower'],
        'secondary_attributes': ['intuition', 'logic'],
        'tertiary_attributes': ['body', 'agility', 'reaction', 'strength'],
        'typical_skills': ['Spellcasting', 'Summoning', 'Binding', 'Assensing', 'Perception'],
        'magic_range': (3, 6),
        'resonance': 0,
        'edge_range': (1, 3),
        'typical_gear': ['magical', 'misc']
    },
    'technomancer': {
        'name': 'Technomancer',
        'primary_attributes': ['resonance', 'logic', 'willpower'],
        'secondary_attributes': ['intuition', 'charisma'],
        'tertiary_attributes': ['body', 'agility', 'reaction', 'strength'],
        'typical_skills': ['Compiling', 'Registering', 'Computer', 'Hacking', 'Software'],
        'magic': 0,
        'resonance_range': (3, 6),
        'edge_range': (2, 4),
        'typical_gear': ['misc']
    },
    'weapon_specialist': {
        'name': 'Weapon Specialist',
        'primary_attributes': ['agility', 'strength', 'body'],
        'secondary_attributes': ['reaction', 'willpower'],
        'tertiary_attributes': ['charisma', 'intuition', 'logic'],
        'typical_skills': ['Longarms', 'Heavy Weapons', 'Automatics', 'Throwing Weapons'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 3),
        'typical_gear': ['weapon', 'armor']
    },
    'covert_ops': {
        'name': 'Covert Ops Specialist',
        'primary_attributes': ['agility', 'intuition', 'reaction'],
        'secondary_attributes': ['logic', 'willpower'],
        'tertiary_attributes': ['body', 'strength', 'charisma'],
        'typical_skills': ['Sneaking', 'Palming', 'Locksmith', 'Disguise', 'Pistols'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['weapon', 'misc']
    },

    # ===== CIVILIAN & VENDOR ARCHETYPES =====
    'gun_vendor': {
        'name': 'Gun Vendor',
        'primary_attributes': ['logic', 'charisma', 'intuition'],
        'secondary_attributes': ['willpower', 'agility'],
        'tertiary_attributes': ['body', 'strength', 'reaction'],
        'typical_skills': ['Negotiation', 'Armorer', 'Firearms Knowledge', 'Etiquette'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (1, 3),
        'typical_gear': ['weapon', 'misc']
    },
    'clothing_vendor': {
        'name': 'Clothing Vendor',
        'primary_attributes': ['charisma', 'intuition', 'logic'],
        'secondary_attributes': ['willpower', 'agility'],
        'tertiary_attributes': ['body', 'strength', 'reaction'],
        'typical_skills': ['Negotiation', 'Etiquette', 'Artisan', 'Fashion Knowledge'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (1, 3),
        'typical_gear': ['misc']
    },
    'melee_vendor': {
        'name': 'Melee Vendor',
        'primary_attributes': ['strength', 'charisma', 'body'],
        'secondary_attributes': ['intuition', 'willpower'],
        'tertiary_attributes': ['logic', 'agility', 'reaction'],
        'typical_skills': ['Negotiation', 'Blades', 'Clubs', 'Artisan'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (1, 3),
        'typical_gear': ['weapon', 'misc']
    },
    'drug_dealer': {
        'name': 'Drug Dealer',
        'primary_attributes': ['charisma', 'intuition', 'willpower'],
        'secondary_attributes': ['agility', 'reaction'],
        'tertiary_attributes': ['body', 'strength', 'logic'],
        'typical_skills': ['Negotiation', 'Con', 'Chemistry', 'Perception', 'Sneaking'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['misc']
    },
    'pawn_shop_vendor': {
        'name': 'Pawn Shop Vendor',
        'primary_attributes': ['logic', 'charisma', 'intuition'],
        'secondary_attributes': ['willpower', 'body'],
        'tertiary_attributes': ['strength', 'agility', 'reaction'],
        'typical_skills': ['Negotiation', 'Appraisal', 'Perception', 'Con'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['misc']
    },
    'food_vendor': {
        'name': 'Food Vendor',
        'primary_attributes': ['body', 'charisma', 'intuition'],
        'secondary_attributes': ['willpower', 'logic'],
        'tertiary_attributes': ['strength', 'agility', 'reaction'],
        'typical_skills': ['Negotiation', 'Artisan', 'Etiquette', 'Perception'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (1, 2),
        'typical_gear': ['misc']
    },
    'street_performer': {
        'name': 'Street Performer',
        'primary_attributes': ['charisma', 'agility', 'intuition'],
        'secondary_attributes': ['willpower', 'reaction'],
        'tertiary_attributes': ['body', 'strength', 'logic'],
        'typical_skills': ['Performance', 'Con', 'Gymnastics', 'Etiquette'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['misc']
    },
    'companion': {
        'name': 'Companion',
        'primary_attributes': ['charisma', 'intuition', 'willpower'],
        'secondary_attributes': ['agility', 'logic'],
        'tertiary_attributes': ['body', 'strength', 'reaction'],
        'typical_skills': ['Con', 'Etiquette', 'Performance', 'Perception'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 3),
        'typical_gear': ['misc']
    },
    'street_doc': {
        'name': 'Street Doc (Ripper Doc)',
        'primary_attributes': ['logic', 'intuition', 'willpower'],
        'secondary_attributes': ['agility', 'charisma'],
        'tertiary_attributes': ['body', 'strength', 'reaction'],
        'typical_skills': ['Medicine', 'Cybertechnology', 'Chemistry', 'Biotechnology'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['cyberware', 'misc']
    },
    'security_guard': {
        'name': 'Security Guard',
        'primary_attributes': ['body', 'reaction', 'willpower'],
        'secondary_attributes': ['strength', 'intuition'],
        'tertiary_attributes': ['charisma', 'logic', 'agility'],
        'typical_skills': ['Perception', 'Pistols', 'Unarmed Combat', 'Intimidation'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (1, 3),
        'typical_gear': ['weapon', 'armor', 'electronics']
    },
    'thug': {
        'name': 'Thug',
        'primary_attributes': ['strength', 'body', 'willpower'],
        'secondary_attributes': ['agility', 'reaction'],
        'tertiary_attributes': ['charisma', 'intuition', 'logic'],
        'typical_skills': ['Unarmed Combat', 'Intimidation', 'Clubs', 'Running'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (1, 2),
        'typical_gear': ['weapon', 'misc']
    },
    'thief': {
        'name': 'Thief',
        'primary_attributes': ['agility', 'intuition', 'reaction'],
        'secondary_attributes': ['logic', 'willpower'],
        'tertiary_attributes': ['body', 'strength', 'charisma'],
        'typical_skills': ['Sneaking', 'Locksmith', 'Palming', 'Perception', 'Running'],
        'magic': 0,
        'resonance': 0,
        'edge_range': (2, 4),
        'typical_gear': ['misc']
    }
}


# Random name generators
FIRST_NAMES = [
    'Jack', 'Sarah', 'Marcus', 'Elena', 'Kai', 'Raven', 'Drake', 'Luna', 'Victor', 'Jade',
    'Axel', 'Nova', 'Zeke', 'Aria', 'Rex', 'Scarlett', 'Blade', 'Phoenix', 'Viper', 'Echo',
    'Crow', 'Storm', 'Wolf', 'Ash', 'Nyx', 'Razor', 'Ghost', 'Shadow', 'Frost', 'Blaze'
]

LAST_NAMES = [
    'Reyes', 'Nakamura', 'O\'Brien', 'Volkov', 'Chen', 'Blackwood', 'Steel', 'Kane', 'Frost',
    'Santiago', 'Tanaka', 'Murphy', 'Petrov', 'Wong', 'Mercer', 'Stone', 'Ryder', 'Cross',
    'Kovacs', 'Sato', 'Lynch', 'Sokolov', 'Liu', 'Graves', 'Blade', 'Hunter', 'Knight', 'Fox'
]

SHADOWRUN_ALIASES = [
    'Razor', 'Ghost', 'Shadow', 'Blade', 'Phoenix', 'Viper', 'Echo', 'Crow', 'Storm', 'Wolf',
    'Ash', 'Nyx', 'Frost', 'Blaze', 'Spike', 'Crash', 'Glitch', 'Byte', 'Cipher', 'Wraith',
    'Spark', 'Nitro', 'Flash', 'Steel', 'Chrome', 'Pulse', 'Vector', 'Matrix', 'Zero', 'Hex'
]


def generate_npc_name(use_alias=True):
    """Generate a random NPC name"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    if use_alias and random.random() > 0.4:
        alias = random.choice(SHADOWRUN_ALIASES)
        return f'"{alias}" {first} {last}'

    return f'{first} {last}'


def generate_attributes(archetype_key, threat_level):
    """Generate random attributes based on archetype and threat level"""
    template = ARCHETYPE_TEMPLATES[archetype_key]
    threat = THREAT_LEVELS[threat_level]
    min_attr, max_attr = threat['attribute_range']

    attributes = {}

    # Primary attributes get higher values
    for attr in template['primary_attributes']:
        if attr == 'magic':
            # Handle magic separately
            continue
        attributes[attr] = random.randint(max(min_attr + 2, 1), min(max_attr + 2, 10))

    # Secondary attributes get medium values
    for attr in template['secondary_attributes']:
        attributes[attr] = random.randint(max(min_attr + 1, 1), min(max_attr + 1, 10))

    # Tertiary attributes get base values
    for attr in template['tertiary_attributes']:
        attributes[attr] = random.randint(min_attr, min(max_attr, 10))

    # Ensure all attributes are set
    all_attrs = ['body', 'agility', 'reaction', 'strength', 'charisma', 'intuition', 'logic', 'willpower']
    for attr in all_attrs:
        if attr not in attributes:
            attributes[attr] = random.randint(min_attr, min(max_attr, 10))

    # Edge
    edge_min, edge_max = template['edge_range']
    attributes['edge'] = random.randint(edge_min, edge_max)

    # Magic
    if 'magic_range' in template:
        mag_min, mag_max = template['magic_range']
        attributes['magic'] = random.randint(mag_min, mag_max)
    else:
        attributes['magic'] = template.get('magic', 0)

    # Resonance
    if 'resonance_range' in template:
        res_min, res_max = template['resonance_range']
        attributes['resonance'] = random.randint(res_min, res_max)
    else:
        attributes['resonance'] = template.get('resonance', 0)

    # Essence (reduced if cyberware is typical)
    if 'cyberware' in template.get('typical_gear', []):
        # More cyberware = less essence
        essence_loss = round(random.uniform(0.5, 3.0), 2)
        attributes['essence'] = Decimal(str(max(1.0, 6.0 - essence_loss)))
    else:
        attributes['essence'] = Decimal('6.00')

    return attributes


def generate_physical_description(race):
    """Generate random physical description based on race"""
    ages = {
        'human': (18, 65),
        'dwarf': (20, 80),
        'elf': (20, 150),
        'ork': (15, 40),
        'troll': (15, 35)
    }

    age = random.randint(*ages.get(race, (20, 50)))

    sexes = ['Male', 'Female', 'Non-binary']
    sex = random.choice(sexes)

    # Height and weight vary by race
    heights = {
        'human': ('5\'6"', '6\'2"'),
        'dwarf': ('3\'10"', '4\'6"'),
        'elf': ('5\'8"', '6\'6"'),
        'ork': ('6\'0"', '6\'8"'),
        'troll': ('7\'0"', '8\'6"')
    }

    weights = {
        'human': ('140 lbs', '200 lbs'),
        'dwarf': ('100 lbs', '140 lbs'),
        'elf': ('120 lbs', '170 lbs'),
        'ork': ('200 lbs', '300 lbs'),
        'troll': ('300 lbs', '450 lbs')
    }

    height = random.choice(heights.get(race, heights['human']))
    weight = random.choice(weights.get(race, weights['human']))

    eye_colors = ['Brown', 'Blue', 'Green', 'Hazel', 'Gray', 'Amber', 'Cyber-red', 'Chrome']
    hair_colors = ['Black', 'Brown', 'Blonde', 'Red', 'Gray', 'White', 'Dyed blue', 'Dyed green', 'Bald']
    skin_tones = ['Pale', 'Fair', 'Olive', 'Tan', 'Brown', 'Dark', 'Ebony']

    eyes = random.choice(eye_colors)
    hair = random.choice(hair_colors)
    skin = random.choice(skin_tones)

    features_list = [
        'Cybernetic eyes', 'Facial scars', 'Tattoos', 'Piercings', 'Mohawk',
        'Gang colors', 'Corporate ID tattoo', 'Ritual scarification', 'Chrome limb',
        'Datajack ports visible', 'Missing finger', 'Burn scars', 'Street fashion'
    ]

    num_features = random.randint(1, 3)
    features = ', '.join(random.sample(features_list, num_features))

    return {
        'age': age,
        'sex': sex,
        'height': height,
        'weight': weight,
        'eyes': eyes,
        'hair': hair,
        'skin': skin,
        'distinguishing_features': features
    }


def generate_background(archetype_key, race):
    """Generate a random background story"""
    archetype = ARCHETYPE_TEMPLATES[archetype_key]['name']

    # Different backgrounds for civilian/vendor NPCs vs runners
    civilian_archetypes = ['gun_vendor', 'clothing_vendor', 'melee_vendor', 'drug_dealer',
                          'pawn_shop_vendor', 'food_vendor', 'street_performer',
                          'companion', 'street_doc', 'security_guard', 'thug', 'thief']

    if archetype_key in civilian_archetypes:
        # Civilian/vendor origins
        origins = [
            f"Has been running a business in the sprawl for years. Known as a reliable {archetype}.",
            f"Started from nothing and built a reputation as a {archetype} in the neighborhood.",
            f"Inherited the family business. Works as a {archetype} in the same spot for generations.",
            f"Former corporate wage slave who opened up shop as a {archetype} after getting laid off.",
            f"Self-made {archetype} who knows everyone in the district.",
            f"Operates as a {archetype} in the shadows of the megaplexes.",
            f"Tribal {race} who brought their skills to the city, now works as a {archetype}."
        ]

        motivations = [
            "Just trying to make an honest living.",
            "Pays protection money to local gangs to stay in business.",
            "Has connections with both sides of the law.",
            "Serves the community and asks few questions.",
            "Owes a debt to someone powerful.",
            "Knows everyone's secrets but keeps them close.",
            "Saves every nuyen to get out of the sprawl someday."
        ]
    else:
        # Runner/shadowrunner origins
        origins = [
            f"Born in the sprawl, raised by the streets. Became a {archetype} to survive.",
            f"Former corporate employee who went freelance after a bad deal. Now works as a {archetype}.",
            f"Military veteran turned shadowrunner. Specializes in {archetype} work.",
            f"Self-taught {archetype} from the Barrens. Learned the hard way.",
            f"Trained by a mentor in the shadows. Carries on the tradition as a {archetype}.",
            f"Escaped from a corporate research facility. Uses abilities as a {archetype}.",
            f"Tribal {race} who came to the city seeking fortune as a {archetype}."
        ]

        motivations = [
            "Motivated by nuyen and survival.",
            "Seeking revenge against a megacorp.",
            "Protecting their community in the Barrens.",
            "Building reputation in the shadows.",
            "Paying off a massive debt.",
            "Searching for a lost family member.",
            "Just trying to make it to tomorrow."
        ]

    return f"{random.choice(origins)} {random.choice(motivations)}"


def generate_npc_data(archetype_key, threat_level, race=None, use_alias=True):
    """
    Generate complete NPC data

    Args:
        archetype_key: Key from ARCHETYPE_TEMPLATES
        threat_level: Key from THREAT_LEVELS
        race: Optional race override (random if None)
        use_alias: Whether to use shadowrun aliases in names

    Returns:
        Dictionary of NPC data ready for Character model
    """
    if archetype_key not in ARCHETYPE_TEMPLATES:
        raise ValueError(f"Invalid archetype: {archetype_key}")

    if threat_level not in THREAT_LEVELS:
        raise ValueError(f"Invalid threat level: {threat_level}")

    # Select race
    races = ['human', 'dwarf', 'elf', 'ork', 'troll']
    if race is None or race not in races:
        race = random.choice(races)

    # Generate name
    name = generate_npc_name(use_alias)

    # Generate attributes
    attributes = generate_attributes(archetype_key, threat_level)

    # Generate physical description
    physical = generate_physical_description(race)

    # Generate background
    background = generate_background(archetype_key, race)

    # Resources and karma based on threat level
    threat = THREAT_LEVELS[threat_level]
    base_resources = random.randint(500, 5000) * threat['resource_multiplier']
    karma_total = threat['karma_base'] + random.randint(0, 50)

    # Lifestyle based on threat level
    lifestyle_map = {
        'low': random.choice(['street', 'squatter', 'low']),
        'medium': random.choice(['low', 'medium']),
        'high': random.choice(['medium', 'high']),
        'extreme': random.choice(['high', 'luxury'])
    }

    lifestyle = lifestyle_map[threat_level]

    # Compile NPC data
    npc_data = {
        'name': name,
        'race': race,
        'archetype': archetype_key,
        'role': _map_archetype_to_role(archetype_key),

        # Attributes
        'body': attributes['body'],
        'agility': attributes['agility'],
        'reaction': attributes['reaction'],
        'strength': attributes['strength'],
        'charisma': attributes['charisma'],
        'intuition': attributes['intuition'],
        'logic': attributes['logic'],
        'willpower': attributes['willpower'],
        'edge': attributes['edge'],
        'essence': attributes['essence'],
        'magic': attributes['magic'],
        'resonance': attributes['resonance'],

        # Resources
        'starting_resources': base_resources,
        'current_resources': base_resources,
        'karma_total': karma_total,
        'karma_spent': 0,
        'karma_available': karma_total,

        # Physical description
        'age': physical['age'],
        'sex': physical['sex'],
        'height': physical['height'],
        'weight': physical['weight'],
        'eyes': physical['eyes'],
        'hair': physical['hair'],
        'skin': physical['skin'],
        'distinguishing_features': physical['distinguishing_features'],

        # Background
        'background': background,
        'lifestyle': lifestyle,

        # Priorities (generic for NPCs)
        'metatype_priority': 'C',
        'attributes_priority': 'B',
        'magic_priority': 'D' if attributes['magic'] == 0 else 'A',
        'skills_priority': 'B',
        'resources_priority': 'C',

        # Status
        'is_complete': True,
        'creation_step': 8,

        # Condition
        'physical_damage': 0,
        'stun_damage': 0,
        'street_cred': random.randint(0, threat['karma_base'] // 20),
        'notoriety': random.randint(0, threat['karma_base'] // 30),
        'public_awareness': random.randint(0, threat['karma_base'] // 40),
    }

    return npc_data


def _map_archetype_to_role(archetype_key):
    """Map archetype to role choices"""
    role_mapping = {
        'street_samurai': 'street_samurai',
        'combat_mage': 'arcane_specialist',
        'decker': 'technology_specialist',
        'face': 'face',
        'adept': 'street_samurai',
        'rigger': 'technology_specialist',
        'street_shaman': 'arcane_specialist',
        'technomancer': 'technology_specialist',
        'weapon_specialist': 'street_samurai',
        'covert_ops': 'street_samurai'
    }
    return role_mapping.get(archetype_key, 'street_samurai')


def get_archetype_choices():
    """Get list of archetype choices for forms"""
    return [(key, template['name']) for key, template in ARCHETYPE_TEMPLATES.items()]


def get_threat_level_choices():
    """Get list of threat level choices for forms"""
    return [(key, data['name']) for key, data in THREAT_LEVELS.items()]
