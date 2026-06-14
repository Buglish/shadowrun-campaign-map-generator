"""
WebSocket URL routing for maps app.

Defines WebSocket URL patterns for real-time collaborative map editing.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/maps/(?P<map_id>\d+)/$', consumers.MapConsumer.as_asgi()),
]
