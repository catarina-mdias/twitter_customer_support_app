# Real-Time Data Sources Implementation Guide

## Overview

This document provides a comprehensive guide to the real-time data source features implemented in the Customer Support Analytics App. These features enable live data access, monitoring, and analysis from multiple data sources.

## Features Implemented

### 1. Database Connector (`src/database_connector.py`)

**Purpose**: Connects to various database systems for real-time data access.

**Supported Databases**:
- SQLite (in-memory and file-based)
- PostgreSQL
- MySQL

**Key Features**:
- Connection management with automatic reconnection
- Live monitoring with configurable refresh intervals
- Data standardization and column mapping
- Query execution with parameter support
- Connection status monitoring

**Usage Example**:
```python
from database_connector import db_connector

# Connect to SQLite database
result = db_connector.connect("sqlite", {"database": ":memory:"})
if result['success']:
    connection_id = result['connection_id']
    
    # Get support data
    data_result = db_connector.get_support_data(connection_id, "support_tickets")
    
    # Start live monitoring
    db_connector.start_live_monitoring(connection_id, "support_tickets", 30)
```

### 2. API Manager (`src/api_manager.py`)

**Purpose**: Manages connections to various API endpoints for real-time data fetching.

**Supported APIs**:
- Zendesk
- Freshdesk
- Intercom
- Slack
- Discord
- Custom APIs

**Key Features**:
- Rate limiting and request throttling
- Automatic retry mechanisms
- Data standardization across different APIs
- Real-time data fetching with callbacks
- Connection status monitoring

**Usage Example**:
```python
from api_manager import api_manager, APIConfig, APIType

# Configure Zendesk API
api_config = APIConfig(
    api_type=APIType.ZENDESK,
    base_url="https://yourcompany.zendesk.com",
    credentials={"email": "user@company.com", "token": "api_token"},
    headers={},
    refresh_interval=60
)

# Add API source
result = api_manager.add_api_source("zendesk_source", api_config)

# Fetch real-time data
data_result = api_manager.get_real_time_data("zendesk_source")
```

### 3. WebSocket Manager (`src/websocket_manager.py`)

**Purpose**: Handles WebSocket connections for real-time streaming data.

**Supported WebSocket Types**:
- Slack RTM (Real-Time Messaging)
- Discord Gateway
- Zendesk Events
- Freshdesk Events
- Custom WebSockets

**Key Features**:
- Automatic reconnection with exponential backoff
- Heartbeat/ping-pong mechanism
- Message processing and standardization
- Subscription management
- Connection status monitoring

**Usage Example**:
```python
from websocket_manager import ws_manager, WebSocketConfig, WebSocketType

# Configure Slack RTM WebSocket
ws_config = WebSocketConfig(
    ws_type=WebSocketType.SLACK_RTM,
    url="wss://slack.com/rtm",
    auth_token="xoxb-your-bot-token",
    heartbeat_interval=30
)

# Connect and subscribe
result = ws_manager.connect("slack_ws", ws_config)
ws_manager.subscribe("slack_ws", callback_function)

# Get latest messages
messages = ws_manager.get_latest_messages("slack_ws", limit=100)
```

### 4. Real-Time Data Manager (`src/realtime_manager.py`)

**Purpose**: Coordinates multiple data sources and provides unified real-time data access.

**Key Features**:
- Multi-source data aggregation
- Real-time monitoring coordination
- Alert system with configurable thresholds
- Data caching and deduplication
- Performance monitoring

**Usage Example**:
```python
from realtime_manager import realtime_manager, DataSourceConfig, DataSourceType

# Add database source
db_config = DataSourceConfig(
    source_type=DataSourceType.DATABASE,
    source_id="main_db",
    config={"type": "sqlite", "params": {"database": ":memory:"}},
    refresh_interval=30
)
realtime_manager.add_data_source(db_config)

# Start monitoring
realtime_manager.start_monitoring()

# Get aggregated data
data_result = realtime_manager.get_aggregated_data()
```

## Application Integration

### New Data Source Options

The main application (`src/app.py`) now includes the following data source options:

1. **📁 CSV Upload** - Traditional file upload (existing)
2. **🐦 Twitter Account** - Twitter API integration (existing)
3. **🔍 Twitter Search** - Twitter search functionality (existing)
4. **🗄️ Database Connection** - Connect to databases (NEW)
5. **🌐 API Endpoint** - Connect to APIs (NEW)
6. **📡 WebSocket Stream** - Real-time streaming (NEW)
7. **☁️ Cloud Storage** - Cloud file monitoring (NEW)
8. **🔄 Real-Time Mode** - Unified real-time management (NEW)

### Real-Time Dashboard Features

The dashboard now includes:

- **Live Status Indicators**: Shows connection status, last update time, and active data sources
- **Real-Time Alerts**: Displays warnings, errors, and notifications
- **Auto-Refresh Controls**: Configurable refresh intervals
- **Data Source Management**: Add/remove data sources dynamically

## Configuration

### Environment Variables

Set the following environment variables for production deployment:

```bash
# Database connections
DB_HOST=localhost
DB_PORT=5432
DB_NAME=support_analytics
DB_USER=analytics_user
DB_PASSWORD=secure_password

# API credentials
ZENDESK_EMAIL=user@company.com
ZENDESK_TOKEN=api_token
FRESHDESK_API_KEY=api_key
INTERCOM_TOKEN=access_token

# WebSocket configurations
SLACK_BOT_TOKEN=xoxb-your-bot-token
DISCORD_BOT_TOKEN=discord_bot_token

# Redis for caching (optional)
REDIS_URL=redis://localhost:6379/0
```

### Configuration Files

Create configuration files for different environments:

**`config/development.json`**:
```json
{
  "database": {
    "type": "sqlite",
    "params": {"database": "dev_support.db"}
  },
  "apis": {
    "zendesk": {
      "base_url": "https://devcompany.zendesk.com",
      "credentials": {
        "email": "dev@company.com",
        "token": "dev_token"
      }
    }
  },
  "websockets": {
    "slack": {
      "url": "wss://slack.com/rtm",
      "auth_token": "dev_slack_token"
    }
  },
  "monitoring": {
    "refresh_interval": 30,
    "alert_thresholds": {
      "response_time_high": 60,
      "sla_breach_rate": 0.1,
      "sentiment_low": -0.2
    }
  }
}
```

## Dependencies

### Core Dependencies

The following packages are required for real-time features:

```txt
# Real-time data source dependencies
requests>=2.31.0
aiohttp>=3.8.0
websockets>=11.0.0
asyncio-mqtt>=0.13.0
redis>=4.5.0

# Database connectors
psycopg2-binary>=2.9.0
pymysql>=1.1.0

# Additional API support
slack-sdk>=3.21.0
discord.py>=2.3.0
python-telegram-bot>=20.0

# Cloud storage
boto3>=1.28.0
google-cloud-storage>=2.10.0
azure-storage-blob>=12.17.0

# Monitoring and alerting
prometheus-client>=0.17.0
grafana-api>=1.0.3
```

### Installation

Install dependencies using pip:

```bash
pip install -r src/requirements.txt
```

For production deployment with all features:

```bash
pip install -r src/requirements.txt
pip install psycopg2-binary pymysql redis
```

## Usage Examples

### 1. Database Integration

```python
# Connect to PostgreSQL database
connection_params = {
    "host": "localhost",
    "port": 5432,
    "database": "support_tickets",
    "user": "analytics_user",
    "password": "secure_password"
}

result = db_connector.connect("postgresql", connection_params)
if result['success']:
    # Load data
    data_result = db_connector.get_support_data(
        result['connection_id'], 
        "tickets", 
        limit=1000
    )
    
    # Start live monitoring
    db_connector.start_live_monitoring(
        result['connection_id'], 
        "tickets", 
        refresh_interval=60
    )
```

### 2. API Integration

```python
# Zendesk API integration
zendesk_config = APIConfig(
    api_type=APIType.ZENDESK,
    base_url="https://company.zendesk.com",
    credentials={
        "email": "analytics@company.com",
        "token": "zendesk_api_token"
    },
    headers={},
    refresh_interval=120
)

api_manager.add_api_source("zendesk", zendesk_config)
api_manager.start_auto_refresh("zendesk", interval=120)

# Fetch tickets
tickets = api_manager.get_real_time_data("zendesk")
```

### 3. WebSocket Integration

```python
# Slack RTM integration
slack_config = WebSocketConfig(
    ws_type=WebSocketType.SLACK_RTM,
    url="wss://slack.com/rtm",
    auth_token="xoxb-slack-bot-token",
    heartbeat_interval=30
)

def message_callback(connection_id, data):
    print(f"New message from {connection_id}: {data}")

ws_manager.connect("slack", slack_config)
ws_manager.subscribe("slack", message_callback)
```

### 4. Multi-Source Real-Time Monitoring

```python
# Add multiple data sources
sources = [
    DataSourceConfig(
        source_type=DataSourceType.DATABASE,
        source_id="main_db",
        config={"type": "postgresql", "params": db_params},
        refresh_interval=60
    ),
    DataSourceConfig(
        source_type=DataSourceType.API,
        source_id="zendesk_api",
        config=zendesk_config,
        refresh_interval=120
    ),
    DataSourceConfig(
        source_type=DataSourceType.WEBSOCKET,
        source_id="slack_ws",
        config=slack_config,
        refresh_interval=30
    )
]

# Add all sources
for source in sources:
    realtime_manager.add_data_source(source)

# Start unified monitoring
realtime_manager.start_monitoring()

# Get aggregated data from all sources
aggregated_data = realtime_manager.get_aggregated_data()
```

## Performance Considerations

### 1. Caching Strategy

- **Redis Integration**: Use Redis for distributed caching
- **Memory Management**: Implement cache size limits
- **TTL Configuration**: Set appropriate time-to-live values

### 2. Rate Limiting

- **API Rate Limits**: Respect external API rate limits
- **Request Throttling**: Implement internal throttling
- **Backoff Strategies**: Use exponential backoff for retries

### 3. Monitoring

- **Connection Health**: Monitor connection status
- **Performance Metrics**: Track response times and throughput
- **Error Handling**: Implement comprehensive error handling

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check connection parameters
   - Verify network connectivity
   - Ensure database permissions

2. **API Authentication Errors**
   - Verify API credentials
   - Check token expiration
   - Validate API endpoints

3. **WebSocket Connection Issues**
   - Check SSL/TLS configuration
   - Verify authentication tokens
   - Monitor network connectivity

4. **Performance Issues**
   - Adjust refresh intervals
   - Implement caching
   - Monitor resource usage

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

Implement health check endpoints:

```python
def health_check():
    status = {
        "database": db_connector.get_all_connections(),
        "apis": api_manager.get_all_sources(),
        "websockets": ws_manager.get_all_connections(),
        "realtime": realtime_manager.get_manager_status()
    }
    return status
```

## Security Considerations

### 1. Credential Management

- Use environment variables for sensitive data
- Implement credential rotation
- Use secure storage solutions

### 2. Network Security

- Use HTTPS/WSS for all connections
- Implement proper SSL/TLS configuration
- Use VPN or private networks when possible

### 3. Access Control

- Implement proper authentication
- Use role-based access control
- Monitor access patterns

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Anomaly detection algorithms
   - Predictive analytics
   - Automated insights

2. **Advanced Monitoring**
   - Grafana dashboards
   - Prometheus metrics
   - Custom alerting rules

3. **Cloud Integration**
   - AWS Kinesis integration
   - Google Cloud Pub/Sub
   - Azure Event Hubs

4. **Mobile Support**
   - Mobile app integration
   - Push notifications
   - Offline capabilities

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the test suite (`test_realtime_features.py`)
3. Check application logs
4. Contact the development team

## Conclusion

The real-time data source implementation provides a robust foundation for live customer support analytics. With support for multiple data sources, comprehensive monitoring, and flexible configuration, it enables organizations to gain real-time insights into their support operations.

The modular design allows for easy extension and customization, while the comprehensive error handling and monitoring ensure reliable operation in production environments.
