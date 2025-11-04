from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Character, Quality, CharacterQuality, Gear, CharacterGear
from .forms import (
    CharacterBasicInfoForm, CharacterRoleHistoryForm, CharacterPrioritiesForm,
    CharacterQualitySelectionForm, CharacterAttributesForm, CharacterKarmaForm,
    CharacterGearSelectionForm, CharacterFinishingForm
)


@login_required
def character_list(request):
    """List all characters for the current user"""
    characters = Character.objects.filter(user=request.user)
    context = {'characters': characters}
    return render(request, 'characters/list.html', context)


@login_required
def character_create(request):
    """Start character creation wizard"""
    # Clear any existing session data
    request.session['character_creation'] = {}
    request.session['character_id'] = None
    return redirect('characters:create_step1')


@login_required
def character_create_step1(request):
    """Step 1: Basic Info - Name, Race, Archetype"""
    character_id = request.session.get('character_id')
    character = None
    if character_id:
        character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterBasicInfoForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.user = request.user
            character.creation_step = 1
            character.save()
            request.session['character_id'] = character.id
            messages.success(request, 'Basic information saved!')
            return redirect('characters:create_step2')
    else:
        form = CharacterBasicInfoForm(instance=character)

    context = {'form': form, 'step': 1, 'step_name': 'Basic Information'}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step2(request):
    """Step 2: Role and History"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterRoleHistoryForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 2
            character.save()
            messages.success(request, 'Role and history saved!')
            return redirect('characters:create_step3')
    else:
        form = CharacterRoleHistoryForm(instance=character)

    context = {'form': form, 'step': 2, 'step_name': 'Role & History', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step3(request):
    """Step 3: Priorities"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterPrioritiesForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 3
            character.save()
            messages.success(request, 'Priorities set!')
            return redirect('characters:create_step4')
    else:
        form = CharacterPrioritiesForm(instance=character)

    context = {'form': form, 'step': 3, 'step_name': 'Priorities', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step4(request):
    """Step 4: Qualities Selection"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterQualitySelectionForm(request.POST)
        if form.is_valid():
            # Clear existing qualities
            CharacterQuality.objects.filter(character=character).delete()

            # Add selected positive qualities
            for quality in form.cleaned_data['positive_qualities']:
                CharacterQuality.objects.create(character=character, quality=quality)

            # Add selected negative qualities
            for quality in form.cleaned_data['negative_qualities']:
                CharacterQuality.objects.create(character=character, quality=quality)

            character.creation_step = 4
            character.save()
            messages.success(request, 'Qualities selected!')
            return redirect('characters:create_step5')
    else:
        # Pre-populate with existing selections
        existing_qualities = character.qualities.all()
        positive_ids = [cq.quality.id for cq in existing_qualities if cq.quality.quality_type == 'positive']
        negative_ids = [cq.quality.id for cq in existing_qualities if cq.quality.quality_type == 'negative']

        form = CharacterQualitySelectionForm(initial={
            'positive_qualities': positive_ids,
            'negative_qualities': negative_ids,
        })

    context = {'form': form, 'step': 4, 'step_name': 'Qualities', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step5(request):
    """Step 5: Attributes"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterAttributesForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 5
            character.save()
            messages.success(request, 'Attributes allocated!')
            return redirect('characters:create_step6')
    else:
        form = CharacterAttributesForm(instance=character)

    context = {'form': form, 'step': 5, 'step_name': 'Attributes', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step6(request):
    """Step 6: Karma Customization"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterKarmaForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 6
            character.save()
            messages.success(request, 'Karma customized!')
            return redirect('characters:create_step7')
    else:
        form = CharacterKarmaForm(instance=character)

    context = {'form': form, 'step': 6, 'step_name': 'Karma', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step7(request):
    """Step 7: Gear Selection"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterGearSelectionForm(request.POST)
        if form.is_valid():
            # Clear existing gear
            CharacterGear.objects.filter(character=character).delete()

            # Add selected gear
            for gear_item in form.cleaned_data['gear_items']:
                CharacterGear.objects.create(
                    character=character,
                    gear=gear_item,
                    quantity=1
                )

            character.creation_step = 7
            character.save()
            messages.success(request, 'Gear selected!')
            return redirect('characters:create_step8')
    else:
        # Pre-populate with existing gear
        existing_gear = character.equipment.all()
        gear_ids = [cg.gear.id for cg in existing_gear]
        form = CharacterGearSelectionForm(initial={'gear_items': gear_ids})

    context = {'form': form, 'step': 7, 'step_name': 'Gear', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step8(request):
    """Step 8: Finishing Touches"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterFinishingForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 8
            character.is_complete = True
            character.save()
            messages.success(request, f'Character {character.name} created successfully!')

            # Clear session
            request.session.pop('character_id', None)
            request.session.pop('character_creation', None)

            return redirect('characters:detail', pk=character.id)
    else:
        form = CharacterFinishingForm(instance=character)

    context = {'form': form, 'step': 8, 'step_name': 'Finishing Touches', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_detail(request, pk):
    """View character details"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    qualities = character.qualities.select_related('quality').all()
    equipment = character.equipment.select_related('gear').all()

    context = {
        'character': character,
        'qualities': qualities,
        'equipment': equipment,
    }
    return render(request, 'characters/detail.html', context)


@login_required
def character_edit(request, pk):
    """Edit a character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    # Set up wizard for editing
    request.session['character_id'] = character.id
    return redirect('characters:create_step1')


@login_required
def character_delete(request, pk):
    """Delete a character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        character_name = character.name
        character.delete()
        messages.success(request, f'Character {character_name} deleted successfully.')
        return redirect('characters:list')

    context = {'character': character}
    return render(request, 'characters/delete_confirm.html', context)
