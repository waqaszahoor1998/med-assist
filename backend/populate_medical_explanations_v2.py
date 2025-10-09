#!/usr/bin/env python3
"""
Enhanced script to populate medical explanations in the Django database
using multiple data sources and generating meaningful explanations.
"""

import os
import sys
import django
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_assistant.settings')
django.setup()

from api.models import Medicine, MedicalKnowledge

def generate_medical_explanation(medicine_data, medical_knowledge=None):
    """Generate a comprehensive medical explanation from available data"""
    
    explanation_parts = []
    
    # Add basic description if available
    if medicine_data.get('description') and len(medicine_data['description']) > 20:
        explanation_parts.append(f"**Description:** {medicine_data['description']}")
    
    # Add category information
    if medicine_data.get('category'):
        explanation_parts.append(f"**Category:** {medicine_data['category']}")
    
    # Add generic name if different from name
    if medicine_data.get('generic_name') and medicine_data['generic_name'] != medicine_data.get('name'):
        explanation_parts.append(f"**Generic Name:** {medicine_data['generic_name']}")
    
    # Add common doses if available
    if medicine_data.get('common_doses'):
        doses = medicine_data['common_doses']
        if isinstance(doses, list) and doses:
            doses_text = ', '.join([str(d) for d in doses[:3]])  # First 3 doses
            explanation_parts.append(f"**Common Doses:** {doses_text}")
        elif isinstance(doses, str) and len(doses) > 5:
            explanation_parts.append(f"**Common Doses:** {doses}")
    
    # Add side effects if available
    if medicine_data.get('side_effects'):
        side_effects = medicine_data['side_effects']
        if isinstance(side_effects, list) and side_effects:
            effects_text = ', '.join([str(e) for e in side_effects[:5]])  # First 5 effects
            explanation_parts.append(f"**Common Side Effects:** {effects_text}")
        elif isinstance(side_effects, str) and len(side_effects) > 10:
            explanation_parts.append(f"**Side Effects:** {side_effects}")
    
    # Add interactions if available
    if medicine_data.get('interactions'):
        interactions = medicine_data['interactions']
        if isinstance(interactions, list) and interactions:
            interactions_text = ', '.join([str(i) for i in interactions[:3]])  # First 3 interactions
            explanation_parts.append(f"**Drug Interactions:** {interactions_text}")
        elif isinstance(interactions, str) and len(interactions) > 10:
            explanation_parts.append(f"**Interactions:** {interactions}")
    
    # Add alternatives if available
    if medicine_data.get('alternatives'):
        alternatives = medicine_data['alternatives']
        if isinstance(alternatives, list) and alternatives:
            alt_text = ', '.join([str(a) for a in alternatives[:3]])  # First 3 alternatives
            explanation_parts.append(f"**Alternative Medicines:** {alt_text}")
    
    # Add medical knowledge if available
    if medical_knowledge:
        explanation_parts.append(f"**Medical Information:** {medical_knowledge['explanation']}")
    
    # Generate basic explanation for common medicine types
    medicine_name = medicine_data.get('name', '').lower()
    
    # Add type-specific information
    if 'acetaminophen' in medicine_name or 'paracetamol' in medicine_name:
        explanation_parts.append("**Mechanism:** Acetaminophen is an analgesic and antipyretic that works by inhibiting prostaglandin synthesis in the central nervous system.")
        explanation_parts.append("**Usage:** Commonly used for pain relief and fever reduction. Safe for most patients when used as directed.")
    
    elif 'ibuprofen' in medicine_name:
        explanation_parts.append("**Mechanism:** Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID) that reduces inflammation, pain, and fever by blocking COX enzymes.")
        explanation_parts.append("**Usage:** Used for pain relief, inflammation reduction, and fever. Should be taken with food to reduce stomach irritation.")
    
    elif 'aspirin' in medicine_name:
        explanation_parts.append("**Mechanism:** Aspirin is an NSAID that inhibits COX enzymes and has antiplatelet effects.")
        explanation_parts.append("**Usage:** Used for pain relief, fever reduction, and cardiovascular protection. Low-dose aspirin is commonly used for heart attack prevention.")
    
    elif 'metformin' in medicine_name:
        explanation_parts.append("**Mechanism:** Metformin is a biguanide antidiabetic drug that decreases glucose production in the liver and improves insulin sensitivity.")
        explanation_parts.append("**Usage:** First-line treatment for type 2 diabetes. Helps control blood sugar levels and may aid in weight management.")
    
    elif 'amlodipine' in medicine_name:
        explanation_parts.append("**Mechanism:** Amlodipine is a calcium channel blocker that relaxes blood vessels and reduces blood pressure.")
        explanation_parts.append("**Usage:** Used to treat high blood pressure and chest pain (angina). Works by preventing calcium from entering heart and blood vessel cells.")
    
    elif 'lisinopril' in medicine_name:
        explanation_parts.append("**Mechanism:** Lisinopril is an ACE inhibitor that relaxes blood vessels by blocking the conversion of angiotensin I to angiotensin II.")
        explanation_parts.append("**Usage:** Used to treat high blood pressure, heart failure, and to improve survival after heart attacks.")
    
    elif 'atorvastatin' in medicine_name or 'simvastatin' in medicine_name or 'statin' in medicine_name:
        explanation_parts.append("**Mechanism:** Statins inhibit HMG-CoA reductase, reducing cholesterol production in the liver.")
        explanation_parts.append("**Usage:** Used to lower cholesterol levels and reduce the risk of heart disease and stroke.")
    
    # Add general medical advice
    explanation_parts.append("**Important:** Always follow your doctor's instructions and dosage recommendations. Consult your healthcare provider if you experience any unusual side effects.")
    
    return '\n\n'.join(explanation_parts) if explanation_parts else None

def populate_medical_explanations():
    """Populate medical explanations from multiple sources"""
    
    print("Loading medical knowledge database...")
    
    # Load medical knowledge
    medical_knowledge_lookup = {}
    try:
        knowledge_entries = MedicalKnowledge.objects.all()
        for entry in knowledge_entries:
            medical_knowledge_lookup[entry.term.lower()] = {
                'explanation': entry.explanation,
                'category': entry.category
            }
        print(f"Loaded {len(medical_knowledge_lookup)} medical knowledge entries")
    except Exception as e:
        print(f"Error loading medical knowledge: {e}")
    
    # Get all medicines from Django database
    django_medicines = Medicine.objects.all()
    print(f"Found {django_medicines.count()} medicines in Django database")
    
    updated_count = 0
    
    for medicine in django_medicines:
        # Prepare medicine data
        medicine_data = {
            'name': medicine.name,
            'generic_name': medicine.generic_name,
            'category': medicine.category,
            'description': medicine.description,
            'common_doses': medicine.common_doses,
            'side_effects': medicine.side_effects,
            'interactions': medicine.interactions,
            'alternatives': medicine.alternatives
        }
        
        # Look up medical knowledge
        medical_knowledge = None
        for term in [medicine.name.lower(), medicine.generic_name or '']:
            if term and term in medical_knowledge_lookup:
                medical_knowledge = medical_knowledge_lookup[term]
                break
        
        # Generate explanation
        explanation = generate_medical_explanation(medicine_data, medical_knowledge)
        
        if explanation and len(explanation) > 50:  # Only save if meaningful
            medicine.medical_explanation = explanation
            medicine.save()
            updated_count += 1
            
            if updated_count % 100 == 0:
                print(f"Updated {updated_count} medicines...")
    
    print(f"\n=== Population Complete ===")
    print(f"Updated medicines: {updated_count}")
    
    # Verify the results
    medicines_with_explanations = Medicine.objects.exclude(
        medical_explanation__isnull=True
    ).exclude(medical_explanation='').count()
    
    total_medicines = Medicine.objects.count()
    coverage = (medicines_with_explanations / total_medicines * 100) if total_medicines > 0 else 0
    
    print(f"Total medicines: {total_medicines}")
    print(f"With explanations: {medicines_with_explanations}")
    print(f"Coverage: {coverage:.1f}%")

if __name__ == '__main__':
    populate_medical_explanations()
