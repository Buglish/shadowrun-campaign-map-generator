"""
User presence tracking for real-time map collaboration.

Manages tracking of connected users, their cursor positions, and provides
user lists per room for the map editing interface.
"""
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserPresence:
    """Represents a user's presence in a room."""
    user_id: int
    username: str
    is_owner: bool
    user_color: str
    cursor_x: Optional[int] = None
    cursor_y: Optional[int] = None
    joined_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


class PresenceManager:
    """
    Manages user presence across map rooms.

    Uses an in-memory store. For multi-server deployments,
    this should be replaced with Redis-based storage.

    Thread-safe using asyncio.Lock for concurrent access.
    """

    def __init__(self):
        # room_name -> {user_id: UserPresence}
        self._rooms: Dict[str, Dict[int, UserPresence]] = {}
        self._lock = asyncio.Lock()

    async def user_joined(
        self,
        room: str,
        user_id: int,
        username: str,
        is_owner: bool,
        user_color: str
    ) -> None:
        """
        Register a user joining a room.

        Args:
            room: The room identifier (e.g., 'map_123')
            user_id: The user's database ID
            username: The user's display name
            is_owner: Whether the user owns the map
            user_color: Assigned color for cursor display
        """
        async with self._lock:
            if room not in self._rooms:
                self._rooms[room] = {}

            self._rooms[room][user_id] = UserPresence(
                user_id=user_id,
                username=username,
                is_owner=is_owner,
                user_color=user_color
            )

    async def user_left(self, room: str, user_id: int) -> None:
        """
        Remove a user from a room.

        Args:
            room: The room identifier
            user_id: The user's database ID
        """
        async with self._lock:
            if room in self._rooms and user_id in self._rooms[room]:
                del self._rooms[room][user_id]

                # Clean up empty rooms
                if not self._rooms[room]:
                    del self._rooms[room]

    async def update_cursor(
        self,
        room: str,
        user_id: int,
        x: int,
        y: int
    ) -> None:
        """
        Update a user's cursor position.

        Args:
            room: The room identifier
            user_id: The user's database ID
            x: Cursor X coordinate (tile position)
            y: Cursor Y coordinate (tile position)
        """
        async with self._lock:
            if room in self._rooms and user_id in self._rooms[room]:
                self._rooms[room][user_id].cursor_x = x
                self._rooms[room][user_id].cursor_y = y
                self._rooms[room][user_id].last_seen = datetime.now()

    async def get_users(self, room: str) -> List[dict]:
        """
        Get all users in a room.

        Args:
            room: The room identifier

        Returns:
            List of user dictionaries with id, username, is_owner,
            user_color, and cursor position
        """
        async with self._lock:
            if room not in self._rooms:
                return []

            return [
                {
                    'id': presence.user_id,
                    'username': presence.username,
                    'is_owner': presence.is_owner,
                    'user_color': presence.user_color,
                    'cursor': {
                        'x': presence.cursor_x,
                        'y': presence.cursor_y
                    } if presence.cursor_x is not None else None
                }
                for presence in self._rooms[room].values()
            ]

    async def get_user_count(self, room: str) -> int:
        """
        Get number of users in a room.

        Args:
            room: The room identifier

        Returns:
            Number of users currently in the room
        """
        async with self._lock:
            return len(self._rooms.get(room, {}))

    async def is_user_in_room(self, room: str, user_id: int) -> bool:
        """
        Check if a user is in a room.

        Args:
            room: The room identifier
            user_id: The user's database ID

        Returns:
            True if the user is in the room
        """
        async with self._lock:
            return room in self._rooms and user_id in self._rooms[room]

    async def get_all_rooms(self) -> List[str]:
        """
        Get all active rooms.

        Returns:
            List of room identifiers with at least one user
        """
        async with self._lock:
            return list(self._rooms.keys())

    async def cleanup_stale_users(self, timeout_seconds: int = 300) -> int:
        """
        Remove users who haven't been seen recently.

        Args:
            timeout_seconds: How long before a user is considered stale

        Returns:
            Number of users removed
        """
        removed = 0
        now = datetime.now()

        async with self._lock:
            rooms_to_delete = []

            for room, users in self._rooms.items():
                users_to_delete = []

                for user_id, presence in users.items():
                    if (now - presence.last_seen).total_seconds() > timeout_seconds:
                        users_to_delete.append(user_id)

                for user_id in users_to_delete:
                    del users[user_id]
                    removed += 1

                if not users:
                    rooms_to_delete.append(room)

            for room in rooms_to_delete:
                del self._rooms[room]

        return removed
