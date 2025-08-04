# Personal Financial Management System - Backend

Django REST Framework backend for Japanese individual business owners' financial management system.

## Features

- **User Management**: Custom user model with role-based access control
- **Business Data**: Income and expense tracking with Japanese tax compliance
- **OCR Processing**: Receipt and invoice processing using Claude API
- **Audit Logging**: Comprehensive audit trail for all operations
- **System Management**: Notifications, health monitoring, and configuration
- **Security**: JWT authentication, rate limiting, and security middleware
- **Blue Tax Return**: Support for Japanese 青色申告 (Blue Tax Return)

## Technology Stack

- **Framework**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: SQL Server 2019 with django-mssql-backend
- **Authentication**: JWT with refresh tokens
- **OCR**: Claude API integration for document processing
- **Cache**: Redis for session and cache storage
- **Task Queue**: Celery for background tasks
- **File Processing**: PIL for image processing, PyPDF2 for PDF handling

## Project Structure

```
backend/
├── financial_system/          # Django project settings
│   ├── settings.py           # Main settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
├── apps/                     # Django applications
│   ├── users/               # User management
│   ├── business/            # Income/expense management
│   ├── system/              # System management
│   ├── files/               # File processing
│   └── audit/               # Audit logging
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
├── Dockerfile              # Docker configuration
└── .env.example            # Environment variables template
```

## Installation

### Prerequisites

- Python 3.10+
- SQL Server 2019+
- Redis (for cache and Celery)
- ODBC Driver 17 for SQL Server

### Local Development Setup

1. **Clone and navigate to backend directory**
   ```bash
   cd Financial/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create database using SQL scripts in ../database/
   python manage.py migrate
   ```

6. **Create initial data**
   ```bash
   python manage.py setup_system --create-superuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Build Docker image**
   ```bash
   docker build -t financial-backend .
   ```

2. **Run with Docker Compose** (from project root)
   ```bash
   docker-compose up -d
   ```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=FinancialSystemDB
DB_USER=sa
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=1433

# OCR
CLAUDE_API_KEY=your-claude-api-key
CLAUDE_MODEL=claude-3-sonnet-20240229

# Cache/Queue
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Database Schema

The system uses the following main tables:

- **User Management**: `T_User`, `T_User_Detail`, `T_User_History`
- **Business Data**: `T_Dat_Incomes`, `T_Dat_Expenses`
- **Categories**: `T_Master_Income_Categories`, `T_Master_Expense_Categories`
- **System**: `T_Notification`, `T_Audit_Log`

## API Documentation

### Authentication

```bash
# Login
POST /api/v1/auth/login/
{
  "username": "your_username",
  "password": "your_password"
}

# Refresh token
POST /api/v1/auth/refresh/
{
  "refresh": "your_refresh_token"
}
```

### Business Operations

```bash
# Income management
GET    /api/v1/business/incomes/
POST   /api/v1/business/incomes/
GET    /api/v1/business/incomes/{id}/
PUT    /api/v1/business/incomes/{id}/
DELETE /api/v1/business/incomes/{id}/

# Expense management
GET    /api/v1/business/expenses/
POST   /api/v1/business/expenses/
GET    /api/v1/business/expenses/{id}/
PUT    /api/v1/business/expenses/{id}/
DELETE /api/v1/business/expenses/{id}/

# Categories
GET    /api/v1/business/income-categories/
GET    /api/v1/business/expense-categories/

# Financial summary
GET    /api/v1/business/summary/
```

### File Processing

```bash
# Upload and process receipt
POST /api/v1/files/upload/
POST /api/v1/files/ocr/process/
```

## Management Commands

### System Setup
```bash
# Initialize system with default data
python manage.py setup_system --create-superuser

# Create superuser only
python manage.py setup_system --create-superuser --username admin --email admin@example.com
```

### Database Operations
```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Load initial data
python manage.py loaddata initial_data.json
```

### Maintenance
```bash
# Collect static files
python manage.py collectstatic

# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Check system health
curl http://localhost:8000/health/
```

## Security Features

- **JWT Authentication** with refresh token rotation
- **Role-based Access Control** (Super Admin, Admin, User)
- **Audit Logging** for all operations
- **Rate Limiting** to prevent abuse
- **Input Validation** and sanitization
- **CORS Configuration** for frontend integration
- **Security Headers** via middleware

## Japanese Tax Compliance

- **Blue Tax Return (青色申告)** support
- **Consumption Tax (消費税)** calculation
- **Business Expense Categories** aligned with Japanese tax law
- **Deduction Calculations** for individual business owners
- **Tax Year Management** (January-December)

## OCR Processing

The system uses Claude API for intelligent document processing:

- **Receipt Processing**: Extracts vendor, amount, date, items
- **Invoice Processing**: Extracts client, invoice number, due date
- **Confidence Scoring**: Provides accuracy estimates
- **Data Validation**: Ensures extracted data quality
- **Japanese Language Support**: Optimized for Japanese documents

## Monitoring and Health Checks

- **Health Check Endpoint**: `/health/`
- **System Health Monitoring**: Database, cache, storage status
- **Audit Log Analysis**: Security and usage monitoring
- **Performance Metrics**: Response times and error rates

## Development

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Run flake8 for linting

### Testing
```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Adding New Features

1. Create models in appropriate app
2. Create serializers for API
3. Implement views/viewsets
4. Add URL patterns
5. Write tests
6. Update documentation

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up SSL/HTTPS
- [ ] Configure database backups
- [ ] Set up log rotation
- [ ] Configure monitoring
- [ ] Test OCR functionality
- [ ] Verify security settings

### Docker Deployment

```bash
# Build production image
docker build -t financial-backend:latest .

# Run with environment file
docker run --env-file .env -p 8000:8000 financial-backend:latest
```

## Troubleshooting

### Common Issues

1. **Database Connection**: Check SQL Server connection and credentials
2. **OCR Not Working**: Verify Claude API key and model settings
3. **File Upload Issues**: Check media directory permissions
4. **Cache Issues**: Verify Redis connection
5. **Migration Errors**: Check database schema and permissions

### Logs

- **Application Logs**: `/app/logs/django.log`
- **Audit Logs**: `/app/logs/audit.log`
- **Error Logs**: Check Django error logging configuration

## Support

For technical support or questions:

1. Check the logs for error details
2. Verify configuration settings
3. Test with minimal data set
4. Contact system administrator

## License

This project is proprietary software for Japanese individual business owners' financial management.