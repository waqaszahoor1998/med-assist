# Medicine Assistant Backend

Django REST API backend for the Medicine Assistant application.

## Architecture

- **Django 5.2.6** - Web framework
- **Django REST Framework** - API framework
- **SQLite** - Development database
- **JWT Authentication** - Secure user authentication
- **BioBERT AI** - Medicine extraction
- **OpenFDA Integration** - External drug data
- **RxNorm Integration** - Drug terminology

## Structure

```
backend/
├── api/                    # API application
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── urls.py            # URL routing
│   ├── auth_views.py      # Authentication views
│   ├── database_views.py  # Database-backed views
│   ├── nlp_processor.py   # NLP processing
│   ├── biobert_processor.py # BioBERT AI
│   ├── drug_interactions.py # Drug interaction checking
│   ├── enhanced_drug_interactions.py # Enhanced checking
│   ├── unified_drug_interactions.py # Unified system
│   ├── allergy_checker.py # Allergy validation
│   ├── openfda_client.py  # OpenFDA API client
│   ├── rxnorm_client.py   # RxNorm API client
│   └── management/        # Django management commands
├── medicine_assistant/     # Django project settings
│   ├── settings.py        # Main settings
│   ├── urls.py            # Root URLs
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
└── db.sqlite3            # SQLite database
```

## Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Populate Database
```bash
python manage.py populate_database
```

### 5. Start Server
```bash
python manage.py runserver 8000
```

## Database Models

### Medicine Model
- 18,802 medicines with comprehensive data
- Side effects, interactions, contraindications
- Molecular structures and cost analysis
- Alternative medicines and substitutes

### UserProfile Model
- User medical history and allergies
- Current conditions and medications
- Emergency contact information
- Personal information and preferences

### MedicalKnowledge Model
- 29,974 medical terms and explanations
- Related terms and categories
- Source information and references
- Cross-referenced medical concepts

### PrescriptionHistory Model
- Complete prescription analysis history
- AI extraction results and confidence scores
- Drug interaction warnings and alerts
- User-specific analysis tracking

### MedicationReminder Model
- Personalized medication reminders
- Flexible scheduling and timing
- Active/inactive status management
- Notes and additional instructions

### Notification Model
- Real-time notification system
- Priority levels and categorization
- Read/unread status tracking
- User-specific notification management

## Authentication

JWT-based authentication with:
- User registration and login
- Token refresh and logout
- Profile management
- Secure API endpoints
- Session management
- Password hashing and security

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_authentication.py
python tests/test_database_migration.py
python tests/test_drug_interactions.py
python tests/test_biobert_processor.py
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - User profile
- `POST /api/auth/profile/update/` - Update profile

### Prescription Analysis Endpoints
- `POST /api/prescription/analyze/` - AI prescription analysis
- `POST /api/prescription/analyze-with-safety/` - Enhanced analysis
- `GET /api/prescription/history/` - Analysis history
- `GET /api/prescription/history/<id>/` - Detailed analysis

### Medicine Database Endpoints
- `GET /api/medicines/search/` - Medicine search
- `GET /api/medicine/<name>/` - Medicine details
- `GET /api/alternatives/<name>/` - Medicine alternatives

### Drug Interaction Endpoints
- `POST /api/interactions/check/` - Basic interaction checking
- `POST /api/interactions/enhanced/check/` - Enhanced checking
- `GET /api/interactions/medicine/<name>/` - Medicine interactions
- `GET /api/interactions/<med1>/<med2>/` - Specific interactions
- `POST /api/interactions/validate-safety/` - Safety validation

### Medical Knowledge Endpoints
- `GET /api/medical-knowledge/search/` - Medical term search
- `GET /api/medical-knowledge/explanation/<term>/` - Term explanations
- `GET /api/medical-knowledge/stats/` - Database statistics

### Reminder Management Endpoints
- `GET /api/reminders/list/` - List reminders
- `POST /api/reminders/create/` - Create reminder
- `PUT /api/reminders/<id>/update/` - Update reminder
- `DELETE /api/reminders/<id>/delete/` - Delete reminder
- `POST /api/reminders/trigger-notifications/` - Trigger notifications
- `GET /api/reminders/stats/` - Reminder statistics

### Notification Endpoints
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread-count/` - Unread count
- `POST /api/notifications/create/` - Create notification
- `POST /api/notifications/<id>/read/` - Mark as read
- `POST /api/notifications/mark-all-read/` - Mark all read
- `DELETE /api/notifications/<id>/delete/` - Delete notification

## Development

### Adding New Models
1. Define model in `api/models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Add tests in `tests/`

### Adding New API Endpoints
1. Add view in `api/views.py`
2. Add URL pattern in `api/urls.py`
3. Add tests in `tests/`
4. Update API documentation

### AI Model Integration
1. Add model files to `ai-models/` directory
2. Create processor in `api/` directory
3. Integrate with main views
4. Add fallback mechanisms
5. Test thoroughly

## Performance

- **Database**: 12MB SQLite with 18,802 medicines
- **Response Time**: Less than 100ms for most API calls
- **AI Processing**: 1-2 seconds for prescription analysis
- **Drug Interactions**: 50ms-2s depending on method
- **Concurrent Users**: Optimized for development (single user)
- **Memory Usage**: Efficient model loading and caching

## Production Deployment

For production, migrate to PostgreSQL:
1. Install PostgreSQL
2. Update database settings in `settings.py`
3. Run migrations: `python manage.py migrate`
4. Deploy with Gunicorn/uWSGI
5. Configure reverse proxy (Nginx)
6. Set up SSL certificates
7. Configure monitoring and logging

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: Django ORM protection
- **CORS Configuration**: Cross-origin request handling
- **Rate Limiting**: API rate limiting (production)
- **Data Encryption**: Sensitive data encryption
- **Audit Logging**: Comprehensive audit trails

## Logs

Logs are written to:
- Django console output
- Application-specific loggers
- Error tracking (configured in production)
- Performance monitoring
- Security audit logs
