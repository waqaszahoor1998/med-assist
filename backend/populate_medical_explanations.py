#!/usr/bin/env python3
"""
Script to populate medical explanations in the Django database
from the enhanced medicine database JSON file.
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

from api.models import Medicine

def populate_medical_explanations():
    """Populate medical explanations from enhanced database"""
    
    # Load the enhanced database
    enhanced_db_path = backend_dir.parent / 'datasets' / 'processed' / 'enhanced_ultimate_medicine_database.json'
    
    if not enhanced_db_path.exists():
        print(f"Enhanced database not found at: {enhanced_db_path}")
        return
    
    print("Loading enhanced database...")
    with open(enhanced_db_path, 'r') as f:
        enhanced_data = json.load(f)
    
    medicines_data = enhanced_data.get('medicines', [])
    print(f"Found {len(medicines_data)} medicines in enhanced database")
    
    # Create a lookup dictionary for faster access
    medicines_lookup = {}
    for medicine in medicines_data:
        medicines_lookup[medicine['name'].lower()] = medicine
    
    print(f"Created lookup for {len(medicines_lookup)} medicines")
    
    # Get all medicines from Django database
    django_medicines = Medicine.objects.all()
    print(f"Found {django_medicines.count()} medicines in Django database")
    
    updated_count = 0
    not_found_count = 0
    
    for medicine in django_medicines:
        # Look up the medicine in enhanced database
        enhanced_medicine = medicines_lookup.get(medicine.name.lower())
        
        if enhanced_medicine:
            # Create medical explanation from available data
            explanation_parts = []
            
            # Add description if available
            if enhanced_medicine.get('description'):
                explanation_parts.append(f"**Description:** {enhanced_medicine['description']}")
            
            # Add mechanism of action if available
            if enhanced_medicine.get('mechanism_of_action'):
                explanation_parts.append(f"**Mechanism of Action:** {enhanced_medicine['mechanism_of_action']}")
            
            # Add indications if available
            if enhanced_medicine.get('indications'):
                if isinstance(enhanced_medicine['indications'], list):
                    indications_text = ', '.join(enhanced_medicine['indications'])
                else:
                    indications_text = str(enhanced_medicine['indications'])
                explanation_parts.append(f"**Indications:** {indications_text}")
            
            # Add pharmacology if available
            if enhanced_medicine.get('pharmacology'):
                explanation_parts.append(f"**Pharmacology:** {enhanced_medicine['pharmacology']}")
            
            # Add pharmacokinetics if available
            if enhanced_medicine.get('pharmacokinetics'):
                explanation_parts.append(f"**Pharmacokinetics:** {enhanced_medicine['pharmacokinetics']}")
            
            # Add dosage information if available
            if enhanced_medicine.get('dosage'):
                explanation_parts.append(f"**Dosage:** {enhanced_medicine['dosage']}")
            
            # Add side effects if available
            if enhanced_medicine.get('side_effects'):
                if isinstance(enhanced_medicine['side_effects'], list):
                    side_effects_text = ', '.join(enhanced_medicine['side_effects'][:5])  # Limit to first 5
                else:
                    side_effects_text = str(enhanced_medicine['side_effects'])
                explanation_parts.append(f"**Side Effects:** {side_effects_text}")
            
            # Combine all parts
            if explanation_parts:
                medical_explanation = '\n\n'.join(explanation_parts)
                medicine.medical_explanation = medical_explanation
                medicine.save()
                updated_count += 1
                
                if updated_count % 100 == 0:
                    print(f"Updated {updated_count} medicines...")
        else:
            not_found_count += 1
    
    print(f"\n=== Population Complete ===")
    print(f"Updated medicines: {updated_count}")
    print(f"Not found in enhanced DB: {not_found_count}")
    
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
