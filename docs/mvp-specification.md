# MVP Specification: AI-Based Post Diagnosis Medicine Assistant

## 🎯 MVP Definition

### **Core User Journey**
```
Patient Input → AI Processing → Medicine Information + Reminders
```

### **MVP Scope (Minimum Viable Product)**

#### **📥 Input Capabilities**
1. **Text Input**: Patient can type/paste prescription text
2. **Manual Entry**: Patient can manually enter medicine names
3. **Prescription Format**: Support common prescription formats
   - "Take Paracetamol 500mg twice daily"
   - "Amoxicillin 250mg, 3 times a day for 7 days"
   - "Metformin 1000mg once daily with meals"

#### **🧠 AI Processing (Core Features)**
1. **Medicine Name Extraction**: 
   - Extract medicine names from text using NLP
   - Handle common misspellings and variations
   - Success rate target: 80%+

2. **Dosage Recognition**:
   - Extract dosage amounts (mg, gm, ml, tablets, spoons)
   - Extract frequency (once/twice/thrice daily, every 8 hours)
   - Extract duration (for 7 days, until finished)

3. **Database Lookup**:
   - Match extracted medicines with database records
   - Retrieve medicine information and properties
   - Find alternatives and generic versions

#### **📤 Output Capabilities**
1. **Medicine Details**:
   - Generic and brand names
   - Purpose/indication (what it treats)
   - Correct dosage and timing
   - Duration of treatment
   - Basic side effects

2. **Alternative Suggestions**:
   - Generic alternatives (cost-effective)
   - Similar medicines with same active ingredient
   - Price comparison (if available)

3. **Safety Alerts**:
   - Common side effects
   - Basic drug interactions (major ones only)
   - Allergy warnings

4. **Reminder System**:
   - Personalized medication schedule
   - Push notifications for medicine intake
   - Track adherence (taken/missed)

#### **👤 User Profile (Basic)**
1. **Personal Information**:
   - Age, weight (for dosage calculations)
   - Known allergies
   - Current medications

2. **Medical History**:
   - Previous prescriptions
   - Medicine effectiveness feedback
   - Adverse reactions history

---

## 🔧 Technical MVP Requirements

### **Backend (Django)**
1. **API Endpoints**:
   - `POST /api/prescription/analyze` - Process prescription text
   - `GET /api/medicine/{id}` - Get medicine details
   - `GET /api/alternatives/{medicine_id}` - Get alternatives
   - `POST /api/reminders` - Set medication reminders
   - `GET /api/user/profile` - User profile management

2. **Database Models**:
   - Medicine (name, generic_name, dosage_forms, indications)
   - User (profile, allergies, medical_history)
   - Prescription (user, medicines, dosages, schedule)
   - Reminder (user, medicine, time, status)
   - Interaction (medicine1, medicine2, severity, description)

3. **NLP Pipeline**:
   - Text preprocessing and cleaning
   - Named Entity Recognition (NER) for medicine names
   - Dosage extraction using regex patterns
   - Frequency and duration parsing

### **Frontend (Flutter)**
1. **Core Screens**:
   - Home/Dashboard
   - Prescription Input (text/camera)
   - Medicine Details View
   - Alternatives & Recommendations
   - Reminder Management
   - User Profile Setup

2. **Features**:
   - Clean, medical-themed UI
   - Offline capability for basic features
   - Push notifications for reminders
   - Medicine search and lookup

### **AI/ML Components**
1. **NLP Model**: 
   - Start with rule-based extraction
   - Upgrade to BioBERT for better accuracy
   - Medicine name standardization

2. **Recommendation Engine**:
   - Rule-based alternative suggestions
   - Cost-effectiveness scoring
   - Safety rating system

---

## ✅ Success Criteria

### **Functional Requirements**
- [ ] Extract medicine names from 80%+ of test prescriptions
- [ ] Correctly identify dosage and frequency 90%+ of the time
- [ ] Provide at least 2 alternatives per medicine
- [ ] Send timely medication reminders
- [ ] Store and retrieve user medical history
- [ ] Detect 20+ common drug interactions

### **Performance Requirements**
- [ ] Prescription analysis < 3 seconds
- [ ] Medicine lookup < 1 second
- [ ] App startup < 2 seconds
- [ ] Offline mode for critical features

### **User Experience**
- [ ] Intuitive prescription input process
- [ ] Clear medicine information display
- [ ] Easy reminder setup and management
- [ ] Accessible design for elderly users

---

## 🚫 MVP Limitations (Out of Scope)

### **Features NOT in MVP**
1. **Image Recognition**: OCR for prescription images (Phase 2)
2. **Doctor Integration**: Direct doctor consultation (Future)
3. **Pharmacy Integration**: Direct medicine ordering (Future)
4. **Advanced AI**: Complex ML recommendations (Phase 2)
5. **Wearable Integration**: Smartwatch reminders (Future)
6. **Multi-language**: English only for MVP
7. **Insurance**: Insurance coverage checking (Future)

### **Technical Limitations**
1. **Prescription Complexity**: Handle simple prescriptions only
2. **Medicine Database**: Limited to common medicines initially
3. **Interactions**: Basic interactions only, not comprehensive
4. **Dosage Calculations**: Standard adult dosages, no pediatric
5. **Medical Advice**: Information only, no medical advice

---

## 📊 MVP Data Requirements

### **Medicine Database (Minimum)**
- **500+ common medicines** with:
  - Generic and brand names
  - Standard dosages
  - Common indications
  - Basic side effects
  - 2-3 alternatives each

### **Test Data**
- **100+ sample prescriptions** for testing
- **20+ drug interaction pairs**
- **User personas** for testing different scenarios

### **Data Sources**
- DrugBank (medicine information)
- OpenFDA (safety data)
- Manual curation for alternatives
- Synthetic prescriptions for testing

---

## 🎯 MVP User Stories

### **As a Patient, I want to:**
1. **Input my prescription** so that I understand what medicines I need to take
2. **See medicine details** so that I know what each medicine does
3. **Get dosage reminders** so that I don't forget to take my medicines
4. **Find cheaper alternatives** so that I can save money on medicines
5. **Check for side effects** so that I know what to expect
6. **Store my medicine history** so that I can track what I've taken

### **As the System, I need to:**
1. **Extract medicine information** from prescription text accurately
2. **Provide reliable medicine data** from trusted sources
3. **Send timely reminders** to improve medication adherence
4. **Warn about interactions** to prevent harmful combinations
5. **Suggest alternatives** to help users save money
6. **Maintain user privacy** and secure medical data

---

## 🔄 MVP Validation Plan

### **Week 1-2: Core Development**
- Build basic NLP extraction
- Set up medicine database
- Create core API endpoints

### **Week 3: Integration Testing**
- Test prescription analysis accuracy
- Validate medicine lookup performance
- Test reminder system functionality

### **Week 4: User Testing**
- Test with 10+ sample prescriptions
- Validate user experience flow
- Gather feedback on UI/UX

---

**MVP Goal**: A working system that can take a simple prescription text, extract medicine information, provide basic guidance, and send medication reminders - all in a clean, user-friendly mobile app.

**Success Metric**: 80% accuracy in prescription processing + positive user feedback on core functionality.
