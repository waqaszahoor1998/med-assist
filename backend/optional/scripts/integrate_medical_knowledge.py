#!/usr/bin/env python3
"""
Integrate medical knowledge from wiki dataset into our ultimate medicine database.
"""

import json
import os

def integrate_medical_knowledge():
    """Integrate wiki medical knowledge into our ultimate medicine database"""
    
    print("INTEGRATING MEDICAL KNOWLEDGE INTO ULTIMATE DATABASE")
    print("=" * 60)
    
    # Load the ultimate medicine database
    ultimate_db_path = "../datasets/processed/ultimate_medicine_database.json"
    with open(ultimate_db_path, 'r') as f:
        ultimate_db = json.load(f)
    
    # Load the medicine knowledge database
    medicine_knowledge_path = "../datasets/processed/medicine_knowledge_database.json"
    with open(medicine_knowledge_path, 'r') as f:
        medicine_knowledge = json.load(f)
    
    print(f"Ultimate database: {len(ultimate_db['medicines'])} medicines")
    print(f"Medicine knowledge: {len(medicine_knowledge['medicines'])} entries")
    
    # Create lookup for medicine knowledge
    knowledge_lookup = {}
    for term, data in medicine_knowledge['medicines'].items():
        # Create multiple lookup keys for better matching
        keys = [
            term.lower(),
            term.lower().replace(' poisoning', ''),
            term.lower().replace(' toxicity', ''),
            term.lower().replace(' syndrome', ''),
            term.lower().replace(' disease', ''),
            term.lower().replace(' disorder', '')
        ]
        
        for key in keys:
            knowledge_lookup[key] = data
    
    print(f"Created knowledge lookup with {len(knowledge_lookup)} keys")
    
    # Integrate knowledge into ultimate database
    enhanced_count = 0
    new_entries_count = 0
    
    # Track which medicines were enhanced
    enhanced_medicines = set()
    
    for medicine in ultimate_db['medicines']:
        medicine_name = medicine.get('name', '').lower()
        generic_name = medicine.get('generic_name', '').lower()
        
        # Try to find matching knowledge
        knowledge_entry = None
        
        # Try exact matches first
        if medicine_name in knowledge_lookup:
            knowledge_entry = knowledge_lookup[medicine_name]
        elif generic_name in knowledge_lookup:
            knowledge_entry = knowledge_lookup[generic_name]
        else:
            # Try partial matches
            for key, data in knowledge_lookup.items():
                if (medicine_name in key or key in medicine_name or
                    generic_name in key or key in generic_name):
                    knowledge_entry = data
                    break
        
        if knowledge_entry:
            # Enhance existing medicine with detailed knowledge
            medicine['detailed_medical_explanation'] = knowledge_entry['detailed_explanation']
            medicine['medical_knowledge_source'] = 'Wiki Medical Terms Dataset'
            medicine['knowledge_keywords'] = knowledge_entry['keywords']
            medicine['explanation_length'] = knowledge_entry['explanation_length']
            
            enhanced_count += 1
            enhanced_medicines.add(medicine_name)
            print(f"Enhanced: {medicine.get('name', 'Unknown')}")
    
    # Add new entries for medicines in knowledge database that aren't in ultimate database
    for term, knowledge_data in medicine_knowledge['medicines'].items():
        # Check if this term is already in ultimate database
        found = False
        for medicine in ultimate_db['medicines']:
            if (term.lower() in medicine.get('name', '').lower() or
                term.lower() in medicine.get('generic_name', '').lower()):
                found = True
                break
        
        if not found and is_direct_medicine(term, knowledge_data):
            # Create new medicine entry
            new_medicine = {
                'name': term.title(),
                'generic_name': term.title(),
                'detailed_medical_explanation': knowledge_data['detailed_explanation'],
                'medical_knowledge_source': 'Wiki Medical Terms Dataset',
                'knowledge_keywords': knowledge_data['keywords'],
                'explanation_length': knowledge_data['explanation_length'],
                'categories': 'medical_knowledge',
                'alternatives': 'Consult medical database for alternatives',
                'brand_names': [],
                'synonyms': [],
                'has_structure': False,
                'source': 'Wiki Medical Knowledge Integration'
            }
            
            ultimate_db['medicines'].append(new_medicine)
            new_entries_count += 1
            print(f"Added new: {term}")
    
    # Update database metadata
    ultimate_db['version'] = '3.0'
    ultimate_db['last_updated'] = '2025-01-27'
    ultimate_db['medical_knowledge_integrated'] = True
    ultimate_db['enhanced_medicines'] = enhanced_count
    ultimate_db['new_medicine_entries'] = new_entries_count
    ultimate_db['total_medicines'] = len(ultimate_db['medicines'])
    
    # Save enhanced ultimate database
    enhanced_db_path = "../datasets/processed/enhanced_ultimate_medicine_database.json"
    with open(enhanced_db_path, 'w') as f:
        json.dump(ultimate_db, f, indent=2)
    
    print(f"\nIntegration complete!")
    print(f"Enhanced medicines: {enhanced_count}")
    print(f"New medicine entries: {new_entries_count}")
    print(f"Total medicines in enhanced database: {len(ultimate_db['medicines'])}")
    print(f"Enhanced database saved to: {enhanced_db_path}")
    
    # Show statistics
    with_detailed_explanations = sum(1 for med in ultimate_db['medicines'] 
                                   if med.get('detailed_medical_explanation'))
    
    print(f"\nEnhanced Database Statistics:")
    print(f"  Total medicines: {len(ultimate_db['medicines']):,}")
    print(f"  With detailed explanations: {with_detailed_explanations:,}")
    print(f"  Enhanced from wiki knowledge: {enhanced_count:,}")
    print(f"  New entries from wiki: {new_entries_count:,}")
    
    return enhanced_db_path

def is_direct_medicine(term, knowledge_data):
    """Check if the term represents a direct medicine (not just poisoning/condition)"""
    term_lower = term.lower()
    explanation = knowledge_data['detailed_explanation'].lower()
    
    # Skip poisoning/toxicity entries
    if any(suffix in term_lower for suffix in ['poisoning', 'toxicity', 'overdose', 'syndrome']):
        return False
    
    # Check if explanation mentions it's a medicine/drug
    medicine_indicators = ['medication', 'drug', 'medicine', 'pharmaceutical', 'pill', 'tablet', 'capsule']
    return any(indicator in explanation for indicator in medicine_indicators)

if __name__ == "__main__":
    integrate_medical_knowledge()
