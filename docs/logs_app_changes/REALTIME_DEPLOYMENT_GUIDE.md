# Real-Time Features Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Customer Support Analytics App with real-time data source features in various environments.

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM (4GB+ recommended for production)
- **Storage**: 1GB free space for dependencies and data
- **Network**: Internet access for API connections and package installation

### Required Services

- **Database**: PostgreSQL, MySQL, or SQLite
- **Redis**: For caching (optional but recommended)
- **Web Server**: Nginx or Apache (for production)
- **Process Manager**: PM2, Supervisor, or systemd

## Installation Methods

### Method 1: Local Development Setup

#### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd m4_assignment_v2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt
```

#### Step 2: Install Additional Dependencies

```bash
# For database connectivity
pip install psycopg2-binary pymysql

# For Redis caching
pip install redis

# For WebSocket support
pip install websockets aiohttp

# For cloud storage
pip install boto3 google-cloud-storage azure-storage-blob
```

#### Step 3: Run the Application

```bash
# Start the application
streamlit run src/app.py --server.port 8501

# Or use the provided scripts
# Windows:
start_app.bat
# Linux/Mac:
./start_app.ps1
```

### Method 2: Docker Deployment

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install psycopg2-binary pymysql redis websockets aiohttp

# Copy application code
COPY src/ .
COPY sample_data/ ./sample_data/

# Expose port
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

#### Step 2: Create Docker Compose

```yaml
version: '3.8'

services:
  support-analytics:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=support_analytics
      - DB_USER=analytics_user
      - DB_PASSWORD=secure_password
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=support_analytics
      - POSTGRES_USER=analytics_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - support-analytics

volumes:
  postgres_data:
  redis_data:
```

#### Step 3: Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f support-analytics

# Scale the application
docker-compose up -d --scale support-analytics=3
```

### Method 3: Cloud Deployment

#### AWS Deployment

##### Step 1: EC2 Instance Setup

```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Instance type: t3.medium or larger

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git nginx -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y
```

##### Step 2: Application Setup

```bash
# Clone repository
git clone <repository-url>
cd m4_assignment_v2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt
pip install psycopg2-binary redis gunicorn

# Configure PostgreSQL
sudo -u postgres createdb support_analytics
sudo -u postgres createuser analytics_user
sudo -u postgres psql -c "ALTER USER analytics_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE support_analytics TO analytics_user;"
```

##### Step 3: Nginx Configuration

```nginx
# /etc/nginx/sites-available/support-analytics
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

##### Step 4: Systemd Service

```ini
# /etc/systemd/system/support-analytics.service
[Unit]
Description=Support Analytics App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/m4_assignment_v2
Environment=PATH=/home/ubuntu/m4_assignment_v2/venv/bin
ExecStart=/home/ubuntu/m4_assignment_v2/venv/bin/streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

##### Step 5: Start Services

```bash
# Enable and start services
sudo systemctl enable support-analytics
sudo systemctl start support-analytics
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status support-analytics
```

#### Google Cloud Platform Deployment

##### Step 1: App Engine Setup

```yaml
# app.yaml
runtime: python311

env_variables:
  DB_HOST: /cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
  DB_NAME: support_analytics
  DB_USER: analytics_user
  DB_PASSWORD: secure_password

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

handlers:
- url: /.*
  script: auto
```

##### Step 2: Deploy to App Engine

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize and deploy
gcloud init
gcloud app deploy
```

#### Azure Deployment

##### Step 1: Azure App Service Setup

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login and create resource group
az login
az group create --name support-analytics-rg --location eastus

# Create App Service plan
az appservice plan create --name support-analytics-plan --resource-group support-analytics-rg --sku B1

# Create web app
az webapp create --resource-group support-analytics-rg --plan support-analytics-plan --name support-analytics-app --runtime "PYTHON|3.11"
```

##### Step 2: Configure Environment Variables

```bash
# Set environment variables
az webapp config appsettings set --resource-group support-analytics-rg --name support-analytics-app --settings \
  DB_HOST="your-db-host" \
  DB_NAME="support_analytics" \
  DB_USER="analytics_user" \
  DB_PASSWORD="secure_password"
```

## Configuration

### Environment Variables

Create a `.env` file for local development:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=support_analytics
DB_USER=analytics_user
DB_PASSWORD=secure_password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Credentials
ZENDESK_EMAIL=user@company.com
ZENDESK_TOKEN=api_token
FRESHDESK_API_KEY=api_key
INTERCOM_TOKEN=access_token

# WebSocket Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
DISCORD_BOT_TOKEN=discord_bot_token

# Application Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

### Database Setup

#### PostgreSQL Setup

```sql
-- Create database and user
CREATE DATABASE support_analytics;
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE support_analytics TO analytics_user;

-- Create sample tables
\c support_analytics;

CREATE TABLE support_tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    customer_message TEXT,
    team VARCHAR(100),
    status VARCHAR(50),
    priority VARCHAR(20)
);

-- Insert sample data
INSERT INTO support_tickets (ticket_id, created_at, responded_at, customer_message, team, status, priority)
VALUES 
    ('T001', '2024-01-01 10:00:00', '2024-01-01 10:15:00', 'I need help with my account', 'Support Team A', 'resolved', 'medium'),
    ('T002', '2024-01-01 11:00:00', '2024-01-01 11:30:00', 'Thank you for the quick response!', 'Support Team B', 'resolved', 'low'),
    ('T003', '2024-01-01 12:00:00', '2024-01-01 12:45:00', 'I''m having issues with payments', 'Support Team A', 'open', 'high');
```

#### MySQL Setup

```sql
-- Create database and user
CREATE DATABASE support_analytics;
CREATE USER 'analytics_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON support_analytics.* TO 'analytics_user'@'localhost';
FLUSH PRIVILEGES;

-- Use the database
USE support_analytics;

-- Create sample tables
CREATE TABLE support_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP NULL,
    customer_message TEXT,
    team VARCHAR(100),
    status VARCHAR(50),
    priority VARCHAR(20)
);

-- Insert sample data
INSERT INTO support_tickets (ticket_id, created_at, responded_at, customer_message, team, status, priority)
VALUES 
    ('T001', '2024-01-01 10:00:00', '2024-01-01 10:15:00', 'I need help with my account', 'Support Team A', 'resolved', 'medium'),
    ('T002', '2024-01-01 11:00:00', '2024-01-01 11:30:00', 'Thank you for the quick response!', 'Support Team B', 'resolved', 'low'),
    ('T003', '2024-01-01 12:00:00', '2024-01-01 12:45:00', 'I''m having issues with payments', 'Support Team A', 'open', 'high');
```

### Redis Configuration

```bash
# Redis configuration file (/etc/redis/redis.conf)
# Enable persistence
save 900 1
save 300 10
save 60 10000

# Set memory limit
maxmemory 256mb
maxmemory-policy allkeys-lru

# Enable authentication (optional)
requirepass your_redis_password
```

## Monitoring and Logging

### Application Monitoring

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'support-analytics'
    static_configs:
      - targets: ['localhost:8501']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Support Analytics Dashboard",
    "panels": [
      {
        "title": "Response Time Trends",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(response_time_seconds)",
            "legendFormat": "Average Response Time"
          }
        ]
      },
      {
        "title": "Ticket Volume",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(tickets_total)",
            "legendFormat": "Total Tickets"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```python
# logging_config.py
import logging
import logging.handlers

def setup_logging():
    # Create logger
    logger = logging.getLogger('support_analytics')
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/support_analytics.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
```

## Security Considerations

### SSL/TLS Configuration

#### Nginx SSL Setup

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Authentication and Authorization

```python
# auth_config.py
import streamlit as st
import hashlib
import secrets

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False
    
    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True
    
    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False
```

## Performance Optimization

### Caching Strategy

```python
# cache_config.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    """Cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

### Database Connection Pooling

```python
# db_pool.py
import psycopg2
from psycopg2 import pool

class DatabasePool:
    def __init__(self, min_conn=1, max_conn=20):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            min_conn, max_conn,
            host='localhost',
            database='support_analytics',
            user='analytics_user',
            password='secure_password'
        )
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        self.connection_pool.putconn(conn)
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U analytics_user -d support_analytics

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

#### 2. Redis Connection Issues

```bash
# Check Redis status
sudo systemctl status redis

# Test Redis connection
redis-cli ping

# View Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

#### 3. Application Startup Issues

```bash
# Check application logs
sudo journalctl -u support-analytics -f

# Check port availability
sudo netstat -tlnp | grep 8501

# Test application manually
cd /path/to/app
source venv/bin/activate
streamlit run src/app.py --server.port 8501
```

### Performance Monitoring

```bash
# Monitor system resources
htop
iostat -x 1
free -h

# Monitor application performance
curl -s http://localhost:8501/health | jq

# Database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U analytics_user support_analytics > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U analytics_user support_analytics > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Application Backup

```bash
# Backup application code
tar -czf app_backup_$(date +%Y%m%d).tar.gz /path/to/app

# Backup configuration
cp -r /path/to/app/config /backups/config_$(date +%Y%m%d)
```

## Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  support-analytics:
    build: .
    ports:
      - "8501-8503:8501"
    environment:
      - DB_HOST=postgres
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3
```

### Load Balancing

```nginx
upstream support_analytics {
    server 127.0.0.1:8501;
    server 127.0.0.1:8502;
    server 127.0.0.1:8503;
}

server {
    listen 80;
    location / {
        proxy_pass http://support_analytics;
    }
}
```

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Customer Support Analytics App with real-time features in various environments. Choose the deployment method that best fits your infrastructure and requirements.

For additional support or questions, refer to the troubleshooting section or contact the development team.
