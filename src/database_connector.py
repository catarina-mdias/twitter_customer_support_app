"""
Database connector module for real-time customer support analytics.
Handles database connections and real-time data access.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from datetime import datetime, timedelta
import sqlite3
import psycopg2
import pymysql
import threading
import time
import json
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Handles database connections and real-time data access for customer support analytics."""
    
    def __init__(self):
        """Initialize the database connector."""
        self.connections = {}
        self.active_queries = {}
        self.monitoring_threads = {}
        self.data_cache = {}
        self.last_update = {}
        
        # Supported database types
        self.supported_databases = {
            'sqlite': sqlite3,
            'postgresql': psycopg2,
            'mysql': pymysql
        }
        
        logger.info("Database connector initialized")
    
    def connect(self, db_type: str, connection_params: Dict) -> Dict:
        """
        Connect to a database.
        
        Args:
            db_type: Type of database ('sqlite', 'postgresql', 'mysql')
            connection_params: Connection parameters
            
        Returns:
            Dict with connection status and connection ID
        """
        try:
            if db_type not in self.supported_databases:
                return {
                    'success': False,
                    'message': f"Unsupported database type: {db_type}"
                }
            
            # Generate connection ID
            connection_id = f"{db_type}_{int(time.time())}"
            
            if db_type == 'sqlite':
                connection = sqlite3.connect(
                    connection_params.get('database', ':memory:'),
                    check_same_thread=False
                )
            elif db_type == 'postgresql':
                connection = psycopg2.connect(
                    host=connection_params.get('host', 'localhost'),
                    port=connection_params.get('port', 5432),
                    database=connection_params.get('database'),
                    user=connection_params.get('user'),
                    password=connection_params.get('password')
                )
            elif db_type == 'mysql':
                connection = pymysql.connect(
                    host=connection_params.get('host', 'localhost'),
                    port=connection_params.get('port', 3306),
                    database=connection_params.get('database'),
                    user=connection_params.get('user'),
                    password=connection_params.get('password')
                )
            
            # Store connection
            self.connections[connection_id] = {
                'connection': connection,
                'type': db_type,
                'params': connection_params,
                'created_at': datetime.now()
            }
            
            logger.info(f"Connected to {db_type} database: {connection_id}")
            
            return {
                'success': True,
                'connection_id': connection_id,
                'message': f"Successfully connected to {db_type} database"
            }
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return {
                'success': False,
                'message': f"Database connection failed: {str(e)}"
            }
    
    def disconnect(self, connection_id: str) -> Dict:
        """
        Disconnect from a database.
        
        Args:
            connection_id: ID of the connection to close
            
        Returns:
            Dict with disconnection status
        """
        try:
            if connection_id in self.connections:
                connection_info = self.connections[connection_id]
                connection_info['connection'].close()
                del self.connections[connection_id]
                
                # Stop any monitoring threads
                if connection_id in self.monitoring_threads:
                    self.monitoring_threads[connection_id]['stop'] = True
                    del self.monitoring_threads[connection_id]
                
                logger.info(f"Disconnected from database: {connection_id}")
                
                return {
                    'success': True,
                    'message': f"Disconnected from database: {connection_id}"
                }
            else:
                return {
                    'success': False,
                    'message': f"Connection not found: {connection_id}"
                }
                
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
            return {
                'success': False,
                'message': f"Disconnection failed: {str(e)}"
            }
    
    def execute_query(self, connection_id: str, query: str, params: Optional[Dict] = None) -> Dict:
        """
        Execute a SQL query.
        
        Args:
            connection_id: ID of the database connection
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Dict with query results
        """
        try:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'message': f"Connection not found: {connection_id}"
                }
            
            connection_info = self.connections[connection_id]
            connection = connection_info['connection']
            
            # Execute query
            if params:
                df = pd.read_sql_query(query, connection, params=params)
            else:
                df = pd.read_sql_query(query, connection)
            
            logger.info(f"Query executed successfully on {connection_id}")
            
            return {
                'success': True,
                'data': df,
                'row_count': len(df),
                'columns': list(df.columns) if not df.empty else []
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                'success': False,
                'message': f"Query execution failed: {str(e)}"
            }
    
    def get_support_data(self, connection_id: str, table_name: str = 'support_tickets', 
                        limit: Optional[int] = None, 
                        where_clause: Optional[str] = None) -> Dict:
        """
        Get customer support data from database.
        
        Args:
            connection_id: ID of the database connection
            table_name: Name of the support tickets table
            limit: Maximum number of records to retrieve
            where_clause: Additional WHERE clause
            
        Returns:
            Dict with support data
        """
        try:
            # Build query
            query = f"SELECT * FROM {table_name}"
            
            if where_clause:
                query += f" WHERE {where_clause}"
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            result = self.execute_query(connection_id, query)
            
            if result['success']:
                # Standardize column names
                df = result['data']
                df = self._standardize_columns(df)
                
                logger.info(f"Retrieved {len(df)} support records from {connection_id}")
                
                return {
                    'success': True,
                    'data': df,
                    'row_count': len(df),
                    'message': f"Retrieved {len(df)} support records"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error getting support data: {e}")
            return {
                'success': False,
                'message': f"Failed to retrieve support data: {str(e)}"
            }
    
    def start_live_monitoring(self, connection_id: str, table_name: str = 'support_tickets',
                            refresh_interval: int = 30, callback: Optional[callable] = None) -> Dict:
        """
        Start live monitoring of database changes.
        
        Args:
            connection_id: ID of the database connection
            table_name: Name of the table to monitor
            refresh_interval: Refresh interval in seconds
            callback: Callback function for data updates
            
        Returns:
            Dict with monitoring status
        """
        try:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'message': f"Connection not found: {connection_id}"
                }
            
            # Stop existing monitoring if any
            if connection_id in self.monitoring_threads:
                self.monitoring_threads[connection_id]['stop'] = True
            
            # Start monitoring thread
            stop_event = threading.Event()
            monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(connection_id, table_name, refresh_interval, callback, stop_event),
                daemon=True
            )
            
            self.monitoring_threads[connection_id] = {
                'thread': monitoring_thread,
                'stop': stop_event,
                'refresh_interval': refresh_interval,
                'callback': callback
            }
            
            monitoring_thread.start()
            
            logger.info(f"Started live monitoring for {connection_id}")
            
            return {
                'success': True,
                'message': f"Live monitoring started for {connection_id}",
                'refresh_interval': refresh_interval
            }
            
        except Exception as e:
            logger.error(f"Error starting live monitoring: {e}")
            return {
                'success': False,
                'message': f"Failed to start live monitoring: {str(e)}"
            }
    
    def stop_live_monitoring(self, connection_id: str) -> Dict:
        """
        Stop live monitoring.
        
        Args:
            connection_id: ID of the database connection
            
        Returns:
            Dict with stop status
        """
        try:
            if connection_id in self.monitoring_threads:
                self.monitoring_threads[connection_id]['stop'].set()
                del self.monitoring_threads[connection_id]
                
                logger.info(f"Stopped live monitoring for {connection_id}")
                
                return {
                    'success': True,
                    'message': f"Live monitoring stopped for {connection_id}"
                }
            else:
                return {
                    'success': False,
                    'message': f"No active monitoring found for {connection_id}"
                }
                
        except Exception as e:
            logger.error(f"Error stopping live monitoring: {e}")
            return {
                'success': False,
                'message': f"Failed to stop live monitoring: {str(e)}"
            }
    
    def _monitoring_loop(self, connection_id: str, table_name: str, 
                        refresh_interval: int, callback: callable, stop_event: threading.Event):
        """Internal monitoring loop."""
        try:
            last_count = 0
            
            while not stop_event.is_set():
                try:
                    # Get current data count
                    count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                    count_result = self.execute_query(connection_id, count_query)
                    
                    if count_result['success']:
                        current_count = count_result['data']['count'].iloc[0]
                        
                        # Check if data has changed
                        if current_count != last_count:
                            # Get latest data
                            data_result = self.get_support_data(connection_id, table_name, limit=100)
                            
                            if data_result['success']:
                                # Update cache
                                self.data_cache[connection_id] = {
                                    'data': data_result['data'],
                                    'timestamp': datetime.now(),
                                    'count': current_count
                                }
                                
                                # Call callback if provided
                                if callback:
                                    callback(connection_id, data_result['data'])
                                
                                last_count = current_count
                                logger.info(f"Data updated for {connection_id}: {current_count} records")
                    
                    # Wait for next check
                    stop_event.wait(refresh_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    stop_event.wait(60)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to match expected format.
        
        Args:
            df: DataFrame to standardize
            
        Returns:
            Standardized DataFrame
        """
        try:
            # Column mapping for common variations
            column_mapping = {
                'id': 'ticket_id',
                'ticket': 'ticket_id',
                'created': 'created_at',
                'timestamp': 'created_at',
                'responded': 'responded_at',
                'response_time': 'responded_at',
                'message': 'customer_message',
                'text': 'customer_message',
                'content': 'customer_message',
                'team_name': 'team',
                'agent': 'team',
                'assignee': 'team'
            }
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Convert datetime columns
            datetime_columns = ['created_at', 'responded_at']
            for col in datetime_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Error standardizing columns: {e}")
            return df
    
    def get_connection_status(self, connection_id: str) -> Dict:
        """
        Get connection status.
        
        Args:
            connection_id: ID of the database connection
            
        Returns:
            Dict with connection status
        """
        try:
            if connection_id not in self.connections:
                return {
                    'success': False,
                    'status': 'disconnected',
                    'message': 'Connection not found'
                }
            
            connection_info = self.connections[connection_id]
            
            # Test connection
            try:
                test_query = "SELECT 1"
                self.execute_query(connection_id, test_query)
                status = 'connected'
            except:
                status = 'error'
            
            return {
                'success': True,
                'status': status,
                'type': connection_info['type'],
                'created_at': connection_info['created_at'],
                'monitoring_active': connection_id in self.monitoring_threads,
                'last_update': self.last_update.get(connection_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting connection status: {e}")
            return {
                'success': False,
                'status': 'error',
                'message': str(e)
            }
    
    def get_all_connections(self) -> Dict:
        """
        Get all active connections.
        
        Returns:
            Dict with all connections
        """
        try:
            connections = {}
            
            for conn_id, conn_info in self.connections.items():
                status = self.get_connection_status(conn_id)
                connections[conn_id] = {
                    'type': conn_info['type'],
                    'created_at': conn_info['created_at'],
                    'status': status.get('status', 'unknown'),
                    'monitoring_active': conn_id in self.monitoring_threads
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
db_connector = DatabaseConnector()
