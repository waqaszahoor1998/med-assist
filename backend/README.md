# 🏥 Medicine Assistant Backend

Django REST API backend for the Medicine Assistant application.

## 🏗️ Architecture

- **Django 5.2.6** - Web framework
- **Django REST Framework** - API framework
- **SQLite** - Development database
- **JWT Authentication** - Secure user authentication
- **BioBERT AI** - Medicine extraction

## 📁 Structure

```
backend/
├── src/
│   ├── api/                    # API application
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API views
│   │   ├── urls.py            # URL routing
│   │   ├── auth_views.py      # Authentication views
│   │   ├── database_views.py  # Database-backed views
│   │   ├── nlp_processor.py   # NLP processing
│   │   ├── biobert_processor.py # BioBERT AI
│   │   └── management/        # Django management commands
│   ├── core/                  # Django project settings
│   │   ├── settings.py        # Main settings
│   │   ├── urls.py            # Root URLs
│   │   ├── wsgi.py            # WSGI config
│   │   └── asgi.py            # ASGI config
│   └── utils/                 # Utility functions
├── scripts/                   # Data processing scripts
├── tests/                     # Test files
├── docs/                      # Documentation
├── manage.py                  # Django management
├── requirements.txt           # Python dependencies
└── db.sqlite3                 # SQLite database
```

## 🚀 Quick Start

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
cd src
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

## 📊 Database Models

### Medicine Model
- 18,802 medicines with comprehensive data
- Side effects, interactions, contraindications
- Molecular structures and cost analysis

### UserProfile Model
- User medical history and allergies
- Current conditions and medications
- Emergency contact information

### MedicalKnowledge Model
- 29,974 medical terms and explanations
- Related terms and categories
- Source information

## 🔐 Authentication

JWT-based authentication with:
- User registration and login
- Token refresh and logout
- Profile management
- Secure API endpoints

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_authentication.py
python tests/test_database_migration.py
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout

### Medical Endpoints
- `POST /api/prescription/analyze/` - Prescription analysis
- `GET /api/medical-knowledge/search/` - Medical knowledge search
- `GET /api/medical-knowledge/explanation/<medicine>/` - Medicine explanation

## 🔧 Development

### Adding New Models
1. Define model in `api/models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`

### Adding New API Endpoints
1. Add view in `api/views.py`
2. Add URL pattern in `api/urls.py`
3. Add tests in `tests/`

## 📈 Performance

- **Database**: 12MB SQLite with 18,802 medicines
- **Response Time**: <100ms for most API calls
- **Concurrent Users**: Optimized for development (single user)

## 🚀 Production Deployment

For production, migrate to PostgreSQL:
1. Install PostgreSQL
2. Update database settings
3. Run migrations
4. Deploy with Gunicorn/uWSGI

## 📝 Logs

Logs are written to:
- Django console output
- Application-specific loggers
- Error tracking (configured in production)
