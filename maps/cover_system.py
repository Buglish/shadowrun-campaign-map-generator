"""
Cover system for procedural map generation.
Defines cover templates and placement logic for different map types.
"""
import random
from typing import List, Tuple, Dict

# Cover levels and their properties
COVER_LEVELS = {
    'light': {
        'name': 'Light Cover',
        'defense_bonus': 2,
        'icon': '🛡',  # Empty shield representation
        'blocks_movement': False,
        'blocks_vision': False,
    },
    'medium': {
        'name': 'Medium Cover',
        'defense_bonus': 4,
        'icon': '🛡️',  # Half-filled shield representation
        'blocks_movement': False,
        'blocks_vision': False,
    },
    'heavy': {
        'name': 'Heavy Cover',
        'defense_bonus': 6,
        'icon': '🛡',  # Fully-filled shield representation
        'blocks_movement': True,
        'blocks_vision': True,
    },
}

# Cover object templates organized by map type
COVER_TEMPLATES = {
    'urban': [
        # Light cover objects
        {'name': 'Trash Can', 'cover_level': 'light', 'color': '#808080'},
        {'name': 'Street Sign', 'cover_level': 'light', 'color': '#FFD700'},
        {'name': 'Mailbox', 'cover_level': 'light', 'color': '#4169E1'},
        {'name': 'Fire Hydrant', 'cover_level': 'light', 'color': '#DC143C'},

        # Medium cover objects
        {'name': 'News Stand', 'cover_level': 'medium', 'color': '#8B4513'},
        {'name': 'Parked Motorcycle', 'cover_level': 'medium', 'color': '#2F4F4F'},
        {'name': 'Street Vendor Cart', 'cover_level': 'medium', 'color': '#CD853F'},
        {'name': 'Dumpster', 'cover_level': 'medium', 'color': '#556B2F'},

        # Heavy cover objects
        {'name': 'Parked Car', 'cover_level': 'heavy', 'color': '#000080'},
        {'name': 'Concrete Barrier', 'cover_level': 'heavy', 'color': '#696969'},
        {'name': 'Large Dumpster', 'cover_level': 'heavy', 'color': '#2F4F4F'},
    ],

    'corporate': [
        # Light cover objects
        {'name': 'Office Chair', 'cover_level': 'light', 'color': '#4682B4'},
        {'name': 'Potted Plant', 'cover_level': 'light', 'color': '#228B22'},
        {'name': 'Water Cooler', 'cover_level': 'light', 'color': '#87CEEB'},
        {'name': 'Filing Cabinet', 'cover_level': 'light', 'color': '#708090'},

        # Medium cover objects
        {'name': 'Desk', 'cover_level': 'medium', 'color': '#8B4513'},
        {'name': 'Server Rack', 'cover_level': 'medium', 'color': '#2F4F4F'},
        {'name': 'Conference Table', 'cover_level': 'medium', 'color': '#A0522D'},
        {'name': 'Vending Machine', 'cover_level': 'medium', 'color': '#CD5C5C'},

        # Heavy cover objects
        {'name': 'Large Server Array', 'cover_level': 'heavy', 'color': '#1C1C1C'},
        {'name': 'Security Desk', 'cover_level': 'heavy', 'color': '#2F4F4F'},
        {'name': 'Metal Cabinet Bank', 'cover_level': 'heavy', 'color': '#696969'},
    ],

    'wilderness': [
        # Light cover objects
        {'name': 'Bush', 'cover_level': 'light', 'color': '#228B22'},
        {'name': 'Small Rock', 'cover_level': 'light', 'color': '#808080'},
        {'name': 'Fallen Branch', 'cover_level': 'light', 'color': '#8B4513'},
        {'name': 'Tall Grass', 'cover_level': 'light', 'color': '#9ACD32'},

        # Medium cover objects
        {'name': 'Large Boulder', 'cover_level': 'medium', 'color': '#696969'},
        {'name': 'Tree Stump', 'cover_level': 'medium', 'color': '#8B4513'},
        {'name': 'Dense Shrub', 'cover_level': 'medium', 'color': '#556B2F'},
        {'name': 'Rock Formation', 'cover_level': 'medium', 'color': '#A9A9A9'},

        # Heavy cover objects
        {'name': 'Large Tree', 'cover_level': 'heavy', 'color': '#2F4F2F'},
        {'name': 'Rock Outcrop', 'cover_level': 'heavy', 'color': '#696969'},
        {'name': 'Fallen Log', 'cover_level': 'heavy', 'color': '#654321'},
    ],

    'underground': [
        # Light cover objects
        {'name': 'Pipe', 'cover_level': 'light', 'color': '#708090'},
        {'name': 'Rubble Pile', 'cover_level': 'light', 'color': '#696969'},
        {'name': 'Debris', 'cover_level': 'light', 'color': '#8B7355'},
        {'name': 'Support Beam', 'cover_level': 'light', 'color': '#CD853F'},

        # Medium cover objects
        {'name': 'Large Pipe Junction', 'cover_level': 'medium', 'color': '#2F4F4F'},
        {'name': 'Concrete Block', 'cover_level': 'medium', 'color': '#696969'},
        {'name': 'Metal Crate', 'cover_level': 'medium', 'color': '#778899'},
        {'name': 'Broken Machinery', 'cover_level': 'medium', 'color': '#8B7355'},

        # Heavy cover objects
        {'name': 'Collapsed Wall', 'cover_level': 'heavy', 'color': '#696969'},
        {'name': 'Large Equipment', 'cover_level': 'heavy', 'color': '#2F4F4F'},
        {'name': 'Structural Column', 'cover_level': 'heavy', 'color': '#808080'},
    ],

    'mixed': [
        # Mix of all types - will randomly select from other categories
    ],
}


def get_cover_template(map_type: str) -> Dict:
    """
    Get a random cover template appropriate for the map type.

    Args:
        map_type: Type of map ('urban', 'corporate', 'wilderness', 'underground', 'mixed')

    Returns:
        Dictionary with cover object properties
    """
    # For mixed maps, randomly select from all categories
    if map_type == 'mixed':
        all_templates = []
        for templates in COVER_TEMPLATES.values():
            if templates:  # Skip empty mixed category
                all_templates.extend(templates)
        if not all_templates:
            map_type = 'urban'  # Fallback
        else:
            return random.choice(all_templates).copy()

    templates = COVER_TEMPLATES.get(map_type, COVER_TEMPLATES['urban'])
    if not templates:
        templates = COVER_TEMPLATES['urban']

    return random.choice(templates).copy()


def calculate_cover_positions(
    floor_tiles: List[Tuple[int, int, str]],
    width: int,
    height: int,
    density: float = 0.1,
    map_type: str = 'urban'
) -> List[Dict]:
    """
    Calculate positions and properties for cover objects.

    Args:
        floor_tiles: List of (x, y, terrain_type) tuples representing walkable floor
        width: Map width
        height: Map height
        density: Cover density (0.0 to 1.0), percentage of floor tiles to have cover
        map_type: Type of map for context-aware cover selection

    Returns:
        List of dictionaries with cover object data ready for MapObject creation
    """
    if density <= 0 or not floor_tiles:
        return []

    # Calculate number of cover objects to place
    num_cover = int(len(floor_tiles) * density)
    num_cover = max(1, num_cover)  # At least one cover object

    # Randomly select floor tile positions for cover
    available_positions = [
(tile[0], tile[1]) for tile in floor_tiles
        if tile[2] == 'floor'  # Only place on floor tiles
    ]

    if not available_positions:
        return []

    # Don't exceed available positions
    num_cover = min(num_cover, len(available_positions))

    # Randomly select positions
    selected_positions = random.sample(available_positions, num_cover)

    # Create cover objects
    cover_objects = []
    for x, y in selected_positions:
        template = get_cover_template(map_type)
        cover_level = template['cover_level']
        cover_props = COVER_LEVELS[cover_level]

        cover_obj = {
            'x': x,
            'y': y,
            'name': template['name'],
            'description': f"{cover_props['name']} providing +{cover_props['defense_bonus']} defense",
            'object_type': 'cover',
            'icon': cover_props['icon'],
            'color': template['color'],
            'blocks_movement': cover_props['blocks_movement'],
            'blocks_vision': cover_props['blocks_vision'],
            'stats': {
                'cover_level': cover_level,
                'defense_bonus': cover_props['defense_bonus'],
            },
        }
        cover_objects.append(cover_obj)

    return cover_objects


def get_cover_display_info(cover_level: str) -> Dict:
    """
    Get display information for a cover level.

    Args:
        cover_level: 'light', 'medium', or 'heavy'

    Returns:
        Dictionary with display properties
    """
    return COVER_LEVELS.get(cover_level, COVER_LEVELS['light'])
