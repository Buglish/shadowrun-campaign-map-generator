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
]
