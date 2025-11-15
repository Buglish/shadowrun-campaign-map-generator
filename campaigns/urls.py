from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Campaign URLs
    path('', views.campaign_list, name='list'),
    path('create/', views.campaign_create, name='create'),
    path('<int:pk>/', views.campaign_detail, name='detail'),
    path('<int:pk>/edit/', views.campaign_edit, name='edit'),
    path('<int:pk>/delete/', views.campaign_delete, name='delete'),

    # Session URLs
    path('<int:campaign_pk>/sessions/create/', views.session_create, name='session_create'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/', views.session_detail, name='session_detail'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/edit/', views.session_edit, name='session_edit'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/delete/', views.session_delete, name='session_delete'),

    # Combat Tracker URLs
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/create/', views.combat_create, name='combat_create'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/', views.combat_detail, name='combat_detail'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/log/', views.combat_log_view, name='combat_log'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/participant/add/', views.combat_participant_add, name='combat_participant_add'),

    # Combat AJAX endpoints
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/next-turn/', views.combat_next_turn, name='combat_next_turn'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/participant/<int:participant_pk>/update-hp/', views.combat_update_hp, name='combat_update_hp'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/start/', views.combat_start, name='combat_start'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/end/', views.combat_end, name='combat_end'),

    # Combat Effects endpoints
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/participant/<int:participant_pk>/effect/add/', views.combat_effect_add, name='combat_effect_add'),
    path('<int:campaign_pk>/sessions/<int:session_pk>/combat/<int:encounter_pk>/effect/<int:effect_pk>/remove/', views.combat_effect_remove, name='combat_effect_remove'),
]
