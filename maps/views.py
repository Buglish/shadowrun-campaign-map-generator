from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def map_list(request):
    """List all maps"""
    return render(request, 'maps/list.html')


@login_required
def map_create(request):
    """Create a new map"""
    return render(request, 'maps/form.html')


@login_required
def map_detail(request, pk):
    """View map details"""
    return render(request, 'maps/detail.html')


@login_required
def map_edit(request, pk):
    """Edit a map"""
    return render(request, 'maps/form.html')


@login_required
def map_delete(request, pk):
    """Delete a map"""
    messages.success(request, 'Map deleted successfully.')
    return redirect('maps:list')


@login_required
def map_generate(request):
    """Generate a map dynamically"""
    return render(request, 'maps/generate.html')
