from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_reset_email(user, token):
    subject = 'Password Reset Request'
    reset_url = settings.SITE_URL + reverse('reset_password', kwargs={'token': str(token)})
    message = f"""
    Hello {user.username},

    You requested a password reset for your account. Click the link below to reset your password:

    {reset_url}

    This link will expire in 1 hour. If you did not request a password reset, please ignore this email.

    Best regards,
    easymoneysniper Team
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_FROM,
        [user.email],
        fail_silently=False,
    )