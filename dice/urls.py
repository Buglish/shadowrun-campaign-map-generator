from django.urls import path
from . import views

app_name = 'dice'

urlpatterns = [
    # Main dice roller
    path('', views.dice_roller, name='roller'),
    path('roll/', views.dice_roller, name='roll'),

    # AJAX endpoint
    path('api/roll/', views.roll_dice_ajax, name='roll_ajax'),

    # Roll details and history
    path('rolls/<int:pk>/', views.roll_detail, name='roll_detail'),
    path('history/', views.roll_history, name='history'),

    # Presets
    path('presets/', views.preset_list, name='preset_list'),
    path('presets/create/', views.preset_create, name='preset_create'),
    path('presets/<int:pk>/edit/', views.preset_edit, name='preset_edit'),
    path('presets/<int:pk>/delete/', views.preset_delete, name='preset_delete'),
    path('presets/<int:pk>/roll/', views.preset_roll, name='preset_roll'),
]
