from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.campaign_list, name='list'),
    path('create/', views.campaign_create, name='create'),
    path('<int:pk>/', views.campaign_detail, name='detail'),
    path('<int:pk>/edit/', views.campaign_edit, name='edit'),
    path('<int:pk>/delete/', views.campaign_delete, name='delete'),
]
