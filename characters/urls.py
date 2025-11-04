from django.urls import path
from . import views

app_name = 'characters'

urlpatterns = [
    path('', views.character_list, name='list'),
    path('create/', views.character_create, name='create'),

    # Character creation wizard steps
    path('create/step1/', views.character_create_step1, name='create_step1'),
    path('create/step2/', views.character_create_step2, name='create_step2'),
    path('create/step3/', views.character_create_step3, name='create_step3'),
    path('create/step4/', views.character_create_step4, name='create_step4'),
    path('create/step5/', views.character_create_step5, name='create_step5'),
    path('create/step6/', views.character_create_step6, name='create_step6'),
    path('create/step7/', views.character_create_step7, name='create_step7'),
    path('create/step8/', views.character_create_step8, name='create_step8'),

    # Character management
    path('<int:pk>/', views.character_detail, name='detail'),
    path('<int:pk>/edit/', views.character_edit, name='edit'),
    path('<int:pk>/delete/', views.character_delete, name='delete'),
]
