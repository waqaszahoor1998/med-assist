# Medicine Assistant Application

An intelligent medicine management system powered by BioBERT AI that helps users analyze prescriptions, manage medications, check for allergies and drug interactions, and receive personalized medicine recommendations.

## Features

### Core Functionality
- **AI-Powered Prescription Analysis**: BioBERT medical NLP model extracts medicines, dosages, and frequencies from prescription text
- **Rule-Based Fallback**: Comprehensive pattern matching system for reliable extraction when AI is unavailable
- **Drug Interaction Warnings**: Real-time checking for dangerous drug combinations
- **Allergy Alert System**: Cross-checks prescriptions against user allergies with severity levels
- **Alternative Medicine Suggestions**: Recommends generic and therapeutic alternatives for cost savings
- **Medical Knowledge Database**: Comprehensive medical information with 1000+ medicines

### User Management
- **User Authentication**: Secure JWT-based login/registration system
- **User Profiles**: Store medical history, allergies, current conditions, and emergency contacts
- **Dual Login**: Support for both username and email authentication

### Medication Management
- **Prescription History**: Automatic saving and retrieval of all analyzed prescriptions
- **Medication Reminders**: Customizable reminders with multiple daily times and frequencies
- **Notification System**: Real-time alerts for reminders, allergies, and drug interactions
- **Safety Monitoring**: Continuous monitoring of user's medication regimen

### User Interface
- **Modern Flutter Web App**: Responsive, minimalistic Material Design 3 interface
- **Dashboard**: 6 quick action buttons for all major features
- **Interactive Screens**: Notifications, prescription history, reminders, profile management
- **Real-time Feedback**: Loading states, error handling, success messages

## Technology Stack

### Backend
- **Framework**: Django 5.2.6 + Django REST Framework
- **Database**: SQLite (development) - PostgreSQL ready
- **Authentication**: Simple JWT
- **AI/NLP**: BioBERT (biobert-v1.1) + Custom rule-based system
- **APIs**: OpenFDA, RxNorm integration
- **Python**: 3.13

### Frontend
- **Framework**: Flutter (Web/Mobile)
- **State Management**: setState with proper architecture
- **HTTP Client**: Native Dart http package
- **UI**: Material Design 3
- **Navigation**: Bottom navigation + push navigation

### Data Sources
- **DrugBank**: Comprehensive medicine database
- **OpenFDA**: Drug interaction data
- **RxNorm**: Medicine terminology and relationships
- **SDF Molecular Structures**: Chemical structure data
- **Medical Knowledge Wiki**: Educational medical content

## Project Structure

```
med-assist/
├── backend/
│   ├── api/
│   │   ├── models.py              # Database models
│   │   ├── views.py               # API endpoints
│   │   ├── urls.py                # URL routing
│   │   ├── auth_views.py          # Authentication endpoints
│   │   ├── database_views.py      # Database-backed views
│   │   ├── allergy_checker.py     # Allergy checking logic
│   │   ├── biobert_processor.py   # BioBERT AI integration
│   │   └── nlp_processor.py       # Rule-based NLP
│   ├── medicine_assistant/        # Django project settings
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/src/medicine_assistant_app/
│   ├── lib/
│   │   ├── models/                # Data models
│   │   │   ├── notification.dart
│   │   │   ├── prescription_history.dart
│   │   │   ├── prescription_analysis.dart
│   │   │   └── medication_reminder.dart
│   │   ├── screens/               # UI screens
│   │   │   ├── login_screen.dart
│   │   │   ├── register_screen.dart
│   │   │   ├── user_dashboard.dart
│   │   │   ├── dashboard_home_screen.dart
│   │   │   ├── prescription_entry_screen.dart
│   │   │   ├── prescription_history_screen.dart
│   │   │   ├── prescription_history_detail_screen.dart
│   │   │   ├── notifications_screen.dart
│   │   │   ├── reminders_screen.dart
│   │   │   ├── create_reminder_screen.dart
│   │   │   ├── medical_knowledge_screen.dart
│   │   │   ├── medicine_search_screen.dart
│   │   │   └── user_profile_screen.dart
│   │   ├── services/              # API integration
│   │   │   ├── api_service.dart
│   │   │   └── user_session.dart
│   │   ├── utils/                 # Utilities
│   │   │   └── constants.dart
│   │   └── main.dart              # App entry point
│   └── pubspec.yaml
│
├── datasets/
│   ├── processed/                 # Processed medicine databases
│   ├── raw/                       # Raw data files
│   └── scripts/                   # Data processing scripts
│
├── ai-models/
│   └── biobert/biobert-v1.1/     # BioBERT model files
│
├── docs/                          # Development documentation
└── tests/                         # Test files
```

## Database Models

### Core Models
- **Medicine**: Complete medicine information (10,000+ entries)
- **UserProfile**: User medical data and preferences
- **PrescriptionHistory**: Auto-saved prescription analyses
- **MedicationReminder**: Scheduled medication reminders
- **Notification**: User notifications and alerts
- **MedicalKnowledge**: Medical terms and explanations

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (username or email)
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update profile

### Prescription Analysis
- `POST /api/prescription/analyze/` - Analyze prescription with BioBERT AI
- `GET /api/prescription/history/` - Get user's prescription history
- `GET /api/prescription/history/<id>/` - Get specific analysis details

### Notifications
- `GET /api/notifications/` - Get all notifications (filterable)
- `GET /api/notifications/unread-count/` - Get unread count
- `POST /api/notifications/<id>/read/` - Mark as read
- `POST /api/notifications/mark-all-read/` - Mark all as read
- `DELETE /api/notifications/<id>/delete/` - Delete notification

### Medication Reminders
- `GET /api/reminders/list/` - Get all reminders
- `POST /api/reminders/create/` - Create new reminder
- `PUT /api/reminders/<id>/update/` - Update reminder
- `DELETE /api/reminders/<id>/delete/` - Delete reminder

### Medical Knowledge
- `GET /api/medical-knowledge/search/` - Search medical database
- `GET /api/medical-knowledge/explanation/<medicine>/` - Get medicine explanation
- `GET /api/medical-knowledge/stats/` - Get database statistics

### Medicine Search
- `GET /api/medicines/search/` - Search medicines by name

## Installation & Setup

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### Frontend Setup

```bash
cd frontend/src/medicine_assistant_app
flutter pub get
flutter run -d web-server --web-port 3000
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## Features in Detail

### 1. Prescription Analysis
- Upload or type prescription text
- AI extracts medicines, dosages, frequencies automatically
- Shows detailed medicine information from database
- Checks for drug interactions
- Validates against user allergies
- Suggests alternative medicines
- Auto-saves to history

### 2. Allergy Checking
- User maintains allergy list in profile
- Real-time checking against prescription
- Severity levels: Critical, High, Medium, Low
- Cross-reactivity detection (e.g., Penicillin family)
- Detailed warnings with recommendations

### 3. Alternative Medicines
- Generic alternatives (cost savings)
- Same therapeutic category suggestions
- Similar indication matches
- Brand name alternatives
- Detailed comparison with original medicine

### 4. Notification System
- 6 notification types: Reminder, Allergy Alert, Interaction Warning, Side Effect, Dosage Alert, Info, System
- 4 priority levels: Critical, High, Medium, Low
- Color-coded visual indicators
- Swipe-to-delete functionality
- Filter by read status
- Real-time badge count

### 5. Medication Reminders
- Multiple reminders per medicine
- 8 frequency options (once, daily, twice daily, 3x, 4x, as needed, weekly, monthly)
- Custom reminder times
- Active/Inactive toggle
- Optional notes
- Automatic notifications

### 6. Prescription History
- Every analysis automatically saved
- View list of past prescriptions
- Detailed view with all extracted data
- Filter and search capabilities
- Export functionality (planned)

## AI/ML Integration

### BioBERT Medical NLP
- Pre-trained on biomedical literature
- Fine-tuned for medicine extraction
- Confidence scoring for each extraction
- Entity recognition for:
  - Medicine names (brand and generic)
  - Dosages (with units)
  - Frequencies (times per day, duration)
  - Route of administration

### Rule-Based Fallback
- Pattern matching for common prescription formats
- Dosage extraction with unit recognition
- Frequency parsing (e.g., "twice daily", "every 6 hours")
- Duration extraction (e.g., "for 7 days")
- Validates against medicine database

## Security Features
- JWT authentication with token refresh
- Password hashing with Django's built-in security
- CORS configuration for web access
- Permission-based API access
- User data isolation (users only see their own data)

## Code Quality
- Comprehensive inline comments
- Modular architecture
- Error handling throughout
- Loading states and user feedback
- Responsive design
- Accessibility considerations

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend/src/medicine_assistant_app
flutter test
```

## Development Progress

### Completed Features
✅ User authentication and profiles  
✅ BioBERT AI integration  
✅ Prescription analysis (AI + Rule-based)  
✅ Drug interaction checking  
✅ Allergy alert system  
✅ Alternative medicine suggestions  
✅ Notification system  
✅ Medication reminders  
✅ Prescription history  
✅ Medical knowledge search  
✅ Medicine database (10,000+ entries)  
✅ Comprehensive Flutter UI  
✅ Multi-file architecture  
✅ Complete API documentation  

### Planned Enhancements
- Real-time reminder notifications
- Email verification
- Password reset functionality
- Export prescription history (PDF/CSV)
- Mobile app deployment (Android/iOS)
- Offline capability
- Push notifications
- Reminder snooze functionality
- Prescription sharing with doctors
- Multi-language support

## Performance
- BioBERT inference: ~2-3 seconds per prescription
- Rule-based fallback: <100ms
- API response time: <200ms average
- Database query optimization with indexes
- Efficient caching for repeated searches

## Database Statistics
- Total Medicines: 10,000+
- Medical Knowledge Entries: 1,000+
- Molecular Structures: 8,000+
- Data Sources: 4 (DrugBank, OpenFDA, RxNorm, Wiki)

## Contributing
This is a medical application. All contributions should prioritize:
1. Medical accuracy
2. User safety
3. Data privacy
4. Code quality

## License
Proprietary - All Rights Reserved

## Contact
For questions or support, please contact the development team.

## Acknowledgments
- BioBERT team for the pre-trained medical NLP model
- DrugBank for comprehensive medicine data
- OpenFDA for drug interaction information
- RxNorm for medical terminology

---

**Version**: 1.0.0  
**Last Updated**: October 9, 2025  
**Status**: Production Ready (Development Servers)
