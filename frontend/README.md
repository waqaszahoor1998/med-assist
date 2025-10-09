# 📱 Medicine Assistant Frontend

Flutter web and mobile application for the Medicine Assistant.

## 🏗️ Architecture

- **Flutter 3.x** - Cross-platform framework
- **Material Design** - Modern UI components
- **HTTP Client** - API communication
- **State Management** - Built-in Flutter state management

## 📁 Structure

```
frontend/
├── src/                       # Flutter app source
│   ├── lib/
│   │   ├── main.dart         # Main app entry point
│   │   ├── screens/          # UI screens
│   │   ├── widgets/          # Reusable widgets
│   │   ├── services/         # API services
│   │   └── models/           # Data models
│   ├── pubspec.yaml          # Dependencies
│   ├── android/              # Android configuration
│   ├── ios/                  # iOS configuration
│   ├── web/                  # Web configuration
│   └── macos/                # macOS configuration
├── tests/                     # Test files
├── docs/                      # Documentation
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Flutter
```bash
# Install Flutter SDK
# Follow: https://flutter.dev/docs/get-started/install
```

### 2. Get Dependencies
```bash
cd src
flutter pub get
```

### 3. Run Application
```bash
# Web
flutter run -d chrome

# Android
flutter run -d android

# iOS
flutter run -d ios
```

## 📱 Features

### Prescription Analysis
- Text input for prescription
- AI-powered medicine extraction
- Detailed medicine information
- Safety alerts and warnings

### Medical Knowledge
- Search medical terms
- Detailed explanations
- Related terms and categories
- Comprehensive database

### User Interface
- Modern Material Design
- Responsive layout
- Bottom navigation
- Easy-to-use forms

## 🔧 Development

### Project Structure
- **main.dart** - App entry point and navigation
- **screens/** - Individual app screens
- **widgets/** - Reusable UI components
- **services/** - API communication
- **models/** - Data structures

### State Management
- Built-in Flutter state management
- setState() for local state
- FutureBuilder for async data
- Provider pattern (if needed)

### API Integration
- HTTP client for backend communication
- JWT token authentication
- Error handling and loading states
- JSON serialization

## 🧪 Testing

```bash
# Run all tests
flutter test

# Run specific test
flutter test test/widget_test.dart

# Integration tests
flutter drive --target=test_driver/app.dart
```

## 📱 Platform Support

### Web
- Responsive design
- Chrome, Firefox, Safari support
- PWA capabilities

### Mobile
- Android 5.0+ (API level 21)
- iOS 11.0+
- Material Design on Android
- Cupertino Design on iOS

### Desktop
- macOS 10.14+
- Windows 10+
- Linux (Ubuntu 18.04+)

## 🎨 UI Components

### Screens
- **PrescriptionInputScreen** - Prescription analysis
- **MedicalKnowledgeScreen** - Medical knowledge search
- **MainNavigationScreen** - Bottom navigation

### Widgets
- **MedicineInfoCard** - Medicine information display
- **SearchBar** - Medical knowledge search
- **InfoRow** - Key-value information display

## 🔐 Authentication

- JWT token storage
- Automatic token refresh
- Secure API communication
- User session management

## 📊 Data Models

### Medicine
```dart
class Medicine {
  String name;
  String genericName;
  List<String> brandNames;
  List<String> sideEffects;
  // ... more fields
}
```

### User
```dart
class User {
  String username;
  String email;
  UserProfile profile;
  // ... more fields
}
```

## 🚀 Build & Deploy

### Web Build
```bash
flutter build web
# Output in build/web/
```

### Android Build
```bash
flutter build apk --release
# Output in build/app/outputs/flutter-apk/
```

### iOS Build
```bash
flutter build ios --release
# Requires Xcode for final build
```

## 🔧 Configuration

### Environment Variables
- API base URL
- Authentication settings
- Feature flags

### Platform-specific
- Android: `android/app/build.gradle`
- iOS: `ios/Runner/Info.plist`
- Web: `web/index.html`

## 📈 Performance

- **Bundle Size**: Optimized for web and mobile
- **Load Time**: <2 seconds on web
- **Memory Usage**: Efficient state management
- **Network**: Optimized API calls

## 🐛 Debugging

### Web Debugging
- Chrome DevTools
- Flutter Inspector
- Network tab for API calls

### Mobile Debugging
- Flutter Inspector
- Device logs
- Hot reload for quick testing

## 📚 Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [Material Design](https://material.io/design)
- [Dart Language](https://dart.dev/guides)
- [API Integration Guide](docs/api-integration.md)
