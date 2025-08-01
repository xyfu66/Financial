# Personal Financial Management System (個人財務管理システム)

A comprehensive financial management system designed for Japanese individual business owners with OCR capabilities, automatic calculations, and PDF reporting.

## System Overview

This system provides:
- Income and expense registration
- Automatic calculations for specified date ranges
- OCR processing for bills and invoices using Claude API
- PDF report generation for financial status
- Multi-user support with role-based access control
- Comprehensive audit logging

## Technology Stack

### Frontend
- Vue.js 3.5.18
- Element Plus UI Framework
- Pinia State Management
- Vue Router 4
- Vue I18n (Japanese/English)

### Backend
- Python 3.10
- FastAPI RESTful API
- JWT Authentication with Refresh Tokens
- SQL Server 2019 with pyodbc
- Claude API Integration for OCR

### Security & Features
- Role-based Access Control (RBAC)
- Comprehensive audit logging
- Data encryption at rest and in transit
- Rate limiting and security headers
- CSV/PDF/IMG import with OCR processing
- Multi-language support

## Project Structure

```
Financial/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Security, config, database
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   ├── requirements.txt    # Python dependencies
│   ├── main.py            # Application entry point
│   └── .env.example       # Environment configuration template
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page components
│   │   ├── stores/         # Pinia stores
│   │   ├── router/         # Vue Router configuration
│   │   ├── services/       # API services
│   │   └── locales/        # Internationalization
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Build configuration
├── database/               # SQL Server database scripts
│   ├── create_database.sql
│   ├── create_business_tables.sql
│   └── initial_data.sql
├── docs/                   # Documentation
├── SETUP.md               # Detailed setup instructions
└── README.md              # This file
```

## Quick Start

### Prerequisites
- **Node.js** >= 18.0.0
- **Python** >= 3.10
- **SQL Server 2019** (Express Edition supported)
- **Git**

### 1. Database Setup
1. Install SQL Server 2019 and SQL Server Management Studio (SSMS)
2. Create database using scripts in `/database` directory:
   ```sql
   -- Execute in order:
   -- 1. create_database.sql
   -- 2. create_business_tables.sql  
   -- 3. initial_data.sql
   ```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database connection details

# Run application
python main.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

## Business Modules

- **Income Management**: Record and categorize income sources
- **Expense Management**: Track and categorize expenses with tax deduction support
- **Financial Calculations**: Automatic calculations for specified periods
- **User Management**: Multi-role user system (Super Admin, Admin, User)
- **Notification System**: System announcements and alerts
- **Audit Logging**: Complete activity tracking
- **File Processing**: CSV/PDF/Image import with OCR capabilities
- **Report Generation**: PDF financial reports for tax purposes

## Key Features

### Japanese Tax Compliance
- Pre-configured income and expense categories for Japanese tax law
- Support for 青色申告 (Blue Form Tax Return)
- Automatic tax deduction calculations
- Business expense categorization

### OCR Integration
- Claude API integration for receipt and invoice processing
- Automatic data extraction from images
- Manual verification and editing of OCR results
- Support for Japanese text recognition

### Security
- JWT-based authentication with refresh tokens
- Role-based access control
- Comprehensive audit logging
- Rate limiting and security headers
- Input validation and sanitization

### Multi-language Support
- Japanese (primary)
- English (secondary)
- Easy to extend for additional languages

## Production Deployment

### Windows Server Deployment
1. Install Python 3.10, Node.js 18+, and SQL Server 2019
2. Clone repository to server (e.g., `C:\inetpub\FinancialSystem\`)
3. Set up backend as Windows Service using NSSM
4. Configure IIS for frontend static files
5. Set up HTTPS with SSL certificates

### Linux Server Deployment
1. Install Python 3.10, Node.js 18+, and SQL Server for Linux
2. Use systemd for backend service management
3. Configure Nginx as reverse proxy
4. Set up SSL certificates with Let's Encrypt

Detailed deployment instructions are available in [SETUP.md](SETUP.md).

## Development

### Backend Development
- FastAPI with automatic API documentation
- SQLAlchemy ORM with SQL Server
- Comprehensive error handling and logging
- Modular architecture for easy extension

### Frontend Development
- Vue 3 Composition API
- Element Plus for consistent UI
- Pinia for state management
- TypeScript support
- Hot reload development server

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Configuration

### Environment Variables
Key configuration options in `.env`:
- Database connection settings
- JWT secret keys
- Claude API credentials
- File upload limits
- CORS settings

### Customization
- Add new income/expense categories in database
- Extend user roles and permissions
- Customize PDF report templates
- Add new languages in frontend

## License

MIT License - See LICENSE file for details

## Support

For technical support or questions:
1. Check the [SETUP.md](SETUP.md) for detailed instructions
2. Review the API documentation at `/api/docs`
3. Check application logs for error details

---

**Important**: This system is designed for personal financial management. For tax filing and other critical financial purposes, please consult with qualified tax professionals.