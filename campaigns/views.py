from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def campaign_list(request):
    """List all campaigns"""
    return render(request, 'campaigns/list.html')


@login_required
def campaign_create(request):
    """Create a new campaign"""
    return render(request, 'campaigns/form.html')


@login_required
def campaign_detail(request, pk):
    """View campaign details"""
    return render(request, 'campaigns/detail.html')


@login_required
def campaign_edit(request, pk):
    """Edit a campaign"""
    return render(request, 'campaigns/form.html')


@login_required
def campaign_delete(request, pk):
    """Delete a campaign"""
    messages.success(request, 'Campaign deleted successfully.')
    return redirect('campaigns:list')
