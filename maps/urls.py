from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    path('', views.map_list, name='list'),
    path('create/', views.map_create, name='create'),
    path('<int:pk>/', views.map_detail, name='detail'),
    path('<int:pk>/edit/', views.map_edit, name='edit'),
    path('<int:pk>/delete/', views.map_delete, name='delete'),
    path('<int:pk>/tile/update/', views.map_tile_update, name='tile_update'),
    path('generate/', views.map_generate, name='generate'),
    path('generate/preview/', views.map_generate_preview, name='generate_preview'),

    # Fog of War URLs
    path('<int:pk>/fog-of-war/toggle/', views.toggle_fog_of_war, name='toggle_fog_of_war'),
    path('<int:pk>/fog-of-war/reveal/', views.reveal_tile, name='reveal_tile'),
    path('<int:pk>/fog-of-war/hide/', views.hide_tile, name='hide_tile'),
    path('<int:pk>/fog-of-war/reset/', views.reset_fog_of_war, name='reset_fog_of_war'),

    # Map Generation Preset URLs
    path('presets/', views.preset_list, name='preset_list'),
    path('presets/create/', views.preset_create, name='preset_create'),
    path('presets/<int:pk>/edit/', views.preset_edit, name='preset_edit'),
    path('presets/<int:pk>/delete/', views.preset_delete, name='preset_delete'),
    path('presets/<int:pk>/load/', views.preset_load, name='preset_load'),
]
