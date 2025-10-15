#!/usr/bin/env python3
"""
Unit Tests for Real-Time Data Source Features
Tests all new real-time data source modules and functionality.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import threading
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class TestDatabaseConnector(unittest.TestCase):
    """Test DatabaseConnector functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from database_connector import DatabaseConnector
            self.db_connector = DatabaseConnector()
        except ImportError:
            self.skipTest("DatabaseConnector not available")
    
    def test_initialization(self):
        """Test DatabaseConnector initialization."""
        self.assertIsNotNone(self.db_connector)
        self.assertIsInstance(self.db_connector.connections, dict)
        self.assertIsInstance(self.db_connector.data_cache, dict)
    
    def test_sqlite_connection(self):
        """Test SQLite connection."""
        connection_params = {"database": ":memory:"}
        result = self.db_connector.connect("sqlite", connection_params)
        
        self.assertTrue(result['success'])
        self.assertIn('connection_id', result)
        
        # Test disconnection
        disconnect_result = self.db_connector.disconnect(result['connection_id'])
        self.assertTrue(disconnect_result['success'])
    
    def test_connection_status(self):
        """Test connection status."""
        connection_params = {"database": ":memory:"}
        result = self.db_connector.connect("sqlite", connection_params)
        
        if result['success']:
            status = self.db_connector.get_connection_status(result['connection_id'])
            self.assertTrue(status['success'])
            self.assertIn('status', status)
    
    def test_column_standardization(self):
        """Test column standardization."""
        test_df = pd.DataFrame({
            'id': [1, 2, 3],
            'created': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'message': ['test1', 'test2', 'test3']
        })
        
        standardized_df = self.db_connector._standardize_columns(test_df)
        
        self.assertIn('ticket_id', standardized_df.columns)
        self.assertIn('created_at', standardized_df.columns)
        self.assertIn('customer_message', standardized_df.columns)

class TestAPIManager(unittest.TestCase):
    """Test APIManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from api_manager import APIManager, APIConfig, APIType
            self.api_manager = APIManager()
            self.api_config = APIConfig(
                api_type=APIType.CUSTOM,
                base_url="https://httpbin.org",
                credentials={"username": "test", "password": "test"},
                headers={},
                refresh_interval=60
            )
        except ImportError:
            self.skipTest("APIManager not available")
    
    def test_initialization(self):
        """Test APIManager initialization."""
        self.assertIsNotNone(self.api_manager)
        self.assertIsInstance(self.api_manager.active_connections, dict)
        self.assertIsInstance(self.api_manager.data_cache, dict)
    
    def test_add_api_source(self):
        """Test adding API source."""
        result = self.api_manager.add_api_source("test_source", self.api_config)
        
        # Note: This might fail due to network requirements, but should not crash
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('message', result)
    
    def test_remove_api_source(self):
        """Test removing API source."""
        # First add a source
        self.api_manager.add_api_source("test_source", self.api_config)
        
        # Then remove it
        result = self.api_manager.remove_api_source("test_source")
        self.assertTrue(result['success'])
    
    def test_get_all_sources(self):
        """Test getting all sources."""
        result = self.api_manager.get_all_sources()
        self.assertTrue(result['success'])
        self.assertIn('sources', result)
        self.assertIn('count', result)

class TestWebSocketManager(unittest.TestCase):
    """Test WebSocketManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from websocket_manager import WebSocketManager, WebSocketConfig, WebSocketType
            self.ws_manager = WebSocketManager()
            self.ws_config = WebSocketConfig(
                ws_type=WebSocketType.CUSTOM,
                url="wss://echo.websocket.org",
                heartbeat_interval=30
            )
        except ImportError:
            self.skipTest("WebSocketManager not available")
    
    def test_initialization(self):
        """Test WebSocketManager initialization."""
        self.assertIsNotNone(self.ws_manager)
        self.assertIsInstance(self.ws_manager.connections, dict)
        self.assertIsInstance(self.ws_manager.subscribers, dict)
    
    def test_connect_websocket(self):
        """Test WebSocket connection."""
        result = self.ws_manager.connect("test_ws", self.ws_config)
        
        # Note: This might fail due to network requirements, but should not crash
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('message', result)
    
    def test_disconnect_websocket(self):
        """Test WebSocket disconnection."""
        # First connect
        self.ws_manager.connect("test_ws", self.ws_config)
        
        # Then disconnect
        result = self.ws_manager.disconnect("test_ws")
        self.assertTrue(result['success'])
    
    def test_subscribe_unsubscribe(self):
        """Test WebSocket subscription."""
        # Connect first
        self.ws_manager.connect("test_ws", self.ws_config)
        
        # Subscribe
        subscribe_result = self.ws_manager.subscribe("test_ws", lambda x, y: None)
        self.assertTrue(subscribe_result['success'])
        
        # Unsubscribe
        unsubscribe_result = self.ws_manager.unsubscribe("test_ws")
        self.assertTrue(unsubscribe_result['success'])
    
    def test_message_processing(self):
        """Test message processing."""
        # Test Slack message processing
        slack_message = {
            'type': 'message',
            'channel': 'C123456',
            'user': 'U123456',
            'text': 'Hello world',
            'ts': '1234567890.123456'
        }
        
        processed = self.ws_manager._process_slack_message(slack_message)
        self.assertIn('type', processed)
        self.assertIn('customer_message', processed)

class TestRealTimeManager(unittest.TestCase):
    """Test RealTimeDataManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from realtime_manager import RealTimeDataManager, DataSourceConfig, DataSourceType
            self.realtime_manager = RealTimeDataManager()
            self.source_config = DataSourceConfig(
                source_type=DataSourceType.DATABASE,
                source_id="test_source",
                config={"type": "sqlite", "params": {"database": ":memory:"}},
                refresh_interval=60
            )
        except ImportError:
            self.skipTest("RealTimeDataManager not available")
    
    def test_initialization(self):
        """Test RealTimeDataManager initialization."""
        self.assertIsNotNone(self.realtime_manager)
        self.assertIsInstance(self.realtime_manager.data_sources, dict)
        self.assertIsInstance(self.realtime_manager.data_cache, dict)
    
    def test_add_data_source(self):
        """Test adding data source."""
        result = self.realtime_manager.add_data_source(self.source_config)
        
        # Note: This might fail due to dependencies, but should not crash
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('message', result)
    
    def test_remove_data_source(self):
        """Test removing data source."""
        # First add a source
        self.realtime_manager.add_data_source(self.source_config)
        
        # Then remove it
        result = self.realtime_manager.remove_data_source("test_source")
        self.assertTrue(result['success'])
    
    def test_get_latest_data(self):
        """Test getting latest data."""
        result = self.realtime_manager.get_latest_data()
        self.assertTrue(result['success'])
        self.assertIn('data', result)
    
    def test_get_aggregated_data(self):
        """Test getting aggregated data."""
        result = self.realtime_manager.get_aggregated_data()
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('row_count', result)
    
    def test_get_manager_status(self):
        """Test getting manager status."""
        result = self.realtime_manager.get_manager_status()
        self.assertTrue(result['success'])
        self.assertIn('status', result)
        
        status = result['status']
        self.assertIn('running', status)
        self.assertIn('data_sources', status)
        self.assertIn('monitoring_active', status)

class TestIntegration(unittest.TestCase):
    """Test integration between modules."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from database_connector import db_connector
            from api_manager import api_manager
            from websocket_manager import ws_manager
            from realtime_manager import realtime_manager
            self.modules_available = True
        except ImportError:
            self.modules_available = False
    
    def test_module_imports(self):
        """Test that all modules can be imported."""
        if not self.modules_available:
            self.skipTest("Real-time modules not available")
        
        self.assertIsNotNone(db_connector)
        self.assertIsNotNone(api_manager)
        self.assertIsNotNone(ws_manager)
        self.assertIsNotNone(realtime_manager)
    
    def test_global_instances(self):
        """Test that global instances are properly initialized."""
        if not self.modules_available:
            self.skipTest("Real-time modules not available")
        
        # Test that global instances exist and have expected attributes
        self.assertTrue(hasattr(db_connector, 'connections'))
        self.assertTrue(hasattr(api_manager, 'active_connections'))
        self.assertTrue(hasattr(ws_manager, 'connections'))
        self.assertTrue(hasattr(realtime_manager, 'data_sources'))

class TestDataProcessing(unittest.TestCase):
    """Test data processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from data_processor import DataProcessor
            self.data_processor = DataProcessor()
        except ImportError:
            self.skipTest("DataProcessor not available")
    
    def test_initialization(self):
        """Test DataProcessor initialization."""
        self.assertIsNotNone(self.data_processor)
        self.assertIsInstance(self.data_processor.required_columns, list)
        self.assertIsInstance(self.data_processor.optional_columns, list)
    
    def test_response_time_calculation(self):
        """Test response time calculation."""
        # Create test data
        test_data = {
            'ticket_id': ['T001', 'T002', 'T003'],
            'created_at': [
                datetime.now() - timedelta(hours=2),
                datetime.now() - timedelta(hours=1),
                datetime.now() - timedelta(minutes=30)
            ],
            'responded_at': [
                datetime.now() - timedelta(hours=1),
                datetime.now() - timedelta(minutes=30),
                datetime.now() - timedelta(minutes=15)
            ],
            'customer_message': ['test1', 'test2', 'test3'],
            'team': ['Team A', 'Team B', 'Team A']
        }
        
        df = pd.DataFrame(test_data)
        result = self.data_processor.calculate_response_times(df)
        
        self.assertIn('response_time_minutes', result.columns)
        self.assertEqual(len(result), 3)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis."""
        # Create test data
        test_data = {
            'ticket_id': ['T001', 'T002', 'T003'],
            'customer_message': [
                'This is great!',
                'This is terrible!',
                'This is okay.'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = self.data_processor.analyze_sentiment(df)
        
        self.assertIn('combined_score', result.columns)
        self.assertIn('category', result.columns)
        self.assertEqual(len(result), 3)

def run_tests():
    """Run all tests and return results."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDatabaseConnector,
        TestAPIManager,
        TestWebSocketManager,
        TestRealTimeManager,
        TestIntegration,
        TestDataProcessing
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == "__main__":
    print("Running Real-Time Data Source Feature Tests")
    print("=" * 50)
    
    result = run_tests()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall Result: {'PASS' if success else 'FAIL'}")
    
    sys.exit(0 if success else 1)
