from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import logging
from .models import Campaign, Session, SessionObjective, CombatEncounter, CombatParticipant, CombatEffect, CombatLog
from .forms import CampaignForm, SessionForm, CombatEncounterForm, CombatParticipantForm, CombatEffectForm
from characters.models import Character

logger = logging.getLogger(__name__)


@login_required
def campaign_list(request):
    """List all campaigns accessible to the user"""
    try:
        # Get campaigns where user is GM or player
        campaigns = Campaign.objects.filter(
            Q(game_master=request.user) | Q(players=request.user)
        ).distinct()

        context = {
            'campaigns': campaigns,
            'gm_campaigns': campaigns.filter(game_master=request.user),
            'player_campaigns': campaigns.filter(players=request.user).exclude(game_master=request.user),
        }
        logger.info(f"User {request.user.username} accessed campaign list")
        return render(request, 'campaigns/list.html', context)
    except Exception as e:
        logger.error(f"Error in campaign_list for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading campaigns.')
        return redirect('home')


@login_required
def campaign_create(request):
    """Create a new campaign"""
    try:
        if request.method == 'POST':
            form = CampaignForm(request.POST, user=request.user)
            if form.is_valid():
                try:
                    campaign = form.save(commit=False)
                    campaign.game_master = request.user
                    campaign.save()
                    form.save_m2m()  # Save many-to-many relationships
                    logger.info(f"User {request.user.username} created campaign '{campaign.name}' (ID: {campaign.pk})")
                    messages.success(request, f'Campaign "{campaign.name}" created successfully!')
                    return redirect('campaigns:detail', pk=campaign.pk)
                except Exception as e:
                    logger.error(f"Error saving campaign for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to create campaign. Please try again.')
        else:
            form = CampaignForm(user=request.user)

        context = {'form': form, 'action': 'Create'}
        return render(request, 'campaigns/form.html', context)
    except Exception as e:
        logger.error(f"Error in campaign_create for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('campaigns:list')


@login_required
def campaign_detail(request, pk):
    """View campaign details"""
    campaign = get_object_or_404(Campaign, pk=pk)

    # Check if user has access (GM or player)
    if campaign.game_master != request.user and request.user not in campaign.players.all():
        messages.error(request, 'You do not have access to this campaign.')
        return redirect('campaigns:list')

    is_gm = campaign.game_master == request.user

    # Get sessions
    sessions = campaign.sessions.all()

    context = {
        'campaign': campaign,
        'sessions': sessions,
        'is_gm': is_gm,
        'upcoming_sessions': sessions.filter(status='planned').order_by('scheduled_date')[:5],
        'recent_sessions': sessions.filter(status='completed').order_by('-actual_date')[:5],
    }
    return render(request, 'campaigns/detail.html', context)


@login_required
def campaign_edit(request, pk):
    """Edit a campaign"""
    campaign = get_object_or_404(Campaign, pk=pk)

    # Only GM can edit
    if campaign.game_master != request.user:
        messages.error(request, 'Only the Game Master can edit this campaign.')
        return redirect('campaigns:detail', pk=pk)

    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Campaign "{campaign.name}" updated successfully!')
            return redirect('campaigns:detail', pk=campaign.pk)
    else:
        form = CampaignForm(instance=campaign, user=request.user)

    context = {'form': form, 'campaign': campaign, 'action': 'Edit'}
    return render(request, 'campaigns/form.html', context)


@login_required
def campaign_delete(request, pk):
    """Delete a campaign"""
    campaign = get_object_or_404(Campaign, pk=pk)

    # Only GM can delete
    if campaign.game_master != request.user:
        messages.error(request, 'Only the Game Master can delete this campaign.')
        return redirect('campaigns:detail', pk=pk)

    if request.method == 'POST':
        campaign_name = campaign.name
        campaign.delete()
        messages.success(request, f'Campaign "{campaign_name}" deleted successfully.')
        return redirect('campaigns:list')

    context = {'campaign': campaign}
    return render(request, 'campaigns/confirm_delete.html', context)


# Session Views

@login_required
def session_create(request, campaign_pk):
    """Create a new session for a campaign"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)

    # Only GM can create sessions
    if campaign.game_master != request.user:
        messages.error(request, 'Only the Game Master can create sessions.')
        return redirect('campaigns:detail', pk=campaign_pk)

    if request.method == 'POST':
        form = SessionForm(request.POST, campaign=campaign)
        if form.is_valid():
            session = form.save(commit=False)
            session.campaign = campaign
            session.save()
            form.save_m2m()
            messages.success(request, f'Session "{session.title}" created successfully!')
            return redirect('campaigns:session_detail', campaign_pk=campaign_pk, session_pk=session.pk)
    else:
        form = SessionForm(campaign=campaign)

    context = {
        'form': form,
        'campaign': campaign,
        'action': 'Create'
    }
    return render(request, 'campaigns/session_form.html', context)


@login_required
def session_detail(request, campaign_pk, session_pk):
    """View session details"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    session = get_object_or_404(Session, pk=session_pk, campaign=campaign)

    # Check if user has access
    if campaign.game_master != request.user and request.user not in campaign.players.all():
        messages.error(request, 'You do not have access to this session.')
        return redirect('campaigns:list')

    is_gm = campaign.game_master == request.user

    context = {
        'campaign': campaign,
        'session': session,
        'is_gm': is_gm,
    }
    return render(request, 'campaigns/session_detail.html', context)


@login_required
def session_edit(request, campaign_pk, session_pk):
    """Edit a session"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    session = get_object_or_404(Session, pk=session_pk, campaign=campaign)

    # Only GM can edit
    if campaign.game_master != request.user:
        messages.error(request, 'Only the Game Master can edit sessions.')
        return redirect('campaigns:session_detail', campaign_pk=campaign_pk, session_pk=session_pk)

    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session, campaign=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, f'Session "{session.title}" updated successfully!')
            return redirect('campaigns:session_detail', campaign_pk=campaign_pk, session_pk=session.pk)
    else:
        form = SessionForm(instance=session, campaign=campaign)

    context = {
        'form': form,
        'campaign': campaign,
        'session': session,
        'action': 'Edit'
    }
    return render(request, 'campaigns/session_form.html', context)


@login_required
def session_delete(request, campaign_pk, session_pk):
    """Delete a session"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    session = get_object_or_404(Session, pk=session_pk, campaign=campaign)

    # Only GM can delete
    if campaign.game_master != request.user:
        messages.error(request, 'Only the Game Master can delete sessions.')
        return redirect('campaigns:session_detail', campaign_pk=campaign_pk, session_pk=session_pk)

    if request.method == 'POST':
        session_title = session.title
        session.delete()
        messages.success(request, f'Session "{session_title}" deleted successfully.')
        return redirect('campaigns:detail', pk=campaign_pk)

    context = {
        'campaign': campaign,
        'session': session
    }
    return render(request, 'campaigns/session_confirm_delete.html', context)


# Combat Tracker Views

@login_required
def combat_create(request, campaign_pk, session_pk):
    """Create a new combat encounter"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    session = get_object_or_404(Session, pk=session_pk, campaign=campaign)

    # Only GM can create combat encounters
    if campaign.game_master != request.user:
        messages.error(request, 'Only the Game Master can create combat encounters.')
        return redirect('campaigns:session_detail', campaign_pk=campaign_pk, session_pk=session_pk)

    if request.method == 'POST':
        form = CombatEncounterForm(request.POST)
        if form.is_valid():
            encounter = form.save(commit=False)
            encounter.session = session
            encounter.save()
            messages.success(request, f'Combat encounter "{encounter.name}" created successfully!')
            return redirect('campaigns:combat_detail', campaign_pk=campaign_pk, session_pk=session_pk, encounter_pk=encounter.pk)
    else:
        form = CombatEncounterForm()

    context = {
        'form': form,
        'campaign': campaign,
        'session': session,
        'action': 'Create'
    }
    return render(request, 'campaigns/combat_form.html', context)


@login_required
def combat_detail(request, campaign_pk, session_pk, encounter_pk):
    """View combat encounter tracker interface"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    session = get_object_or_404(Session, pk=session_pk, campaign=campaign)
    encounter = get_object_or_404(CombatEncounter, pk=encounter_pk, session=session)

    # Check access
    if campaign.game_master != request.user and request.user not in campaign.players.all():
        messages.error(request, 'You do not have access to this combat.')
        return redirect('campaigns:list')

    is_gm = campaign.game_master == request.user
    participants = encounter.participants.filter(is_active=True).order_by('-initiative')

    context = {
        'campaign': campaign,
        'session': session,
        'encounter': encounter,
        'participants': participants,
        'is_gm': is_gm,
    }
    return render(request, 'campaigns/combat_detail.html', context)


@login_required
def combat_participant_add(request, campaign_pk, session_pk, encounter_pk):
    """Add a participant to combat"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    session = get_object_or_404(Session, pk=session_pk, campaign=campaign)
    encounter = get_object_or_404(CombatEncounter, pk=encounter_pk, session=session)

    # Only GM can add participants
    if campaign.game_master != request.user:
        messages.error(request, 'Only the Game Master can add participants.')
        return redirect('campaigns:combat_detail', campaign_pk=campaign_pk, session_pk=session_pk, encounter_pk=encounter_pk)

    if request.method == 'POST':
        form = CombatParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.encounter = encounter
            participant.save()
            messages.success(request, f'Added {participant.name} to combat.')
            return redirect('campaigns:combat_detail', campaign_pk=campaign_pk, session_pk=session_pk, encounter_pk=encounter_pk)
    else:
        form = CombatParticipantForm()
        # Pre-populate character choices from campaign
        form.fields['character'].queryset = campaign.characters.all()

    context = {
        'form': form,
        'campaign': campaign,
        'session': session,
        'encounter': encounter,
        'action': 'Add'
    }
    return render(request, 'campaigns/combat_participant_form.html', context)


# AJAX endpoints for real-time combat updates

@login_required
def combat_next_turn(request, campaign_pk, session_pk, encounter_pk):
    """Advance to the next turn (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    encounter = get_object_or_404(CombatEncounter, pk=encounter_pk)

    # Only GM can advance turns
    if campaign.game_master != request.user:
        return JsonResponse({'success': False, 'error': 'Only GM can advance turns'})

    participants = encounter.participants.filter(is_active=True).order_by('-initiative')
    participant_count = participants.count()

    if participant_count == 0:
        return JsonResponse({'success': False, 'error': 'No active participants'})

    # Advance turn
    encounter.current_turn += 1

    # If we've gone through all participants, start a new round
    if encounter.current_turn >= participant_count:
        encounter.current_turn = 0
        encounter.current_round += 1

        # Log new round
        CombatLog.log_event(
            encounter=encounter,
            event_type='round_start',
            description=f'Round {encounter.current_round} begins'
        )

        # Decrement effect durations
        for participant in participants:
            for effect in participant.effects.filter(is_active=True):
                effect.rounds_remaining -= 1
                if effect.rounds_remaining <= 0:
                    effect.is_active = False
                    # Log effect expiration
                    CombatLog.log_event(
                        encounter=encounter,
                        event_type='effect_expired',
                        description=f'{effect.name} has expired on {participant.name}',
                        target=participant
                    )
                effect.save()

    encounter.save()

    current_participant = encounter.current_participant

    # Log turn start
    if current_participant:
        CombatLog.log_event(
            encounter=encounter,
            event_type='turn_start',
            description=f"{current_participant.name}'s turn",
            actor=current_participant
        )
    return JsonResponse({
        'success': True,
        'current_round': encounter.current_round,
        'current_turn': encounter.current_turn,
        'current_participant': {
            'id': current_participant.id if current_participant else None,
            'name': current_participant.name if current_participant else None,
        }
    })


@login_required
def combat_update_hp(request, campaign_pk, session_pk, encounter_pk, participant_pk):
    """Update participant HP (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    participant = get_object_or_404(CombatParticipant, pk=participant_pk)

    # Only GM can update HP
    if campaign.game_master != request.user:
        return JsonResponse({'success': False, 'error': 'Only GM can update HP'})

    try:
        hp_change = int(request.POST.get('hp_change', 0))
        damage_type = request.POST.get('damage_type', 'physical')  # physical or stun

        if damage_type == 'physical':
            participant.physical_damage = max(0, participant.physical_damage - hp_change)
        elif damage_type == 'stun':
            participant.stun_damage = max(0, participant.stun_damage - hp_change)

        # Update current HP based on damage
        total_damage = participant.physical_damage + participant.stun_damage
        participant.current_hp = max(0, participant.max_hp - total_damage)

        # Log damage or healing
        encounter = participant.encounter
        if hp_change < 0:
            # Damage taken
            CombatLog.log_event(
                encounter=encounter,
                event_type='damage',
                description=f'{participant.name} takes {abs(hp_change)} {damage_type} damage',
                target=participant,
                data={'damage_amount': abs(hp_change), 'damage_type': damage_type}
            )
        elif hp_change > 0:
            # Healing received
            CombatLog.log_event(
                encounter=encounter,
                event_type='healing',
                description=f'{participant.name} is healed for {hp_change} HP',
                target=participant,
                data={'healing_amount': hp_change}
            )

        # Check if defeated
        was_defeated = participant.is_defeated
        if participant.current_hp == 0 and not was_defeated:
            participant.is_defeated = True
            participant.is_active = False
            # Log defeat
            CombatLog.log_event(
                encounter=encounter,
                event_type='defeated',
                description=f'{participant.name} has been defeated',
                target=participant
            )

        participant.save()

        return JsonResponse({
            'success': True,
            'current_hp': participant.current_hp,
            'max_hp': participant.max_hp,
            'physical_damage': participant.physical_damage,
            'stun_damage': participant.stun_damage,
            'hp_percentage': participant.hp_percentage,
            'condition': participant.condition,
            'is_defeated': participant.is_defeated
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def combat_start(request, campaign_pk, session_pk, encounter_pk):
    """Start combat encounter (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    encounter = get_object_or_404(CombatEncounter, pk=encounter_pk)

    # Only GM can start combat
    if campaign.game_master != request.user:
        return JsonResponse({'success': False, 'error': 'Only GM can start combat'})

    from django.utils import timezone
    encounter.status = 'active'
    encounter.started_at = timezone.now()
    encounter.save()

    # Log combat start
    CombatLog.log_event(
        encounter=encounter,
        event_type='combat_start',
        description=f'Combat encounter "{encounter.name}" has started'
    )

    return JsonResponse({
        'success': True,
        'status': encounter.status,
        'started_at': encounter.started_at.isoformat()
    })


@login_required
def combat_end(request, campaign_pk, session_pk, encounter_pk):
    """End combat encounter (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    encounter = get_object_or_404(CombatEncounter, pk=encounter_pk)

    # Only GM can end combat
    if campaign.game_master != request.user:
        return JsonResponse({'success': False, 'error': 'Only GM can end combat'})

    from django.utils import timezone
    encounter.status = 'completed'
    encounter.ended_at = timezone.now()
    encounter.save()

    # Log combat end
    enemies_defeated = encounter.participants.filter(team='enemy', is_defeated=True).count()
    CombatLog.log_event(
        encounter=encounter,
        event_type='combat_end',
        description=f'Combat encounter "{encounter.name}" has ended after {encounter.current_round} rounds',
        data={'enemies_defeated': enemies_defeated}
    )

    # Update session statistics
    session = encounter.session
    session.encounters_faced += 1
    session.enemies_defeated += enemies_defeated
    session.save()

    return JsonResponse({
        'success': True,
        'status': encounter.status,
        'ended_at': encounter.ended_at.isoformat()
    })


@login_required
def combat_log_view(request, campaign_pk, session_pk, encounter_pk):
    """View combat log history for an encounter"""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    session = get_object_or_404(Session, pk=session_pk, campaign=campaign)
    encounter = get_object_or_404(CombatEncounter, pk=encounter_pk, session=session)

    # Check access
    if campaign.game_master != request.user and request.user not in campaign.players.all():
        messages.error(request, 'You do not have access to this combat log.')
        return redirect('campaigns:list')

    # Get all logs for this encounter, ordered chronologically
    logs = encounter.combat_logs.all().order_by('timestamp')

    # Group logs by round for easier viewing
    logs_by_round = {}
    for log in logs:
        round_num = log.round_number
        if round_num not in logs_by_round:
            logs_by_round[round_num] = []
        logs_by_round[round_num].append(log)

    context = {
        'campaign': campaign,
        'session': session,
        'encounter': encounter,
        'logs': logs,
        'logs_by_round': sorted(logs_by_round.items()),
        'is_gm': campaign.game_master == request.user,
    }
    return render(request, 'campaigns/combat_log.html', context)


@login_required
def combat_effect_add(request, campaign_pk, session_pk, encounter_pk, participant_pk):
    """Add a status effect to a combat participant (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    participant = get_object_or_404(CombatParticipant, pk=participant_pk)
    encounter = participant.encounter

    # Only GM can add effects
    if campaign.game_master != request.user:
        return JsonResponse({'success': False, 'error': 'Only GM can add effects'})

    try:
        # Get effect data from POST
        name = request.POST.get('name', '').strip()
        effect_type = request.POST.get('effect_type', 'condition')
        description = request.POST.get('description', '').strip()
        duration_rounds = int(request.POST.get('duration_rounds', 1))

        if not name:
            return JsonResponse({'success': False, 'error': 'Effect name is required'})

        # Create the effect
        effect = CombatEffect.objects.create(
            participant=participant,
            name=name,
            effect_type=effect_type,
            description=description,
            duration_rounds=duration_rounds,
            rounds_remaining=duration_rounds,
            is_active=True
        )

        # Log the effect application
        CombatLog.log_event(
            encounter=encounter,
            event_type='effect_applied',
            description=f'{name} applied to {participant.name} for {duration_rounds} rounds',
            target=participant,
            data={'effect_name': name, 'effect_type': effect_type, 'duration': duration_rounds}
        )

        return JsonResponse({
            'success': True,
            'effect': {
                'id': effect.id,
                'name': effect.name,
                'effect_type': effect.effect_type,
                'rounds_remaining': effect.rounds_remaining,
                'description': effect.description
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def combat_effect_remove(request, campaign_pk, session_pk, encounter_pk, effect_pk):
    """Remove/deactivate a status effect (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    campaign = get_object_or_404(Campaign, pk=campaign_pk)
    effect = get_object_or_404(CombatEffect, pk=effect_pk)
    participant = effect.participant
    encounter = participant.encounter

    # Only GM can remove effects
    if campaign.game_master != request.user:
        return JsonResponse({'success': False, 'error': 'Only GM can remove effects'})

    try:
        # Deactivate the effect
        effect.is_active = False
        effect.rounds_remaining = 0
        effect.save()

        # Log the effect removal
        CombatLog.log_event(
            encounter=encounter,
            event_type='effect_expired',
            description=f'{effect.name} removed from {participant.name}',
            target=participant,
            data={'effect_name': effect.name, 'manually_removed': True}
        )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
