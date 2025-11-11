from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import random
import json

from . import models
from .forms import MapForm, MapObjectForm, MapGenerationForm, MapGenerationPresetForm
from .generators import (
    generate_bsp_map,
    generate_cellular_automata_map,
    generate_random_walk_map,
    generate_maze_map
)


@login_required
def map_list(request):
    """List all maps accessible to the user"""
    # Get user's own maps and maps shared with them
    user_maps = models.Map.objects.filter(owner=request.user)
    shared_maps = models.Map.objects.filter(shared_with=request.user)
    public_maps = models.Map.objects.filter(is_public=True).exclude(owner=request.user)

    context = {
        'user_maps': user_maps,
        'shared_maps': shared_maps,
        'public_maps': public_maps,
    }
    return render(request, 'maps/list.html', context)


@login_required
def map_create(request):
    """Create a new map"""
    if request.method == 'POST':
        form = MapForm(request.POST)
        if form.is_valid():
            map_obj = form.save(commit=False)
            map_obj.owner = request.user
            map_obj.save()

            # Initialize the map with default floor tiles
            for y in range(map_obj.height):
                for x in range(map_obj.width):
                    models.MapTile.objects.create(
                        map=map_obj,
                        x=x,
                        y=y,
                        terrain_type='floor',
                        is_walkable=True,
                        is_transparent=True,
                        color='#E8E8E8'
                    )

            messages.success(request, f'Map "{map_obj.name}" created successfully!')
            return redirect('maps:detail', pk=map_obj.pk)
    else:
        form = MapForm()

    context = {'form': form, 'action': 'Create'}
    return render(request, 'maps/form.html', context)


@login_required
def map_detail(request, pk):
    """View map details and builder interface"""
    map_obj = get_object_or_404(models.Map, pk=pk)

    # Check if user has permission to view this map
    if not (map_obj.owner == request.user or
            request.user in map_obj.shared_with.all() or
            map_obj.is_public):
        messages.error(request, 'You do not have permission to view this map.')
        return redirect('maps:list')

    # Get all tiles and objects for this map
    tiles = map_obj.tiles.all()
    objects = map_obj.map_objects.all()

    # Check if user can edit (only owner)
    can_edit = map_obj.owner == request.user

    context = {
        'map': map_obj,
        'tiles': tiles,
        'objects': objects,
        'can_edit': can_edit,
    }
    return render(request, 'maps/detail.html', context)


@login_required
def map_edit(request, pk):
    """Edit a map's basic settings"""
    map_obj = get_object_or_404(models.Map, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = MapForm(request.POST, instance=map_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Map "{map_obj.name}" updated successfully!')
            return redirect('maps:detail', pk=map_obj.pk)
    else:
        form = MapForm(instance=map_obj)

    context = {'form': form, 'map': map_obj, 'action': 'Edit'}
    return render(request, 'maps/form.html', context)


@login_required
def map_delete(request, pk):
    """Delete a map"""
    map_obj = get_object_or_404(models.Map, pk=pk, owner=request.user)

    if request.method == 'POST':
        map_name = map_obj.name
        map_obj.delete()
        messages.success(request, f'Map "{map_name}" deleted successfully.')
        return redirect('maps:list')

    context = {'map': map_obj}
    return render(request, 'maps/delete_confirm.html', context)


@login_required
def map_tile_update(request, pk):
    """Update a single tile via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

    # Get the map and verify ownership
    map_obj = get_object_or_404(models.Map, pk=pk, owner=request.user)

    try:
        # Get tile coordinates and new terrain type from request
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        terrain_type = request.POST.get('terrain_type')
        color = request.POST.get('color')

        # Validate coordinates
        if x < 0 or x >= map_obj.width or y < 0 or y >= map_obj.height:
            return JsonResponse({
                'success': False,
                'error': 'Invalid coordinates'
            }, status=400)

        # Get or create the tile
        tile = models.MapTile.objects.filter(map=map_obj, x=x, y=y).first()

        if tile:
            # Update existing tile
            tile.terrain_type = terrain_type
            tile.color = color

            # Set walkable and transparent based on terrain type
            if terrain_type in ['wall', 'building', 'water', 'mountain']:
                tile.is_walkable = False
            else:
                tile.is_walkable = True

            if terrain_type in ['wall', 'building', 'door', 'forest']:
                tile.is_transparent = False
            else:
                tile.is_transparent = True

            tile.save()

            return JsonResponse({
                'success': True,
                'tile': {
                    'x': tile.x,
                    'y': tile.y,
                    'terrain_type': tile.terrain_type,
                    'color': tile.color,
                    'is_walkable': tile.is_walkable,
                    'is_transparent': tile.is_transparent
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Tile not found'
            }, status=404)

    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }, status=400)


@login_required
def map_generate_preview(request):
    """Generate a map preview without saving to database"""
    if request.method == 'POST':
        form = MapGenerationForm(request.user, request.POST)
        if form.is_valid():
            # Extract form data
            width = form.cleaned_data['width']
            height = form.cleaned_data['height']
            map_type = form.cleaned_data['map_type']
            seed = form.cleaned_data.get('seed') or str(random.randint(1000, 9999))
            algorithm = form.cleaned_data.get('algorithm', 'random')

            # Collect algorithm-specific parameters
            params = {}
            if algorithm == 'bsp':
                if form.cleaned_data.get('min_room_size') is not None:
                    params['min_room_size'] = form.cleaned_data['min_room_size']
                if form.cleaned_data.get('max_room_size') is not None:
                    params['max_room_size'] = form.cleaned_data['max_room_size']
                if form.cleaned_data.get('corridor_width') is not None:
                    params['corridor_width'] = form.cleaned_data['corridor_width']
            elif algorithm == 'cellular_automata':
                if form.cleaned_data.get('iterations') is not None:
                    params['iterations'] = form.cleaned_data['iterations']
                if form.cleaned_data.get('wall_probability') is not None:
                    params['wall_probability'] = form.cleaned_data['wall_probability']
            elif algorithm == 'random_walk':
                if form.cleaned_data.get('steps') is not None:
                    params['steps'] = form.cleaned_data['steps']
                if form.cleaned_data.get('tunnel_width_probability') is not None:
                    params['tunnel_width_probability'] = form.cleaned_data['tunnel_width_probability']
            elif algorithm == 'maze':
                if form.cleaned_data.get('path_width') is not None:
                    params['path_width'] = form.cleaned_data['path_width']

            # Generate tile data without creating database objects
            tile_data = generate_preview_tiles(width, height, map_type, seed, algorithm, params)

            # Store data in session for later saving
            request.session['preview_data'] = {
                'name': form.cleaned_data['name'],
                'width': width,
                'height': height,
                'map_type': map_type,
                'seed': seed,
                'algorithm': algorithm,
                'params': params,
                'tile_data': tile_data
            }

            return JsonResponse({
                'success': True,
                'width': width,
                'height': height,
                'tiles': tile_data,
                'seed': seed
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def map_generate(request):
    """Generate a map dynamically using presets"""
    if request.method == 'POST':
        # Check if this is a final save after preview
        if request.POST.get('confirm_save') == 'true' and 'preview_data' in request.session:
            preview_data = request.session['preview_data']

            # Create the map
            map_obj = models.Map.objects.create(
                name=preview_data['name'],
                owner=request.user,
                width=preview_data['width'],
                height=preview_data['height'],
                map_type=preview_data['map_type'],
                is_generated=True,
                generation_seed=preview_data['seed']
            )

            # Create tiles from preview data
            for tile_info in preview_data['tile_data']:
                models.MapTile.objects.create(
                    map=map_obj,
                    x=tile_info['x'],
                    y=tile_info['y'],
                    terrain_type=tile_info['terrain_type'],
                    is_walkable=tile_info['is_walkable'],
                    is_transparent=tile_info['is_transparent'],
                    color=tile_info['color']
                )

            # Clear preview data from session
            del request.session['preview_data']

            messages.success(request, f'Map "{map_obj.name}" generated successfully!')
            return JsonResponse({'success': True, 'redirect_url': f'/maps/{map_obj.pk}/'})

        # Regular form submission (legacy support or direct save without preview)
        form = MapGenerationForm(request.user, request.POST)
        if form.is_valid():
            # Create the map
            map_obj = models.Map.objects.create(
                name=form.cleaned_data['name'],
                owner=request.user,
                width=form.cleaned_data['width'],
                height=form.cleaned_data['height'],
                map_type=form.cleaned_data['map_type'],
                is_generated=True,
                generation_seed=form.cleaned_data.get('seed') or str(random.randint(1000, 9999))
            )

            # Get algorithm from form
            algorithm = form.cleaned_data.get('algorithm', 'random')

            # Collect algorithm-specific parameters
            params = {}
            if algorithm == 'bsp':
                if form.cleaned_data.get('min_room_size') is not None:
                    params['min_room_size'] = form.cleaned_data['min_room_size']
                if form.cleaned_data.get('max_room_size') is not None:
                    params['max_room_size'] = form.cleaned_data['max_room_size']
                if form.cleaned_data.get('corridor_width') is not None:
                    params['corridor_width'] = form.cleaned_data['corridor_width']
            elif algorithm == 'cellular_automata':
                if form.cleaned_data.get('iterations') is not None:
                    params['iterations'] = form.cleaned_data['iterations']
                if form.cleaned_data.get('wall_probability') is not None:
                    params['wall_probability'] = form.cleaned_data['wall_probability']
            elif algorithm == 'random_walk':
                if form.cleaned_data.get('steps') is not None:
                    params['steps'] = form.cleaned_data['steps']
                if form.cleaned_data.get('tunnel_width_probability') is not None:
                    params['tunnel_width_probability'] = form.cleaned_data['tunnel_width_probability']
            elif algorithm == 'maze':
                if form.cleaned_data.get('path_width') is not None:
                    params['path_width'] = form.cleaned_data['path_width']

            # Generate tiles based on algorithm
            generate_map_tiles(map_obj, algorithm=algorithm, params=params)

            messages.success(request, f'Map "{map_obj.name}" generated successfully!')
            return redirect('maps:detail', pk=map_obj.pk)
    else:
        form = MapGenerationForm(request.user)

    context = {'form': form}
    return render(request, 'maps/generate.html', context)


def generate_preview_tiles(width, height, map_type, seed, algorithm='random', params=None):
    """
    Generate tile data for preview without saving to database.

    Args:
        width: Map width
        height: Map height
        map_type: Type of map (urban, wilderness, etc.)
        seed: Generation seed
        algorithm: Generation algorithm ('random', 'bsp', 'cellular_automata', 'random_walk', 'maze')
        params: Dictionary of algorithm-specific parameters

    Returns:
        List of tile dictionaries with x, y, terrain_type, is_walkable, is_transparent, color
    """
    if params is None:
        params = {}

    # Define terrain settings based on map type
    terrain_config = {
        'urban': {
            'floor': {'type': 'street', 'color': '#555555', 'walkable': True, 'transparent': True},
            'wall': {'type': 'building', 'color': '#8B4513', 'walkable': False, 'transparent': False},
            'door': {'type': 'door', 'color': '#CD853F', 'walkable': True, 'transparent': False},
            'secondary': {'type': 'sidewalk', 'color': '#AAAAAA', 'walkable': True, 'transparent': True},
        },
        'wilderness': {
            'floor': {'type': 'grass', 'color': '#7CFC00', 'walkable': True, 'transparent': True},
            'wall': {'type': 'water', 'color': '#4169E1', 'walkable': False, 'transparent': True},
            'cave': {'type': 'forest', 'color': '#228B22', 'walkable': True, 'transparent': False},
            'secondary': {'type': 'mountain', 'color': '#8B7355', 'walkable': False, 'transparent': True},
        },
        'corporate': {
            'floor': {'type': 'floor', 'color': '#E8E8E8', 'walkable': True, 'transparent': True},
            'wall': {'type': 'wall', 'color': '#696969', 'walkable': False, 'transparent': False},
            'door': {'type': 'door', 'color': '#8B4513', 'walkable': True, 'transparent': False},
            'tunnel': {'type': 'stairs', 'color': '#A9A9A9', 'walkable': True, 'transparent': True},
        },
        'underground': {
            'floor': {'type': 'tunnel', 'color': '#8B7355', 'walkable': True, 'transparent': True},
            'wall': {'type': 'wall', 'color': '#2F4F4F', 'walkable': False, 'transparent': False},
            'cave': {'type': 'cave', 'color': '#654321', 'walkable': True, 'transparent': True},
            'tunnel': {'type': 'sewer', 'color': '#556B2F', 'walkable': True, 'transparent': True},
        },
        'mixed': {
            'floor': {'type': 'floor', 'color': '#E8E8E8', 'walkable': True, 'transparent': True},
            'wall': {'type': 'wall', 'color': '#696969', 'walkable': False, 'transparent': False},
            'door': {'type': 'door', 'color': '#8B4513', 'walkable': True, 'transparent': False},
            'cave': {'type': 'grass', 'color': '#7CFC00', 'walkable': True, 'transparent': True},
        }
    }

    config = terrain_config.get(map_type, terrain_config['corporate'])

    # Generate tile data using selected algorithm
    if algorithm == 'bsp':
        raw_tile_data = generate_bsp_map(width, height, seed, params)
    elif algorithm == 'cellular_automata':
        raw_tile_data = generate_cellular_automata_map(width, height, seed, params)
    elif algorithm == 'random_walk':
        raw_tile_data = generate_random_walk_map(width, height, seed, params)
    elif algorithm == 'maze':
        raw_tile_data = generate_maze_map(width, height, seed, params)
    else:
        # Random/default algorithm
        raw_tile_data = generate_random_tiles(width, height, seed, config)

    # Convert to tile dictionaries
    tiles = []
    for x, y, base_terrain in raw_tile_data:
        # Map algorithm terrain types to map-type specific terrain
        terrain_info = config.get(base_terrain, config['floor'])

        tiles.append({
            'x': x,
            'y': y,
            'terrain_type': terrain_info['type'],
            'is_walkable': terrain_info['walkable'],
            'is_transparent': terrain_info['transparent'],
            'color': terrain_info['color']
        })

    return tiles


def generate_map_tiles(map_obj, algorithm='random', params=None):
    """
    Generate tiles for a map based on algorithm and map type.

    Args:
        map_obj: The Map model instance
        algorithm: Generation algorithm ('random', 'bsp', 'cellular_automata', 'random_walk', 'maze')
        params: Dictionary of algorithm-specific parameters
    """
    seed = map_obj.generation_seed
    if params is None:
        params = {}

    # Define terrain settings based on map type
    terrain_config = {
        'urban': {
            'floor': {'type': 'street', 'color': '#555555', 'walkable': True, 'transparent': True},
            'wall': {'type': 'building', 'color': '#8B4513', 'walkable': False, 'transparent': False},
            'door': {'type': 'door', 'color': '#CD853F', 'walkable': True, 'transparent': False},
            'secondary': {'type': 'sidewalk', 'color': '#AAAAAA', 'walkable': True, 'transparent': True},
        },
        'wilderness': {
            'floor': {'type': 'grass', 'color': '#7CFC00', 'walkable': True, 'transparent': True},
            'wall': {'type': 'water', 'color': '#4169E1', 'walkable': False, 'transparent': True},
            'cave': {'type': 'forest', 'color': '#228B22', 'walkable': True, 'transparent': False},
            'secondary': {'type': 'mountain', 'color': '#8B7355', 'walkable': False, 'transparent': True},
        },
        'corporate': {
            'floor': {'type': 'floor', 'color': '#E8E8E8', 'walkable': True, 'transparent': True},
            'wall': {'type': 'wall', 'color': '#696969', 'walkable': False, 'transparent': False},
            'door': {'type': 'door', 'color': '#8B4513', 'walkable': True, 'transparent': False},
            'tunnel': {'type': 'stairs', 'color': '#A9A9A9', 'walkable': True, 'transparent': True},
        },
        'underground': {
            'floor': {'type': 'tunnel', 'color': '#8B7355', 'walkable': True, 'transparent': True},
            'wall': {'type': 'wall', 'color': '#2F4F4F', 'walkable': False, 'transparent': False},
            'cave': {'type': 'cave', 'color': '#654321', 'walkable': True, 'transparent': True},
            'tunnel': {'type': 'sewer', 'color': '#556B2F', 'walkable': True, 'transparent': True},
        },
        'mixed': {
            'floor': {'type': 'floor', 'color': '#E8E8E8', 'walkable': True, 'transparent': True},
            'wall': {'type': 'wall', 'color': '#696969', 'walkable': False, 'transparent': False},
            'door': {'type': 'door', 'color': '#8B4513', 'walkable': True, 'transparent': False},
            'cave': {'type': 'grass', 'color': '#7CFC00', 'walkable': True, 'transparent': True},
        }
    }

    config = terrain_config.get(map_obj.map_type, terrain_config['corporate'])

    # Generate tile data using selected algorithm
    if algorithm == 'bsp':
        tile_data = generate_bsp_map(map_obj.width, map_obj.height, seed, params)
    elif algorithm == 'cellular_automata':
        tile_data = generate_cellular_automata_map(map_obj.width, map_obj.height, seed, params)
    elif algorithm == 'random_walk':
        tile_data = generate_random_walk_map(map_obj.width, map_obj.height, seed, params)
    elif algorithm == 'maze':
        tile_data = generate_maze_map(map_obj.width, map_obj.height, seed, params)
    else:
        # Random/default algorithm
        tile_data = generate_random_tiles(map_obj.width, map_obj.height, seed, config)

    # Create tiles in database
    for x, y, base_terrain in tile_data:
        # Map algorithm terrain types to map-type specific terrain
        terrain_info = config.get(base_terrain, config['floor'])

        models.MapTile.objects.create(
            map=map_obj,
            x=x,
            y=y,
            terrain_type=terrain_info['type'],
            is_walkable=terrain_info['walkable'],
            is_transparent=terrain_info['transparent'],
            color=terrain_info['color']
        )


def generate_random_tiles(width, height, seed, config):
    """Generate random tiles (original algorithm)"""
    if seed:
        random.seed(hash(seed))

    tiles = []
    for y in range(height):
        for x in range(width):
            rand_val = random.random()

            if rand_val < 0.15:  # 15% obstacles
                terrain = 'wall'
            elif rand_val < 0.35:  # 20% secondary terrain
                terrain = 'secondary' if 'secondary' in config else 'floor'
            else:  # 65% primary terrain
                terrain = 'floor'

            tiles.append((x, y, terrain))

    return tiles
