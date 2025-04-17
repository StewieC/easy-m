# contributions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create-group/', views.create_group, name='create_group'),
    path('create-contribution-group/', views.create_contribution_group, name='create_contribution_group'),
    path('create-merry-go-round-group/', views.create_merry_go_round_group, name='create_merry_go_round_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/contribute/', views.make_contribution, name='make_contribution'),
    path('join-group/', views.join_group, name='join_group'),
    # path('help/', views.help_page, name='help_page'),
]