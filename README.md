# Medicine Assistant

AI-powered medicine management system for prescription analysis, drug interaction checking, and medication tracking.

## Overview

Medicine Assistant uses BioBERT medical NLP to analyze prescriptions, check for drug interactions, validate against allergies, and suggest alternative medicines. Built with Django backend and Flutter frontend.

## Key Features

- **Prescription Analysis** - AI extracts medicines, dosages, and frequencies from prescription text
- **Drug Interaction Checking** - Real-time warnings for dangerous drug combinations
- **Allergy Alerts** - Cross-checks prescriptions against user allergies
- **Alternative Medicines** - Suggests generic and therapeutic alternatives
- **Medication Reminders** - Customizable reminders with notifications
- **Prescription History** - Auto-saves all analyses for later reference
- **Medical Knowledge Search** - Database of 10,000+ medicines with detailed information

## Tech Stack

**Backend**: Django 5.2.6, Django REST Framework, Simple JWT  
**Frontend**: Flutter (Web/Mobile), Material Design 3  
**AI/ML**: BioBERT (biobert-v1.1)  
**Database**: SQLite (dev), PostgreSQL-ready  
**Data Sources**: DrugBank, OpenFDA, RxNorm, Medical Wiki  

## Installation

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### Frontend
```bash
cd frontend/src/medicine_assistant_app
flutter pub get
flutter run -d web-server --web-port 3000
```

### Access
- App: http://localhost:3000
- API: http://localhost:8000
- Admin: http://localhost:8000/admin

## Project Structure

```
med-assist/
├── backend/              # Django REST API
│   ├── api/             # API endpoints, models, views
│   └── medicine_assistant/  # Project settings
├── frontend/src/medicine_assistant_app/  # Flutter app
│   └── lib/
│       ├── models/      # Data models
│       ├── screens/     # UI screens
│       └── services/    # API integration
├── datasets/            # Medicine databases
├── ai-models/           # BioBERT model
└── docs/                # Documentation
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login (username or email)
- `GET /api/auth/profile/` - Get user profile

### Prescription
- `POST /api/prescription/analyze/` - Analyze prescription
- `GET /api/prescription/history/` - Get analysis history

### Notifications & Reminders
- `GET /api/notifications/` - Get notifications
- `POST /api/reminders/create/` - Create medication reminder

### Medical Knowledge
- `GET /api/medical-knowledge/search/` - Search medical database
- `GET /api/medicines/search/` - Search medicines

## Features in Detail

**Prescription Analysis**  
BioBERT AI or rule-based extraction → Database lookup → Interaction checking → Allergy validation → Alternative suggestions → Auto-save to history

**Allergy System**  
User maintains allergy list → Real-time checking → Cross-reactivity detection → Severity levels → Detailed warnings

**Reminders**  
Multiple times per day → 8 frequency options → Active/inactive toggle → Automatic notifications

**Notifications**  
6 types (reminder, allergy, interaction, side effect, dosage, info, system) → 4 priority levels → Color-coded → Swipe-to-delete

## Database

**10,000+ Medicines** from DrugBank, OpenFDA, RxNorm  
**1,000+ Medical Knowledge** entries  
**8,000+ Molecular Structures**  
**Models**: Medicine, UserProfile, PrescriptionHistory, MedicationReminder, Notification, MedicalKnowledge

## Performance

- BioBERT inference: ~2-3 seconds
- Rule-based fallback: <100ms
- API response: <200ms average
- Database queries optimized with indexes

## Security

- JWT authentication
- Password hashing
- CORS configuration
- Permission-based API access
- User data isolation

## License

Proprietary - All Rights Reserved

## Version

1.0.0 - Production Ready (October 2025)
