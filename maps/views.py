from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import random
import json
import logging

from . import models
from .forms import MapForm, MapObjectForm, MapGenerationForm, MapGenerationPresetForm
from .generators import (
    generate_bsp_map,
    generate_cellular_automata_map,
    generate_random_walk_map,
    generate_maze_map
)
from .cover_system import calculate_cover_positions

logger = logging.getLogger(__name__)


@login_required
def map_list(request):
    """List all maps accessible to the user"""
    try:
        # Get user's own maps and maps shared with them
        user_maps = models.Map.objects.filter(owner=request.user)
        shared_maps = models.Map.objects.filter(shared_with=request.user)
        public_maps = models.Map.objects.filter(is_public=True).exclude(owner=request.user)

        context = {
            'user_maps': user_maps,
            'shared_maps': shared_maps,
            'public_maps': public_maps,
        }
        logger.info(f"User {request.user.username} accessed map list")
        return render(request, 'maps/list.html', context)
    except Exception as e:
        logger.error(f"Error in map_list for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading maps.')
        return redirect('home')


@login_required
def map_create(request):
    """Create a new map"""
    try:
        if request.method == 'POST':
            form = MapForm(request.POST, user=request.user)
            if form.is_valid():
                try:
                    map_obj = form.save(commit=False)
                    map_obj.owner = request.user
                    map_obj.save()
                    form.save_m2m()  # Save many-to-many relationships (shared_with)

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

                    logger.info(f"User {request.user.username} created map '{map_obj.name}' (ID: {map_obj.pk})")
                    messages.success(request, f'Map "{map_obj.name}" created successfully!')
                    return redirect('maps:detail', pk=map_obj.pk)
                except Exception as e:
                    logger.error(f"Error creating map for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to create map. Please try again.')
                    return redirect('maps:list')
        else:
            form = MapForm(user=request.user)

        context = {'form': form, 'action': 'Create'}
        return render(request, 'maps/form.html', context)
    except Exception as e:
        logger.error(f"Error in map_create for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('maps:list')


@login_required
def map_detail(request, pk):
    """View map details and builder interface"""
    try:
        map_obj = get_object_or_404(models.Map, pk=pk)

        # Check if user has permission to view this map
        if not (map_obj.owner == request.user or
                request.user in map_obj.shared_with.all() or
                map_obj.is_public):
            logger.warning(f"User {request.user.username} attempted to access unauthorized map {pk}")
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
        logger.info(f"User {request.user.username} viewed map '{map_obj.name}' (ID: {pk})")
        return render(request, 'maps/detail.html', context)
    except Exception as e:
        logger.error(f"Error in map_detail for user {request.user.username}, map {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading the map.')
        return redirect('maps:list')


@login_required
def map_edit(request, pk):
    """Edit a map's basic settings"""
    try:
        map_obj = get_object_or_404(models.Map, pk=pk, owner=request.user)

        if request.method == 'POST':
            form = MapForm(request.POST, instance=map_obj, user=request.user)
            if form.is_valid():
                try:
                    form.save()
                    logger.info(f"User {request.user.username} updated map '{map_obj.name}' (ID: {pk})")
                    messages.success(request, f'Map "{map_obj.name}" updated successfully!')
                    return redirect('maps:detail', pk=map_obj.pk)
                except Exception as e:
                    logger.error(f"Error saving map {pk} for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to update map. Please try again.')
        else:
            form = MapForm(instance=map_obj, user=request.user)

        context = {'form': form, 'map': map_obj, 'action': 'Edit'}
        return render(request, 'maps/form.html', context)
    except Exception as e:
        logger.error(f"Error in map_edit for user {request.user.username}, map {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('maps:list')


@login_required
def map_delete(request, pk):
    """Delete a map"""
    try:
        map_obj = get_object_or_404(models.Map, pk=pk, owner=request.user)

        if request.method == 'POST':
            try:
                map_name = map_obj.name
                map_obj.delete()
                logger.info(f"User {request.user.username} deleted map '{map_name}' (ID: {pk})")
                messages.success(request, f'Map "{map_name}" deleted successfully.')
                return redirect('maps:list')
            except Exception as e:
                logger.error(f"Error deleting map {pk} for user {request.user.username}: {str(e)}", exc_info=True)
                messages.error(request, 'Failed to delete map. Please try again.')
                return redirect('maps:detail', pk=pk)

        context = {'map': map_obj}
        return render(request, 'maps/delete_confirm.html', context)
    except Exception as e:
        logger.error(f"Error in map_delete for user {request.user.username}, map {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('maps:list')


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
        logger.error(f"Invalid data in map_tile_update for user {request.user.username}, map {pk}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in map_tile_update for user {request.user.username}, map {pk}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred'
        }, status=500)


@login_required
def map_generate_preview(request):
    """Generate a map preview without saving to database"""
    try:
        if request.method == 'POST':
            form = MapGenerationForm(request.user, request.POST)
            if form.is_valid():
                try:
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

                    logger.info(f"User {request.user.username} generated map preview: {algorithm} {width}x{height}")
                    return JsonResponse({
                        'success': True,
                        'width': width,
                        'height': height,
                        'tiles': tile_data,
                        'seed': seed
                    })
                except Exception as e:
                    logger.error(f"Error generating preview for user {request.user.username}: {str(e)}", exc_info=True)
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to generate map preview'
                    }, status=500)
            else:
                logger.warning(f"Invalid form data in map_generate_preview for user {request.user.username}: {form.errors}")
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)

        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in map_generate_preview for user {request.user.username}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred'
        }, status=500)


@login_required
def map_generate(request):
    """Generate a map dynamically using presets"""
    try:
        if request.method == 'POST':
            # Check if this is a final save after preview
            if request.POST.get('confirm_save') == 'true' and 'preview_data' in request.session:
                try:
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

                    logger.info(f"User {request.user.username} saved generated map '{map_obj.name}' (ID: {map_obj.pk})")
                    messages.success(request, f'Map "{map_obj.name}" generated successfully!')
                    return JsonResponse({'success': True, 'redirect_url': f'/maps/{map_obj.pk}/'})
                except Exception as e:
                    logger.error(f"Error saving generated map for user {request.user.username}: {str(e)}", exc_info=True)
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to save generated map'
                    }, status=500)

            # Regular form submission (legacy support or direct save without preview)
            form = MapGenerationForm(request.user, request.POST)
            if form.is_valid():
                try:
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
                    floor_tiles = generate_map_tiles(map_obj, algorithm=algorithm, params=params)

                    # Place cover objects if density > 0
                    cover_density = form.cleaned_data.get('cover_density', 0.0)
                    if cover_density and cover_density > 0 and floor_tiles:
                        cover_objects = calculate_cover_positions(
                            floor_tiles=floor_tiles,
                            width=map_obj.width,
                            height=map_obj.height,
                            density=cover_density,
                            map_type=map_obj.map_type
                        )

                        # Create cover objects in database
                        for cover_data in cover_objects:
                            models.MapObject.objects.create(
                                map=map_obj,
                                **cover_data
                            )

                        logger.info(f"Placed {len(cover_objects)} cover objects on map '{map_obj.name}'")

                    logger.info(f"User {request.user.username} generated map '{map_obj.name}' (ID: {map_obj.pk}) with {algorithm}")
                    messages.success(request, f'Map "{map_obj.name}" generated successfully!')
                    return redirect('maps:detail', pk=map_obj.pk)
                except Exception as e:
                    logger.error(f"Error generating map for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to generate map. Please try again.')
                    return redirect('maps:list')
        else:
            form = MapGenerationForm(request.user)

        # Get available presets for user
        user_presets = models.MapGenerationPreset.objects.filter(owner=request.user).order_by('name')
        public_presets = models.MapGenerationPreset.objects.filter(
            is_public=True
        ).exclude(owner=request.user).order_by('name')

        context = {
            'form': form,
            'user_presets': user_presets,
            'public_presets': public_presets,
        }
        return render(request, 'maps/generate.html', context)
    except Exception as e:
        logger.error(f"Unexpected error in map_generate for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An unexpected error occurred.')
        return redirect('maps:list')


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

    # Create tiles in database and collect floor tiles for cover placement
    floor_tiles = []
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

        # Collect walkable floor tiles for cover placement
        if terrain_info['walkable'] and base_terrain in ['floor', 'cave', 'tunnel']:
            floor_tiles.append((x, y, base_terrain))

    return floor_tiles


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


# Fog of War Views

@login_required
def toggle_fog_of_war(request, pk):
    """Toggle fog of war for a map (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    map_obj = get_object_or_404(models.Map, pk=pk)

    # Only owner can toggle fog of war
    if map_obj.owner != request.user:
        return JsonResponse({'success': False, 'error': 'Only the map owner can toggle fog of war'})

    map_obj.fog_of_war_enabled = not map_obj.fog_of_war_enabled
    map_obj.save()

    return JsonResponse({
        'success': True,
        'fog_of_war_enabled': map_obj.fog_of_war_enabled
    })


@login_required
def reveal_tile(request, pk):
    """Reveal a tile in fog of war (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    map_obj = get_object_or_404(models.Map, pk=pk)

    # Only owner can reveal tiles
    if map_obj.owner != request.user:
        return JsonResponse({'success': False, 'error': 'Only the map owner can reveal tiles'})

    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        radius = int(request.POST.get('radius', 1))  # Reveal radius

        revealed_tiles = map_obj.revealed_tiles if isinstance(map_obj.revealed_tiles, list) else []

        # Reveal tiles in radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tile_x = x + dx
                tile_y = y + dy

                # Check if within map bounds
                if 0 <= tile_x < map_obj.width and 0 <= tile_y < map_obj.height:
                    tile_coords = [tile_x, tile_y]
                    if tile_coords not in revealed_tiles:
                        revealed_tiles.append(tile_coords)

        map_obj.revealed_tiles = revealed_tiles
        map_obj.save()

        return JsonResponse({
            'success': True,
            'revealed_count': len(revealed_tiles)
        })

    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }, status=400)


@login_required
def hide_tile(request, pk):
    """Hide a tile in fog of war (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    map_obj = get_object_or_404(models.Map, pk=pk)

    # Only owner can hide tiles
    if map_obj.owner != request.user:
        return JsonResponse({'success': False, 'error': 'Only the map owner can hide tiles'})

    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        radius = int(request.POST.get('radius', 1))  # Hide radius

        revealed_tiles = map_obj.revealed_tiles if isinstance(map_obj.revealed_tiles, list) else []

        # Hide tiles in radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tile_x = x + dx
                tile_y = y + dy
                tile_coords = [tile_x, tile_y]

                if tile_coords in revealed_tiles:
                    revealed_tiles.remove(tile_coords)

        map_obj.revealed_tiles = revealed_tiles
        map_obj.save()

        return JsonResponse({
            'success': True,
            'revealed_count': len(revealed_tiles)
        })

    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }, status=400)


@login_required
def reset_fog_of_war(request, pk):
    """Reset all fog of war (hide all tiles) (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    map_obj = get_object_or_404(models.Map, pk=pk)

    # Only owner can reset fog of war
    if map_obj.owner != request.user:
        return JsonResponse({'success': False, 'error': 'Only the map owner can reset fog of war'})

    map_obj.revealed_tiles = []
    map_obj.save()

    return JsonResponse({
        'success': True,
        'revealed_count': 0
    })


# ===== Map Generation Preset Views =====

@login_required
def preset_list(request):
    """List all map generation presets (user's own + public)"""
    try:
        # Get user's own presets
        user_presets = models.MapGenerationPreset.objects.filter(owner=request.user).order_by('name')

        # Get public presets from other users
        public_presets = models.MapGenerationPreset.objects.filter(
            is_public=True
        ).exclude(owner=request.user).order_by('name')

        context = {
            'user_presets': user_presets,
            'public_presets': public_presets,
        }

        return render(request, 'maps/preset_list.html', context)
    except Exception as e:
        logger.error(f"Error listing presets for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading presets.')
        return redirect('maps:list')


@login_required
def preset_create(request):
    """Create a new map generation preset"""
    try:
        if request.method == 'POST':
            form = MapGenerationPresetForm(request.POST)
            if form.is_valid():
                preset = form.save(commit=False)
                preset.owner = request.user
                preset.save()
                logger.info(f"User {request.user.username} created preset '{preset.name}' (ID: {preset.pk})")
                messages.success(request, f'Preset "{preset.name}" created successfully!')
                return redirect('maps:preset_list')
        else:
            form = MapGenerationPresetForm()

        context = {
            'form': form,
            'action': 'Create',
        }

        return render(request, 'maps/preset_form.html', context)
    except Exception as e:
        logger.error(f"Error creating preset for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while creating the preset.')
        return redirect('maps:preset_list')


@login_required
def preset_edit(request, pk):
    """Edit an existing map generation preset"""
    try:
        preset = get_object_or_404(models.MapGenerationPreset, pk=pk, owner=request.user)

        if request.method == 'POST':
            form = MapGenerationPresetForm(request.POST, instance=preset)
            if form.is_valid():
                form.save()
                logger.info(f"User {request.user.username} updated preset '{preset.name}' (ID: {preset.pk})")
                messages.success(request, f'Preset "{preset.name}" updated successfully!')
                return redirect('maps:preset_list')
        else:
            form = MapGenerationPresetForm(instance=preset)

        context = {
            'form': form,
            'preset': preset,
            'action': 'Edit',
        }

        return render(request, 'maps/preset_form.html', context)
    except Exception as e:
        logger.error(f"Error editing preset {pk} for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while editing the preset.')
        return redirect('maps:preset_list')


@login_required
def preset_delete(request, pk):
    """Delete a map generation preset"""
    try:
        preset = get_object_or_404(models.MapGenerationPreset, pk=pk, owner=request.user)

        if request.method == 'POST':
            preset_name = preset.name
            preset.delete()
            logger.info(f"User {request.user.username} deleted preset '{preset_name}' (ID: {pk})")
            messages.success(request, f'Preset "{preset_name}" deleted successfully!')
            return redirect('maps:preset_list')

        context = {
            'preset': preset,
        }

        return render(request, 'maps/preset_delete_confirm.html', context)
    except Exception as e:
        logger.error(f"Error deleting preset {pk} for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while deleting the preset.')
        return redirect('maps:preset_list')


@login_required
def preset_load(request, pk):
    """Load a preset's parameters (AJAX endpoint)"""
    try:
        # Allow loading own presets or public presets
        preset = get_object_or_404(
            models.MapGenerationPreset,
            Q(owner=request.user) | Q(is_public=True),
            pk=pk
        )

        # Return preset data as JSON
        data = {
            'success': True,
            'preset': {
                'name': preset.name,
                'width': preset.width,
                'height': preset.height,
                'map_type': preset.map_type,
                'obstacle_density': preset.obstacle_density,
                'object_density': preset.object_density,
                'generation_algorithm': preset.generation_algorithm,
                'custom_parameters': preset.custom_parameters,
            }
        }

        logger.info(f"User {request.user.username} loaded preset '{preset.name}' (ID: {preset.pk})")
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error loading preset {pk} for user {request.user.username}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to load preset'
        }, status=500)
