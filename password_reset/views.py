from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import PasswordResetToken
from .utils import send_reset_email
from django.utils import timezone

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Create a new password reset token
            token = PasswordResetToken(user=user)
            token.save()
            # Send the reset email
            send_reset_email(user, token.token)
            messages.success(request, "If an account with that email exists, we've sent a reset link to your email.")
        except User.DoesNotExist:
            # Even if the email doesn't exist, show the same message to prevent enumeration
            messages.success(request, "If an account with that email exists, we've sent a reset link to your email.")
        return redirect('login')
    return render(request, 'password_reset/forgot_password.html')

def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if reset_token.is_expired():
            messages.error(request, "This password reset link has expired.")
            return redirect('core:login')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid password reset link.")
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'password_reset/reset_password.html', {'token': token})
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'password_reset/reset_password.html', {'token': token})
        
        # Update the user's password
        user = reset_token.user
        user.set_password(password)
        user.save()
        # Invalidate the token
        reset_token.delete()
        messages.success(request, "Your password has been reset successfully. Please log in.")
        return redirect('login')
    
    return render(request, 'password_reset/reset_password.html', {'token': token})