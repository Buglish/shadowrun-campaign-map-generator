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
def map_generate(request):
    """Generate a map dynamically using presets"""
    if request.method == 'POST':
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

            # Generate tiles based on algorithm
            generate_map_tiles(map_obj, algorithm=algorithm)

            messages.success(request, f'Map "{map_obj.name}" generated successfully!')
            return redirect('maps:detail', pk=map_obj.pk)
    else:
        form = MapGenerationForm(request.user)

    context = {'form': form}
    return render(request, 'maps/generate.html', context)


def generate_map_tiles(map_obj, algorithm='random'):
    """
    Generate tiles for a map based on algorithm and map type.

    Args:
        map_obj: The Map model instance
        algorithm: Generation algorithm ('random', 'bsp', 'cellular_automata', 'random_walk', 'maze')
    """
    seed = map_obj.generation_seed

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
        tile_data = generate_bsp_map(map_obj.width, map_obj.height, seed)
    elif algorithm == 'cellular_automata':
        tile_data = generate_cellular_automata_map(map_obj.width, map_obj.height, seed)
    elif algorithm == 'random_walk':
        tile_data = generate_random_walk_map(map_obj.width, map_obj.height, seed)
    elif algorithm == 'maze':
        tile_data = generate_maze_map(map_obj.width, map_obj.height, seed)
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
