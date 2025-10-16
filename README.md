# 🏥 Medicine Assistant - AI-Powered Prescription Analysis

A comprehensive medical assistant application that uses AI to analyze prescriptions, check drug interactions, and provide medical knowledge.

## 🚀 Features

- **AI Prescription Analysis** - BioBERT-powered medicine extraction
- **Drug Interaction Checking** - Safety alerts and contraindications
- **Medical Knowledge Base** - 29,974 medical terms and explanations
- **User Authentication** - JWT-based secure authentication
- **Medication Reminders** - Personalized reminder system
- **18,802 Medicine Database** - Comprehensive medicine information
- **Web & Mobile Ready** - Flutter frontend with responsive design

## 📁 Project Structure

```
med-assist-clean/
├── backend/                 # Django backend
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Django settings
│   │   └── utils/          # Utility functions
│   ├── scripts/            # Data processing scripts
│   ├── tests/              # Backend tests
│   └── docs/               # Backend documentation
├── frontend/               # Flutter frontend
│   ├── src/                # Flutter app source
│   ├── tests/              # Frontend tests
│   └── docs/               # Frontend documentation
├── ai-models/              # AI model files
│   ├── biobert/            # BioBERT model
│   └── scripts/            # Model scripts
├── datasets/               # Medical datasets
│   ├── raw/                # Raw data files
│   ├── processed/          # Processed datasets
│   └── scripts/            # Data processing scripts
├── docs/                   # Project documentation
│   ├── api/                # API documentation
│   ├── deployment/         # Deployment guides
│   └── development/        # Development docs
├── tests/                  # Integration tests
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
└── deployment/             # Deployment configs
    ├── docker/             # Docker files
    ├── kubernetes/         # K8s configs
    └── cloud/              # Cloud deployment
```

## 🛠️ Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/manage.py migrate
python src/manage.py runserver
```

### Frontend Setup
```bash
cd frontend/src
flutter pub get
flutter run
```

## 📊 Database

- **SQLite** (Development) - 12MB with 18,802 medicines
- **PostgreSQL** (Production) - For scaling to thousands of users

## 🔐 Authentication

- JWT-based authentication
- User profiles with medical history
- Secure API endpoints

## 🎯 Current Status

- ✅ Database migration completed
- ✅ User authentication implemented
- ✅ API endpoints functional
- ✅ Frontend integration working
- ⏳ Mobile app deployment (next)

## 📱 API Endpoints

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/prescription/analyze/` - Prescription analysis
- `GET /api/medical-knowledge/search/` - Medical knowledge search

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend/src
flutter test
```

## 📚 Documentation

- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)
- [Development Guide](docs/development/)

