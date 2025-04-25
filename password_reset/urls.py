from django.urls import path
from . import views

# app_name = 'password_reset'

urlpatterns = [
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset_password'),
]