/**
 * Real-time collaborative map editing client.
 * Handles WebSocket connection, message passing, and UI updates.
 */

class MapCollaborationClient {
    constructor(mapId, options = {}) {
        this.mapId = mapId;
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
        this.reconnectInterval = options.reconnectInterval || 1000;
        this.heartbeatInterval = options.heartbeatInterval || 30000;
        this.heartbeatTimer = null;
        this.pendingUpdates = [];
        this.users = new Map();
        this.cursorThrottleMs = 50;
        this.lastCursorUpdate = 0;

        // Callbacks
        this.onConnected = options.onConnected || (() => {});
        this.onDisconnected = options.onDisconnected || (() => {});
        this.onTileUpdate = options.onTileUpdate || (() => {});
        this.onObjectUpdate = options.onObjectUpdate || (() => {});
        this.onFogUpdate = options.onFogUpdate || (() => {});
        this.onUserJoined = options.onUserJoined || (() => {});
        this.onUserLeft = options.onUserLeft || (() => {});
        this.onCursorMove = options.onCursorMove || (() => {});
        this.onPresenceUpdate = options.onPresenceUpdate || (() => {});
        this.onError = options.onError || (() => {});

        // User info (populated on connect)
        this.userId = null;
        this.username = null;
        this.canEdit = false;
        this.isOwner = false;
        this.userColor = null;
    }

    /**
     * Connect to the WebSocket server.
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/maps/${this.mapId}/`;

        console.log(`[Collab] Connecting to ${wsUrl}...`);
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log('[Collab] WebSocket connected');
            this.connected = true;
            this.reconnectAttempts = 0;
            this.startHeartbeat();
            this.flushPendingUpdates();
        };

        this.socket.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };

        this.socket.onclose = (event) => {
            console.log(`[Collab] WebSocket closed: ${event.code}`);
            this.connected = false;
            this.stopHeartbeat();
            this.onDisconnected(event.code);

            // Attempt reconnection for unexpected closures
            if (event.code !== 4001 && event.code !== 4003 && event.code !== 1000) {
                this.attemptReconnect();
            }
        };

        this.socket.onerror = (error) => {
            console.error('[Collab] WebSocket error:', error);
            this.onError({ message: 'Connection error', code: 'CONNECTION_ERROR' });
        };
    }

    /**
     * Disconnect from the WebSocket server.
     */
    disconnect() {
        this.stopHeartbeat();
        if (this.socket) {
            this.socket.close(1000, 'Client disconnect');
            this.socket = null;
        }
        this.connected = false;
    }

    /**
     * Attempt to reconnect after disconnection.
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('[Collab] Max reconnection attempts reached');
            this.onError({
                message: 'Unable to reconnect. Please refresh the page.',
                code: 'MAX_RECONNECT'
            });
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`[Collab] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect(), delay);
    }

    /**
     * Start heartbeat to keep connection alive.
     */
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.connected) {
                this.send({ type: 'ping', data: {} });
            }
        }, this.heartbeatInterval);
    }

    /**
     * Stop heartbeat timer.
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Send a message to the server.
     */
    send(message) {
        if (this.connected && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
            return true;
        } else {
            // Queue message for when connection is restored
            this.pendingUpdates.push(message);
            return false;
        }
    }

    /**
     * Flush pending updates after reconnection.
     */
    flushPendingUpdates() {
        while (this.pendingUpdates.length > 0) {
            const message = this.pendingUpdates.shift();
            this.send(message);
        }
    }

    /**
     * Handle incoming WebSocket messages.
     */
    handleMessage(message) {
        const { type, data } = message;

        switch (type) {
            case 'connected':
                this.userId = data.user_id;
                this.username = data.username;
                this.canEdit = data.can_edit;
                this.isOwner = data.is_owner;
                this.userColor = data.user_color;

                // Initialize users from current_users
                this.users.clear();
                for (const user of data.current_users || []) {
                    this.users.set(user.id, user);
                }

                this.onConnected(data);
                this.onPresenceUpdate(Array.from(this.users.values()));
                break;

            case 'tile_update':
                // Always forward tile updates - let the callback decide what to do
                this.onTileUpdate(data);
                break;

            case 'object_update':
                this.onObjectUpdate(data);
                break;

            case 'fog_update':
                this.onFogUpdate(data);
                break;

            case 'user_joined':
                this.users.set(data.user_id, {
                    id: data.user_id,
                    username: data.username,
                    user_color: data.user_color,
                    cursor: null
                });
                this.onUserJoined(data);
                this.onPresenceUpdate(Array.from(this.users.values()));
                break;

            case 'user_left':
                this.users.delete(data.user_id);
                this.onUserLeft(data);
                this.onPresenceUpdate(Array.from(this.users.values()));
                break;

            case 'cursor_move':
                if (this.users.has(data.user_id)) {
                    const user = this.users.get(data.user_id);
                    user.cursor = { x: data.x, y: data.y };
                    this.users.set(data.user_id, user);
                }
                this.onCursorMove(data);
                break;

            case 'presence_update':
                this.users.clear();
                for (const user of data.users || []) {
                    this.users.set(user.id, user);
                }
                this.onPresenceUpdate(Array.from(this.users.values()));
                break;

            case 'error':
                console.error('[Collab] Server error:', data);
                this.onError(data);
                break;

            case 'pong':
                // Heartbeat response - connection is alive
                break;

            default:
                console.warn('[Collab] Unknown message type:', type);
        }
    }

    // API Methods for sending updates

    /**
     * Send tile updates to the server.
     * @param {Array} tiles - Array of tile objects with x, y, terrain_type, color
     */
    sendTileUpdate(tiles) {
        if (!this.canEdit) {
            console.warn('[Collab] Cannot edit: no permission');
            return false;
        }

        return this.send({
            type: 'tile_update',
            data: {
                tiles: tiles,
                timestamp: Date.now()
            }
        });
    }

    /**
     * Send object update to the server.
     * @param {string} action - 'create', 'update', or 'delete'
     * @param {object} obj - Object data
     */
    sendObjectUpdate(action, obj) {
        if (!this.canEdit) {
            console.warn('[Collab] Cannot edit: no permission');
            return false;
        }

        return this.send({
            type: 'object_update',
            data: {
                action: action,
                object: obj,
                timestamp: Date.now()
            }
        });
    }

    /**
     * Send fog of war update to the server.
     * @param {string} action - 'reveal', 'hide', 'reset', or 'toggle'
     * @param {Array} tiles - Array of [x, y] coordinates
     * @param {number} radius - Reveal/hide radius
     */
    sendFogUpdate(action, tiles = [], radius = 1) {
        if (!this.isOwner) {
            console.warn('[Collab] Cannot modify fog: not owner');
            return false;
        }

        return this.send({
            type: 'fog_update',
            data: {
                action: action,
                tiles: tiles,
                radius: radius
            }
        });
    }

    /**
     * Send cursor position update (throttled).
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     */
    sendCursorMove(x, y) {
        const now = Date.now();
        if (now - this.lastCursorUpdate < this.cursorThrottleMs) {
            return false;
        }

        this.lastCursorUpdate = now;
        return this.send({
            type: 'cursor_move',
            data: { x, y }
        });
    }

    /**
     * Get list of connected users.
     */
    getUsers() {
        return Array.from(this.users.values());
    }

    /**
     * Check if the client can edit.
     */
    canUserEdit() {
        return this.canEdit;
    }

    /**
     * Check if the client is the owner.
     */
    isUserOwner() {
        return this.isOwner;
    }

    /**
     * Check if client is connected.
     */
    isConnected() {
        return this.connected;
    }
}

// Export for use in templates
window.MapCollaborationClient = MapCollaborationClient;
