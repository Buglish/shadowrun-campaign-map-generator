from django.urls import path
from . import views

app_name = 'characters'

urlpatterns = [
    path('', views.character_list, name='list'),
    path('create/', views.character_create, name='create'),
    path('<int:pk>/', views.character_detail, name='detail'),
    path('<int:pk>/edit/', views.character_edit, name='edit'),
    path('<int:pk>/delete/', views.character_delete, name='delete'),
]
