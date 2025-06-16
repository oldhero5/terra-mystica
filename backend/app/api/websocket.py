"""
WebSocket endpoints for real-time updates
"""

from typing import Dict, Set
import json
import asyncio

from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from jose import jwt, JWTError

from app.core.config import settings
from app.core.logging import logger


class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and track a new WebSocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send a message to all connections for a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {str(e)}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def send_progress_update(
        self,
        user_id: str,
        image_id: str,
        progress: float,
        status: str,
        message: str,
    ):
        """Send a progress update for image processing"""
        update = {
            "type": "progress",
            "image_id": image_id,
            "progress": progress,
            "status": status,
            "message": message,
        }
        await self.send_personal_message(json.dumps(update), user_id)
    
    async def send_completion(
        self,
        user_id: str,
        image_id: str,
        success: bool,
        result: Dict = None,
        error: str = None,
    ):
        """Send a completion notification"""
        update = {
            "type": "complete",
            "image_id": image_id,
            "success": success,
        }
        if result:
            update["result"] = result
        if error:
            update["error"] = error
        
        await self.send_personal_message(json.dumps(update), user_id)


# Global connection manager
manager = ConnectionManager()


async def get_current_user_ws(token: str = Query(...)) -> str:
    """Validate WebSocket connection token and return user ID"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token")
        return user_id
    except JWTError:
        raise ValueError("Invalid token")


async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time image processing updates.
    
    Connect with: ws://localhost:8000/ws?token=YOUR_JWT_TOKEN
    
    Message types:
    - progress: Processing progress updates
    - complete: Processing completed (success or failure)
    - error: Connection or processing errors
    """
    user_id = None
    try:
        # Authenticate the connection
        user_id = await get_current_user_ws(token)
        await manager.connect(websocket, user_id)
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "WebSocket connection established",
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for any message from client (ping/pong)
                data = await websocket.receive_text()
                
                # Handle ping
                if data == "ping":
                    await websocket.send_text("pong")
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                break
                
    except ValueError as e:
        # Authentication failed
        await websocket.close(code=1008, reason="Authentication failed")
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        if websocket.client_state.value == 1:  # CONNECTED
            await websocket.close(code=1011, reason="Internal server error")
    finally:
        if user_id:
            manager.disconnect(websocket, user_id)


def create_progress_callback(user_id: str, image_id: str):
    """Create a progress callback function for image processing"""
    async def callback(progress: float, message: str):
        await manager.send_progress_update(
            user_id=user_id,
            image_id=image_id,
            progress=progress,
            status="processing",
            message=message,
        )
    return callback