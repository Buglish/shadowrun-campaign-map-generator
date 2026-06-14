import heapq

# Movement cost per terrain type (in movement points, normal terrain = 1)
# None = impassable
TERRAIN_COSTS = {
    'street': 1,
    'sidewalk': 1,
    'floor': 1,
    'alley': 1,
    'parking': 1,
    'grass': 1,
    'desert': 1,
    'door': 1,
    'elevator': 1,
    'tunnel': 1,
    'sewer': 1,
    'cave': 1,
    'custom': 1,
    'forest': 2,
    'stairs': 2,
    'window': 2,
    'water': 4,
    'mountain': 3,
    'wall': None,
    'building': None,
    'void': None,
}

TERRAIN_COST_LABELS = {
    1: 'Normal',
    2: 'Difficult',
    3: 'Very Difficult',
    4: 'Extreme',
}


def astar(tiles_dict, start, end, width, height, allow_diagonal=True):
    """
    A* pathfinding with terrain cost calculation.

    tiles_dict: {(x, y): {'is_walkable': bool, 'terrain_type': str, 'movement_cost': int}}
    Returns: {'path': [(x, y), ...], 'total_cost': float, 'reachable': bool, 'terrain_breakdown': {...}}
    """
    if start == end:
        return {'path': [start], 'total_cost': 0.0, 'reachable': True, 'terrain_breakdown': {}}

    def heuristic(a, b):
        if allow_diagonal:
            return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if allow_diagonal:
        directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    open_heap = [(heuristic(start, end), 0.0, start)]
    g_score = {start: 0.0}
    came_from = {}

    while open_heap:
        _f, g, current = heapq.heappop(open_heap)

        if current == end:
            path = []
            node = current
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()

            # Build terrain breakdown for display
            breakdown = {}
            for pos in path[1:]:
                tile = tiles_dict.get(pos, {})
                terrain = tile.get('terrain_type', 'floor')
                breakdown[terrain] = breakdown.get(terrain, 0) + 1

            return {
                'path': path,
                'total_cost': round(g_score[end], 1),
                'reachable': True,
                'terrain_breakdown': breakdown,
            }

        if g > g_score.get(current, float('inf')):
            continue

        cx, cy = current
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            neighbor = (nx, ny)

            if not (0 <= nx < width and 0 <= ny < height):
                continue

            tile = tiles_dict.get(neighbor)
            if tile is None or not tile['is_walkable']:
                continue

            terrain = tile.get('terrain_type', 'floor')
            base_cost = TERRAIN_COSTS.get(terrain)
            if base_cost is None:
                continue

            # Respect GM-customized movement_cost if higher than terrain default
            stored_cost = tile.get('movement_cost', 1)
            actual_cost = max(base_cost, stored_cost)

            # Diagonal movement costs ~1.414× more
            if dx != 0 and dy != 0:
                actual_cost *= 1.414

            tentative_g = g_score[current] + actual_cost

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_new = tentative_g + heuristic(neighbor, end)
                heapq.heappush(open_heap, (f_new, tentative_g, neighbor))

    return {'path': [], 'total_cost': 0.0, 'reachable': False, 'terrain_breakdown': {}}
