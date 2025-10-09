#!/usr/bin/env python3
"""
Script to populate the medical knowledge database with real medical information
including conditions, symptoms, treatments, and medical concepts.
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_assistant.settings')
django.setup()

from api.models import MedicalKnowledge

def populate_real_medical_knowledge():
    """Populate medical knowledge database with comprehensive medical information"""
    
    # Clear existing brand name entries
    print("Clearing existing brand name entries...")
    MedicalKnowledge.objects.filter(category='Brand Name').delete()
    print("Cleared brand name entries")
    
    # Comprehensive medical knowledge data
    medical_knowledge_data = [
        # Cardiovascular Conditions
        {
            "term": "Hypertension",
            "explanation": "High blood pressure is a common condition where the force of blood against artery walls is consistently too high. Normal blood pressure is below 120/80 mmHg. Hypertension increases the risk of heart disease, stroke, and kidney disease. Treatment includes lifestyle changes (diet, exercise, weight management) and medications like ACE inhibitors, diuretics, and calcium channel blockers.",
            "category": "Cardiovascular Condition",
            "related_terms": ["High blood pressure", "Blood pressure", "Cardiovascular disease", "Heart disease"]
        },
        {
            "term": "High blood pressure",
            "explanation": "Also known as hypertension, this is a condition where blood pressure is consistently elevated above normal levels (140/90 mmHg or higher). It's often called the 'silent killer' because it typically has no symptoms until it causes serious health problems. Risk factors include age, family history, obesity, lack of exercise, high salt diet, and stress.",
            "category": "Cardiovascular Condition",
            "related_terms": ["Hypertension", "Blood pressure", "Cardiovascular disease"]
        },
        {
            "term": "Heart disease",
            "explanation": "A general term for conditions that affect the heart's structure and function. Includes coronary artery disease, heart failure, arrhythmias, and heart valve problems. Risk factors include smoking, diabetes, high cholesterol, high blood pressure, obesity, and family history. Symptoms may include chest pain, shortness of breath, fatigue, and irregular heartbeat.",
            "category": "Cardiovascular Condition",
            "related_terms": ["Cardiovascular disease", "Coronary artery disease", "Heart failure", "Cardiac condition"]
        },
        {
            "term": "Coronary artery disease",
            "explanation": "The most common type of heart disease, caused by atherosclerosis (plaque buildup in coronary arteries). This reduces blood flow to the heart muscle, potentially leading to chest pain (angina) or heart attack. Risk factors include high cholesterol, smoking, diabetes, high blood pressure, and sedentary lifestyle. Treatment includes medications, lifestyle changes, and procedures like angioplasty or bypass surgery.",
            "category": "Cardiovascular Condition",
            "related_terms": ["Heart disease", "Atherosclerosis", "Angina", "Heart attack"]
        },
        
        # Diabetes and Metabolic Conditions
        {
            "term": "Diabetes",
            "explanation": "A group of metabolic diseases characterized by high blood glucose levels. Type 1 diabetes is an autoimmune condition where the pancreas produces little or no insulin. Type 2 diabetes is more common and occurs when the body becomes resistant to insulin or doesn't produce enough. Symptoms include increased thirst, frequent urination, fatigue, and slow-healing wounds. Management includes blood glucose monitoring, diet, exercise, and medications.",
            "category": "Metabolic Condition",
            "related_terms": ["Type 1 diabetes", "Type 2 diabetes", "Blood glucose", "Insulin", "Hyperglycemia"]
        },
        {
            "term": "Type 2 diabetes",
            "explanation": "The most common form of diabetes, affecting how the body processes glucose. The body becomes resistant to insulin or doesn't produce enough insulin. Risk factors include obesity, family history, age, and sedentary lifestyle. Symptoms develop gradually and may include increased thirst, frequent urination, fatigue, blurred vision, and slow-healing wounds. Treatment focuses on lifestyle changes, blood glucose monitoring, and medications like metformin.",
            "category": "Metabolic Condition",
            "related_terms": ["Diabetes", "Insulin resistance", "Blood glucose", "Metformin", "Hyperglycemia"]
        },
        {
            "term": "Hyperglycemia",
            "explanation": "High blood glucose levels, typically above 126 mg/dL when fasting or above 200 mg/dL after eating. Common in diabetes but can occur in other conditions. Symptoms include increased thirst, frequent urination, fatigue, blurred vision, and headache. Severe hyperglycemia can lead to diabetic ketoacidosis (DKA) in type 1 diabetes or hyperosmolar hyperglycemic state (HHS) in type 2 diabetes.",
            "category": "Metabolic Condition",
            "related_terms": ["High blood sugar", "Diabetes", "Blood glucose", "DKA", "HHS"]
        },
        
        # Respiratory Conditions
        {
            "term": "Asthma",
            "explanation": "A chronic respiratory condition characterized by inflammation and narrowing of airways, causing breathing difficulties. Symptoms include wheezing, shortness of breath, chest tightness, and coughing. Triggers include allergens, exercise, cold air, stress, and respiratory infections. Treatment includes bronchodilators (rescue inhalers) and anti-inflammatory medications (controller medications).",
            "category": "Respiratory Condition",
            "related_terms": ["Wheezing", "Bronchospasm", "Airway inflammation", "Rescue inhaler", "Controller medication"]
        },
        {
            "term": "COPD",
            "explanation": "Chronic Obstructive Pulmonary Disease is a group of lung diseases that block airflow and make breathing difficult. Includes emphysema and chronic bronchitis. Most commonly caused by smoking. Symptoms include shortness of breath, chronic cough with mucus, wheezing, and chest tightness. Treatment includes bronchodilators, corticosteroids, oxygen therapy, and smoking cessation.",
            "category": "Respiratory Condition",
            "related_terms": ["Chronic bronchitis", "Emphysema", "Lung disease", "Smoking", "Bronchodilators"]
        },
        
        # Mental Health Conditions
        {
            "term": "Depression",
            "explanation": "A mood disorder characterized by persistent sadness, hopelessness, and loss of interest in activities. Symptoms include low mood, fatigue, changes in sleep and appetite, difficulty concentrating, and thoughts of death or suicide. Risk factors include genetics, life events, medical conditions, and substance abuse. Treatment includes psychotherapy, medications (antidepressants), and lifestyle changes.",
            "category": "Mental Health Condition",
            "related_terms": ["Major depressive disorder", "Mood disorder", "Antidepressants", "Psychotherapy", "Mental health"]
        },
        {
            "term": "Anxiety",
            "explanation": "A mental health condition characterized by excessive worry, fear, or nervousness that interferes with daily life. Types include generalized anxiety disorder, panic disorder, and social anxiety disorder. Symptoms include restlessness, fatigue, difficulty concentrating, irritability, muscle tension, and sleep problems. Treatment includes therapy, medications (antidepressants, benzodiazepines), and stress management techniques.",
            "category": "Mental Health Condition",
            "related_terms": ["Generalized anxiety disorder", "Panic disorder", "Social anxiety", "Stress", "Mental health"]
        },
        
        # Pain and Inflammation
        {
            "term": "Arthritis",
            "explanation": "Inflammation of one or more joints, causing pain, stiffness, and decreased range of motion. The two most common types are osteoarthritis (wear and tear) and rheumatoid arthritis (autoimmune). Symptoms include joint pain, stiffness, swelling, and reduced mobility. Treatment includes pain medications, anti-inflammatory drugs, physical therapy, and in severe cases, surgery.",
            "category": "Musculoskeletal Condition",
            "related_terms": ["Joint inflammation", "Osteoarthritis", "Rheumatoid arthritis", "Joint pain", "Anti-inflammatory"]
        },
        {
            "term": "Migraine",
            "explanation": "A neurological condition characterized by severe, recurring headaches often accompanied by nausea, vomiting, and sensitivity to light and sound. Migraines can last hours to days and significantly impact daily life. Triggers include stress, certain foods, hormonal changes, and environmental factors. Treatment includes pain medications, preventive medications, and lifestyle modifications.",
            "category": "Neurological Condition",
            "related_terms": ["Headache", "Neurological disorder", "Pain management", "Triggers", "Preventive treatment"]
        },
        
        # Common Symptoms
        {
            "term": "Fever",
            "explanation": "An elevated body temperature above the normal range (98.6°F or 37°C). Often indicates infection or inflammation. Symptoms include elevated temperature, chills, sweating, headache, and muscle aches. Treatment depends on the underlying cause and may include antipyretics (fever reducers) like acetaminophen or ibuprofen, rest, and fluids.",
            "category": "Symptom",
            "related_terms": ["Elevated temperature", "Infection", "Inflammation", "Antipyretics", "Body temperature"]
        },
        {
            "term": "Cough",
            "explanation": "A reflex action to clear the airways of mucus, irritants, or foreign particles. Can be acute (short-term) or chronic (long-term). Types include dry cough, productive cough (with mucus), and whooping cough. Common causes include colds, flu, allergies, asthma, and smoking. Treatment depends on the cause and may include cough suppressants, expectorants, or addressing the underlying condition.",
            "category": "Symptom",
            "related_terms": ["Respiratory symptom", "Mucus", "Irritation", "Cold", "Flu"]
        },
        {
            "term": "Headache",
            "explanation": "Pain or discomfort in the head or neck area. Can be primary (tension, migraine, cluster) or secondary (caused by another condition). Symptoms vary by type but may include throbbing pain, pressure, sensitivity to light/sound, and nausea. Treatment includes pain medications, rest, stress management, and identifying triggers.",
            "category": "Symptom",
            "related_terms": ["Head pain", "Migraine", "Tension headache", "Pain management", "Triggers"]
        },
        
        # Medications and Treatments
        {
            "term": "Antibiotics",
            "explanation": "Medications that fight bacterial infections by killing bacteria or stopping their growth. They are not effective against viral infections. Common types include penicillins, cephalosporins, macrolides, and fluoroquinolones. Important to take as prescribed and complete the full course to prevent antibiotic resistance. Side effects may include nausea, diarrhea, and allergic reactions.",
            "category": "Medication Class",
            "related_terms": ["Bacterial infection", "Antimicrobial", "Antibiotic resistance", "Prescription medication", "Side effects"]
        },
        {
            "term": "Pain relievers",
            "explanation": "Medications used to reduce or eliminate pain. Include acetaminophen (Tylenol), NSAIDs like ibuprofen and aspirin, and opioid medications. Acetaminophen is effective for mild to moderate pain and fever. NSAIDs also reduce inflammation. Opioids are for severe pain but carry risk of dependence. Important to follow dosing instructions and be aware of potential side effects.",
            "category": "Medication Class",
            "related_terms": ["Analgesics", "Acetaminophen", "NSAIDs", "Opioids", "Pain management"]
        },
        {
            "term": "Blood pressure medications",
            "explanation": "Medications used to treat hypertension and protect against heart disease and stroke. Include ACE inhibitors, ARBs, diuretics, beta-blockers, and calcium channel blockers. Each class works differently to lower blood pressure. Side effects vary by medication class. Often requires combination therapy and regular monitoring to achieve target blood pressure.",
            "category": "Medication Class",
            "related_terms": ["Hypertension", "ACE inhibitors", "Diuretics", "Beta-blockers", "Cardiovascular protection"]
        },
        
        # Lifestyle and Prevention
        {
            "term": "Exercise",
            "explanation": "Physical activity that improves or maintains physical fitness and overall health. Benefits include improved cardiovascular health, weight management, bone strength, mental health, and reduced risk of chronic diseases. Recommended: 150 minutes of moderate-intensity aerobic activity per week plus muscle-strengthening activities. Important to start gradually and choose activities you enjoy.",
            "category": "Lifestyle Factor",
            "related_terms": ["Physical activity", "Fitness", "Cardiovascular health", "Weight management", "Mental health"]
        },
        {
            "term": "Healthy diet",
            "explanation": "A balanced diet that provides essential nutrients while limiting harmful substances. Key components include fruits, vegetables, whole grains, lean proteins, and healthy fats. Limit processed foods, added sugars, sodium, and saturated fats. Benefits include reduced risk of heart disease, diabetes, and certain cancers. Consider portion control and regular meal timing.",
            "category": "Lifestyle Factor",
            "related_terms": ["Nutrition", "Balanced diet", "Nutrients", "Heart disease prevention", "Weight management"]
        },
        {
            "term": "Stress management",
            "explanation": "Techniques and strategies to cope with and reduce stress in daily life. Chronic stress can negatively impact physical and mental health. Effective strategies include relaxation techniques (deep breathing, meditation), regular exercise, adequate sleep, time management, social support, and professional counseling when needed. Important for overall well-being and disease prevention.",
            "category": "Lifestyle Factor",
            "related_terms": ["Mental health", "Relaxation", "Meditation", "Coping strategies", "Well-being"]
        }
    ]
    
    print(f"Adding {len(medical_knowledge_data)} medical knowledge entries...")
    
    created_count = 0
    for entry_data in medical_knowledge_data:
        # Create or update medical knowledge entry
        entry, created = MedicalKnowledge.objects.get_or_create(
            term=entry_data['term'],
            defaults={
                'explanation': entry_data['explanation'],
                'category': entry_data['category'],
                'related_terms': entry_data['related_terms'],
                'source': 'Medical Knowledge Database'
            }
        )
        
        if created:
            created_count += 1
        
        # Update existing entries with better information
        if not created and len(entry.explanation) < len(entry_data['explanation']):
            entry.explanation = entry_data['explanation']
            entry.category = entry_data['category']
            entry.related_terms = entry_data['related_terms']
            entry.source = 'Medical Knowledge Database'
            entry.save()
            created_count += 1
    
    print(f"Created/updated {created_count} medical knowledge entries")
    
    # Verify the results
    total_entries = MedicalKnowledge.objects.count()
    categories = MedicalKnowledge.objects.values_list('category', flat=True).distinct()
    
    print(f"\n=== Medical Knowledge Database Updated ===")
    print(f"Total entries: {total_entries}")
    print(f"Categories: {list(categories)}")
    
    # Show sample entries
    print("\nSample medical knowledge entries:")
    samples = MedicalKnowledge.objects.exclude(category='Brand Name')[:5]
    for entry in samples:
        print(f"- {entry.term} ({entry.category}): {entry.explanation[:100]}...")

if __name__ == '__main__':
    populate_real_medical_knowledge()
