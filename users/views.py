from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile


def register(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Tobaz Autos, {user.first_name}!')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Register - Tobaz Autos',
        'meta_description': 'Create your Tobaz Autos account to access exclusive features and manage your orders.',
    }
    return render(request, 'users/register.html', context)


def user_login(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or username}!')
                next_url = request.GET.get('next', 'dashboard:dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': 'Login - Tobaz Autos',
        'meta_description': 'Sign in to your Tobaz Autos account to manage your profile and orders.',
    }
    return render(request, 'users/login.html', context)


@login_required
def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:home')


@login_required
def profile(request):
    """
    User profile view.
    """
    user = request.user
    profile = user.profile
    
    context = {
        'user': user,
        'profile': profile,
        'title': 'My Profile - Tobaz Autos',
        'meta_description': 'Manage your Tobaz Autos profile and preferences.',
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """
    Edit user profile view.
    """
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Edit Profile - Tobaz Autos',
        'meta_description': 'Update your Tobaz Autos profile information.',
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def settings(request):
    """
    User settings view with theme toggle.
    """
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        # Handle theme preference
        theme = request.POST.get('theme', 'light')
        response = redirect('users:settings')
        response.set_cookie('theme', theme, max_age=365*24*60*60)
        
        # Handle notification preferences
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.sms_notifications = request.POST.get('sms_notifications') == 'on'
        profile.save()
        
        messages.success(request, 'Settings updated successfully!')
        return response
    
    context = {
        'profile': profile,
        'title': 'Settings - Tobaz Autos',
        'meta_description': 'Manage your Tobaz Autos account settings and preferences.',
    }
    return render(request, 'users/settings.html', context)
