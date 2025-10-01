#!/usr/bin/env python3
"""
Fix missing data for common medicines in the ultimate database.
"""

import json
import os

def fix_common_medicines():
    """Fix missing categories and alternatives for common medicines"""
    
    print("FIXING MISSING DATA FOR COMMON MEDICINES")
    print("=" * 50)
    
    # Load the ultimate database
    db_path = "../datasets/processed/ultimate_medicine_database.json"
    with open(db_path, 'r') as f:
        data = json.load(f)
    
    medicines = data['medicines']
    print(f"Loaded {len(medicines)} medicines")
    
    # Common medicine fixes
    medicine_fixes = {
        'acetylsalicylic acid': {
            'categories': 'analgesic',
            'alternatives': 'Ibuprofen, Paracetamol, Naproxen, Celecoxib',
            'generic_name': 'Acetylsalicylic Acid',
            'brand_names': 'Aspirin, Bufferin, Bayer Aspirin, Ecotrin',
            'common_doses': '81mg, 325mg, 500mg',
            'indications': 'Pain relief, fever reduction, anti-inflammatory, blood thinner'
        },
        'acetaminophen': {
            'categories': 'analgesic',
            'alternatives': 'Ibuprofen, Aspirin, Naproxen, Codeine',
            'generic_name': 'Acetaminophen',
            'brand_names': 'Tylenol, Panadol, Paracetamol, Tempra',
            'common_doses': '325mg, 500mg, 650mg',
            'indications': 'Pain relief, fever reduction'
        },
        'paracetamol': {
            'categories': 'analgesic',
            'alternatives': 'Ibuprofen, Aspirin, Naproxen, Codeine',
            'generic_name': 'Paracetamol',
            'brand_names': 'Tylenol, Panadol, Acetaminophen, Tempra',
            'common_doses': '325mg, 500mg, 650mg',
            'indications': 'Pain relief, fever reduction'
        },
        'ibuprofen': {
            'categories': 'analgesic',
            'alternatives': 'Aspirin, Paracetamol, Naproxen, Celecoxib',
            'generic_name': 'Ibuprofen',
            'brand_names': 'Advil, Motrin, Nurofen, Brufen',
            'common_doses': '200mg, 400mg, 600mg, 800mg',
            'indications': 'Pain relief, fever reduction, anti-inflammatory'
        },
        'naproxen': {
            'categories': 'analgesic',
            'alternatives': 'Ibuprofen, Aspirin, Paracetamol, Celecoxib',
            'generic_name': 'Naproxen',
            'brand_names': 'Aleve, Naprosyn, Anaprox, Naprelan',
            'common_doses': '220mg, 375mg, 500mg',
            'indications': 'Pain relief, anti-inflammatory'
        },
        'metformin': {
            'categories': 'antidiabetic',
            'alternatives': 'Insulin, Glipizide, Glyburide, Sitagliptin, Pioglitazone',
            'generic_name': 'Metformin',
            'brand_names': 'Glucophage, Fortamet, Glumetza, Riomet',
            'common_doses': '500mg, 750mg, 850mg, 1000mg',
            'indications': 'Type 2 diabetes management, blood sugar control'
        }
    }
    
    fixed_count = 0
    for medicine in medicines:
        name = medicine.get('name', '').lower()
        
        # Check if this medicine needs fixing
        for fix_key, fix_data in medicine_fixes.items():
            if fix_key in name or medicine.get('generic_name', '').lower() == fix_key:
                print(f"Fixing: {medicine.get('name', 'Unknown')}")
                
                # Apply fixes
                for field, value in fix_data.items():
                    if field not in medicine or not medicine[field]:
                        medicine[field] = value
                        fixed_count += 1
                        print(f"  Added {field}: {value}")
                
                print()
                break
    
    print(f"Total fixes applied: {fixed_count}")
    
    # Update database metadata
    data['last_updated'] = '2025-01-27'
    data['version'] = '2.1'
    data['common_medicines_fixed'] = True
    
    # Save the updated database
    with open(db_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated database saved: {db_path}")
    
    # Show statistics
    with_alternatives = sum(1 for med in medicines if med.get('alternatives'))
    with_categories = sum(1 for med in medicines if med.get('categories'))
    
    print(f"\nUpdated Statistics:")
    print(f"  Medicines with alternatives: {with_alternatives}")
    print(f"  Medicines with categories: {with_categories}")
    
    return db_path

if __name__ == "__main__":
    fix_common_medicines()
