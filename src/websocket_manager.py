"""
WebSocket Manager module for real-time customer support analytics.
Handles WebSocket connections and real-time data streaming.
"""

import asyncio
import websockets
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import logging
from datetime import datetime, timedelta
import threading
import time
import queue
from dataclasses import dataclass
from enum import Enum
import ssl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketType(Enum):
    """Supported WebSocket types."""
    CUSTOM = "custom"
    SLACK_RTM = "slack_rtm"
    DISCORD_GATEWAY = "discord_gateway"
    ZENDESK_EVENTS = "zendesk_events"
    FRESHDESK_EVENTS = "freshdesk_events"

@dataclass
class WebSocketConfig:
    """WebSocket configuration data class."""
    ws_type: WebSocketType
    url: str
    headers: Dict[str, str] = None
    auth_token: str = None
    heartbeat_interval: int = 30
    reconnect_interval: int = 5
    max_reconnect_attempts: int = 10
    ssl_context: ssl.SSLContext = None

class WebSocketManager:
    """Manages WebSocket connections for real-time customer support analytics."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.connections = {}
        self.subscribers = {}
        self.message_queues = {}
        self.reconnect_tasks = {}
        self.heartbeat_tasks = {}
        self.data_cache = {}
        self.last_message = {}
        
        # WebSocket URLs for different services
        self.ws_urls = {
            WebSocketType.SLACK_RTM: "wss://slack.com/rtm",
            WebSocketType.DISCORD_GATEWAY: "wss://gateway.discord.gg/?v=10&encoding=json",
            WebSocketType.ZENDESK_EVENTS: "wss://{subdomain}.zendesk.com/api/v2/events",
            WebSocketType.FRESHDESK_EVENTS: "wss://{subdomain}.freshdesk.com/api/v2/events"
        }
        
        logger.info("WebSocket Manager initialized")
    
    def connect(self, connection_id: str, config: WebSocketConfig) -> Dict:
        """
        Connect to a WebSocket.
        
        Args:
            connection_id: Unique identifier for the connection
            config: WebSocket configuration
            
        Returns:
            Dict with connection status
        """
        try:
            # Validate configuration
            validation_result = self._validate_config(config)
            if not validation_result['success']:
                return validation_result
            
            # Store configuration
            self.connections[connection_id] = {
                'config': config,
                'created_at': datetime.now(),
                'status': 'connecting',
                'websocket': None,
                'last_heartbeat': None,
                'reconnect_count': 0
            }
            
            # Initialize message queue
            self.message_queues[connection_id] = queue.Queue()
            
            # Start connection in a separate thread
            connection_thread = threading.Thread(
                target=self._connect_websocket,
                args=(connection_id,),
                daemon=True
            )
            connection_thread.start()
            
            logger.info(f"Initiated WebSocket connection: {connection_id}")
            
            return {
                'success': True,
                'connection_id': connection_id,
                'message': f"WebSocket connection initiated for {config.ws_type.value}"
            }
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            return {
                'success': False,
                'message': f"WebSocket connection failed: {str(e)}"
            }
    
    def disconnect(self, connection_id: str) -> Dict:
        """
        Disconnect from a WebSocket.
        
        Args:
            connection_id: ID of the connection to close
            
        Returns:
            Dict with disconnection status
        """
        try:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'message': f"Connection not found: {connection_id}"
                }
            
            connection_info = self.connections[connection_id]
            
            # Stop reconnect task
            if connection_id in self.reconnect_tasks:
                self.reconnect_tasks[connection_id]['stop'] = True
                del self.reconnect_tasks[connection_id]
            
            # Stop heartbeat task
            if connection_id in self.heartbeat_tasks:
                self.heartbeat_tasks[connection_id]['stop'] = True
                del self.heartbeat_tasks[connection_id]
            
            # Close WebSocket if open
            if connection_info['websocket']:
                try:
                    asyncio.run(connection_info['websocket'].close())
                except:
                    pass
            
            # Clean up
            del self.connections[connection_id]
            if connection_id in self.message_queues:
                del self.message_queues[connection_id]
            if connection_id in self.data_cache:
                del self.data_cache[connection_id]
            if connection_id in self.last_message:
                del self.last_message[connection_id]
            
            logger.info(f"Disconnected WebSocket: {connection_id}")
            
            return {
                'success': True,
                'message': f"WebSocket disconnected: {connection_id}"
            }
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
            return {
                'success': False,
                'message': f"Disconnection failed: {str(e)}"
            }
    
    def subscribe(self, connection_id: str, callback: Callable) -> Dict:
        """
        Subscribe to WebSocket messages.
        
        Args:
            connection_id: ID of the WebSocket connection
            callback: Callback function for messages
            
        Returns:
            Dict with subscription status
        """
        try:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'message': f"Connection not found: {connection_id}"
                }
            
            self.subscribers[connection_id] = callback
            
            logger.info(f"Subscribed to WebSocket messages: {connection_id}")
            
            return {
                'success': True,
                'message': f"Subscribed to {connection_id}"
            }
            
        except Exception as e:
            logger.error(f"Error subscribing to WebSocket: {e}")
            return {
                'success': False,
                'message': f"Subscription failed: {str(e)}"
            }
    
    def unsubscribe(self, connection_id: str) -> Dict:
        """
        Unsubscribe from WebSocket messages.
        
        Args:
            connection_id: ID of the WebSocket connection
            
        Returns:
            Dict with unsubscription status
        """
        try:
            if connection_id in self.subscribers:
                del self.subscribers[connection_id]
                
                logger.info(f"Unsubscribed from WebSocket messages: {connection_id}")
                
                return {
                    'success': True,
                    'message': f"Unsubscribed from {connection_id}"
                }
            else:
                return {
                    'success': False,
                    'message': f"No subscription found for {connection_id}"
                }
                
        except Exception as e:
            logger.error(f"Error unsubscribing from WebSocket: {e}")
            return {
                'success': False,
                'message': f"Unsubscription failed: {str(e)}"
            }
    
    def send_message(self, connection_id: str, message: Dict) -> Dict:
        """
        Send a message through WebSocket.
        
        Args:
            connection_id: ID of the WebSocket connection
            message: Message to send
            
        Returns:
            Dict with send status
        """
        try:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'message': f"Connection not found: {connection_id}"
                }
            
            connection_info = self.connections[connection_id]
            
            if connection_info['status'] != 'connected':
                return {
                    'success': False,
                    'message': f"WebSocket not connected: {connection_info['status']}"
                }
            
            websocket = connection_info['websocket']
            
            # Send message
            asyncio.run(websocket.send(json.dumps(message)))
            
            logger.info(f"Sent message through {connection_id}")
            
            return {
                'success': True,
                'message': f"Message sent through {connection_id}"
            }
            
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            return {
                'success': False,
                'message': f"Failed to send message: {str(e)}"
            }
    
    def get_latest_messages(self, connection_id: str, limit: int = 100) -> Dict:
        """
        Get latest messages from WebSocket.
        
        Args:
            connection_id: ID of the WebSocket connection
            limit: Maximum number of messages to retrieve
            
        Returns:
            Dict with messages
        """
        try:
            if connection_id not in self.message_queues:
                return {
                    'success': False,
                    'message': f"Message queue not found: {connection_id}"
                }
            
            messages = []
            message_queue = self.message_queues[connection_id]
            
            # Get messages from queue
            while not message_queue.empty() and len(messages) < limit:
                try:
                    message = message_queue.get_nowait()
                    messages.append(message)
                except queue.Empty:
                    break
            
            return {
                'success': True,
                'messages': messages,
                'count': len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error getting latest messages: {e}")
            return {
                'success': False,
                'message': f"Failed to get messages: {str(e)}"
            }
    
    def _validate_config(self, config: WebSocketConfig) -> Dict:
        """Validate WebSocket configuration."""
        try:
            if not config.url:
                return {
                    'success': False,
                    'message': "WebSocket URL is required"
                }
            
            if config.ws_type not in WebSocketType:
                return {
                    'success': False,
                    'message': f"Unsupported WebSocket type: {config.ws_type}"
                }
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Configuration validation failed: {str(e)}"
            }
    
    def _connect_websocket(self, connection_id: str):
        """Connect to WebSocket in a separate thread."""
        try:
            connection_info = self.connections[connection_id]
            config = connection_info['config']
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run connection
            loop.run_until_complete(self._async_connect(connection_id))
            
        except Exception as e:
            logger.error(f"Error in WebSocket connection thread: {e}")
            if connection_id in self.connections:
                self.connections[connection_id]['status'] = 'error'
    
    async def _async_connect(self, connection_id: str):
        """Async WebSocket connection."""
        try:
            connection_info = self.connections[connection_id]
            config = connection_info['config']
            
            # Prepare connection parameters
            extra_headers = config.headers or {}
            if config.auth_token:
                extra_headers['Authorization'] = f"Bearer {config.auth_token}"
            
            # Connect to WebSocket
            websocket = await websockets.connect(
                config.url,
                extra_headers=extra_headers,
                ssl=config.ssl_context
            )
            
            connection_info['websocket'] = websocket
            connection_info['status'] = 'connected'
            connection_info['last_heartbeat'] = datetime.now()
            
            logger.info(f"WebSocket connected: {connection_id}")
            
            # Start heartbeat
            self._start_heartbeat(connection_id)
            
            # Start message handling
            await self._handle_messages(connection_id)
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            connection_info['status'] = 'error'
            
            # Start reconnection
            self._start_reconnection(connection_id)
    
    async def _handle_messages(self, connection_id: str):
        """Handle incoming WebSocket messages."""
        try:
            connection_info = self.connections[connection_id]
            websocket = connection_info['websocket']
            config = connection_info['config']
            
            async for message in websocket:
                try:
                    # Parse message
                    if isinstance(message, str):
                        data = json.loads(message)
                    else:
                        data = message
                    
                    # Process message based on WebSocket type
                    processed_data = self._process_message(data, config.ws_type)
                    
                    # Store in message queue
                    self.message_queues[connection_id].put({
                        'data': processed_data,
                        'timestamp': datetime.now(),
                        'raw_message': data
                    })
                    
                    # Update cache
                    self.data_cache[connection_id] = {
                        'data': processed_data,
                        'timestamp': datetime.now()
                    }
                    
                    self.last_message[connection_id] = datetime.now()
                    
                    # Notify subscribers
                    if connection_id in self.subscribers:
                        try:
                            self.subscribers[connection_id](connection_id, processed_data)
                        except Exception as e:
                            logger.error(f"Error in subscriber callback: {e}")
                    
                    logger.debug(f"Processed message from {connection_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"WebSocket connection closed: {connection_id}")
            connection_info['status'] = 'disconnected'
            self._start_reconnection(connection_id)
        except Exception as e:
            logger.error(f"Error handling messages: {e}")
            connection_info['status'] = 'error'
            self._start_reconnection(connection_id)
    
    def _process_message(self, data: Dict, ws_type: WebSocketType) -> Dict:
        """Process WebSocket message based on type."""
        try:
            if ws_type == WebSocketType.SLACK_RTM:
                return self._process_slack_message(data)
            elif ws_type == WebSocketType.DISCORD_GATEWAY:
                return self._process_discord_message(data)
            elif ws_type == WebSocketType.ZENDESK_EVENTS:
                return self._process_zendesk_message(data)
            elif ws_type == WebSocketType.FRESHDESK_EVENTS:
                return self._process_freshdesk_message(data)
            else:
                return data
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return data
    
    def _process_slack_message(self, data: Dict) -> Dict:
        """Process Slack RTM message."""
        try:
            processed = {
                'type': data.get('type', 'unknown'),
                'channel': data.get('channel'),
                'user': data.get('user'),
                'text': data.get('text'),
                'timestamp': data.get('ts'),
                'team': data.get('team')
            }
            
            # Convert to support ticket format if applicable
            if processed['type'] == 'message' and processed['text']:
                processed['customer_message'] = processed['text']
                processed['created_at'] = datetime.fromtimestamp(float(processed['timestamp']))
                processed['team'] = processed['channel']
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing Slack message: {e}")
            return data
    
    def _process_discord_message(self, data: Dict) -> Dict:
        """Process Discord Gateway message."""
        try:
            processed = {
                'op': data.get('op'),
                't': data.get('t'),
                'd': data.get('d')
            }
            
            # Process message events
            if processed['t'] == 'MESSAGE_CREATE':
                message_data = processed['d']
                processed['customer_message'] = message_data.get('content')
                processed['created_at'] = datetime.now()
                processed['channel'] = message_data.get('channel_id')
                processed['user'] = message_data.get('author', {}).get('username')
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing Discord message: {e}")
            return data
    
    def _process_zendesk_message(self, data: Dict) -> Dict:
        """Process Zendesk events message."""
        try:
            processed = {
                'event_type': data.get('event_type'),
                'ticket_id': data.get('ticket_id'),
                'created_at': data.get('created_at'),
                'data': data.get('data', {})
            }
            
            # Convert to support ticket format
            if processed['event_type'] == 'ticket_created':
                processed['customer_message'] = processed['data'].get('description')
                processed['created_at'] = datetime.fromisoformat(processed['created_at'].replace('Z', '+00:00'))
                processed['team'] = processed['data'].get('assignee_id')
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing Zendesk message: {e}")
            return data
    
    def _process_freshdesk_message(self, data: Dict) -> Dict:
        """Process Freshdesk events message."""
        try:
            processed = {
                'event_type': data.get('event_type'),
                'ticket_id': data.get('ticket_id'),
                'created_at': data.get('created_at'),
                'data': data.get('data', {})
            }
            
            # Convert to support ticket format
            if processed['event_type'] == 'ticket_created':
                processed['customer_message'] = processed['data'].get('description')
                processed['created_at'] = datetime.fromisoformat(processed['created_at'].replace('Z', '+00:00'))
                processed['team'] = processed['data'].get('responder_id')
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing Freshdesk message: {e}")
            return data
    
    def _start_heartbeat(self, connection_id: str):
        """Start heartbeat for WebSocket connection."""
        try:
            connection_info = self.connections[connection_id]
            config = connection_info['config']
            
            stop_event = threading.Event()
            heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                args=(connection_id, config.heartbeat_interval, stop_event),
                daemon=True
            )
            
            self.heartbeat_tasks[connection_id] = {
                'thread': heartbeat_thread,
                'stop': stop_event
            }
            
            heartbeat_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting heartbeat: {e}")
    
    def _heartbeat_loop(self, connection_id: str, interval: int, stop_event: threading.Event):
        """Heartbeat loop."""
        try:
            while not stop_event.is_set():
                try:
                    if connection_id in self.connections:
                        connection_info = self.connections[connection_id]
                        
                        if connection_info['status'] == 'connected':
                            # Send ping
                            ping_message = {'type': 'ping'}
                            send_result = self.send_message(connection_id, ping_message)
                            
                            if send_result['success']:
                                connection_info['last_heartbeat'] = datetime.now()
                            else:
                                logger.warning(f"Heartbeat failed for {connection_id}")
                        
                    stop_event.wait(interval)
                    
                except Exception as e:
                    logger.error(f"Error in heartbeat loop: {e}")
                    stop_event.wait(60)
                    
        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}")
    
    def _start_reconnection(self, connection_id: str):
        """Start reconnection process."""
        try:
            connection_info = self.connections[connection_id]
            config = connection_info['config']
            
            if connection_info['reconnect_count'] >= config.max_reconnect_attempts:
                logger.error(f"Max reconnection attempts reached for {connection_id}")
                connection_info['status'] = 'failed'
                return
            
            stop_event = threading.Event()
            reconnect_thread = threading.Thread(
                target=self._reconnect_loop,
                args=(connection_id, config.reconnect_interval, stop_event),
                daemon=True
            )
            
            self.reconnect_tasks[connection_id] = {
                'thread': reconnect_thread,
                'stop': stop_event
            }
            
            reconnect_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting reconnection: {e}")
    
    def _reconnect_loop(self, connection_id: str, interval: int, stop_event: threading.Event):
        """Reconnection loop."""
        try:
            while not stop_event.is_set():
                try:
                    if connection_id in self.connections:
                        connection_info = self.connections[connection_id]
                        
                        logger.info(f"Attempting to reconnect {connection_id}")
                        
                        # Update reconnect count
                        connection_info['reconnect_count'] += 1
                        
                        # Try to reconnect
                        connection_thread = threading.Thread(
                            target=self._connect_websocket,
                            args=(connection_id,),
                            daemon=True
                        )
                        connection_thread.start()
                        
                        # Wait for connection result
                        time.sleep(5)
                        
                        if connection_info['status'] == 'connected':
                            logger.info(f"Successfully reconnected {connection_id}")
                            stop_event.set()
                            break
                    
                    stop_event.wait(interval)
                    
                except Exception as e:
                    logger.error(f"Error in reconnect loop: {e}")
                    stop_event.wait(60)
                    
        except Exception as e:
            logger.error(f"Reconnect loop error: {e}")
    
    def get_connection_status(self, connection_id: str) -> Dict:
        """Get WebSocket connection status."""
        try:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'status': 'not_found',
                    'message': 'Connection not found'
                }
            
            connection_info = self.connections[connection_id]
            
            return {
                'success': True,
                'status': connection_info['status'],
                'ws_type': connection_info['config'].ws_type.value,
                'created_at': connection_info['created_at'],
                'last_heartbeat': connection_info['last_heartbeat'],
                'reconnect_count': connection_info['reconnect_count'],
                'last_message': self.last_message.get(connection_id),
                'message_count': self.message_queues[connection_id].qsize() if connection_id in self.message_queues else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting connection status: {e}")
            return {
                'success': False,
                'status': 'error',
                'message': str(e)
            }
    
    def get_all_connections(self) -> Dict:
        """Get all WebSocket connections."""
        try:
            connections = {}
            
            for conn_id, conn_info in self.connections.items():
                status = self.get_connection_status(conn_id)
                connections[conn_id] = {
                    'ws_type': conn_info['config'].ws_type.value,
                    'created_at': conn_info['created_at'],
                    'status': status.get('status', 'unknown'),
                    'reconnect_count': conn_info['reconnect_count']
                }
            
            return {
                'success': True,
                'connections': connections,
                'count': len(connections)
            }
            
        except Exception as e:
            logger.error(f"Error getting all connections: {e}")
            return {
                'success': False,
                'message': str(e)
            }

# Global instance
ws_manager = WebSocketManager()
