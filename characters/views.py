from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def character_list(request):
    """List all characters for the current user"""
    return render(request, 'characters/list.html')


@login_required
def character_create(request):
    """Create a new character"""
    return render(request, 'characters/form.html')


@login_required
def character_detail(request, pk):
    """View character details"""
    return render(request, 'characters/detail.html')


@login_required
def character_edit(request, pk):
    """Edit a character"""
    return render(request, 'characters/form.html')


@login_required
def character_delete(request, pk):
    """Delete a character"""
    messages.success(request, 'Character deleted successfully.')
    return redirect('characters:list')
