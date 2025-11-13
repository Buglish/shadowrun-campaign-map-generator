from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging
from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)


def register(request):
    """User registration view"""
    try:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save()
                    login(request, user)
                    logger.info(f"New user registered: {user.username}")
                    messages.success(request, 'Registration successful! Welcome to Shadowrun Campaign Manager.')
                    return redirect('home')
                except Exception as e:
                    logger.error(f"Error saving user during registration: {str(e)}", exc_info=True)
                    messages.error(request, 'Registration failed. Please try again.')
        else:
            form = CustomUserCreationForm()
        return render(request, 'accounts/register.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in register view: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('home')


@login_required
def profile(request):
    """User profile view"""
    try:
        logger.info(f"User {request.user.username} accessed profile page")
        return render(request, 'accounts/profile.html')
    except Exception as e:
        logger.error(f"Error in profile view for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading your profile.')
        return redirect('home')
