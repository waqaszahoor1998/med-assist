# Medicine Assistant App - Flutter Frontend

Cross-platform Flutter application for the Medicine Assistant system, providing AI-powered prescription analysis, drug interaction checking, and medication management.

## Architecture

- **Flutter 3.x** - Cross-platform UI framework
- **Dart Language** - Modern programming language
- **Material Design** - Google's design system
- **HTTP Client** - RESTful API communication
- **State Management** - Custom service architecture
- **Responsive Design** - Multi-device compatibility

## Platform Support

- **Web Application** - Full-featured web interface
- **iOS App** - Native iOS application
- **Android App** - Native Android application
- **macOS App** - Desktop macOS application
- **Windows App** - Desktop Windows application (planned)

## Project Structure

```
lib/
├── main.dart                 # Application entry point
├── models/                   # Data models
│   ├── medicine.dart         # Medicine data model
│   ├── prescription_analysis.dart # Analysis result model
│   ├── prescription_history.dart  # History model
│   ├── medication_reminder.dart   # Reminder model
│   ├── notification.dart     # Notification model
│   └── medical_knowledge.dart # Medical knowledge model
├── screens/                  # Application screens
│   ├── login_screen.dart     # User authentication
│   ├── registration_screen.dart # User registration
│   ├── user_dashboard.dart   # Main dashboard
│   ├── prescription_entry_screen.dart # Prescription analysis
│   ├── prescription_history_screen.dart # Analysis history
│   ├── prescription_history_detail_screen.dart # Detailed view
│   ├── medicine_search_screen.dart # Medicine database search
│   ├── medical_knowledge_screen.dart # Medical knowledge search
│   ├── reminders_screen.dart # Reminder management
│   ├── create_reminder_screen.dart # Create reminders
│   ├── edit_reminder_screen.dart # Edit reminders
│   ├── notifications_screen.dart # Notification management
│   ├── user_profile_screen.dart # User profile
│   ├── personal_info_screen.dart # Personal information
│   ├── medical_history_screen.dart # Medical history
│   ├── settings_screen.dart # Application settings
│   └── dashboard_home_screen.dart # Enhanced dashboard
├── services/                # Service layer
│   ├── api_service.dart     # API communication
│   └── user_session.dart    # User session management
├── widgets/                 # Reusable widgets
│   ├── action_card.dart     # Action card widget
│   ├── info_row.dart        # Information row widget
│   ├── modern_action_card.dart # Modern action card
│   ├── modern_dashboard_card.dart # Dashboard card
│   └── modern_loading_overlay.dart # Loading overlay
└── utils/                   # Utility functions
    ├── constants.dart       # Application constants
    ├── screen_mixins.dart  # Screen mixins
    └── ui_helpers.dart     # UI helper functions
```

## Features

### Authentication & User Management
- **User Registration** - Complete user onboarding
- **User Login** - Secure authentication
- **Profile Management** - Personal and medical information
- **Session Management** - Automatic token refresh
- **Logout** - Secure session termination

### Prescription Analysis
- **AI-Powered Analysis** - BioBERT integration for medicine extraction
- **Real-time Processing** - Instant prescription analysis
- **Confidence Scoring** - AI confidence levels
- **Multiple Formats** - Handles various prescription formats
- **Fallback System** - Rule-based extraction when AI fails

### Drug Interaction Checking
- **Safety Validation** - Automatic drug interaction checking
- **Severity Levels** - HIGH, MEDIUM, LOW risk classifications
- **Safety Recommendations** - Specific monitoring advice
- **Alternative Suggestions** - Safe medicine alternatives
- **Real-time Alerts** - Immediate safety warnings

### Medical Knowledge Database
- **29,974 Medical Terms** - Comprehensive medical terminology
- **Advanced Search** - Fuzzy search with multiple criteria
- **Detailed Explanations** - In-depth medical information
- **Related Terms** - Cross-referenced medical concepts
- **Source Attribution** - Reliable medical sources

### Medication Reminder System
- **Flexible Scheduling** - Multiple daily dose support
- **Multiple Times** - Support for complex schedules
- **Active/Inactive Toggle** - Easy reminder management
- **Edit Functionality** - Complete CRUD operations
- **End Date Support** - Optional reminder expiration
- **Notes Field** - Additional medication instructions

### Notification System
- **Real-time Notifications** - Instant reminder alerts
- **Notification History** - Complete notification tracking
- **Read/Unread Status** - Notification management
- **Bulk Operations** - Mark all as read, delete multiple
- **Badge Counters** - Unread notification indicators
- **Priority Levels** - High, medium, low priority notifications

### Prescription History
- **Auto-Save** - Automatic analysis storage
- **Detailed History** - Complete analysis results
- **Search & Filter** - Find specific analyses
- **Export Capability** - Data export functionality
- **Pagination** - Efficient large dataset handling
- **User Privacy** - Secure data isolation

### Medicine Database
- **18,802 Medicine Database** - Comprehensive medicine information
- **Advanced Search** - Fuzzy search with multiple criteria
- **Medicine Details** - Side effects, interactions, contraindications
- **Alternative Medicines** - Similar effect alternatives
- **Cost Analysis** - Medicine pricing information
- **Molecular Structures** - 3D molecular visualization

### Allergy Management
- **Personal Allergy Database** - User allergy tracking
- **Prescription Validation** - Automatic allergy checking
- **Safety Alerts** - Immediate allergy warnings
- **Alternative Suggestions** - Safe medicine alternatives
- **Risk Assessment** - Allergy risk level evaluation

## Quick Start

### Prerequisites
- Flutter SDK 3.0 or higher
- Dart SDK 3.0 or higher
- Android Studio / Xcode (for mobile development)
- VS Code / Android Studio (for development)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd frontend/src/medicine_assistant_app
```

2. **Install dependencies**
```bash
flutter pub get
```

3. **Run the application**
```bash
# Web
flutter run -d chrome

# iOS
flutter run -d ios

# Android
flutter run -d android

# macOS
flutter run -d macos
```

### Development Setup

1. **Configure API endpoint**
   - Update `lib/services/api_service.dart`
   - Set correct backend URL
   - Configure authentication settings

2. **Run in debug mode**
```bash
flutter run --debug
```

3. **Run tests**
```bash
flutter test
```

## Dependencies

### Core Dependencies
- **flutter**: Flutter SDK
- **cupertino_icons**: iOS-style icons
- **http**: HTTP client for API communication
- **flutter_staggered_grid_view**: Enhanced grid layouts
- **flutter_svg**: SVG image support
- **cached_network_image**: Image caching
- **webview_flutter**: Web view integration
- **json_annotation**: JSON serialization

### Development Dependencies
- **flutter_test**: Testing framework
- **flutter_lints**: Code linting

## API Integration

### Service Layer
- **ApiService**: Main API communication service
- **UserSession**: User session and authentication management
- **Error Handling**: Comprehensive error handling
- **Token Management**: Automatic token refresh

### Endpoints Used
- Authentication endpoints (login, register, profile)
- Prescription analysis endpoints
- Medicine database endpoints
- Drug interaction endpoints
- Medical knowledge endpoints
- Reminder management endpoints
- Notification endpoints

## State Management

### Architecture
- **Service-based Architecture**: Custom service layer
- **API Service**: Centralized API communication
- **User Session**: Authentication state management
- **Local Storage**: Secure data persistence
- **Error Handling**: Comprehensive error management

### Data Flow
1. User interaction triggers API call
2. ApiService handles HTTP communication
3. Response data updates UI state
4. Error handling provides user feedback
5. Local storage persists user data

## UI/UX Design

### Design System
- **Material Design**: Google's design guidelines
- **Responsive Layout**: Adaptive to all screen sizes
- **Accessibility**: Accessible design principles
- **Dark/Light Theme**: Theme support (planned)
- **Custom Widgets**: Reusable UI components

### Screen Organization
- **Authentication Screens**: Login, registration, profile
- **Core Application Screens**: Dashboard, analysis, history
- **Management Screens**: Reminders, notifications
- **Settings Screens**: Profile, preferences, settings

## Testing

### Test Structure
- **Unit Tests**: Individual function testing
- **Widget Tests**: UI component testing
- **Integration Tests**: End-to-end testing
- **API Tests**: Backend communication testing

### Running Tests
```bash
# Run all tests
flutter test

# Run specific test file
flutter test test/widget_test.dart

# Run with coverage
flutter test --coverage
```

## Performance Optimization

### Optimization Features
- **Image Caching**: Efficient image loading
- **Lazy Loading**: On-demand content loading
- **Memory Management**: Efficient memory usage
- **Network Optimization**: Reduced API calls
- **State Optimization**: Minimal state updates

### Performance Metrics
- **App Launch Time**: Less than 2 seconds
- **Screen Transition**: Smooth animations
- **API Response**: Real-time updates
- **Memory Usage**: Optimized for mobile devices
- **Battery Usage**: Efficient power consumption

## Security Features

### Data Protection
- **Secure Storage**: Encrypted local storage
- **API Security**: HTTPS communication
- **Token Management**: Secure JWT handling
- **Input Validation**: Client-side validation
- **Error Handling**: Secure error responses

### Privacy Compliance
- **Data Minimization**: Minimal data collection
- **User Consent**: Clear data usage policies
- **Data Retention**: Configurable data storage
- **Access Control**: User-specific data isolation

## Deployment

### Web Deployment
- **Flutter Web**: Optimized web build
- **PWA Support**: Progressive Web App features
- **Responsive Design**: Mobile-friendly interface
- **Performance**: Optimized for web browsers

### Mobile Deployment
- **iOS App Store**: Ready for submission
- **Google Play Store**: Ready for submission
- **Code Signing**: Proper certificate management
- **App Icons**: Platform-specific icons

### Desktop Deployment
- **macOS App**: Native macOS application
- **Windows App**: Windows application (planned)
- **Linux App**: Linux application (planned)

## Troubleshooting

### Common Issues
- **API Connection**: Check backend server status
- **Authentication**: Verify JWT token validity
- **Dependencies**: Run `flutter pub get`
- **Platform Issues**: Check platform-specific setup

### Debug Mode
```bash
# Enable debug mode
flutter run --debug

# Check logs
flutter logs

# Analyze performance
flutter run --profile
```

## Contributing

### Development Guidelines
- Follow Flutter/Dart best practices
- Use meaningful variable names
- Add comprehensive comments
- Write unit tests for new features
- Update documentation

### Code Style
- Use `flutter_lints` for code quality
- Follow Material Design guidelines
- Maintain consistent naming conventions
- Use proper error handling

This Flutter application provides a comprehensive, cross-platform solution for medical prescription analysis and medication management, integrating seamlessly with the Django backend API.
