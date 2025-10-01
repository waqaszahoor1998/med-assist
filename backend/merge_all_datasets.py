#!/usr/bin/env python3
"""
Merge all unused datasets into the comprehensive database to create the ultimate medicine database.
"""

import json
import os
from collections import defaultdict

def load_json_file(filepath):
    """Load JSON file safely"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def merge_datasets():
    """Merge all datasets into one comprehensive database"""
    
    print("MERGING ALL DATASETS INTO COMPREHENSIVE DATABASE")
    print("=" * 60)
    
    # Load the main comprehensive database
    comprehensive_path = "../datasets/processed/comprehensive_medicine_database.json"
    print(f"Loading main database: {comprehensive_path}")
    main_data = load_json_file(comprehensive_path)
    
    if not main_data:
        print("ERROR: Could not load main comprehensive database!")
        return
    
    main_medicines = {med['name'].lower(): med for med in main_data['medicines']}
    print(f"Main database: {len(main_medicines)} medicines")
    
    # Load enhanced database (API-enhanced data)
    enhanced_path = "../datasets/processed/enhanced_medicine_database.json"
    print(f"Loading enhanced database: {enhanced_path}")
    enhanced_data = load_json_file(enhanced_path)
    
    if enhanced_data:
        enhanced_medicines = {med['name'].lower(): med for med in enhanced_data['medicines']}
        print(f"Enhanced database: {len(enhanced_medicines)} medicines")
        
        # Merge enhanced data into main
        merge_count = 0
        for name, enhanced_med in enhanced_medicines.items():
            if name in main_medicines:
                main_med = main_medicines[name]
                
                # Add missing fields from enhanced database
                fields_to_add = [
                    'generic_name', 'brand_names', 'dosage_forms', 'common_doses',
                    'indications', 'warnings', 'max_daily_dose', 'frequency',
                    'category', 'chemical_structure'
                ]
                
                for field in fields_to_add:
                    if field in enhanced_med and enhanced_med[field] and (field not in main_med or not main_med[field]):
                        main_med[field] = enhanced_med[field]
                        merge_count += 1
                        
        print(f"Enhanced data merged: {merge_count} field updates")
    
    # Load drugbank structures
    structures_path = "../datasets/processed/drugbank_structures.json"
    print(f"Loading structures database: {structures_path}")
    structures_data = load_json_file(structures_path)
    
    if structures_data:
        structures = structures_data.get('structures', [])
        print(f"Structures database: {len(structures)} structures")
        
        # Create lookup for structures
        structure_lookup = {struct.get('name', '').lower(): struct for struct in structures}
        
        # Add missing structures to medicines
        structure_count = 0
        for name, med in main_medicines.items():
            if name in structure_lookup and not med.get('has_structure', False):
                structure = structure_lookup[name]
                med['has_structure'] = True
                med['chemical_structure'] = structure.get('structure', '')
                med['molecular_formula'] = structure.get('formula', '')
                med['molecular_weight'] = structure.get('weight', '')
                structure_count += 1
                
        print(f"Structures added: {structure_count} medicines")
    
    # Load drugbank parsed (detailed medical info)
    parsed_path = "../datasets/processed/drugbank_parsed.json"
    print(f"Loading parsed database: {parsed_path}")
    parsed_data = load_json_file(parsed_path)
    
    if parsed_data:
        parsed_medicines = {med['name'].lower(): med for med in parsed_data['medicines']}
        print(f"Parsed database: {len(parsed_medicines)} medicines")
        
        # Add detailed medical information
        medical_count = 0
        medical_fields = [
            'description', 'pharmacology', 'mechanism_of_action', 'toxicity',
            'metabolism', 'absorption', 'half_life', 'protein_binding',
            'route_of_elimination', 'volume_of_distribution', 'clearance',
            'food_interactions', 'drug_interactions', 'brands', 'manufacturers',
            'prices', 'fda_label', 'patents', 'targets', 'enzymes'
        ]
        
        for name, parsed_med in parsed_medicines.items():
            if name in main_medicines:
                main_med = main_medicines[name]
                
                for field in medical_fields:
                    if field in parsed_med and parsed_med[field] and (field not in main_med or not main_med[field]):
                        main_med[field] = parsed_med[field]
                        medical_count += 1
                        
        print(f"Medical data added: {medical_count} field updates")
    
    # Load all medicines (additional data)
    all_medicines_path = "../datasets/processed/all_medicines.json"
    print(f"Loading all medicines: {all_medicines_path}")
    all_medicines_data = load_json_file(all_medicines_path)
    
    if all_medicines_data:
        all_medicines = {med['name'].lower(): med for med in all_medicines_data}
        print(f"All medicines: {len(all_medicines)} medicines")
        
        # Add any missing medicines
        new_medicines = 0
        for name, med in all_medicines.items():
            if name not in main_medicines:
                main_medicines[name] = med
                new_medicines += 1
                
        print(f"New medicines added: {new_medicines}")
    
    # Convert back to list and create final database
    final_medicines = list(main_medicines.values())
    
    # Count statistics
    with_structures = sum(1 for med in final_medicines if med.get('has_structure', False))
    with_alternatives = sum(1 for med in final_medicines if med.get('alternatives'))
    with_medical_info = sum(1 for med in final_medicines if med.get('description'))
    
    # Create enhanced comprehensive database
    enhanced_comprehensive = {
        "version": "2.0",
        "source": "DrugBank + OpenFDA + RxNorm + SDF Structures + Enhanced Processing",
        "last_updated": "2025-01-27",
        "total_medicines": len(final_medicines),
        "with_structures": with_structures,
        "with_alternatives": with_alternatives,
        "with_medical_info": with_medical_info,
        "api_enhanced": True,
        "databases_merged": [
            "comprehensive_medicine_database.json",
            "enhanced_medicine_database.json", 
            "drugbank_structures.json",
            "drugbank_parsed.json",
            "all_medicines.json"
        ],
        "medicines": final_medicines
    }
    
    # Save the enhanced comprehensive database
    output_path = "../datasets/processed/ultimate_medicine_database.json"
    print(f"\nSaving ultimate database: {output_path}")
    
    with open(output_path, 'w') as f:
        json.dump(enhanced_comprehensive, f, indent=2)
    
    print("\n" + "=" * 60)
    print("ULTIMATE DATABASE CREATED!")
    print("=" * 60)
    print(f"Total medicines: {len(final_medicines):,}")
    print(f"With structures: {with_structures:,}")
    print(f"With alternatives: {with_alternatives:,}")
    print(f"With medical info: {with_medical_info:,}")
    print(f"Databases merged: {len(enhanced_comprehensive['databases_merged'])}")
    print(f"Output file: {output_path}")
    
    return output_path

if __name__ == "__main__":
    merge_datasets()
