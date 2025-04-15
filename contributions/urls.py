# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('contribute/', views.contribute, name='contribute'),
    path('cycle/', views.manage_cycle, name='cycle'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('create_group/', views.create_group, name='create_group'),
    path('join_group/', views.join_group, name='join_group'),
    path('group/<int:group_id>/history/', views.contribution_history, name='contribution_history'),
    path('help/', views.help_page, name='help_page'),
]