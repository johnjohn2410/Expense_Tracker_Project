# Expense Tracker - Production Grade Django Application

A comprehensive, production-ready expense tracking application built with Django, featuring advanced financial management capabilities, secure API endpoints, and enterprise-grade infrastructure.

## Features

### Core Functionality
- **Expense & Income Tracking**: Comprehensive transaction management with categorization
- **Budget Management**: Multi-period budgets with rollover support and alerts
- **Account Management**: Multiple financial accounts (checking, savings, credit cards, etc.)
- **Auto-categorization**: Smart rules engine for automatic transaction categorization
- **Import/Export**: CSV, OFX/QFX import with deduplication and bulk operations
- **Receipt Management**: File attachments with OCR support
- **Recurring Transactions**: Automated recurring expense/income management

### Production Features
- **RESTful API**: Complete Django REST Framework API with OpenAPI documentation
- **Security**: HTTPS enforcement, HSTS, CSP, rate limiting, and 2FA support
- **Background Processing**: Celery + Redis for async tasks and scheduled operations
- **Monitoring**: Sentry integration, structured logging, and health checks
- **Scalability**: PostgreSQL database, Redis caching, and S3-compatible storage
- **CI/CD**: GitHub Actions pipeline with automated testing and deployment

## Screenshots

*Visual showcase of the application's modern interface and functionality.*

### Dashboard Overview
![Dashboard Overview](screenshots/dashboard.png)
*The main dashboard displays a personalized welcome message, key financial statistics in modern cards, and a budget progress bar showing spending against monthly limits. Features a clean, professional design with the signature black and blue color scheme.*

### Dashboard Analytics
![Dashboard Analytics](screenshots/lower-dashboard.png)
*The lower dashboard section showcases interactive Chart.js visualizations including pie charts for expense categories, monthly spending trends, and income vs. expense comparisons. Provides comprehensive financial insights at a glance.*

### User Authentication
![Login Page](screenshots/login.png)
*Modern login interface featuring floating label forms, animated background with expense tracking themes, and the signature black and blue color scheme. Includes smooth transitions and professional styling.*

![Signup Page](screenshots/signup.png)
*Registration page with animated background video/GIF, floating label forms, and modern UI elements. The design maintains consistency with the overall application theme while providing an engaging user experience.*

### Financial Management
![Add Expense](screenshots/add-expense.png)
*Expense entry form with Bootstrap 5 floating labels, comprehensive field validation, and intuitive layout. Includes fields for amount, currency, description, category, account, date, merchant, and optional notes.*

![Add Income](screenshots/add-income.png)
*Income tracking form mirroring the expense form design for consistency. Features the same modern UI elements and validation patterns to ensure a unified user experience.*

![Budget Management](screenshots/budget.png)
*Budget configuration interface allowing users to set spending limits, define periods, select categories, and assign multiple accounts. Features a responsive grid layout and multi-select functionality for comprehensive budget planning.*

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │   Background    │
│   (Django       │◄──►│   (DRF +        │◄──►│   Tasks         │
│   Templates)    │    │   Allauth)      │    │   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   + Queue       │
                       └─────────────────┘
```

## Technology Stack

- **Backend**: Django 5.1 + Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache/Queue**: Redis
- **Background Tasks**: Celery + Celery Beat
- **Authentication**: Django Allauth with email verification
- **Security**: Django Axes, CSP, HSTS
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)
- **Monitoring**: Sentry SDK
- **File Storage**: S3-compatible storage (DigitalOcean Spaces, Backblaze)
- **Email**: Brevo (free tier - 300 emails/day)
- **Containerization**: Docker + Docker Compose

## Prerequisites

### For Simple Local Development
- Python 3.11+
- Git

### For Full Production Setup
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## Quick Start

### Option 1: Simple Local Development (Recommended for First Time)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Expense_Tracker_Project
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Create logs directory**
   ```bash
   mkdir -p logs
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Web App: http://127.0.0.1:8000
   - Login: http://127.0.0.1:8000/login/
   - Signup: http://127.0.0.1:8000/signup/

**Note**: The application automatically uses simplified settings (`settings-simple`) for local development, which includes SQLite database and disabled production features for easier setup.

### Option 2: Docker Compose (Production-like Environment)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Expense_Tracker_Project
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   docker compose up -d
   ```

4. **Run migrations**
   ```bash
   docker compose exec web python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. **Access the application**
   - Web App: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs/
   - Admin: http://localhost:8000/admin/

### Option 3: Full Production Setup

1. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install all dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   ```bash
   # Create database and user
   createdb expense_tracker
   createuser expense_user
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Update DATABASE_URL and other settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start Redis**
   ```bash
   redis-server
   ```

7. **Start Celery worker**
   ```bash
   celery -A Expense_Tracker_Project worker --loglevel=info
   ```

8. **Start Celery beat**
   ```bash
   celery -A Expense_Tracker_Project beat --loglevel=info
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Django Core
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgres://user:password@localhost:5432/expense_tracker

# Email (Brevo - Free tier)
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_HOST_USER=your-brevo-username
EMAIL_HOST_PASSWORD=your-brevo-api-key

# Redis
REDIS_URL=redis://localhost:6379/0

# File Storage (DigitalOcean Spaces)
AWS_ACCESS_KEY_ID=your-spaces-access-key
AWS_SECRET_ACCESS_KEY=your-spaces-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com

# Sentry (Free tier)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Security Settings

The application includes comprehensive security features:

- **HTTPS Enforcement**: Automatic redirect to HTTPS in production
- **HSTS**: HTTP Strict Transport Security headers
- **CSP**: Content Security Policy for XSS protection
- **Rate Limiting**: Login throttling and API rate limits
- **Password Policy**: Strong password requirements (12+ characters)
- **CSRF Protection**: Cross-site request forgery protection
- **Secure Cookies**: HttpOnly and Secure flags

## API Documentation

### Available Endpoints

- **Authentication**: `/api/auth/`
- **Categories**: `/api/categories/`
- **Accounts**: `/api/accounts/`
- **Transactions**: `/api/transactions/`
- **Budgets**: `/api/budgets/`
- **Rules**: `/api/rules/`
- **Attachments**: `/api/attachments/`
- **Imports**: `/api/imports/`
- **Dashboard**: `/api/dashboard/overview/`

### API Documentation

- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

### Example API Usage

```bash
# Get user's transactions
curl -H "Authorization: Token your-token" \
     http://localhost:8000/api/transactions/

# Create new expense
curl -X POST \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{"amount": "25.50", "description": "Lunch", "date": "2024-01-15"}' \
     http://localhost:8000/api/transactions/
```

## Background Tasks

The application uses Celery for background processing:

- **Import Processing**: CSV/OFX file imports
- **Budget Alerts**: Automated budget notifications
- **Weekly Reports**: Scheduled financial reports
- **Data Cleanup**: Automated maintenance tasks
- **Recurring Transactions**: Automated transaction creation

### Monitoring Celery

```bash
# Check worker status
celery -A Expense_Tracker_Project status

# Monitor tasks
celery -A Expense_Tracker_Project monitor

# Check scheduled tasks
celery -A Expense_Tracker_Project beat --loglevel=info
```

## Testing

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tracker/tests.py

# Run tests in Docker
docker-compose exec web python -m pytest
```

### Test Coverage

The application maintains >85% test coverage on core functionality:

- Model validation and business logic
- API endpoints and serializers
- Background tasks and services
- Security middleware and permissions

## Deployment

### Production Deployment Options

1. **Vercel (Frontend) + Supabase (Backend)**
   - Free tier available
   - Automatic deployments from GitHub
   - Built-in CDN and edge functions

2. **DigitalOcean App Platform**
   - Managed containers and databases
   - Automatic scaling and SSL
   - Integrated monitoring

3. **Railway**
   - Simple container deployment
   - PostgreSQL and Redis included
   - Automatic deployments

4. **Self-hosted**
   - Docker containers on VPS
   - Nginx reverse proxy
   - Let's Encrypt SSL certificates

### Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Configure production database
- [ ] Set up SSL certificates
- [ ] Configure email backend
- [ ] Set up monitoring (Sentry)
- [ ] Configure file storage
- [ ] Set up backups
- [ ] Configure logging
- [ ] Set up health checks

## Monitoring & Observability

### Health Checks

- **Application Health**: `/api/health/`
- **Database Connectivity**: Automatic database checks
- **Redis Connectivity**: Cache and queue monitoring
- **Background Tasks**: Celery worker status

### Logging

Structured JSON logging for production:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("User action", extra={
    "user_id": user.id,
    "action": "transaction_created",
    "amount": transaction.amount
})
```

### Error Tracking

Sentry integration for production error monitoring:

- Automatic error capture
- Performance monitoring
- Release tracking
- User feedback collection

## Security Features

### Authentication & Authorization

- **Email-based authentication** with verification
- **Two-factor authentication** support (TOTP)
- **Session management** with secure cookies
- **API token authentication** for mobile apps
- **Role-based access control** for admin features

### Data Protection

- **PII minimization** - only essential data stored
- **Encrypted storage** for sensitive information
- **Audit logging** for all user actions
- **Data export/import** with user control
- **Automatic data cleanup** for old records

## Mobile & API Support

### RESTful API

- **Standard HTTP methods** (GET, POST, PUT, DELETE)
- **JSON responses** with consistent formatting
- **Pagination** for large datasets
- **Filtering and sorting** on all endpoints
- **Bulk operations** for efficient data management

### Mobile Optimization

- **Responsive design** for mobile browsers
- **API rate limiting** to prevent abuse
- **Offline support** with local storage
- **Push notifications** for budget alerts

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards

- **Python**: PEP 8 compliance with Black formatting
- **Django**: Follow Django best practices
- **Testing**: Maintain >85% coverage
- **Documentation**: Update docs for new features
- **Security**: Follow OWASP guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Getting Help

- **Documentation**: Check this README and API docs
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact support@yourdomain.com

### Common Issues

- **Database connection errors**: Check PostgreSQL service and credentials
- **Redis connection issues**: Verify Redis is running and accessible
- **Email not sending**: Check Brevo credentials and SMTP settings
- **File upload failures**: Verify S3 storage configuration

## Roadmap

### Phase 1 (Current) - Production Foundation
- [x] Enhanced data models and API
- [x] Security middleware and authentication
- [x] Background task processing
- [x] Monitoring and observability
- [x] CI/CD pipeline

### Phase 2 (Next) - Advanced Features
- [ ] Bank sync integration (Plaid/Teller)
- [ ] Machine learning categorization
- [ ] Advanced reporting and analytics
- [ ] Mobile app (React Native)
- [ ] Multi-currency support

### Phase 3 (Future) - Business Features
- [ ] Subscription plans and billing
- [ ] Team/shared budgets
- [ ] Advanced integrations
- [ ] White-label solutions
- [ ] Enterprise features

---

**Built with Django and modern web technologies**
