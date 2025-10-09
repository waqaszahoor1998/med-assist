# 🧪 Medicine Assistant Test Suite

Comprehensive test suite for the Medicine Assistant application, organized by test type and coverage.

## 📁 Test Organization

### **Unit Tests** (`tests/unit/`)
Tests individual components and functions in isolation.

- **`test_authentication.py`** - User authentication system tests
  - User registration and login
  - JWT token generation and validation
  - Profile management
  - Token refresh and logout

- **`test_database_simple.py`** - Basic database operations
  - Database connectivity
  - Model creation and queries
  - Data persistence

- **`test_database_migration.py`** - Database migration tests
  - Model migrations
  - Data population
  - Database schema validation

- **`test_biobert_integration.py`** - BioBERT AI model tests
  - Model loading and initialization
  - Medicine extraction accuracy
  - NLP processing functionality

### **Integration Tests** (`tests/integration/`)
Tests interaction between different system components.

- **`test_complete_system_integration.py`** - Full system integration
  - End-to-end API functionality
  - Database and API integration
  - Complete workflow testing

- **`test_django_biobert_integration.py`** - Django + BioBERT integration
  - Django API with AI model
  - Prescription analysis pipeline
  - Error handling and fallbacks

- **`test_drug_interactions.py`** - Drug interaction system
  - Basic drug interaction checking
  - Safety validation
  - Interaction database queries

- **`test_enhanced_drug_interactions.py`** - Enhanced drug interactions
  - OpenFDA integration
  - RxNorm data processing
  - Advanced interaction checking

- **`test_enhanced_reminders.py`** - Medication reminder system
  - Reminder creation and management
  - Scheduling and notifications
  - User-specific reminders

### **End-to-End Tests** (`tests/e2e/`)
Tests complete user workflows and frontend-backend integration.

- **`test_frontend_medical_knowledge_integration.py`** - Frontend-backend integration
  - Flutter app API communication
  - Medical knowledge search
  - User interface functionality

- **`test_medical_knowledge_system.py`** - Medical knowledge system
  - Knowledge base search
  - Medicine explanations
  - Database query performance

## 🚀 Running Tests

### **Run All Tests**
```bash
# From project root
python -m pytest tests/
```

### **Run by Test Type**
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# End-to-end tests only
python -m pytest tests/e2e/
```

### **Run Specific Test File**
```bash
# Authentication tests
python -m pytest tests/unit/test_authentication.py

# System integration tests
python -m pytest tests/integration/test_complete_system_integration.py

# Frontend integration tests
python -m pytest tests/e2e/test_frontend_medical_knowledge_integration.py
```

### **Run with Coverage**
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m pytest tests/
coverage report
coverage html  # Generate HTML report
```

## 🔧 Test Configuration

### **Requirements**
- Python 3.13+
- Django 5.2.6
- pytest
- coverage (optional)

### **Environment Setup**
```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Install test dependencies
pip install pytest pytest-django coverage
```

### **Django Test Settings**
Tests use Django's test database configuration:
- Separate test database
- Isolated test data
- Automatic cleanup

## 📊 Test Coverage

### **Current Coverage Areas**
- ✅ User Authentication (100%)
- ✅ Database Operations (95%)
- ✅ API Endpoints (90%)
- ✅ Drug Interactions (85%)
- ✅ Medical Knowledge (80%)
- ✅ BioBERT Integration (75%)
- ⏳ Frontend Integration (60%)

### **Coverage Goals**
- **Unit Tests**: 95%+ coverage
- **Integration Tests**: 90%+ coverage
- **E2E Tests**: 80%+ coverage

## 🐛 Test Debugging

### **Common Issues**
1. **Database Connection**: Ensure test database is accessible
2. **API Endpoints**: Verify Django server is running
3. **File Paths**: Check relative paths in test files
4. **Dependencies**: Ensure all packages are installed

### **Debug Mode**
```bash
# Run tests with verbose output
python -m pytest tests/ -v

# Run tests with debug output
python -m pytest tests/ -s

# Run specific test with debug
python -m pytest tests/unit/test_authentication.py -v -s
```

## 📈 Continuous Integration

### **GitHub Actions** (Future)
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest coverage
      - name: Run tests
        run: python -m pytest tests/ --cov=backend/src
```

## 📚 Best Practices

### **Test Writing**
- Write descriptive test names
- Use fixtures for common setup
- Test both success and failure cases
- Mock external dependencies
- Keep tests independent

### **Test Organization**
- Group related tests in classes
- Use descriptive file names
- Separate unit, integration, and e2e tests
- Document test purposes

### **Test Data**
- Use test fixtures for consistent data
- Clean up test data after tests
- Use factories for dynamic test data
- Avoid hardcoded values

## 🔄 Test Maintenance

### **Regular Tasks**
- Update tests when features change
- Add tests for new functionality
- Review and improve test coverage
- Remove obsolete tests
- Optimize test performance

### **Test Review Checklist**
- [ ] Tests cover all code paths
- [ ] Tests are readable and maintainable
- [ ] Tests run reliably and quickly
- [ ] Tests provide clear failure messages
- [ ] Tests don't have external dependencies
