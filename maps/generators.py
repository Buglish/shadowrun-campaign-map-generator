"""
Advanced map generation algorithms for procedural map creation.
Includes BSP (Binary Space Partitioning), Cellular Automata, and other algorithms.
"""
import random
from typing import List, Tuple, Dict


class Room:
    """Represents a room in BSP algorithm"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2


class BSPNode:
    """Node for Binary Space Partitioning tree"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left = None
        self.right = None
        self.room = None

    def split(self, min_room_size: int = 5) -> bool:
        """Split the node into two children"""
        # If already split, don't split again
        if self.left or self.right:
            return False

        # Decide split direction based on width/height ratio
        split_horizontally = random.choice([True, False])
        if self.width > self.height and self.width / self.height >= 1.25:
            split_horizontally = False
        elif self.height > self.width and self.height / self.width >= 1.25:
            split_horizontally = True

        # Determine the maximum size
        if split_horizontally:
            max_size = self.height - min_room_size
        else:
            max_size = self.width - min_room_size

        # Area too small to split
        if max_size <= min_room_size:
            return False

        # Split position
        split_pos = random.randint(min_room_size, max_size)

        # Create child nodes
        if split_horizontally:
            self.left = BSPNode(self.x, self.y, self.width, split_pos)
            self.right = BSPNode(self.x, self.y + split_pos, self.width, self.height - split_pos)
        else:
            self.left = BSPNode(self.x, self.y, split_pos, self.height)
            self.right = BSPNode(self.x + split_pos, self.y, self.width - split_pos, self.height)

        return True

    def create_rooms(self, min_room_size: int = 5) -> List[Room]:
        """Create rooms in leaf nodes"""
        if self.left or self.right:
            # This is not a leaf, create rooms in children
            rooms = []
            if self.left:
                rooms.extend(self.left.create_rooms(min_room_size))
            if self.right:
                rooms.extend(self.right.create_rooms(min_room_size))
            return rooms
        else:
            # This is a leaf, create a room
            # Ensure we have enough space for a room
            max_width = max(min_room_size, self.width - 2)
            max_height = max(min_room_size, self.height - 2)

            room_width = random.randint(min_room_size, max_width) if max_width > min_room_size else min_room_size
            room_height = random.randint(min_room_size, max_height) if max_height > min_room_size else min_room_size

            # Make sure room fits in the node
            room_width = min(room_width, self.width - 2)
            room_height = min(room_height, self.height - 2)

            # Position room within node
            x_offset = random.randint(0, max(0, self.width - room_width - 1))
            y_offset = random.randint(0, max(0, self.height - room_height - 1))
            room_x = self.x + x_offset
            room_y = self.y + y_offset

            self.room = Room(room_x, room_y, room_width, room_height)
            return [self.room]


def generate_bsp_map(width: int, height: int, seed: str = None) -> List[Tuple[int, int, str]]:
    """
    Generate a map using Binary Space Partitioning algorithm.
    Returns a list of (x, y, terrain_type) tuples.
    """
    if seed:
        random.seed(hash(seed))

    # Initialize all tiles as walls
    tiles = {}
    for y in range(height):
        for x in range(width):
            tiles[(x, y)] = 'wall'

    # Create BSP tree
    root = BSPNode(0, 0, width, height)

    # Split recursively
    nodes = [root]
    while nodes:
        node = nodes.pop(0)
        if node.split(min_room_size=5):
            if node.left:
                nodes.append(node.left)
            if node.right:
                nodes.append(node.right)

    # Create rooms
    rooms = root.create_rooms(min_room_size=5)

    # Fill rooms with floor tiles
    for room in rooms:
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < width and 0 <= y < height:
                    tiles[(x, y)] = 'floor'

    # Create corridors between rooms
    for i in range(len(rooms) - 1):
        room1 = rooms[i]
        room2 = rooms[i + 1]

        # Create L-shaped corridor
        if random.choice([True, False]):
            # Horizontal then vertical
            for x in range(min(room1.center_x, room2.center_x), max(room1.center_x, room2.center_x) + 1):
                if 0 <= x < width and 0 <= room1.center_y < height:
                    tiles[(x, room1.center_y)] = 'floor'
            for y in range(min(room1.center_y, room2.center_y), max(room1.center_y, room2.center_y) + 1):
                if 0 <= room2.center_x < width and 0 <= y < height:
                    tiles[(room2.center_x, y)] = 'floor'
        else:
            # Vertical then horizontal
            for y in range(min(room1.center_y, room2.center_y), max(room1.center_y, room2.center_y) + 1):
                if 0 <= room1.center_x < width and 0 <= y < height:
                    tiles[(room1.center_x, y)] = 'floor'
            for x in range(min(room1.center_x, room2.center_x), max(room1.center_x, room2.center_x) + 1):
                if 0 <= x < width and 0 <= room2.center_y < height:
                    tiles[(x, room2.center_y)] = 'floor'

    # Add doors at room entrances (randomly)
    for room in rooms:
        # Add doors at random edges
        if random.random() < 0.3:
            door_x = random.randint(room.x, room.x + room.width - 1)
            if 0 <= door_x < width and room.y > 0:
                if tiles[(door_x, room.y - 1)] == 'floor':
                    tiles[(door_x, room.y)] = 'door'

    # Convert to list format
    result = []
    for (x, y), terrain in tiles.items():
        result.append((x, y, terrain))

    return result


def generate_cellular_automata_map(width: int, height: int, seed: str = None,
                                   iterations: int = 5, wall_probability: float = 0.45) -> List[Tuple[int, int, str]]:
    """
    Generate a cave-like map using Cellular Automata algorithm.
    Returns a list of (x, y, terrain_type) tuples.
    """
    if seed:
        random.seed(hash(seed))

    # Initialize random map
    tiles = {}
    for y in range(height):
        for x in range(width):
            # Edges are always walls
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                tiles[(x, y)] = 'wall'
            else:
                tiles[(x, y)] = 'wall' if random.random() < wall_probability else 'cave'

    # Apply cellular automata rules
    for _ in range(iterations):
        new_tiles = tiles.copy()
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                wall_count = count_walls_around(tiles, x, y, width, height)

                # Cellular automata rules (4-5 rule)
                if wall_count > 4:
                    new_tiles[(x, y)] = 'wall'
                elif wall_count < 4:
                    new_tiles[(x, y)] = 'cave'
                # If exactly 4, keep current state

        tiles = new_tiles

    # Smooth pass - remove single isolated tiles
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            wall_count = count_walls_around(tiles, x, y, width, height)
            if tiles[(x, y)] == 'wall' and wall_count < 3:
                tiles[(x, y)] = 'cave'
            elif tiles[(x, y)] == 'cave' and wall_count > 6:
                tiles[(x, y)] = 'wall'

    # Convert to list format
    result = []
    for (x, y), terrain in tiles.items():
        result.append((x, y, terrain))

    return result


def count_walls_around(tiles: Dict, x: int, y: int, width: int, height: int, radius: int = 1) -> int:
    """Count wall tiles in a radius around a position"""
    count = 0
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if tiles.get((nx, ny)) == 'wall':
                    count += 1
            else:
                # Count edges as walls
                count += 1
    return count


def generate_random_walk_map(width: int, height: int, seed: str = None,
                             steps: int = None) -> List[Tuple[int, int, str]]:
    """
    Generate a map using random walk algorithm (creates winding paths).
    Returns a list of (x, y, terrain_type) tuples.
    """
    if seed:
        random.seed(hash(seed))

    if steps is None:
        steps = (width * height) // 2

    # Initialize all tiles as walls
    tiles = {}
    for y in range(height):
        for x in range(width):
            tiles[(x, y)] = 'wall'

    # Start from center
    current_x = width // 2
    current_y = height // 2
    tiles[(current_x, current_y)] = 'tunnel'

    # Random walk
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up, right, down, left
    for _ in range(steps):
        dx, dy = random.choice(directions)
        new_x = current_x + dx
        new_y = current_y + dy

        # Check bounds
        if 1 <= new_x < width - 1 and 1 <= new_y < height - 1:
            current_x = new_x
            current_y = new_y
            tiles[(current_x, current_y)] = 'tunnel'

            # Sometimes create wider paths
            if random.random() < 0.3:
                for dx2, dy2 in directions:
                    adj_x = current_x + dx2
                    adj_y = current_y + dy2
                    if 1 <= adj_x < width - 1 and 1 <= adj_y < height - 1:
                        tiles[(adj_x, adj_y)] = 'tunnel'

    # Convert to list format
    result = []
    for (x, y), terrain in tiles.items():
        result.append((x, y, terrain))

    return result


def generate_maze_map(width: int, height: int, seed: str = None) -> List[Tuple[int, int, str]]:
    """
    Generate a maze using recursive backtracking.
    Returns a list of (x, y, terrain_type) tuples.
    """
    if seed:
        random.seed(hash(seed))

    # Initialize all tiles as walls
    tiles = {}
    for y in range(height):
        for x in range(width):
            tiles[(x, y)] = 'wall'

    # Create maze using recursive backtracking
    # Start from (1, 1) and ensure odd dimensions for proper maze
    start_x, start_y = 1, 1
    stack = [(start_x, start_y)]
    visited = {(start_x, start_y)}
    tiles[(start_x, start_y)] = 'floor'

    directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # up, right, down, left (step by 2)

    while stack:
        current_x, current_y = stack[-1]

        # Get unvisited neighbors
        neighbors = []
        for dx, dy in directions:
            nx, ny = current_x + dx, current_y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and (nx, ny) not in visited:
                neighbors.append((nx, ny, dx, dy))

        if neighbors:
            # Choose random unvisited neighbor
            nx, ny, dx, dy = random.choice(neighbors)

            # Carve path to neighbor
            tiles[(current_x + dx // 2, current_y + dy // 2)] = 'floor'
            tiles[(nx, ny)] = 'floor'

            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            # Backtrack
            stack.pop()

    # Convert to list format
    result = []
    for (x, y), terrain in tiles.items():
        result.append((x, y, terrain))

    return result
