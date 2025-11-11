from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Campaign, Session, SessionObjective
from .forms import CampaignForm, SessionForm
from characters.models import Character


@login_required
def campaign_list(request):
    """List all campaigns accessible to the user"""
    # Get campaigns where user is GM or player
    campaigns = Campaign.objects.filter(
        Q(game_master=request.user) | Q(players=request.user)
    ).distinct()

    context = {
        'campaigns': campaigns,
        'gm_campaigns': campaigns.filter(game_master=request.user),
        'player_campaigns': campaigns.filter(players=request.user).exclude(game_master=request.user),
    }
    return render(request, 'campaigns/list.html', context)


@login_required
def campaign_create(request):
    """Create a new campaign"""
    if request.method == 'POST':
        form = CampaignForm(request.POST, user=request.user)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.game_master = request.user
            campaign.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f'Campaign "{campaign.name}" created successfully!')
            return redirect('campaigns:detail', pk=campaign.pk)
    else:
        form = CampaignForm(user=request.user)

    context = {'form': form, 'action': 'Create'}
    return render(request, 'campaigns/form.html', context)


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
