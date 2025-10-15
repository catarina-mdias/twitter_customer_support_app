# Configuration Files

This directory contains configuration files for the Support Analytics App with real-time features.

## Files Overview

### Environment Configurations
- **`development.json`** - Development environment configuration
- **`production.json`** - Production environment configuration
- **`env.example`** - Example environment variables file

### Docker Configuration
- **`docker-compose.yml`** - Docker Compose configuration for full stack deployment
- **`nginx.conf`** - Nginx reverse proxy configuration
- **`prometheus.yml`** - Prometheus monitoring configuration
- **`redis.conf`** - Redis cache configuration

### Database Configuration
- **`init.sql`** - PostgreSQL database initialization script

### Utilities
- **`config_loader.py`** - Configuration loader utility

## Quick Start

### 1. Environment Setup

Copy the example environment file and update with your values:

```bash
cp config/env.example .env
# Edit .env with your actual values
```

### 2. Development Setup

For development, the default configuration will work out of the box:

```bash
# Start the application
streamlit run src/app.py
```

### 3. Production Setup

For production deployment:

```bash
# Set environment variables
export ENVIRONMENT=production
export DB_PASSWORD=your_secure_password
export REDIS_PASSWORD=your_redis_password
# ... other environment variables

# Start with Docker Compose
docker-compose -f config/docker-compose.yml up -d
```

## Configuration Details

### Database Configuration

The app supports multiple database types:

- **SQLite** (development): File-based database
- **PostgreSQL** (production): Full-featured relational database
- **MySQL** (production): Popular open-source database

### API Integrations

Supported APIs:
- **Zendesk**: Customer service platform
- **Freshdesk**: Help desk software
- **Intercom**: Customer messaging platform
- **Slack**: Team communication platform
- **Custom APIs**: Any REST API endpoint

### WebSocket Streaming

Supported WebSocket types:
- **Slack RTM**: Real-time messaging from Slack
- **Discord Gateway**: Live Discord server data
- **Zendesk Events**: Real-time ticket updates
- **Custom WebSockets**: Any WebSocket endpoint

### Cloud Storage

Supported cloud storage providers:
- **AWS S3**: Amazon Web Services
- **Google Cloud Storage**: Google Cloud Platform
- **Azure Blob Storage**: Microsoft Azure

### Monitoring and Alerting

The configuration includes:
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization
- **Email alerts**: SMTP configuration
- **Slack notifications**: Webhook integration
- **PagerDuty**: Incident management

## Security Considerations

### Production Security

For production deployments:

1. **Use environment variables** for sensitive data
2. **Enable SSL/TLS** for all connections
3. **Set strong passwords** for databases and services
4. **Configure firewall rules** to restrict access
5. **Enable authentication** and authorization
6. **Use encryption** for data at rest and in transit

### Environment Variables

Key environment variables to set:

```bash
# Database
DB_HOST=your-db-host
DB_PASSWORD=your-secure-password

# Redis
REDIS_PASSWORD=your-redis-password

# API Credentials
ZENDESK_TOKEN=your-zendesk-token
SLACK_BOT_TOKEN=your-slack-token

# Security
ENCRYPTION_KEY_FILE=/path/to/encryption.key
```

## Customization

### Adding New APIs

To add a new API integration:

1. Add configuration to `development.json` and `production.json`
2. Update the API manager in `src/api_manager.py`
3. Add environment variables to `env.example`
4. Test the integration

### Adding New WebSockets

To add a new WebSocket integration:

1. Add configuration to the `websockets` section
2. Update the WebSocket manager in `src/websocket_manager.py`
3. Add environment variables to `env.example`
4. Test the integration

### Custom Monitoring

To customize monitoring:

1. Update `prometheus.yml` with new scrape targets
2. Modify alert rules in `alert_rules.yml`
3. Update Grafana dashboards
4. Configure notification channels

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials
   - Verify network connectivity
   - Ensure database is running

2. **API Authentication Errors**
   - Verify API tokens and credentials
   - Check API endpoint URLs
   - Review rate limiting settings

3. **WebSocket Connection Issues**
   - Check authentication tokens
   - Verify WebSocket URLs
   - Review firewall settings

4. **Configuration Loading Errors**
   - Verify JSON syntax in config files
   - Check file permissions
   - Review environment variable names

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
```

### Health Checks

Check service health:

```bash
# Application health
curl http://localhost:8501/health

# Database health
pg_isready -h localhost -p 5432

# Redis health
redis-cli ping
```

## Support

For configuration issues:

1. Check the logs in `/var/log/support-analytics/`
2. Review the troubleshooting section
3. Contact the development team
4. Check the main README.md for additional help
