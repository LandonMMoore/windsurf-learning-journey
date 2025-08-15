from typing import Any, Dict

import socketio
from fastapi import FastAPI
from loguru import logger

from src.core.config import configs


class SocketIOService:
    def __init__(
        self,
        cors_origins: str = "*",
        client_manager: socketio.AsyncRedisManager = None,
        transports: list = None,
        logger: bool = False,
        engineio_logger: bool = False,
    ):
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=cors_origins,
            transports=transports,
            client_manager=client_manager,
            logger=logger,
            engineio_logger=engineio_logger,
        )

        # Register Socket.IO event handlers
        self._register_events()

    def _register_events(self):
        """Register Socket.IO event handlers"""

        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"Client connected: {sid}")
            await self.sio.emit(
                "connection_status",
                {
                    "status": "connected",
                    "sid": sid,
                    "message": "Connected to workflow updates",
                },
                to=sid,
            )

        @self.sio.event
        async def disconnect(sid):
            logger.info(f"Client disconnected: {sid}")

        @self.sio.event
        async def join_workflow_room(sid, data):
            """Join a specific workflow room to receive updates"""
            workflow_id = data.get("workflow_id")
            if workflow_id:
                await self.sio.enter_room(sid, f"workflow_{workflow_id}")
                logger.info(
                    f"Client {sid} joined workflow room: workflow_{workflow_id}"
                )
                await self.sio.emit(
                    "room_joined",
                    {
                        "workflow_id": workflow_id,
                        "message": f"Joined workflow room: {workflow_id}",
                    },
                    to=sid,
                )

        @self.sio.event
        async def leave_workflow_room(sid, data):
            """Leave a specific workflow room"""
            workflow_id = data.get("workflow_id")
            if workflow_id:
                await self.sio.leave_room(sid, f"workflow_{workflow_id}")
                logger.info(f"Client {sid} left workflow room: workflow_{workflow_id}")
                await self.sio.emit(
                    "room_left",
                    {
                        "workflow_id": workflow_id,
                        "message": f"Left workflow room: {workflow_id}",
                    },
                    to=sid,
                )

        @self.sio.event
        async def ping(sid, data):
            """Handle ping messages for testing"""
            await self.sio.emit(
                "pong",
                {"message": "Pong received", "timestamp": "2024-01-01T00:00:00Z"},
                to=sid,
            )

    def bind_app(self, fastapi_app: FastAPI):
        return socketio.ASGIApp(self.sio, other_asgi_app=fastapi_app)

    async def emit_to_sid(self, sid: str, event: str, data: Dict[str, Any]):
        await self.sio.emit(event, data, to=sid)

    async def emit_broadcast(
        self, event: str, data: Dict[str, Any], namespace: str = None
    ):
        if namespace:
            await self.sio.emit(event, data, namespace=namespace)
        else:
            await self.sio.emit(event, data)

    async def join_room(self, sid: str, room: str):
        await self.sio.enter_room(sid, room)
        logger.info(f"{sid} joined room {room}")

    async def leave_room(self, sid: str, room: str):
        await self.sio.leave_room(sid, room)
        logger.info(f"{sid} left room {room}")

    async def emit_to_room(
        self, event: str, room: str, data: Dict[str, Any], namespace: str = "/"
    ):
        logger.info(f"Emitting to room: {room}")
        await self.sio.emit(event, data, room=room, namespace=namespace)

    async def emit_workflow_update(
        self,
        workflow_id: str,
        status: str,
        data: Dict[str, Any] = None,
        broadcast: bool = False,
    ):
        """
        Emit workflow update to specific workflow room only (unless broadcast=True)

        Args:
            workflow_id: The workflow ID
            status: The workflow status
            data: Additional data to send
            broadcast: If True, also broadcast to all clients (default: False)
        """
        update_data = {
            "workflow_id": workflow_id,
            "status": status,
            "timestamp": "2024-01-01T00:00:00Z",
            **(data if data else {}),
        }

        # TODO: Uncomment this for brodcasting to specific room
        # room = f"workflow_{workflow_id}"
        # logger.info(f"Emitting workflow update to room: {room}")
        # Always emit to specific workflow room
        # await self.emit_to_room("workflow_update", room, update_data)

        # Only broadcast to all clients if explicitly requested
        if broadcast:
            await self.emit_broadcast(configs.WORKFLOW_UPDATES, update_data)

    async def emit_workflow_update_to_room_only(
        self, workflow_id: str, status: str, data: Dict[str, Any] = None
    ):
        """
        Emit workflow update ONLY to specific workflow room (no broadcast)
        This is a convenience method that calls emit_workflow_update with broadcast=False
        """
        await self.emit_workflow_update(workflow_id, status, data, broadcast=False)

    async def emit_workflow_update_with_broadcast(
        self, workflow_id: str, status: str, data: Dict[str, Any] = None
    ):
        """
        Emit workflow update to specific workflow room AND broadcast to all clients
        This is a convenience method that calls emit_workflow_update with broadcast=True
        """
        await self.emit_workflow_update(workflow_id, status, data, broadcast=True)
