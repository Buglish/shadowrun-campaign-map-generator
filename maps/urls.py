from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    path('', views.map_list, name='list'),
    path('create/', views.map_create, name='create'),
    path('<int:pk>/', views.map_detail, name='detail'),
    path('<int:pk>/edit/', views.map_edit, name='edit'),
    path('<int:pk>/delete/', views.map_delete, name='delete'),
    path('generate/', views.map_generate, name='generate'),
]
