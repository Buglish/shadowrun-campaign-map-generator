qfrom django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import logging
from .models import DiceRoll, DicePreset
from .forms import DiceRollForm, QuickRollForm, DicePresetForm
from .utils import roll_shadowrun_dice, check_success, format_dice_results, get_hit_description
from campaigns.models import Campaign, Session
from characters.models import Character

logger = logging.getLogger(__name__)


@login_required
def dice_roller(request):
    """Main dice roller page with full form"""
    try:
        if request.method == 'POST':
            form = DiceRollForm(request.POST)
            if form.is_valid():
                try:
                    # Get form data
                    pool_size = form.cleaned_data['pool_size']
                    threshold = form.cleaned_data.get('threshold')
                    use_rule_of_six = form.cleaned_data['use_rule_of_six']
                    edge_used = form.cleaned_data['edge_used']
                    description = form.cleaned_data.get('description', '')

                    # Roll the dice
                    result = roll_shadowrun_dice(pool_size, use_rule_of_six, edge_used)

                    # Create DiceRoll record
                    dice_roll = DiceRoll.objects.create(
                        user=request.user,
                        description=description,
                        pool_size=pool_size,
                        threshold=threshold,
                        use_rule_of_six=use_rule_of_six,
                        edge_used=edge_used,
                        dice_results=','.join(map(str, result['dice_results'])),
                        total_hits=result['total_hits'],
                        ones_count=result['ones_count'],
                        is_glitch=result['is_glitch'],
                        is_critical_glitch=result['is_critical_glitch'],
                        success=check_success(result['total_hits'], threshold),
                    )

                    # Add optional context if provided
                    campaign_id = form.cleaned_data.get('campaign_id')
                    session_id = form.cleaned_data.get('session_id')
                    character_id = form.cleaned_data.get('character_id')

                    if campaign_id:
                        try:
                            dice_roll.campaign = Campaign.objects.get(pk=campaign_id)
                        except Campaign.DoesNotExist:
                            logger.warning(f"Campaign {campaign_id} not found for dice roll by user {request.user.username}")

                    if session_id:
                        try:
                            dice_roll.session = Session.objects.get(pk=session_id)
                        except Session.DoesNotExist:
                            logger.warning(f"Session {session_id} not found for dice roll by user {request.user.username}")

                    if character_id:
                        try:
                            dice_roll.character = Character.objects.get(pk=character_id, user=request.user)
                        except Character.DoesNotExist:
                            logger.warning(f"Character {character_id} not found for dice roll by user {request.user.username}")

                    dice_roll.save()

                    logger.info(f"User {request.user.username} rolled {pool_size}d6, hits: {dice_roll.total_hits}")
                    messages.success(request, f'Rolled {pool_size}d6: {dice_roll.get_result_summary()}')
                    return redirect('dice:roll_detail', pk=dice_roll.pk)
                except Exception as e:
                    logger.error(f"Error creating dice roll for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to roll dice. Please try again.')
        else:
            form = DiceRollForm()

        # Get recent rolls
        recent_rolls = DiceRoll.objects.filter(user=request.user)[:10]

        # Get user's presets
        presets = DicePreset.objects.filter(user=request.user)

        context = {
            'form': form,
            'recent_rolls': recent_rolls,
            'presets': presets,
        }
        return render(request, 'dice/roller.html', context)
    except Exception as e:
        logger.error(f"Error in dice_roller for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('home')


@login_required
@require_http_methods(["POST"])
def roll_dice_ajax(request):
    """AJAX endpoint for rolling dice"""
    import json

    try:
        data = json.loads(request.body)
        pool_size = int(data.get('pool_size', 6))
        threshold = data.get('threshold')
        use_rule_of_six = data.get('use_rule_of_six', True)
        edge_used = data.get('edge_used', False)
        description = data.get('description', '')

        if threshold:
            threshold = int(threshold)

        # Validate pool size
        if pool_size < 1 or pool_size > 50:
            return JsonResponse({'error': 'Pool size must be between 1 and 50'}, status=400)

        # Roll the dice
        result = roll_shadowrun_dice(pool_size, use_rule_of_six, edge_used)

        # Create DiceRoll record
        dice_roll = DiceRoll.objects.create(
            user=request.user,
            description=description,
            pool_size=pool_size,
            threshold=threshold,
            use_rule_of_six=use_rule_of_six,
            edge_used=edge_used,
            dice_results=','.join(map(str, result['dice_results'])),
            total_hits=result['total_hits'],
            ones_count=result['ones_count'],
            is_glitch=result['is_glitch'],
            is_critical_glitch=result['is_critical_glitch'],
            success=check_success(result['total_hits'], threshold),
        )

        # Format response
        response_data = {
            'success': True,
            'roll_id': dice_roll.pk,
            'pool_size': pool_size,
            'dice_results': result['dice_results'],
            'total_hits': result['total_hits'],
            'ones_count': result['ones_count'],
            'is_glitch': result['is_glitch'],
            'is_critical_glitch': result['is_critical_glitch'],
            'success': dice_roll.success,
            'threshold': threshold,
            'formatted_dice': format_dice_results(
                result['dice_results'],
                len(result['original_dice'])
            ),
            'hit_description': get_hit_description(result['total_hits']),
            'summary': dice_roll.get_result_summary(),
        }

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error in roll_dice_ajax for user {request.user.username}: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred while rolling dice'}, status=500)


@login_required
def roll_detail(request, pk):
    """View details of a specific roll"""
    try:
        dice_roll = get_object_or_404(DiceRoll, pk=pk, user=request.user)

        context = {
            'dice_roll': dice_roll,
            'dice_list': dice_roll.get_dice_list(),
            'formatted_dice': format_dice_results(dice_roll.get_dice_list()),
            'hit_description': get_hit_description(dice_roll.total_hits),
        }
        return render(request, 'dice/roll_detail.html', context)
    except Exception as e:
        logger.error(f"Error in roll_detail for user {request.user.username}, roll {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading roll details.')
        return redirect('dice:dice_roller')


@login_required
def roll_history(request):
    """View roll history with filtering"""
    try:
        rolls = DiceRoll.objects.filter(user=request.user)

        # Filter by campaign if provided
        campaign_id = request.GET.get('campaign')
        if campaign_id:
            rolls = rolls.filter(campaign_id=campaign_id)

        # Filter by character if provided
        character_id = request.GET.get('character')
        if character_id:
            rolls = rolls.filter(character_id=character_id)

        # Filter by glitches
        show_glitches = request.GET.get('glitches')
        if show_glitches == 'true':
            rolls = rolls.filter(is_glitch=True)

        # Pagination
        paginator = Paginator(rolls, 20)  # Show 20 rolls per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get user's campaigns and characters for filters
        campaigns = Campaign.objects.filter(
            game_master=request.user
        ) | Campaign.objects.filter(
            players=request.user
        )
        characters = Character.objects.filter(user=request.user)

        context = {
            'page_obj': page_obj,
            'campaigns': campaigns.distinct(),
            'characters': characters,
            'selected_campaign': campaign_id,
            'selected_character': character_id,
            'show_glitches': show_glitches,
        }
        logger.info(f"User {request.user.username} accessed roll history")
        return render(request, 'dice/history.html', context)
    except Exception as e:
        logger.error(f"Error in roll_history for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading roll history.')
        return redirect('dice:dice_roller')


@login_required
def preset_list(request):
    """List all presets for the user"""
    presets = DicePreset.objects.filter(user=request.user)

    # Group by character
    character_presets = {}
    general_presets = []

    for preset in presets:
        if preset.character:
            char_name = preset.character.name
            if char_name not in character_presets:
                character_presets[char_name] = []
            character_presets[char_name].append(preset)
        else:
            general_presets.append(preset)

    context = {
        'presets': presets,
        'general_presets': general_presets,
        'character_presets': character_presets,
    }
    return render(request, 'dice/preset_list.html', context)


@login_required
def preset_create(request):
    """Create a new dice preset"""
    try:
        if request.method == 'POST':
            form = DicePresetForm(request.POST, user=request.user)
            if form.is_valid():
                try:
                    preset = form.save(commit=False)
                    preset.user = request.user
                    preset.save()
                    logger.info(f"User {request.user.username} created preset '{preset.name}' (ID: {preset.pk})")
                    messages.success(request, f'Preset "{preset.name}" created successfully!')
                    return redirect('dice:preset_list')
                except Exception as e:
                    logger.error(f"Error saving preset for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to create preset. Please try again.')
        else:
            form = DicePresetForm(user=request.user)

        context = {'form': form, 'action': 'Create'}
        return render(request, 'dice/preset_form.html', context)
    except Exception as e:
        logger.error(f"Error in preset_create for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('dice:preset_list')


@login_required
def preset_edit(request, pk):
    """Edit a dice preset"""
    try:
        preset = get_object_or_404(DicePreset, pk=pk, user=request.user)

        if request.method == 'POST':
            form = DicePresetForm(request.POST, instance=preset, user=request.user)
            if form.is_valid():
                try:
                    form.save()
                    logger.info(f"User {request.user.username} updated preset '{preset.name}' (ID: {pk})")
                    messages.success(request, f'Preset "{preset.name}" updated successfully!')
                    return redirect('dice:preset_list')
                except Exception as e:
                    logger.error(f"Error saving preset {pk} for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to update preset. Please try again.')
        else:
            form = DicePresetForm(instance=preset, user=request.user)

        context = {'form': form, 'preset': preset, 'action': 'Edit'}
        return render(request, 'dice/preset_form.html', context)
    except Exception as e:
        logger.error(f"Error in preset_edit for user {request.user.username}, preset {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('dice:preset_list')


@login_required
def preset_delete(request, pk):
    """Delete a dice preset"""
    try:
        preset = get_object_or_404(DicePreset, pk=pk, user=request.user)

        if request.method == 'POST':
            try:
                name = preset.name
                preset.delete()
                logger.info(f"User {request.user.username} deleted preset '{name}' (ID: {pk})")
                messages.success(request, f'Preset "{name}" deleted successfully!')
                return redirect('dice:preset_list')
            except Exception as e:
                logger.error(f"Error deleting preset {pk} for user {request.user.username}: {str(e)}", exc_info=True)
                messages.error(request, 'Failed to delete preset. Please try again.')
                return redirect('dice:preset_list')

        context = {'preset': preset}
        return render(request, 'dice/preset_confirm_delete.html', context)
    except Exception as e:
        logger.error(f"Error in preset_delete for user {request.user.username}, preset {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('dice:preset_list')


@login_required
def preset_roll(request, pk):
    """Roll dice using a preset"""
    try:
        preset = get_object_or_404(DicePreset, pk=pk, user=request.user)

        # Roll using preset parameters
        result = roll_shadowrun_dice(
            preset.pool_size,
            preset.use_rule_of_six,
            edge_used=False
        )

        # Create DiceRoll record
        dice_roll = DiceRoll.objects.create(
            user=request.user,
            description=f"{preset.name}",
            pool_size=preset.pool_size,
            threshold=preset.threshold,
            use_rule_of_six=preset.use_rule_of_six,
            edge_used=False,
            dice_results=','.join(map(str, result['dice_results'])),
            total_hits=result['total_hits'],
            ones_count=result['ones_count'],
            is_glitch=result['is_glitch'],
            is_critical_glitch=result['is_critical_glitch'],
            success=check_success(result['total_hits'], preset.threshold),
            character=preset.character,
        )

        logger.info(f"User {request.user.username} rolled preset '{preset.name}', hits: {dice_roll.total_hits}")
        messages.success(request, f'Rolled preset "{preset.name}": {dice_roll.get_result_summary()}')
        return redirect('dice:roll_detail', pk=dice_roll.pk)
    except Exception as e:
        logger.error(f"Error in preset_roll for user {request.user.username}, preset {pk}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while rolling preset.')
        return redirect('dice:preset_list')
