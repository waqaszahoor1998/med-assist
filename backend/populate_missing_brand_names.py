#!/usr/bin/env python3
"""
Populate missing brand names and merge duplicate medicine entries in the database.
"""

import json
import os

def populate_missing_brand_names():
    """Add missing brand names to medicines and merge duplicates"""
    
    print("POPULATING MISSING BRAND NAMES AND MERGING DUPLICATES")
    print("=" * 60)
    
    # Load the ultimate database
    db_path = "../datasets/processed/ultimate_medicine_database.json"
    with open(db_path, 'r') as f:
        data = json.load(f)
    
    medicines = data['medicines']
    print(f"Loaded {len(medicines)} medicines")
    
    # Medicine brand name mappings (common names that should be added)
    brand_name_additions = {
        'acetylsalicylic acid': [
            'Aspirin', 'Bufferin', 'Bayer Aspirin', 'Ecotrin', 'ASA'
        ],
        'acetaminophen': [
            'Tylenol', 'Panadol', 'Calpol', 'Tempra', 'APAP', 'Paracetamol'
        ],
        'ibuprofen': [
            'Advil', 'Motrin', 'Nurofen', 'Brufen', 'Ibuprofen'
        ],
        'metformin': [
            'Glucophage', 'Fortamet', 'Glumetza', 'Riomet'
        ],
        'naproxen': [
            'Aleve', 'Naprosyn', 'Anaprox', 'Naprelan'
        ]
    }
    
    # Find and update medicines
    updated_count = 0
    for medicine in medicines:
        name = medicine.get('name', '').lower()
        generic_name = medicine.get('generic_name', '').lower()
        
        # Check if this medicine needs brand name updates
        for med_key, brand_names in brand_name_additions.items():
            if name == med_key or generic_name == med_key:
                current_brands = medicine.get('brand_names', [])
                
                # Convert to lowercase for comparison
                current_brands_lower = [str(b).lower() for b in current_brands]
                
                # Add missing brand names
                new_brands = []
                for brand in brand_names:
                    if brand.lower() not in current_brands_lower:
                        new_brands.append(brand)
                
                if new_brands:
                    medicine['brand_names'] = current_brands + new_brands
                    print(f"Updated {medicine.get('name')}: Added brands {new_brands}")
                    updated_count += 1
                
                break
    
    # Find and merge duplicate entries (Paracetamol -> Acetaminophen)
    print(f"\nLooking for duplicate entries to merge...")
    
    # Find Paracetamol entry
    paracetamol_entry = None
    acetaminophen_entry = None
    
    for medicine in medicines:
        name = medicine.get('name', '').lower()
        if name == 'paracetamol':
            paracetamol_entry = medicine
        elif name == 'acetaminophen':
            acetaminophen_entry = medicine
    
    if paracetamol_entry and acetaminophen_entry:
        print(f"Found Paracetamol entry, merging with Acetaminophen...")
        
        # Merge brand names from Paracetamol to Acetaminophen
        paracetamol_brands = paracetamol_entry.get('brand_names', [])
        acetaminophen_brands = acetaminophen_entry.get('brand_names', [])
        
        # Add Paracetamol brands to Acetaminophen if not already present
        for brand in paracetamol_brands:
            if brand not in acetaminophen_brands:
                acetaminophen_brands.append(brand)
        
        acetaminophen_entry['brand_names'] = acetaminophen_brands
        
        # Remove the duplicate Paracetamol entry
        medicines.remove(paracetamol_entry)
        
        print(f"Merged Paracetamol brands into Acetaminophen: {paracetamol_brands}")
        updated_count += 1
    
    # Update database metadata
    data['last_updated'] = '2025-01-27'
    data['version'] = '2.2'
    data['brand_names_enhanced'] = True
    
    # Save the updated database
    with open(db_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nUpdated database saved: {db_path}")
    print(f"Total updates: {updated_count}")
    
    # Show statistics
    with_brand_names = sum(1 for med in medicines if med.get('brand_names'))
    with_synonyms = sum(1 for med in medicines if med.get('synonyms'))
    
    print(f"\nUpdated Statistics:")
    print(f"  Medicines with brand names: {with_brand_names}")
    print(f"  Medicines with synonyms: {with_synonyms}")
    print(f"  Total medicines: {len(medicines)}")
    
    return db_path

if __name__ == "__main__":
    populate_missing_brand_names()
