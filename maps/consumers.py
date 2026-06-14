"""
WebSocket consumers for real-time map collaboration.

Handles WebSocket connections for collaborative map editing, including:
- User connection/disconnection
- Tile updates
- Object updates
- Fog of war updates
- User cursor positions
- Presence tracking
"""
import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Map, MapTile, MapObject
from .presence import PresenceManager

logger = logging.getLogger(__name__)


class MapConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for collaborative map editing.

    Handles real-time synchronization of map edits between multiple users.
    """

    # Class-level presence manager (shared across instances)
    presence_manager = PresenceManager()

    # User colors for cursor display
    USER_COLORS = [
        '#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#f39c12',
        '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b'
    ]

    async def connect(self):
        """Handle WebSocket connection."""
        self.map_id = self.scope['url_route']['kwargs']['map_id']
        self.room_group_name = f'map_{self.map_id}'
        self.user = self.scope['user']

        # Check if user is authenticated
        if not self.user.is_authenticated:
            logger.warning(f"Unauthenticated WebSocket connection attempt for map {self.map_id}")
            await self.close(code=4001)
            return

        # Check if user has permission to view this map
        can_view, can_edit, is_owner = await self.check_permissions()
        if not can_view:
            logger.warning(f"User {self.user.username} denied access to map {self.map_id}")
            await self.close(code=4003)
            return

        self.can_edit = can_edit
        self.is_owner = is_owner

        # Assign user color based on order of connection
        user_index = await self.presence_manager.get_user_count(self.room_group_name)
        self.user_color = self.USER_COLORS[user_index % len(self.USER_COLORS)]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Register presence
        await self.presence_manager.user_joined(
            self.room_group_name,
            self.user.id,
            self.user.username,
            self.is_owner,
            self.user_color
        )

        # Get current users in the room
        current_users = await self.presence_manager.get_users(self.room_group_name)

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'data': {
                'user_id': self.user.id,
                'username': self.user.username,
                'map_id': int(self.map_id),
                'can_edit': self.can_edit,
                'is_owner': self.is_owner,
                'user_color': self.user_color,
                'current_users': current_users
            }
        }))

        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
                'user_color': self.user_color
            }
        )

        logger.info(f"User {self.user.username} connected to map {self.map_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user') and self.user.is_authenticated:
            # Remove from presence
            await self.presence_manager.user_left(
                self.room_group_name,
                self.user.id
            )

            # Notify others that user left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )

            logger.info(f"User {self.user.username} disconnected from map {self.map_id}")

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            message_data = data.get('data', {})

            # Route to appropriate handler
            handlers = {
                'tile_update': self.handle_tile_update,
                'object_update': self.handle_object_update,
                'fog_update': self.handle_fog_update,
                'cursor_move': self.handle_cursor_move,
                'ping': self.handle_ping,
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(message_data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_error("Unknown message type", "UNKNOWN_TYPE")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from {self.user.username}")
            await self.send_error("Invalid JSON", "INVALID_JSON")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            await self.send_error("Internal error", "INTERNAL_ERROR")

    async def handle_tile_update(self, data):
        """Handle tile paint updates."""
        if not self.can_edit:
            await self.send_error("Permission denied", "PERMISSION_DENIED")
            return

        tiles = data.get('tiles', [])
        timestamp = data.get('timestamp', datetime.now().timestamp() * 1000)

        # Validate and save tiles to database
        saved_tiles = await self.save_tiles(tiles)

        if saved_tiles:
            # Broadcast to all clients including sender
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_tile_update',
                    'tiles': saved_tiles,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timestamp
                }
            )

    async def handle_object_update(self, data):
        """Handle map object updates."""
        if not self.can_edit:
            await self.send_error("Permission denied", "PERMISSION_DENIED")
            return

        action = data.get('action')
        obj_data = data.get('object', {})
        timestamp = data.get('timestamp', datetime.now().timestamp() * 1000)

        # Process object update in database
        result = await self.save_object(action, obj_data)

        if result:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_object_update',
                    'action': action,
                    'object': result,
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'timestamp': timestamp
                }
            )

    async def handle_fog_update(self, data):
        """Handle fog of war updates."""
        if not self.is_owner:
            await self.send_error("Only map owner can modify fog of war", "PERMISSION_DENIED")
            return

        action = data.get('action')
        tiles = data.get('tiles', [])
        radius = data.get('radius', 1)

        # Process fog update
        result = await self.update_fog(action, tiles, radius)

        if result:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_fog_update',
                    'revealed_tiles': result['revealed_tiles'],
                    'fog_enabled': result['fog_enabled'],
                    'user_id': self.user.id
                }
            )

    async def handle_cursor_move(self, data):
        """Handle cursor position updates."""
        x = data.get('x')
        y = data.get('y')

        # Update presence with cursor position
        await self.presence_manager.update_cursor(
            self.room_group_name,
            self.user.id,
            x, y
        )

        # Broadcast cursor position to other clients
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_cursor_move',
                'user_id': self.user.id,
                'username': self.user.username,
                'x': x,
                'y': y,
                'color': self.user_color
            }
        )

    async def handle_ping(self, data):
        """Handle heartbeat ping."""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'data': {}
        }))

    # Database operations (sync_to_async wrapped)

    @database_sync_to_async
    def check_permissions(self):
        """Check if user can view/edit the map."""
        try:
            map_obj = Map.objects.get(pk=self.map_id)
            is_owner = map_obj.owner_id == self.user.id
            is_shared = self.user in map_obj.shared_with.all()
            is_public = map_obj.is_public

            can_view = is_owner or is_shared or is_public
            can_edit = is_owner or is_shared  # Shared users can edit

            return can_view, can_edit, is_owner
        except Map.DoesNotExist:
            return False, False, False

    @database_sync_to_async
    def save_tiles(self, tiles):
        """Save tile updates to database."""
        saved = []
        try:
            map_obj = Map.objects.get(pk=self.map_id)

            for tile_data in tiles:
                x = tile_data.get('x')
                y = tile_data.get('y')
                terrain_type = tile_data.get('terrain_type')
                color = tile_data.get('color')

                # Validate coordinates
                if x is None or y is None:
                    continue
                if x < 0 or x >= map_obj.width or y < 0 or y >= map_obj.height:
                    continue

                # Determine walkable and transparent based on terrain
                non_walkable = ['wall', 'building', 'water', 'mountain', 'void']
                non_transparent = ['wall', 'building', 'door', 'forest']

                is_walkable = terrain_type not in non_walkable
                is_transparent = terrain_type not in non_transparent

                tile, created = MapTile.objects.update_or_create(
                    map=map_obj, x=x, y=y,
                    defaults={
                        'terrain_type': terrain_type,
                        'color': color,
                        'is_walkable': is_walkable,
                        'is_transparent': is_transparent
                    }
                )

                saved.append({
                    'x': x,
                    'y': y,
                    'terrain_type': tile.terrain_type,
                    'color': tile.color,
                    'is_walkable': tile.is_walkable,
                    'is_transparent': tile.is_transparent
                })

            return saved
        except Exception as e:
            logger.error(f"Error saving tiles: {str(e)}")
            return []

    @database_sync_to_async
    def save_object(self, action, obj_data):
        """Save map object updates to database."""
        try:
            map_obj = Map.objects.get(pk=self.map_id)

            if action == 'create':
                obj = MapObject.objects.create(
                    map=map_obj,
                    x=obj_data.get('x', 0),
                    y=obj_data.get('y', 0),
                    name=obj_data.get('name', 'New Object'),
                    object_type=obj_data.get('object_type', 'marker'),
                    icon=obj_data.get('icon', ''),
                    color=obj_data.get('color', '#FF0000'),
                    is_visible_to_players=obj_data.get('is_visible_to_players', True),
                    blocks_movement=obj_data.get('blocks_movement', False),
                    blocks_vision=obj_data.get('blocks_vision', False)
                )
                return {
                    'id': obj.id,
                    'x': obj.x,
                    'y': obj.y,
                    'name': obj.name,
                    'object_type': obj.object_type,
                    'icon': obj.icon,
                    'color': obj.color,
                    'is_visible_to_players': obj.is_visible_to_players
                }

            elif action == 'update':
                obj_id = obj_data.get('id')
                if not obj_id:
                    return None

                obj = MapObject.objects.get(pk=obj_id, map=map_obj)

                # Update allowed fields
                for field in ['x', 'y', 'name', 'object_type', 'icon', 'color',
                              'is_visible_to_players', 'blocks_movement', 'blocks_vision']:
                    if field in obj_data:
                        setattr(obj, field, obj_data[field])

                obj.save()
                return {
                    'id': obj.id,
                    'x': obj.x,
                    'y': obj.y,
                    'name': obj.name,
                    'object_type': obj.object_type,
                    'icon': obj.icon,
                    'color': obj.color,
                    'is_visible_to_players': obj.is_visible_to_players
                }

            elif action == 'delete':
                obj_id = obj_data.get('id')
                if not obj_id:
                    return None

                MapObject.objects.filter(pk=obj_id, map=map_obj).delete()
                return {'id': obj_id, 'deleted': True}

            return None
        except MapObject.DoesNotExist:
            logger.warning(f"Object not found: {obj_data.get('id')}")
            return None
        except Exception as e:
            logger.error(f"Error saving object: {str(e)}")
            return None

    @database_sync_to_async
    def update_fog(self, action, tiles, radius):
        """Update fog of war state."""
        try:
            map_obj = Map.objects.get(pk=self.map_id)

            if action == 'toggle':
                map_obj.fog_of_war_enabled = not map_obj.fog_of_war_enabled
                map_obj.save()

            elif action == 'reset':
                map_obj.revealed_tiles = []
                map_obj.save()

            elif action in ['reveal', 'hide']:
                revealed = list(map_obj.revealed_tiles) if map_obj.revealed_tiles else []

                for tile in tiles:
                    # Handle both list format [x, y] and dict format {x, y}
                    if isinstance(tile, list):
                        x, y = tile
                    else:
                        x, y = tile.get('x'), tile.get('y')

                    if x is None or y is None:
                        continue

                    # Apply radius
                    for dy in range(-radius + 1, radius):
                        for dx in range(-radius + 1, radius):
                            tx, ty = x + dx, y + dy
                            if 0 <= tx < map_obj.width and 0 <= ty < map_obj.height:
                                coord = [tx, ty]
                                if action == 'reveal':
                                    if coord not in revealed:
                                        revealed.append(coord)
                                elif action == 'hide':
                                    if coord in revealed:
                                        revealed.remove(coord)

                map_obj.revealed_tiles = revealed
                map_obj.save()

            return {
                'revealed_tiles': map_obj.revealed_tiles,
                'fog_enabled': map_obj.fog_of_war_enabled
            }
        except Exception as e:
            logger.error(f"Error updating fog: {str(e)}")
            return None

    # Broadcast handlers (called by channel_layer.group_send)

    async def broadcast_tile_update(self, event):
        """Send tile update to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'tile_update',
            'data': {
                'tiles': event['tiles'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }
        }))

    async def broadcast_object_update(self, event):
        """Send object update to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'object_update',
            'data': {
                'action': event['action'],
                'object': event['object'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }
        }))

    async def broadcast_fog_update(self, event):
        """Send fog update to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'fog_update',
            'data': {
                'revealed_tiles': event['revealed_tiles'],
                'fog_enabled': event['fog_enabled'],
                'user_id': event['user_id']
            }
        }))

    async def broadcast_cursor_move(self, event):
        """Send cursor move to WebSocket client."""
        # Don't send cursor back to the user who moved it
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'cursor_move',
                'data': {
                    'user_id': event['user_id'],
                    'username': event['username'],
                    'x': event['x'],
                    'y': event['y'],
                    'color': event['color']
                }
            }))

    async def user_joined(self, event):
        """Handle user joined notification."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'data': {
                    'user_id': event['user_id'],
                    'username': event['username'],
                    'user_color': event.get('user_color', '#999999')
                }
            }))

    async def user_left(self, event):
        """Handle user left notification."""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'data': {
                'user_id': event['user_id'],
                'username': event['username']
            }
        }))

    async def send_error(self, message, code):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'data': {
                'message': message,
                'code': code
            }
        }))
