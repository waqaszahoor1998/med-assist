# AI-Based Post Diagnosis Medicine Assistant - Development Plan

## 20-Day Development Timeline

### **Phase 1: Setup & Requirements (Day 1–3)**

#### **Day 1: Project Foundation**
- [x] Set up GitHub repository
- [x] Create project structure
- [ ] Set up development environment (Flutter, Django, DB)
- [ ] Define MVP scope (input prescription → output medicine details + reminder)

#### **Day 2: Data Collection**
- [ ] Collect datasets: DrugBank / OpenFDA (medicines, dosages, side effects)
- [ ] Prepare synthetic prescription dataset for NLP testing
- [ ] Set up basic data preprocessing pipeline

#### **Day 3: Architecture Design**
- [ ] Finalize system architecture (draw diagrams)
- [ ] Set up Django backend starter
- [ ] Set up Flutter starter app
- [ ] Create simple API endpoints structure

---

### **Phase 2: AI Core Development (Day 4–9)**

#### **Day 4–5: NLP Pipeline**
- [ ] Implement NLP pipeline (HuggingFace BioBERT or simple NER first)
- [ ] Extract medicine names + dosage from text
- [ ] Test with sample prescriptions

#### **Day 6: Medicine Database**
- [ ] Build basic medicine database (SQLite/Postgres) with medicine info & side effects
- [ ] Include basic medicine interaction checking logic

#### **Day 7–8: Recommendation System**
- [ ] Create recommendation logic: if medicine X → suggest alternatives & cost-effective options (rule-based first)
- [ ] Implement cost comparison logic

#### **Day 9: Safety Checks**
- [ ] Implement safety check (lookup side effects + harmful interactions)
- [ ] Create alert system for dangerous combinations

---

### **Phase 3: App & Backend Features (Day 10–15)**

#### **Day 10–11: Flutter UI**
- [ ] Flutter UI: screen for entering prescription / medicine
- [ ] Display results (name, dosage, purpose, side effects)
- [ ] Basic navigation and user flow

#### **Day 12: Reminder System**
- [ ] Add reminder/notification system (medicine intake alerts)
- [ ] Schedule management interface

#### **Day 13–14: User Profiling**
- [ ] Implement user profiling (store medical history in DB)
- [ ] Medical history tracking and analysis

#### **Day 15: Integration**
- [ ] Connect AI backend fully with Flutter app (end-to-end working MVP)
- [ ] Integration testing + bug fixing buffer

---

### **Phase 4: Testing, Refinement & Deployment (Day 16–20)**

#### **Day 16–17: Testing**
- [ ] Test NLP extraction accuracy
- [ ] Test recommendations against real dataset samples
- [ ] Validate safety checks

#### **Day 18: UI Polish**
- [ ] Polish Flutter UI (cleaner screens, better UX)
- [ ] Improve user experience and accessibility

#### **Day 19: Documentation**
- [ ] Write comprehensive documentation (project flow, AI explanation, diagrams)
- [ ] Create user guides and API documentation

#### **Day 20: Demo Preparation**
- [ ] Final demo prep → record a demo video or presentation with app flow
- [ ] Prepare presentation materials

---

## MVP Definition

### **Core Functionality**
1. **Input**: Patient prescription (text format initially)
2. **Processing**: NLP extraction + database lookup + rule-based recommendations
3. **Output**: 
   - Medicine name and purpose
   - Correct dosage (mg/gm/spoons)
   - Side effects and warnings
   - Alternative medicines (cost-effective)
   - Personalized reminder schedule

### **Success Criteria**
- [ ] Successfully extract medicine names from 80%+ of test prescriptions
- [ ] Provide accurate dosage recommendations
- [ ] Identify at least 2 alternatives per medicine
- [ ] Detect common drug interactions
- [ ] Send timely medication reminders
- [ ] Maintain user medical history

### **Technical Milestones**
- [ ] Working NLP pipeline
- [ ] Functional medicine database
- [ ] Flutter app with core screens
- [ ] Django API with all endpoints
- [ ] End-to-end data flow
- [ ] Basic AI recommendations

---

## Risk Mitigation

### **Potential Risks & Solutions**
1. **NLP Accuracy**: Start with rule-based extraction, improve iteratively
2. **Dataset Quality**: Use multiple sources (DrugBank + OpenFDA + manual curation)
3. **Integration Complexity**: Build and test incrementally
4. **Time Constraints**: Focus on MVP first, advanced features later

### **Fallback Plans**
- If BioBERT is too complex → Use simpler regex + keyword matching
- If Django is slow → Use Flask for faster prototyping
- If Flutter has issues → Build web-first, mobile later

---

**Last Updated**: Day 1
**Current Phase**: Phase 1 - Setup & Requirements
**Next Milestone**: Development environment setup
