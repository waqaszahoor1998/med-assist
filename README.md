# Medicine Assistant - AI-Powered Prescription Analysis

A comprehensive medical assistant application that uses AI to analyze prescriptions, check drug interactions, and provide medical knowledge.

## Features

- **AI Prescription Analysis** - BioBERT-powered medicine extraction
- **Drug Interaction Checking** - Safety alerts and contraindications
- **Medical Knowledge Base** - 29,974 medical terms and explanations
- **User Authentication** - JWT-based secure authentication
- **Medication Reminders** - Personalized reminder system
- **18,802 Medicine Database** - Comprehensive medicine information
- **Web & Mobile Ready** - Flutter frontend with responsive design
- **Notification System** - Real-time medication reminders
- **Prescription History** - Complete analysis tracking
- **Allergy Checking** - Personal allergy validation

## Project Structure

```
med-assist/
├── backend/                 # Django REST API backend
│   ├── api/                # API endpoints and models
│   ├── medicine_assistant/  # Django project settings
│   ├── manage.py           # Django management
│   ├── requirements.txt    # Python dependencies
│   └── db.sqlite3          # SQLite database
├── frontend/               # Flutter frontend
│   └── src/medicine_assistant_app/
│       ├── lib/            # Flutter app source code
│       ├── android/        # Android configuration
│       ├── ios/            # iOS configuration
│       ├── web/            # Web configuration
│       └── pubspec.yaml    # Flutter dependencies
├── ai-models/              # AI model files
│   └── biobert/            # BioBERT v1.1 model
├── datasets/               # Medical datasets
│   ├── raw/                # Raw data files
│   ├── processed/          # Processed datasets
│   └── scripts/            # Data processing scripts
├── docs/                   # Project documentation
│   ├── api/                # API documentation
│   ├── deployment/         # Deployment guides
│   └── development/        # Development docs
└── deployment/             # Deployment configurations
    ├── docker/             # Docker files
    ├── kubernetes/         # K8s configs
    └── cloud/              # Cloud deployment
```

## Complete Setup Guide

### Prerequisites
- Python 3.8+ with pip
- Flutter SDK 3.0+ with Dart
- Git (for cloning the repository)

### Step 1: Clone the Repository
```bash
git clone https://github.com/waqaszahoor1998/med-assist.git
cd med-assist
```

### Step 2: Setup BioBERT AI Model
The BioBERT model files are large (~400MB) and not included in the repository. You need to download them:

```bash
# Navigate to ai-models directory
cd ai-models/biobert

# Clone the BioBERT model repository
git clone https://huggingface.co/dmis-lab/biobert-base-cased-v1.1 biobert-v1.1

# Verify the model files are present
ls biobert-v1.1/
# Should show: config.json, pytorch_model.bin, vocab.txt, etc.
```

### Step 3: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Populate the database with medical data
python manage.py populate_database

# Start the backend server
python manage.py runserver
```

### Step 4: Frontend Setup
```bash
cd frontend/src/medicine_assistant_app

# Install Flutter dependencies
flutter pub get

# Run the Flutter app
flutter run
```

### Step 5: Verify Installation
1. Backend should be running on `http://localhost:8000`
2. Frontend should open in your browser or mobile device
3. Test the API: `curl http://localhost:8000/api/ping/`

### Quick Start Scripts
Use the provided scripts for faster setup:

```bash
# Start backend
./start_backend.sh

# Start frontend
./start_frontend.sh

# Start web version
./start_web.sh

# Start iOS simulator
./start_iphone.sh
```

### Troubleshooting
- **BioBERT Model Issues**: Ensure the model files are downloaded correctly
- **Database Issues**: Run `python manage.py migrate` and `python manage.py populate_database`
- **Flutter Issues**: Run `flutter doctor` to check Flutter setup
- **Port Conflicts**: Change ports in settings if 8000 is occupied

## Database

- **SQLite** (Development) - 12MB with 18,802 medicines
- **PostgreSQL** (Production) - For scaling to thousands of users
- **Medical Knowledge** - 29,974 medical terms and explanations
- **Drug Interactions** - Comprehensive safety database

## Authentication

- JWT-based authentication
- User profiles with medical history
- Secure API endpoints
- Token refresh and logout

## Current Status

- Database migration completed
- User authentication implemented
- API endpoints functional (35 endpoints)
- Frontend integration working (17 screens)
- AI integration with BioBERT
- Drug interaction checking
- Medication reminder system
- Notification system
- Multi-platform support (Web, iOS, Android, macOS)

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - User profile

### Prescription Analysis
- `POST /api/prescription/analyze/` - AI prescription analysis
- `GET /api/prescription/history/` - Analysis history
- `POST /api/prescription/analyze-with-safety/` - Enhanced analysis

### Medicine Database
- `GET /api/medicines/search/` - Medicine search
- `GET /api/medicine/<name>/` - Medicine details
- `GET /api/alternatives/<name>/` - Medicine alternatives

### Drug Interactions
- `POST /api/interactions/check/` - Basic interaction checking
- `POST /api/interactions/enhanced/check/` - Enhanced checking
- `GET /api/interactions/medicine/<name>/` - Medicine interactions

### Medical Knowledge
- `GET /api/medical-knowledge/search/` - Medical term search
- `GET /api/medical-knowledge/explanation/<term>/` - Term explanations

### Reminders & Notifications
- `GET /api/reminders/list/` - List reminders
- `POST /api/reminders/create/` - Create reminder
- `PUT /api/reminders/<id>/update/` - Update reminder
- `DELETE /api/reminders/<id>/delete/` - Delete reminder
- `GET /api/notifications/` - List notifications

## Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend/src/medicine_assistant_app
flutter test
```

## Documentation

- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)
- [Development Guide](docs/development/)
- [BioBERT Model Documentation](ai-models/biobert/README.md)

